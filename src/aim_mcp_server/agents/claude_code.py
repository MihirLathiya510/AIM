"""
Claude Code agent implementation for Pro users without API keys.

This agent delegates work back to Claude Code itself, allowing Pro users
to use AIM without needing separate API access.
"""

from typing import List, Optional

from .base import Agent, AgentType, AgentCapability, AgentTask, AgentOutput


class ClaudeCodeAgent(Agent):
    """
    Agent implementation that delegates work back to Claude Code.
    
    This is for users with Claude Pro subscription but without API access.
    Instead of making direct API calls, it returns prompts that Claude Code
    will execute through the MCP protocol.
    """
    
    def __init__(
        self,
        agent_type: AgentType = AgentType.GENERAL,
        capabilities: Optional[List[AgentCapability]] = None
    ):
        """
        Initialize Claude Code agent.
        
        Args:
            agent_type: Type of agent
            capabilities: List of capabilities (defaults to all)
        """
        if capabilities is None:
            capabilities = list(AgentCapability)
        
        super().__init__(agent_type, capabilities)
        
        self.agent_type = agent_type
    
    async def execute(self, task: AgentTask) -> AgentOutput:
        """
        Execute a task by delegating to Claude Code.
        
        Instead of making API calls, this returns a structured prompt that
        Claude Code will execute. The MCP server will pass this back to
        Claude Code to handle.
        
        Args:
            task: The task to execute
            
        Returns:
            Agent output containing the prompt for Claude Code to execute
        """
        # Build the prompt that Claude Code will execute
        prompt = self._build_execution_prompt(task)
        
        # Return as a special output format that indicates delegation
        return AgentOutput(
            task_id=task.id,
            success=True,
            output=prompt,
            metadata={
                "mode": "claude_code_delegation",
                "agent_type": self.agent_type.value,
                "iteration": task.iteration,
                "requires_human_execution": True
            }
        )
    
    async def validate_capability(self, capability: AgentCapability) -> bool:
        """Check if agent has a capability."""
        return capability in self.capabilities
    
    def _build_execution_prompt(self, task: AgentTask) -> str:
        """
        Build a prompt for Claude Code to execute.
        
        This creates a well-structured prompt that Claude Code can follow
        to accomplish the task according to AIM's requirements.
        """
        # Build specialized prompt based on agent type
        type_context = {
            AgentType.CODING: "You are a coding specialist. Focus on writing high-quality, well-structured code.",
            AgentType.TESTING: "You are a testing specialist. Focus on comprehensive test coverage and quality.",
            AgentType.DOCUMENTATION: "You are a documentation specialist. Create clear, detailed documentation.",
            AgentType.REVIEW: "You are a code reviewer. Carefully validate the output against requirements.",
            AgentType.GENERAL: "You are a versatile AI assistant capable of handling various tasks."
        }
        
        prompt = f"""**AIM Task Execution Request**

{type_context.get(self.agent_type, type_context[AgentType.GENERAL])}

**Task Description:**
{task.description}
"""
        
        # Add context if provided
        if task.context:
            prompt += "\n**Context:**\n"
            for key, value in task.context.items():
                prompt += f"- {key}: {value}\n"
        
        # Add constraints
        if task.constraints:
            prompt += "\n**CRITICAL - You must satisfy ALL of these constraints:**\n"
            for i, constraint in enumerate(task.constraints, 1):
                prompt += f"{i}. {constraint}\n"
        
        # Add iteration feedback if this is a refinement
        if task.iteration > 0 and task.feedback:
            prompt += f"\n**Iteration {task.iteration + 1} - Feedback from previous attempt:**\n"
            prompt += f"{task.feedback}\n\n"
            prompt += "Please address ALL the feedback points and ensure ALL constraints are met.\n"
        
        # Add execution instructions
        prompt += """
**Instructions:**
1. Read all requirements and constraints carefully
2. Complete the task exactly as specified
3. Verify that your output meets ALL constraints
4. If this is a refinement iteration, address ALL feedback points

Please proceed with the task now.
"""
        
        return prompt

