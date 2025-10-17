"""
Tests for task manager.
"""

import pytest
from aim_mcp_server.task_manager import TaskManager
from aim_mcp_server.storage import TaskStatus


def test_create_task():
    """Test task creation."""
    manager = TaskManager()
    
    task = manager.create_task(
        description="Create a Python function to calculate fibonacci numbers with unit tests",
        context={"language": "Python"}
    )
    
    assert task is not None
    assert task.task_id is not None
    assert task.description is not None
    assert task.status == TaskStatus.PENDING
    assert len(task.subtasks) > 0


def test_get_task():
    """Test task retrieval."""
    manager = TaskManager()
    
    # Create a task
    task = manager.create_task(
        description="Test task",
        context={}
    )
    
    # Retrieve it
    retrieved = manager.get_task(task.task_id)
    
    assert retrieved is not None
    assert retrieved.task_id == task.task_id
    assert retrieved.description == task.description


def test_update_task_status():
    """Test task status update."""
    manager = TaskManager()
    
    # Create a task
    task = manager.create_task(
        description="Test task",
        context={}
    )
    
    # Update status
    success = manager.update_task_status(task.task_id, TaskStatus.IN_PROGRESS)
    assert success is True
    
    # Verify update
    retrieved = manager.get_task(task.task_id)
    assert retrieved.status == TaskStatus.IN_PROGRESS


def test_list_tasks():
    """Test task listing."""
    manager = TaskManager()
    
    # Create some tasks
    manager.create_task("Task 1", {})
    manager.create_task("Task 2", {})
    
    # List all tasks
    tasks = manager.list_tasks()
    
    assert len(tasks) >= 2


def test_constraint_parsing():
    """Test constraint extraction."""
    manager = TaskManager()
    
    task = manager.create_task(
        description="Implement feature with >90% test coverage using TypeScript and FIDO2 compliance",
        context={}
    )
    
    assert len(task.constraints) > 0

