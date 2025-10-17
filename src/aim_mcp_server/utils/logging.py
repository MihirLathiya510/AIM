"""
Audit trail and logging utilities.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
import os


class AuditLogger:
    """Manages audit trail logging for task execution."""
    
    def __init__(self, log_dir: Optional[Path] = None):
        """
        Initialize audit logger.
        
        Args:
            log_dir: Directory for audit logs (defaults to ~/.aim/logs/)
        """
        if log_dir is None:
            log_dir = Path.home() / ".aim" / "logs"
        
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup Python logger
        self.logger = logging.getLogger("aim_mcp_server")
        self.logger.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        
        if not self.logger.handlers:
            self.logger.addHandler(console_handler)
    
    def log_event(self, task_id: str, event_type: str, data: Dict[str, Any]) -> None:
        """
        Log an event to the audit trail.
        
        Args:
            task_id: The task ID
            event_type: Type of event (e.g., 'task_created', 'subtask_assigned')
            data: Event data
        """
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "task_id": task_id,
            "event_type": event_type,
            "data": data
        }
        
        # Log to file
        log_file = self.log_dir / f"{task_id}.jsonl"
        with open(log_file, "a") as f:
            f.write(json.dumps(event) + "\n")
        
        # Log to console
        self.logger.info(f"[{task_id}] {event_type}: {json.dumps(data, indent=2)}")
    
    def get_audit_trail(self, task_id: str) -> list[Dict[str, Any]]:
        """
        Retrieve audit trail for a task.
        
        Args:
            task_id: The task ID
            
        Returns:
            List of audit events
        """
        log_file = self.log_dir / f"{task_id}.jsonl"
        
        if not log_file.exists():
            return []
        
        events = []
        with open(log_file, "r") as f:
            for line in f:
                if line.strip():
                    events.append(json.loads(line))
        
        return events

