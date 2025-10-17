"""
MCP Server implementation for AIM.
"""

import asyncio
from typing import Any, Dict, Optional
from mcp.server import Server
from mcp.types import Tool, TextContent, Resource, Prompt

from .task_manager import TaskManager
from .refinement_loop import RefinementLoop
from .review import ReviewSystem
from .agents.registry import AgentRegistry
from .storage import Storage, TaskStatus
from .utils.logging import AuditLogger


def create_server() -> Server:
    """Create and configure the AIM MCP server."""
    
    # Initialize components
    storage = Storage()
    audit_logger = AuditLogger()
    agent_registry = AgentRegistry()
    task_manager = TaskManager(storage, audit_logger, agent_registry)
    review_system = ReviewSystem(agent_registry)
    refinement_loop = RefinementLoop(agent_registry, review_system, audit_logger)
    
    # Create MCP server
    server = Server("aim-mcp-server")
    
    # Register tools
    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List available tools."""
        return [
            Tool(
                name="create_task",
                description="Create a new orchestrated task with automatic decomposition and constraint parsing",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "description": {
                            "type": "string",
                            "description": "Detailed task description including requirements and constraints"
                        },
                        "context": {
                            "type": "object",
                            "description": "Additional context for the task (optional)",
                            "additionalProperties": True
                        },
                        "deadline": {
                            "type": "string",
                            "description": "Optional deadline in ISO format (optional)"
                        }
                    },
                    "required": ["description"]
                }
            ),
            Tool(
                name="get_task_status",
                description="Get the current status and progress of a task",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "description": "The task ID"
                        }
                    },
                    "required": ["task_id"]
                }
            ),
            Tool(
                name="get_task_output",
                description="Get the final validated output or current iteration results for a task",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "description": "The task ID"
                        }
                    },
                    "required": ["task_id"]
                }
            ),
            Tool(
                name="execute_task",
                description="Execute a task with iterative refinement until all constraints are met",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "description": "The task ID to execute"
                        }
                    },
                    "required": ["task_id"]
                }
            ),
            Tool(
                name="review_and_iterate",
                description="Manually trigger additional refinement iterations with user feedback",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "description": "The task ID"
                        },
                        "feedback": {
                            "type": "string",
                            "description": "User feedback for refinement"
                        }
                    },
                    "required": ["task_id", "feedback"]
                }
            ),
            Tool(
                name="list_tasks",
                description="List all tasks with optional status filter",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "enum": ["pending", "in_progress", "completed", "failed", "cancelled"],
                            "description": "Filter by status (optional)"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of tasks to return (default: 100)",
                            "default": 100
                        }
                    }
                }
            )
        ]
    
    @server.call_tool()
    async def call_tool(name: str, arguments: Any) -> list[TextContent]:
        """Handle tool calls."""
        
        if name == "create_task":
            task = task_manager.create_task(
                description=arguments["description"],
                context=arguments.get("context"),
                deadline=arguments.get("deadline")
            )
            
            result = {
                "task_id": task.task_id,
                "status": task.status.value,
                "num_subtasks": len(task.subtasks),
                "num_constraints": len(task.constraints),
                "subtasks": [
                    {
                        "id": st.id,
                        "description": st.description,
                        "agent_type": st.agent_type.value,
                        "status": st.status.value
                    }
                    for st in task.subtasks
                ],
                "constraints": [str(c) for c in task.constraints]
            }
            
            return [TextContent(
                type="text",
                text=f"Task created successfully!\n\n{format_dict(result)}"
            )]
        
        elif name == "get_task_status":
            task = task_manager.get_task(arguments["task_id"])
            
            if not task:
                return [TextContent(
                    type="text",
                    text=f"Task {arguments['task_id']} not found"
                )]
            
            result = {
                "task_id": task.task_id,
                "description": task.description,
                "status": task.status.value,
                "created_at": task.created_at,
                "subtasks": [
                    {
                        "id": st.id,
                        "description": st.description,
                        "status": st.status.value,
                        "agent_type": st.agent_type.value
                    }
                    for st in task.subtasks
                ]
            }
            
            return [TextContent(
                type="text",
                text=format_dict(result)
            )]
        
        elif name == "get_task_output":
            task = task_manager.get_task(arguments["task_id"])
            
            if not task:
                return [TextContent(
                    type="text",
                    text=f"Task {arguments['task_id']} not found"
                )]
            
            if task.output:
                output_text = f"Task Output:\n\n{task.output}"
            else:
                # Show subtask outputs
                output_text = "Subtask Outputs:\n\n"
                for st in task.subtasks:
                    output_text += f"## {st.description}\n"
                    output_text += f"Status: {st.status.value}\n"
                    if st.output:
                        output_text += f"Output:\n{st.output}\n\n"
                    else:
                        output_text += "No output yet\n\n"
            
            return [TextContent(type="text", text=output_text)]
        
        elif name == "execute_task":
            task = task_manager.get_task(arguments["task_id"])
            
            if not task:
                return [TextContent(
                    type="text",
                    text=f"Task {arguments['task_id']} not found"
                )]
            
            # Update task status
            task_manager.update_task_status(task.task_id, TaskStatus.IN_PROGRESS)
            
            # Execute each subtask with refinement
            all_outputs = []
            for subtask in task.subtasks:
                success = await refinement_loop.refine_subtask(
                    task_manager,
                    task.task_id,
                    subtask.id
                )
                
                # Reload task to get updated subtask
                task = task_manager.get_task(task.task_id)
                for st in task.subtasks:
                    if st.id == subtask.id:
                        all_outputs.append({
                            "subtask": st.description,
                            "success": success,
                            "output": st.output
                        })
                        break
            
            # Update overall task status
            all_success = all(task.subtasks[i].status == TaskStatus.COMPLETED for i in range(len(task.subtasks)))
            final_status = TaskStatus.COMPLETED if all_success else TaskStatus.FAILED
            task_manager.update_task_status(task.task_id, final_status)
            
            # Compile final output
            final_output = "\n\n".join([
                f"=== {out['subtask']} ===\n{out['output']}"
                for out in all_outputs if out['output']
            ])
            
            # Save final output to task
            task = task_manager.get_task(task.task_id)
            task.output = final_output
            task_manager._save_task(task)
            
            result_text = f"Task Execution Complete!\n\n"
            result_text += f"Status: {final_status.value}\n"
            result_text += f"Subtasks Completed: {sum(1 for st in task.subtasks if st.status == TaskStatus.COMPLETED)}/{len(task.subtasks)}\n\n"
            result_text += f"Final Output:\n\n{final_output}"
            
            return [TextContent(type="text", text=result_text)]
        
        elif name == "review_and_iterate":
            task = task_manager.get_task(arguments["task_id"])
            
            if not task:
                return [TextContent(
                    type="text",
                    text=f"Task {arguments['task_id']} not found"
                )]
            
            # Get current output
            current_output = task.output or "No output yet"
            
            # Create refinement task with user feedback
            result = await refinement_loop.refine_until_perfect(
                task_description=task.description + "\n\nUser Feedback: " + arguments["feedback"],
                constraints=task.constraints,
                context=task.context,
                task_id=task.task_id
            )
            
            # Update task
            task.output = result.final_output
            task_manager._save_task(task)
            
            result_text = f"Refinement Complete!\n\n"
            result_text += f"Iterations: {result.total_iterations}\n"
            result_text += f"Final Score: {result.final_score:.2f}\n"
            result_text += f"Success: {result.success}\n\n"
            result_text += f"Output:\n\n{result.final_output}"
            
            return [TextContent(type="text", text=result_text)]
        
        elif name == "list_tasks":
            status = None
            if "status" in arguments:
                status = TaskStatus(arguments["status"])
            
            limit = arguments.get("limit", 100)
            
            tasks = task_manager.list_tasks(status, limit)
            
            if not tasks:
                return [TextContent(
                    type="text",
                    text="No tasks found"
                )]
            
            result_text = f"Tasks (showing {len(tasks)}):\n\n"
            for task_info in tasks:
                result_text += f"- {task_info['task_id']}\n"
                result_text += f"  Description: {task_info['description']}\n"
                result_text += f"  Status: {task_info['status']}\n"
                result_text += f"  Created: {task_info['created_at']}\n\n"
            
            return [TextContent(type="text", text=result_text)]
        
        return [TextContent(
            type="text",
            text=f"Unknown tool: {name}"
        )]
    
    # Register resources
    @server.list_resources()
    async def list_resources() -> list[Resource]:
        """List available resources."""
        return [
            Resource(
                uri="aim://tasks",
                name="All Tasks",
                description="Access to all task data",
                mimeType="application/json"
            ),
            Resource(
                uri="aim://audit-logs",
                name="Audit Logs",
                description="Access to audit trail logs",
                mimeType="application/json"
            )
        ]
    
    @server.read_resource()
    async def read_resource(uri: str) -> str:
        """Read resource content."""
        if uri == "aim://tasks":
            tasks = task_manager.list_tasks()
            import json
            return json.dumps(tasks, indent=2)
        elif uri == "aim://audit-logs":
            # Would need to implement reading all audit logs
            return "Audit logs access not fully implemented"
        
        return f"Unknown resource: {uri}"
    
    return server


def format_dict(d: Dict[str, Any], indent: int = 0) -> str:
    """Format dictionary for readable output."""
    import json
    return json.dumps(d, indent=2)

