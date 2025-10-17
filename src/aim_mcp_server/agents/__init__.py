"""Agent interfaces and implementations."""

from .base import Agent, AgentType, AgentCapability
from .claude import ClaudeAgent
from .registry import AgentRegistry

__all__ = ["Agent", "AgentType", "AgentCapability", "ClaudeAgent", "AgentRegistry"]

