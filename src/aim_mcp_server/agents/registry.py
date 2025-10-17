"""
Agent registry for managing and routing to different agent types.

Supports two modes:
1. API Mode: Uses ClaudeAgent with API key (full autonomous operation)
2. Claude Code Mode: Uses ClaudeCodeAgent (for Pro users without API key)
"""

from typing import Dict, List, Optional
from .base import Agent, AgentType, AgentCapability, AgentTask
from .claude import ClaudeAgent
from .claude_code import ClaudeCodeAgent


class AgentRegistry:
    """Registry for managing different agent types."""
    
    def __init__(self):
        """Initialize agent registry."""
        self.agents: Dict[AgentType, Agent] = {}
        self.mode: str = "unknown"  # "api" or "claude_code"
        self._initialize_default_agents()
    
    def _initialize_default_agents(self) -> None:
        """
        Initialize default agent pool.
        
        Supports two modes:
        1. API Mode: If ANTHROPIC_API_KEY is set, use ClaudeAgent (autonomous)
        2. Claude Code Mode: If no API key, use ClaudeCodeAgent (delegated)
        """
        import os
        import sys
        
        has_api_key = bool(os.getenv("ANTHROPIC_API_KEY"))
        
        if has_api_key:
            # MODE 1: API Key available - Use ClaudeAgent for autonomous operation
            print("🔑 AIM Mode: API Key detected - Using autonomous Claude API", file=sys.stderr)
            self.mode = "api"
            
            try:
                # Create specialized agents with API access
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
                
                print("✓ All API-based agents initialized successfully", file=sys.stderr)
            
            except ValueError:
                # Re-raise ValueError (from API key validation)
                raise
            except Exception as e:
                # For other unexpected errors, provide clear error message
                error_msg = f"Failed to initialize API agents: {e}"
                print(f"ERROR: {error_msg}", file=sys.stderr)
                raise RuntimeError(error_msg) from e
        
        else:
            # MODE 2: No API Key - Use ClaudeCodeAgent (delegated mode)
            print("💬 AIM Mode: No API key - Using Claude Code delegation", file=sys.stderr)
            print("   Tasks will be delegated back to Claude Code for execution", file=sys.stderr)
            print("   This mode works with Claude Pro without requiring API access", file=sys.stderr)
            self.mode = "claude_code"
            
            try:
                # Create specialized agents that delegate to Claude Code
                self.agents[AgentType.CODING] = ClaudeCodeAgent(
                    agent_type=AgentType.CODING,
                    capabilities=[
                        AgentCapability.CODE_GENERATION,
                        AgentCapability.REFACTORING,
                    ]
                )
                
                self.agents[AgentType.TESTING] = ClaudeCodeAgent(
                    agent_type=AgentType.TESTING,
                    capabilities=[AgentCapability.TEST_GENERATION]
                )
                
                self.agents[AgentType.DOCUMENTATION] = ClaudeCodeAgent(
                    agent_type=AgentType.DOCUMENTATION,
                    capabilities=[AgentCapability.DOCUMENTATION]
                )
                
                self.agents[AgentType.REVIEW] = ClaudeCodeAgent(
                    agent_type=AgentType.REVIEW,
                    capabilities=[
                        AgentCapability.CODE_REVIEW,
                        AgentCapability.VALIDATION,
                    ]
                )
                
                self.agents[AgentType.GENERAL] = ClaudeCodeAgent(
                    agent_type=AgentType.GENERAL,
                    capabilities=list(AgentCapability)
                )
                
                print("✓ All Claude Code delegation agents initialized successfully", file=sys.stderr)
            
            except Exception as e:
                # For unexpected errors
                error_msg = f"Failed to initialize Claude Code agents: {e}"
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

