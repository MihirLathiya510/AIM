"""
Tests for MCP server implementation.
"""

import pytest
from aim_mcp_server.server import create_server


def test_create_server():
    """Test server creation."""
    server = create_server()
    assert server is not None
    assert server.name == "aim-mcp-server"


@pytest.mark.asyncio
async def test_list_tools():
    """Test tool listing."""
    server = create_server()
    
    # Get the list_tools handler
    tools = await server._tool_list_handler()
    
    assert len(tools) > 0
    tool_names = [t.name for t in tools]
    
    assert "create_task" in tool_names
    assert "execute_task" in tool_names
    assert "get_task_status" in tool_names
    assert "get_task_output" in tool_names
    assert "review_and_iterate" in tool_names
    assert "list_tasks" in tool_names


@pytest.mark.asyncio
async def test_list_resources():
    """Test resource listing."""
    server = create_server()
    
    # Get the list_resources handler
    resources = await server._resource_list_handler()
    
    assert len(resources) > 0
    resource_uris = [r.uri for r in resources]
    
    assert "aim://tasks" in resource_uris
    assert "aim://audit-logs" in resource_uris

