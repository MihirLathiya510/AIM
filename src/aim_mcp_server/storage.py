"""
Storage layer for persisting tasks and state.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from enum import Enum


class TaskStatus(Enum):
    """Status of a task or subtask."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Storage:
    """Manages persistent storage for tasks and state."""
    
    def __init__(self, storage_dir: Optional[Path] = None):
        """
        Initialize storage.
        
        Args:
            storage_dir: Directory for storage (defaults to ~/.aim/tasks/)
        """
        if storage_dir is None:
            storage_dir = Path.home() / ".aim" / "tasks"
        
        self.storage_dir = storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)
    
    def save_task(self, task_id: str, task_data: Dict[str, Any]) -> None:
        """
        Save task data.
        
        Args:
            task_id: The task ID
            task_data: Task data to save
        """
        task_file = self.storage_dir / f"{task_id}.json"
        
        # Add metadata
        task_data["last_updated"] = datetime.utcnow().isoformat()
        
        with open(task_file, "w") as f:
            json.dump(task_data, f, indent=2)
    
    def load_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Load task data.
        
        Args:
            task_id: The task ID
            
        Returns:
            Task data or None if not found
        """
        task_file = self.storage_dir / f"{task_id}.json"
        
        if not task_file.exists():
            return None
        
        with open(task_file, "r") as f:
            return json.load(f)
    
    def list_tasks(
        self,
        status: Optional[TaskStatus] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        List all tasks.
        
        Args:
            status: Filter by status
            limit: Maximum number of tasks to return
            
        Returns:
            List of task summaries
        """
        tasks = []
        
        for task_file in sorted(
            self.storage_dir.glob("*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )[:limit]:
            try:
                with open(task_file, "r") as f:
                    task_data = json.load(f)
                    
                    if status is None or task_data.get("status") == status.value:
                        tasks.append({
                            "task_id": task_data.get("task_id"),
                            "description": task_data.get("description", "")[:100],
                            "status": task_data.get("status"),
                            "created_at": task_data.get("created_at"),
                            "last_updated": task_data.get("last_updated"),
                        })
            except Exception:
                continue
        
        return tasks
    
    def delete_task(self, task_id: str) -> bool:
        """
        Delete a task.
        
        Args:
            task_id: The task ID
            
        Returns:
            True if deleted, False if not found
        """
        task_file = self.storage_dir / f"{task_id}.json"
        
        if task_file.exists():
            task_file.unlink()
            return True
        
        return False
    
    def update_task_status(self, task_id: str, status: TaskStatus) -> bool:
        """
        Update task status.
        
        Args:
            task_id: The task ID
            status: New status
            
        Returns:
            True if updated, False if not found
        """
        task_data = self.load_task(task_id)
        
        if task_data is None:
            return False
        
        task_data["status"] = status.value
        self.save_task(task_id, task_data)
        
        return True

