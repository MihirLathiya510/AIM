"""
Iterative refinement loop for ensuring exact user requirements.
"""

from dataclasses import dataclass
from typing import Any, List, Optional

from .agents.base import AgentTask, Agent
from .agents.registry import AgentRegistry
from .review import ReviewSystem, ValidationResult
from .storage import TaskStatus
from .task_manager import Task, TaskManager
from .utils.constraints import Constraint
from .utils.logging import AuditLogger


@dataclass
class RefinementIteration:
    """Represents a single iteration in the refinement loop."""
    iteration: int
    output: Any
    validation: ValidationResult
    agent_metadata: dict


@dataclass
class RefinementResult:
    """Result of the complete refinement process."""
    success: bool
    final_output: Any
    iterations: List[RefinementIteration]
    total_iterations: int
    final_score: float


class RefinementLoop:
    """Manages iterative refinement until output meets all requirements."""
    
    def __init__(
        self,
        agent_registry: Optional[AgentRegistry] = None,
        review_system: Optional[ReviewSystem] = None,
        audit_logger: Optional[AuditLogger] = None,
        max_iterations: int = 10
    ):
        """
        Initialize refinement loop.
        
        Args:
            agent_registry: Agent registry
            review_system: Review system
            audit_logger: Audit logger
            max_iterations: Maximum refinement iterations
        """
        self.agent_registry = agent_registry or AgentRegistry()
        self.review_system = review_system or ReviewSystem(self.agent_registry)
        self.audit_logger = audit_logger or AuditLogger()
        self.max_iterations = max_iterations
    
    async def refine_until_perfect(
        self,
        task_description: str,
        constraints: List[Constraint],
        agent: Optional[Agent] = None,
        context: Optional[dict] = None,
        task_id: Optional[str] = None
    ) -> RefinementResult:
        """
        Iteratively refine output until all constraints are met.
        
        Args:
            task_description: The task to execute
            constraints: List of constraints to satisfy
            agent: Agent to use (auto-selected if None)
            context: Additional context
            task_id: Task ID for logging
            
        Returns:
            Refinement result with final output and history
        """
        iterations = []
        current_output = None
        current_feedback = None
        
        # Auto-select agent if not provided
        if agent is None:
            agent_task = AgentTask(
                id=task_id or "auto",
                description=task_description,
                context=context or {},
                constraints=constraints
            )
            agent = self.agent_registry.get_agent_for_task(agent_task)
        
        for iteration in range(self.max_iterations):
            # Log iteration start
            if task_id:
                self.audit_logger.log_event(
                    task_id=task_id,
                    event_type="refinement_iteration_start",
                    data={"iteration": iteration}
                )
            
            # Create agent task
            agent_task = AgentTask(
                id=f"{task_id or 'task'}_{iteration}",
                description=task_description,
                context=context or {},
                constraints=constraints,
                iteration=iteration,
                feedback=current_feedback
            )
            
            # Execute task
            agent_output = await agent.execute(agent_task)
            
            if not agent_output.success:
                # Agent execution failed
                if task_id:
                    self.audit_logger.log_event(
                        task_id=task_id,
                        event_type="refinement_iteration_failed",
                        data={
                            "iteration": iteration,
                            "error": agent_output.error
                        }
                    )
                
                # Return partial result
                return RefinementResult(
                    success=False,
                    final_output=current_output,
                    iterations=iterations,
                    total_iterations=iteration + 1,
                    final_score=0.0
                )
            
            current_output = agent_output.output
            
            # Validate output
            validation = await self.review_system.validate_output(
                output=current_output,
                constraints=constraints,
                task_description=task_description,
                iteration=iteration
            )
            
            # Record iteration
            iteration_record = RefinementIteration(
                iteration=iteration,
                output=current_output,
                validation=validation,
                agent_metadata=agent_output.metadata
            )
            iterations.append(iteration_record)
            
            # Log iteration result
            if task_id:
                self.audit_logger.log_event(
                    task_id=task_id,
                    event_type="refinement_iteration_complete",
                    data={
                        "iteration": iteration,
                        "score": validation.score,
                        "perfect_match": validation.perfect_match,
                        "num_issues": len(validation.issues)
                    }
                )
            
            # Check if perfect
            if validation.perfect_match:
                return RefinementResult(
                    success=True,
                    final_output=current_output,
                    iterations=iterations,
                    total_iterations=iteration + 1,
                    final_score=validation.score
                )
            
            # Prepare feedback for next iteration
            current_feedback = validation.feedback
            
            # Check if making progress (score improving)
            if iteration > 0:
                previous_score = iterations[iteration - 1].validation.score
                if validation.score <= previous_score:
                    # Not making progress, add note to feedback
                    current_feedback += "\n\nNOTE: Previous iteration had similar or better score. Please try a different approach."
        
        # Max iterations reached without perfection
        final_score = iterations[-1].validation.score if iterations else 0.0
        
        if task_id:
            self.audit_logger.log_event(
                task_id=task_id,
                event_type="refinement_max_iterations_reached",
                data={
                    "total_iterations": self.max_iterations,
                    "final_score": final_score,
                    "perfect_match": False
                }
            )
        
        return RefinementResult(
            success=False,  # Didn't achieve perfection
            final_output=current_output,
            iterations=iterations,
            total_iterations=self.max_iterations,
            final_score=final_score
        )
    
    async def refine_subtask(
        self,
        task_manager: TaskManager,
        task_id: str,
        subtask_id: str
    ) -> bool:
        """
        Execute and refine a specific subtask.
        
        Args:
            task_manager: Task manager instance
            task_id: Parent task ID
            subtask_id: Subtask to execute
            
        Returns:
            True if subtask completed successfully
        """
        task = task_manager.get_task(task_id)
        
        if not task:
            return False
        
        # Find subtask
        subtask = None
        for st in task.subtasks:
            if st.id == subtask_id:
                subtask = st
                break
        
        if not subtask:
            return False
        
        # Update status to in progress
        task_manager.update_subtask(task_id, subtask_id, TaskStatus.IN_PROGRESS)
        
        # Execute with refinement
        result = await self.refine_until_perfect(
            task_description=subtask.description,
            constraints=task.constraints,
            context=task.context,
            task_id=f"{task_id}_{subtask_id}"
        )
        
        # Update subtask with result
        if result.success or result.final_score >= 0.8:  # Accept if good enough
            task_manager.update_subtask(
                task_id,
                subtask_id,
                TaskStatus.COMPLETED,
                result.final_output
            )
            return True
        else:
            task_manager.update_subtask(
                task_id,
                subtask_id,
                TaskStatus.FAILED,
                result.final_output
            )
            return False

