"""
Agent registry for managing and routing to different agent types.
"""

from typing import Dict, List, Optional
from .base import Agent, AgentType, AgentCapability, AgentTask
from .claude import ClaudeAgent


class AgentRegistry:
    """Registry for managing different agent types."""
    
    def __init__(self):
        """Initialize agent registry."""
        self.agents: Dict[AgentType, Agent] = {}
        self._initialize_default_agents()
    
    def _initialize_default_agents(self) -> None:
        """Initialize default agent pool."""
        import os
        import sys
        
        # Check for API key before attempting to initialize agents
        if not os.getenv("ANTHROPIC_API_KEY"):
            error_msg = (
                "ANTHROPIC_API_KEY environment variable not set.\n"
                "AIM requires an Anthropic API key to function.\n\n"
                "Please set it with:\n"
                "  export ANTHROPIC_API_KEY='your-key-here'\n\n"
                "Or add it to your Claude Desktop config:\n"
                '  "env": {"ANTHROPIC_API_KEY": "your-key-here"}'
            )
            print(f"ERROR: {error_msg}", file=sys.stderr)
            raise ValueError(error_msg)
        
        try:
            # Create specialized agents
            self.agents[AgentType.CODING] = ClaudeAgent(
                agent_type=AgentType.CODING,
                capabilities=[
                    AgentCapability.CODE_GENERATION,
                    AgentCapability.REFACTORING,
                ]
            )
            
            self.agents[AgentType.TESTING] = ClaudeAgent(
                agent_type=AgentType.TESTING,
                capabilities=[AgentCapability.TEST_GENERATION]
            )
            
            self.agents[AgentType.DOCUMENTATION] = ClaudeAgent(
                agent_type=AgentType.DOCUMENTATION,
                capabilities=[AgentCapability.DOCUMENTATION]
            )
            
            self.agents[AgentType.REVIEW] = ClaudeAgent(
                agent_type=AgentType.REVIEW,
                capabilities=[
                    AgentCapability.CODE_REVIEW,
                    AgentCapability.VALIDATION,
                ]
            )
            
            self.agents[AgentType.GENERAL] = ClaudeAgent(
                agent_type=AgentType.GENERAL,
                capabilities=list(AgentCapability)
            )
        
        except ValueError:
            # Re-raise ValueError (from API key check or ClaudeAgent init)
            raise
        except Exception as e:
            # For other unexpected errors, provide clear error message
            error_msg = f"Failed to initialize AI agents: {e}"
            print(f"ERROR: {error_msg}", file=sys.stderr)
            raise RuntimeError(error_msg) from e
    
    def register_agent(self, agent_type: AgentType, agent: Agent) -> None:
        """
        Register a new agent.
        
        Args:
            agent_type: The type of agent
            agent: The agent instance
        """
        self.agents[agent_type] = agent
    
    def get_agent(self, agent_type: AgentType) -> Optional[Agent]:
        """
        Get an agent by type.
        
        Args:
            agent_type: The type of agent needed
            
        Returns:
            The agent instance or None
        """
        return self.agents.get(agent_type)
    
    def get_agent_for_task(self, task: AgentTask) -> Agent:
        """
        Get the most suitable agent for a task.
        
        Args:
            task: The task to execute
            
        Returns:
            The most suitable agent
        """
        # Simple routing logic based on keywords in task description
        description_lower = task.description.lower()
        
        if any(word in description_lower for word in ["test", "testing", "unit test", "coverage"]):
            agent = self.agents.get(AgentType.TESTING)
            if agent and agent.can_handle(task):
                return agent
        
        if any(word in description_lower for word in ["document", "documentation", "readme", "docs"]):
            agent = self.agents.get(AgentType.DOCUMENTATION)
            if agent and agent.can_handle(task):
                return agent
        
        if any(word in description_lower for word in ["code", "implement", "refactor", "develop"]):
            agent = self.agents.get(AgentType.CODING)
            if agent and agent.can_handle(task):
                return agent
        
        # Default to general agent
        return self.agents.get(AgentType.GENERAL, list(self.agents.values())[0])
    
    def get_review_agent(self) -> Agent:
        """Get the review agent."""
        return self.agents.get(AgentType.REVIEW, self.agents.get(AgentType.GENERAL))
    
    def list_agents(self) -> List[AgentType]:
        """List all registered agent types."""
        return list(self.agents.keys())

