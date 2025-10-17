"""
Review and validation system.
"""

from dataclasses import dataclass
from typing import Any, List, Optional

from .agents.base import AgentTask, AgentOutput, Agent
from .agents.registry import AgentRegistry
from .utils.constraints import Constraint, ConstraintParser


@dataclass
class ValidationIssue:
    """Represents a validation issue found in output."""
    constraint: str
    severity: str  # "critical", "warning", "info"
    description: str
    suggestion: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of validating output against constraints."""
    perfect_match: bool
    issues: List[ValidationIssue]
    score: float  # 0.0 to 1.0
    feedback: str


class ReviewSystem:
    """Manages output review and validation."""
    
    def __init__(self, agent_registry: Optional[AgentRegistry] = None):
        """
        Initialize review system.
        
        Args:
            agent_registry: Agent registry for accessing review agents
        """
        self.agent_registry = agent_registry or AgentRegistry()
    
    async def validate_output(
        self,
        output: Any,
        constraints: List[Constraint],
        task_description: str,
        iteration: int = 0
    ) -> ValidationResult:
        """
        Validate output against constraints.
        
        Args:
            output: The output to validate
            constraints: List of constraints to check
            task_description: Original task description
            iteration: Current iteration number
            
        Returns:
            Validation result with issues and feedback
        """
        issues = []
        
        # Check each constraint
        for constraint in constraints:
            is_valid, error = ConstraintParser.validate_constraint(constraint, output)
            
            if not is_valid:
                issues.append(ValidationIssue(
                    constraint=str(constraint),
                    severity="critical",
                    description=error or "Constraint not met",
                    suggestion=f"Ensure output satisfies: {constraint}"
                ))
        
        # Use review agent for semantic validation
        review_agent = self.agent_registry.get_review_agent()
        
        if review_agent:
            review_task = AgentTask(
                id=f"review_{iteration}",
                description=self._build_review_prompt(
                    task_description,
                    output,
                    constraints
                ),
                context={
                    "task_description": task_description,
                    "output": str(output),
                    "iteration": iteration,
                },
                constraints=constraints,
                iteration=iteration
            )
            
            review_output = await review_agent.execute(review_task)
            
            if review_output.success:
                # Parse review agent's output for additional issues
                additional_issues = self._parse_review_output(review_output.output)
                issues.extend(additional_issues)
        
        # Calculate score based on issues
        if not issues:
            score = 1.0
            perfect_match = True
        else:
            critical_issues = sum(1 for i in issues if i.severity == "critical")
            warning_issues = sum(1 for i in issues if i.severity == "warning")
            
            # Score calculation: penalize critical more than warnings
            penalty = (critical_issues * 0.3) + (warning_issues * 0.1)
            score = max(0.0, 1.0 - penalty)
            perfect_match = False
        
        # Generate feedback
        feedback = self._generate_feedback(issues, constraints, iteration)
        
        return ValidationResult(
            perfect_match=perfect_match,
            issues=issues,
            score=score,
            feedback=feedback
        )
    
    def _build_review_prompt(
        self,
        task_description: str,
        output: Any,
        constraints: List[Constraint]
    ) -> str:
        """Build prompt for review agent."""
        prompt = f"""Review the following output for the given task.

TASK:
{task_description}

CONSTRAINTS:
"""
        for i, constraint in enumerate(constraints, 1):
            prompt += f"{i}. {constraint}\n"
        
        prompt += f"""
OUTPUT TO REVIEW:
{output}

Please carefully review the output and identify any issues:
1. Does it fully satisfy the task requirements?
2. Does it meet all specified constraints?
3. Are there any errors, inconsistencies, or quality issues?
4. Is anything missing or incomplete?

Provide specific, actionable feedback for any issues found.
If the output is perfect, clearly state "OUTPUT IS PERFECT - ALL CONSTRAINTS MET".
"""
        return prompt
    
    def _parse_review_output(self, review_text: str) -> List[ValidationIssue]:
        """Parse review agent output to extract issues."""
        issues = []
        
        # Check if review agent says output is perfect
        if "OUTPUT IS PERFECT" in review_text.upper() or "ALL CONSTRAINTS MET" in review_text.upper():
            return issues
        
        # Simple parsing - look for common issue indicators
        lines = review_text.split("\n")
        for line in lines:
            line_lower = line.lower()
            
            # Look for error/issue indicators
            if any(word in line_lower for word in ["error", "issue", "problem", "missing", "incorrect"]):
                severity = "critical" if any(word in line_lower for word in ["error", "critical", "must"]) else "warning"
                
                issues.append(ValidationIssue(
                    constraint="Quality Review",
                    severity=severity,
                    description=line.strip(),
                    suggestion=None
                ))
        
        return issues
    
    def _generate_feedback(
        self,
        issues: List[ValidationIssue],
        constraints: List[Constraint],
        iteration: int
    ) -> str:
        """Generate actionable feedback from issues."""
        if not issues:
            return "Output meets all requirements and constraints. Excellent work!"
        
        feedback = f"Iteration {iteration + 1} - Issues Found:\n\n"
        
        # Group by severity
        critical = [i for i in issues if i.severity == "critical"]
        warnings = [i for i in issues if i.severity == "warning"]
        
        if critical:
            feedback += "CRITICAL ISSUES (must fix):\n"
            for i, issue in enumerate(critical, 1):
                feedback += f"{i}. {issue.description}\n"
                if issue.suggestion:
                    feedback += f"   Suggestion: {issue.suggestion}\n"
            feedback += "\n"
        
        if warnings:
            feedback += "WARNINGS (should fix):\n"
            for i, issue in enumerate(warnings, 1):
                feedback += f"{i}. {issue.description}\n"
                if issue.suggestion:
                    feedback += f"   Suggestion: {issue.suggestion}\n"
            feedback += "\n"
        
        feedback += "Please address these issues in the next iteration."
        
        return feedback

