"""
AI Agent Manager (AIM) - MCP Server

A Meta Control Plane server for orchestrating multi-agent tasks with
iterative refinement, constraint enforcement, and validation.
"""

__version__ = "0.1.0"

from .server import create_server

__all__ = ["create_server", "__version__"]

