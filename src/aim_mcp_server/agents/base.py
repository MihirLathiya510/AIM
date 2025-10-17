"""
Abstract base classes for AI agents.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class AgentType(Enum):
    """Types of specialized agents."""
    CODING = "coding"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    REVIEW = "review"
    GENERAL = "general"


class AgentCapability(Enum):
    """Capabilities that agents can have."""
    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review"
    TEST_GENERATION = "test_generation"
    DOCUMENTATION = "documentation"
    VALIDATION = "validation"
    REFACTORING = "refactoring"


@dataclass
class AgentTask:
    """Represents a task to be executed by an agent."""
    id: str
    description: str
    context: Dict[str, Any]
    constraints: List[Any]  # List of Constraint objects
    iteration: int = 0
    feedback: Optional[str] = None


@dataclass
class AgentOutput:
    """Output from an agent execution."""
    task_id: str
    success: bool
    output: Any
    metadata: Dict[str, Any]
    error: Optional[str] = None


class Agent(ABC):
    """Abstract base class for all AI agents."""
    
    def __init__(self, agent_type: AgentType, capabilities: List[AgentCapability]):
        """
        Initialize an agent.
        
        Args:
            agent_type: The type of agent
            capabilities: List of capabilities this agent has
        """
        self.agent_type = agent_type
        self.capabilities = capabilities
    
    @abstractmethod
    async def execute(self, task: AgentTask) -> AgentOutput:
        """
        Execute a task.
        
        Args:
            task: The task to execute
            
        Returns:
            The agent's output
        """
        pass
    
    @abstractmethod
    async def validate_capability(self, capability: AgentCapability) -> bool:
        """
        Check if agent has a specific capability.
        
        Args:
            capability: The capability to check
            
        Returns:
            True if agent has the capability
        """
        pass
    
    def can_handle(self, task: AgentTask) -> bool:
        """
        Determine if this agent can handle a task.
        
        Args:
            task: The task to check
            
        Returns:
            True if agent can handle the task
        """
        # Basic implementation - can be overridden
        return True

