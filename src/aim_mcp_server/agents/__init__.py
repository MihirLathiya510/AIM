"""Agent interfaces and implementations."""

from .base import Agent, AgentType, AgentCapability
from .claude import ClaudeAgent
from .claude_code import ClaudeCodeAgent
from .registry import AgentRegistry

__all__ = ["Agent", "AgentType", "AgentCapability", "ClaudeAgent", "ClaudeCodeAgent", "AgentRegistry"]

