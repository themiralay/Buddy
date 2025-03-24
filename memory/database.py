import sqlite3
import json
import logging
import os
import datetime
from typing import Dict, List, Optional, Any, Union

class Database:
    """SQLite database for persistent storage."""
    
    def __init__(self, db_path: str = "memory/data.db"):
        """Initialize the database.
        
        Args:
            db_path: Path to the SQLite database file
        """
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self.db_path = db_path
        self.logger = logging.getLogger("assistant.database")
        
        # Initialize the database
        self._init_db()
        
        self.logger.info(f"Database initialized at {db_path}")
    
    def _init_db(self):
        """Initialize the database schema if it doesn't exist."""
        with self._connect() as conn:
            cursor = conn.cursor()
            
            # Create conversations table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                message TEXT NOT NULL,
                response TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
            ''')
            
            # Create user profiles table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id TEXT PRIMARY KEY,
                profile_data TEXT NOT NULL,
                last_updated TEXT NOT NULL
            )
            ''')
            
            # Create tasks table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                description TEXT NOT NULL,
                due_date TEXT,
                created_at TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending'
            )
            ''')
            
            conn.commit()
    
    def _connect(self):
        """Create a database connection."""
        return sqlite3.connect(self.db_path)
    
    def store_conversation(self, user_id: str, message: str, response: str) -> int:
        """Store a conversation in the database.
        
        Args:
            user_id: Identifier for the user
            message: The user's message
            response: The assistant's response
            
        Returns:
            ID of the stored conversation
        """
        timestamp = self.get_timestamp()
        
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''
                INSERT INTO conversations (user_id, message, response, timestamp)
                VALUES (?, ?, ?, ?)
                ''',
                (user_id, message, response, timestamp)
            )
            conn.commit()
            return cursor.lastrowid
    
    def get_recent_conversations(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversations for a user.
        
        Args:
            user_id: Identifier for the user
            limit: Maximum number of conversations to retrieve
            
        Returns:
            List of conversation dictionaries
        """
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                '''
                SELECT id, message, response, timestamp
                FROM conversations
                WHERE user_id = ?
                ORDER BY id DESC
                LIMIT ?
                ''',
                (user_id, limit)
            )
            
            rows = cursor.fetchall()
            # Convert rows to dictionaries and reverse to get chronological order
            conversations = [dict(row) for row in rows]
            conversations.reverse()
            
            return conversations
    
    def store_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> bool:
        """Store a user profile in the database.
        
        Args:
            user_id: Identifier for the user
            profile_data: Profile data dictionary
            
        Returns:
            True if successful
        """
        timestamp = self.get_timestamp()
        profile_json = json.dumps(profile_data)
        
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''
                INSERT OR REPLACE INTO user_profiles (user_id, profile_data, last_updated)
                VALUES (?, ?, ?)
                ''',
                (user_id, profile_json, timestamp)
            )
            conn.commit()
            return True
    
    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a user profile from the database.
        
        Args:
            user_id: Identifier for the user
            
        Returns:
            User profile dictionary or None if not found
        """
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                '''
                SELECT profile_data FROM user_profiles
                WHERE user_id = ?
                ''',
                (user_id,)
            )
            
            row = cursor.fetchone()
            if row:
                return json.loads(row['profile_data'])
            return None
    
    def store_task(self, user_id: str, task: Dict[str, Any]) -> int:
        """Store a task in the database.
        
        Args:
            user_id: Identifier for the user
            task: Task dictionary
            
        Returns:
            ID of the stored task
        """
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''
                INSERT INTO tasks (user_id, description, due_date, created_at, status)
                VALUES (?, ?, ?, ?, ?)
                ''',
                (
                    user_id,
                    task.get('description', ''),
                    task.get('due_date'),
                    task.get('created_at', self.get_timestamp()),
                    task.get('status', 'pending')
                )
            )
            conn.commit()
            return cursor.lastrowid
    
    def get_tasks(self, user_id: str, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get tasks for a user.
        
        Args:
            user_id: Identifier for the user
            status: Filter by status ('pending', 'completed')
            
        Returns:
            List of task dictionaries
        """
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if status:
                cursor.execute(
                    '''
                    SELECT * FROM tasks
                    WHERE user_id = ? AND status = ?
                    ORDER BY created_at DESC
                    ''',
                    (user_id, status)
                )
            else:
                cursor.execute(
                    '''
                    SELECT * FROM tasks
                    WHERE user_id = ?
                    ORDER BY created_at DESC
                    ''',
                    (user_id,)
                )
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def update_task_status(self, task_id: int, status: str) -> bool:
        """Update the status of a task.
        
        Args:
            task_id: Task identifier
            status: New status ('pending', 'completed')
            
        Returns:
            True if successful, False if task not found
        """
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''
                UPDATE tasks
                SET status = ?
                WHERE id = ?
                ''',
                (status, task_id)
            )
            conn.commit()
            return cursor.rowcount > 0
    
    def get_due_tasks(self, user_id: str) -> List[Dict[str, Any]]:
        """Get tasks that are due today or overdue.
        
        Args:
            user_id: Identifier for the user
            
        Returns:
            List of due task dictionaries
        """
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                '''
                SELECT * FROM tasks
                WHERE user_id = ? AND status = 'pending' AND due_date <= ?
                ORDER BY due_date ASC
                ''',
                (user_id, today)
            )
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_timestamp(self) -> str:
        """Get the current timestamp in ISO format.
        
        Returns:
            Timestamp string
        """
        return datetime.datetime.now().isoformat()