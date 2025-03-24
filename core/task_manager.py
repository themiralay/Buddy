import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Any

from memory.database import Database

class TaskManager:
    """Extracts and manages tasks from conversations."""
    
    def __init__(self, database: Database):
        """Initialize the task manager.
        
        Args:
            database: Database for storing tasks
        """
        self.database = database
        self.logger = logging.getLogger("assistant.tasks")
    
    def extract_tasks(self, message: str) -> List[Dict[str, Any]]:
        """Extract potential tasks from a user message.
        
        Args:
            message: The user's message
            
        Returns:
            List of extracted tasks
        """
        tasks = []
        
        # Simple rule-based extraction - in production, use an LLM for this
        # Look for phrases like "remind me to", "I need to", etc.
        task_indicators = [
            r"remind me to (.+?)(?:\.|$)",
            r"I need to (.+?)(?:\.|$)",
            r"don't let me forget to (.+?)(?:\.|$)",
            r"todo: (.+?)(?:\.|$)",
            r"task: (.+?)(?:\.|$)"
        ]
        
        for pattern in task_indicators:
            matches = re.finditer(pattern, message, re.IGNORECASE)
            for match in matches:
                task_description = match.group(1).strip()
                if task_description:
                    # Try to extract a due date if present
                    due_date = None
                    date_patterns = [
                        r"by (tomorrow|today|monday|tuesday|wednesday|thursday|friday|saturday|sunday)",
                        r"by (\d{1,2}(?:st|nd|rd|th)?(?:\s+of)?\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec))",
                        r"by (\d{1,2}/\d{1,2}(?:/\d{2,4})?)"
                    ]
                    
                    for date_pattern in date_patterns:
                        date_match = re.search(date_pattern, task_description, re.IGNORECASE)
                        if date_match:
                            due_date = date_match.group(1)
                            # Remove the date part from the task description
                            task_description = re.sub(f"by {re.escape(due_date)}", "", task_description, flags=re.IGNORECASE).strip()
                    
                    tasks.append({
                        "description": task_description,
                        "due_date": due_date,
                        "created_at": datetime.now().isoformat(),
                        "status": "pending"
                    })
        
        self.logger.debug(f"Extracted {len(tasks)} tasks from message")
        return tasks
    
    def add_task(self, task: Dict[str, Any], user_id: str) -> int:
        """Add a task to the database.
        
        Args:
            task: Task dictionary with description, etc
            user_id: Identifier for the user
            
        Returns:
            Task ID
        """
        task_id = self.database.store_task(user_id, task)
        self.logger.info(f"Added task {task_id} for user {user_id}: {task['description'][:30]}...")
        return task_id
    
    def get_tasks_for_user(self, user_id: str, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all tasks for a specific user.
        
        Args:
            user_id: Identifier for the user
            status: Filter by status (e.g., 'pending', 'completed')
            
        Returns:
            List of tasks
        """
        tasks = self.database.get_tasks(user_id, status)
        self.logger.debug(f"Retrieved {len(tasks)} tasks for user {user_id}")
        return tasks
    
    def update_task_status(self, task_id: int, status: str) -> bool:
        """Update the status of a task.
        
        Args:
            task_id: Task identifier
            status: New status ('pending', 'completed', 'cancelled')
            
        Returns:
            True if successful, False otherwise
        """
        success = self.database.update_task_status(task_id, status)
        if success:
            self.logger.info(f"Updated task {task_id} status to '{status}'")
        else:
            self.logger.warning(f"Failed to update task {task_id}")
        return success
    
    def get_due_tasks(self, user_id: str) -> List[Dict[str, Any]]:
        """Get tasks that are due today or overdue.
        
        Args:
            user_id: Identifier for the user
            
        Returns:
            List of due or overdue tasks
        """
        return self.database.get_due_tasks(user_id)