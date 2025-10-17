"""
Task manager for orchestrating complex tasks.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from .agents.base import AgentTask, AgentType
from .agents.registry import AgentRegistry
from .storage import Storage, TaskStatus
from .utils.constraints import ConstraintParser, Constraint
from .utils.logging import AuditLogger


@dataclass
class Subtask:
    """Represents a subtask within a larger task."""
    id: str
    description: str
    agent_type: AgentType
    status: TaskStatus = TaskStatus.PENDING
    output: Optional[Any] = None
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Task:
    """Represents a complete task with subtasks."""
    task_id: str
    description: str
    constraints: List[Constraint]
    status: TaskStatus
    subtasks: List[Subtask]
    created_at: str
    output: Optional[Any] = None
    context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class TaskManager:
    """Manages task decomposition, assignment, and execution."""
    
    def __init__(
        self,
        storage: Optional[Storage] = None,
        audit_logger: Optional[AuditLogger] = None,
        agent_registry: Optional[AgentRegistry] = None
    ):
        """
        Initialize task manager.
        
        Args:
            storage: Storage instance
            audit_logger: Audit logger instance
            agent_registry: Agent registry instance
        """
        self.storage = storage or Storage()
        self.audit_logger = audit_logger or AuditLogger()
        self.agent_registry = agent_registry or AgentRegistry()
    
    def create_task(
        self,
        description: str,
        context: Optional[Dict[str, Any]] = None,
        deadline: Optional[str] = None
    ) -> Task:
        """
        Create a new task with automatic decomposition.
        
        Args:
            description: Task description
            context: Additional context
            deadline: Optional deadline
            
        Returns:
            Created task
        """
        task_id = str(uuid.uuid4())
        
        # Parse constraints from description
        constraints = ConstraintParser.parse(description)
        
        # Decompose into subtasks
        subtasks = self._decompose_task(description, constraints)
        
        # Create task
        task = Task(
            task_id=task_id,
            description=description,
            constraints=constraints,
            status=TaskStatus.PENDING,
            subtasks=subtasks,
            created_at=datetime.utcnow().isoformat(),
            context=context or {},
            metadata={"deadline": deadline} if deadline else {}
        )
        
        # Persist task
        self._save_task(task)
        
        # Log event
        self.audit_logger.log_event(
            task_id=task_id,
            event_type="task_created",
            data={
                "description": description,
                "num_subtasks": len(subtasks),
                "num_constraints": len(constraints),
            }
        )
        
        return task
    
    def _decompose_task(
        self,
        description: str,
        constraints: List[Constraint]
    ) -> List[Subtask]:
        """
        Decompose a task into subtasks.
        
        Args:
            description: Task description
            constraints: List of constraints
            
        Returns:
            List of subtasks
        """
        subtasks = []
        
        # Simple keyword-based decomposition
        # In production, this would use an LLM for intelligent decomposition
        
        description_lower = description.lower()
        
        # Check for coding tasks
        if any(word in description_lower for word in ["code", "implement", "refactor", "develop"]):
            subtasks.append(Subtask(
                id=str(uuid.uuid4()),
                description=f"Implement: {description}",
                agent_type=AgentType.CODING
            ))
        
        # Check for testing tasks
        if any(word in description_lower for word in ["test", "testing", "unit test", "coverage"]):
            subtasks.append(Subtask(
                id=str(uuid.uuid4()),
                description=f"Create tests for: {description}",
                agent_type=AgentType.TESTING,
                dependencies=[subtasks[0].id] if subtasks else []
            ))
        
        # Check for documentation tasks
        if any(word in description_lower for word in ["document", "documentation", "readme", "docs", "api doc"]):
            subtasks.append(Subtask(
                id=str(uuid.uuid4()),
                description=f"Generate documentation for: {description}",
                agent_type=AgentType.DOCUMENTATION,
                dependencies=[st.id for st in subtasks]
            ))
        
        # If no specific subtasks identified, create a general task
        if not subtasks:
            subtasks.append(Subtask(
                id=str(uuid.uuid4()),
                description=description,
                agent_type=AgentType.GENERAL
            ))
        
        return subtasks
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """
        Get a task by ID.
        
        Args:
            task_id: The task ID
            
        Returns:
            Task or None if not found
        """
        task_data = self.storage.load_task(task_id)
        
        if not task_data:
            return None
        
        return self._task_from_dict(task_data)
    
    def update_task_status(self, task_id: str, status: TaskStatus) -> bool:
        """
        Update task status.
        
        Args:
            task_id: The task ID
            status: New status
            
        Returns:
            True if updated
        """
        success = self.storage.update_task_status(task_id, status)
        
        if success:
            self.audit_logger.log_event(
                task_id=task_id,
                event_type="status_updated",
                data={"new_status": status.value}
            )
        
        return success
    
    def update_subtask(
        self,
        task_id: str,
        subtask_id: str,
        status: Optional[TaskStatus] = None,
        output: Optional[Any] = None
    ) -> bool:
        """
        Update a subtask.
        
        Args:
            task_id: The task ID
            subtask_id: The subtask ID
            status: New status (optional)
            output: New output (optional)
            
        Returns:
            True if updated
        """
        task = self.get_task(task_id)
        
        if not task:
            return False
        
        for subtask in task.subtasks:
            if subtask.id == subtask_id:
                if status:
                    subtask.status = status
                if output is not None:
                    subtask.output = output
                
                self._save_task(task)
                
                self.audit_logger.log_event(
                    task_id=task_id,
                    event_type="subtask_updated",
                    data={
                        "subtask_id": subtask_id,
                        "status": status.value if status else None,
                    }
                )
                
                return True
        
        return False
    
    def list_tasks(
        self,
        status: Optional[TaskStatus] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        List tasks.
        
        Args:
            status: Filter by status
            limit: Maximum number of tasks
            
        Returns:
            List of task summaries
        """
        return self.storage.list_tasks(status, limit)
    
    def _save_task(self, task: Task) -> None:
        """Save task to storage."""
        task_dict = self._task_to_dict(task)
        self.storage.save_task(task.task_id, task_dict)
    
    def _task_to_dict(self, task: Task) -> Dict[str, Any]:
        """Convert task to dictionary."""
        return {
            "task_id": task.task_id,
            "description": task.description,
            "constraints": [str(c) for c in task.constraints],
            "status": task.status.value,
            "subtasks": [
                {
                    "id": st.id,
                    "description": st.description,
                    "agent_type": st.agent_type.value,
                    "status": st.status.value,
                    "output": st.output,
                    "dependencies": st.dependencies,
                    "metadata": st.metadata,
                }
                for st in task.subtasks
            ],
            "created_at": task.created_at,
            "output": task.output,
            "context": task.context,
            "metadata": task.metadata,
        }
    
    def _task_from_dict(self, data: Dict[str, Any]) -> Task:
        """Convert dictionary to task."""
        return Task(
            task_id=data["task_id"],
            description=data["description"],
            constraints=[],  # Would need to deserialize properly
            status=TaskStatus(data["status"]),
            subtasks=[
                Subtask(
                    id=st["id"],
                    description=st["description"],
                    agent_type=AgentType(st["agent_type"]),
                    status=TaskStatus(st["status"]),
                    output=st.get("output"),
                    dependencies=st.get("dependencies", []),
                    metadata=st.get("metadata", {}),
                )
                for st in data.get("subtasks", [])
            ],
            created_at=data["created_at"],
            output=data.get("output"),
            context=data.get("context", {}),
            metadata=data.get("metadata", {}),
        )

