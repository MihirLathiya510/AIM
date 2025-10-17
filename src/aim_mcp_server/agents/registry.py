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
        
        except Exception as e:
            # If agent initialization fails, log but don't crash
            print(f"Warning: Failed to initialize some agents: {e}")
    
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

