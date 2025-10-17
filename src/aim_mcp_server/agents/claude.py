"""
Claude AI agent implementation.
"""

import os
from typing import List, Optional
from anthropic import Anthropic, AsyncAnthropic

from .base import Agent, AgentType, AgentCapability, AgentTask, AgentOutput


class ClaudeAgent(Agent):
    """Agent implementation using Claude API."""
    
    def __init__(
        self,
        agent_type: AgentType = AgentType.GENERAL,
        capabilities: Optional[List[AgentCapability]] = None,
        model: str = "claude-3-5-sonnet-20241022",
        api_key: Optional[str] = None
    ):
        """
        Initialize Claude agent.
        
        Args:
            agent_type: Type of agent
            capabilities: List of capabilities (defaults to all)
            model: Claude model to use
            api_key: Anthropic API key (defaults to env var)
        """
        if capabilities is None:
            capabilities = list(AgentCapability)
        
        super().__init__(agent_type, capabilities)
        
        self.model = model
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        
        self.client = AsyncAnthropic(api_key=self.api_key)
    
    async def execute(self, task: AgentTask) -> AgentOutput:
        """
        Execute a task using Claude.
        
        Args:
            task: The task to execute
            
        Returns:
            Agent output
        """
        try:
            # Build system prompt based on agent type
            system_prompt = self._build_system_prompt(task)
            
            # Build user prompt with task and context
            user_prompt = self._build_user_prompt(task)
            
            # Call Claude API
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            # Extract text content
            output_text = ""
            for block in response.content:
                if hasattr(block, "text"):
                    output_text += block.text
            
            return AgentOutput(
                task_id=task.id,
                success=True,
                output=output_text,
                metadata={
                    "model": self.model,
                    "agent_type": self.agent_type.value,
                    "iteration": task.iteration,
                    "usage": {
                        "input_tokens": response.usage.input_tokens,
                        "output_tokens": response.usage.output_tokens,
                    }
                }
            )
        
        except Exception as e:
            return AgentOutput(
                task_id=task.id,
                success=False,
                output=None,
                metadata={
                    "model": self.model,
                    "agent_type": self.agent_type.value,
                    "iteration": task.iteration,
                },
                error=str(e)
            )
    
    async def validate_capability(self, capability: AgentCapability) -> bool:
        """Check if agent has a capability."""
        return capability in self.capabilities
    
    def _build_system_prompt(self, task: AgentTask) -> str:
        """Build system prompt based on agent type."""
        base_prompt = "You are a highly capable AI assistant specialized in "
        
        type_prompts = {
            AgentType.CODING: "writing high-quality, well-structured code. You follow best practices, write clean code, and ensure maintainability.",
            AgentType.TESTING: "creating comprehensive test suites. You write thorough unit tests, integration tests, and ensure high code coverage.",
            AgentType.DOCUMENTATION: "creating clear, comprehensive documentation. You write detailed API docs, README files, and user guides.",
            AgentType.REVIEW: "reviewing and validating outputs. You check for errors, constraint violations, and ensure quality standards are met.",
            AgentType.GENERAL: "solving complex problems across various domains. You are versatile and can handle diverse tasks effectively.",
        }
        
        prompt = base_prompt + type_prompts.get(self.agent_type, type_prompts[AgentType.GENERAL])
        
        # Add constraint awareness
        if task.constraints:
            prompt += "\n\nIMPORTANT: You must strictly adhere to the following constraints:\n"
            for i, constraint in enumerate(task.constraints, 1):
                prompt += f"{i}. {constraint}\n"
        
        # Add feedback if this is a refinement iteration
        if task.feedback:
            prompt += f"\n\nFEEDBACK FROM PREVIOUS ITERATION:\n{task.feedback}\n"
            prompt += "Please address all feedback and ensure all constraints are met in this iteration."
        
        return prompt
    
    def _build_user_prompt(self, task: AgentTask) -> str:
        """Build user prompt with task details."""
        prompt = f"TASK:\n{task.description}\n"
        
        if task.context:
            prompt += "\n\nCONTEXT:\n"
            for key, value in task.context.items():
                prompt += f"- {key}: {value}\n"
        
        if task.iteration > 0:
            prompt += f"\n\nThis is iteration {task.iteration + 1}. "
            prompt += "Please refine your previous output based on the feedback provided."
        
        return prompt

