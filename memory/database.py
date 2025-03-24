"""
SQLite database for persistent storage.
"""
import os
import sqlite3
import logging
import json
import datetime
import shutil

class Database:
    """SQLite database for persistent storage"""
    
    def __init__(self, db_path):
        """Initialize database connection"""
        self.logger = logging.getLogger(__name__)
        self.db_path = db_path
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Connect to database
        self.conn = sqlite3.connect(db_path)
        self._setup_database()
        
        self.logger.info(f"Database initialized at {db_path}")
    
    def _setup_database(self):
        """Set up the database tables"""
        cursor = self.conn.cursor()
        
        # Create conversations table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY,
            timestamp TEXT,
            user_input TEXT,
            assistant_response TEXT,
            emotion TEXT
        )
        ''')
        
        # Create user_profile table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_profile (
            id INTEGER PRIMARY KEY,
            profile_data TEXT,
            updated_at TEXT
        )
        ''')
        
        # Create user_notes table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_notes (
            id INTEGER PRIMARY KEY,
            title TEXT,
            content TEXT,
            category TEXT,
            created_at TEXT,
            updated_at TEXT
        )
        ''')
        
        # Create tasks table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            description TEXT,
            due_date TEXT,
            status TEXT,
            created_at TEXT,
            updated_at TEXT
        )
        ''')
        
        self.conn.commit()
    
    def add_conversation(self, timestamp, user_input, assistant_response, emotion=None):
        """Add a conversation to the database"""
        cursor = self.conn.cursor()
        
        cursor.execute(
            "INSERT INTO conversations (timestamp, user_input, assistant_response, emotion) VALUES (?, ?, ?, ?)",
            (timestamp, user_input, assistant_response, emotion)
        )
        
        self.conn.commit()
        return cursor.lastrowid
    
    def get_recent_conversations(self, limit=10):
        """Get recent conversations from database"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT timestamp, user_input, assistant_response FROM conversations ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        )
        return cursor.fetchall()
    
    def get_conversation_count(self):
        """Get the total number of conversations"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM conversations")
        return cursor.fetchone()[0]
    
    def get_user_profile(self):
        """Get the most recent user profile"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT profile_data FROM user_profile ORDER BY updated_at DESC LIMIT 1")
        result = cursor.fetchone()
        
        if result:
            return json.loads(result[0])
        return None
    
    def save_user_profile(self, profile):
        """Save user profile to database"""
        cursor = self.conn.cursor()
        timestamp = datetime.datetime.now().isoformat()
        
        cursor.execute(
            "INSERT INTO user_profile (profile_data, updated_at) VALUES (?, ?)",
            (json.dumps(profile), timestamp)
        )
        
        self.conn.commit()
        return cursor.lastrowid
    
    def add_note(self, title, content, category="general"):
        """Add a user note to the database"""
        cursor = self.conn.cursor()
        timestamp = datetime.datetime.now().isoformat()
        
        cursor.execute(
            "INSERT INTO user_notes (title, content, category, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (title, content, category, timestamp, timestamp)
        )
        
        self.conn.commit()
        return cursor.lastrowid
    
    def get_notes(self, category=None, limit=10):
        """Get user notes from database"""
        cursor = self.conn.cursor()
        
        if category:
            cursor.execute(
                "SELECT id, title, content, category, created_at FROM user_notes WHERE category = ? ORDER BY updated_at DESC LIMIT ?",
                (category, limit)
            )
        else:
            cursor.execute(
                "SELECT id, title, content, category, created_at FROM user_notes ORDER BY updated_at DESC LIMIT ?",
                (limit,)
            )
            
        return cursor.fetchall()
    
    def add_task(self, description, due_date=None, status="pending"):
        """Add a task to the database"""
        cursor = self.conn.cursor()
        timestamp = datetime.datetime.now().isoformat()
        
        cursor.execute(
            "INSERT INTO tasks (description, due_date, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (description, due_date, status, timestamp, timestamp)
        )
        
        self.conn.commit()
        return cursor.lastrowid
    
    def get_tasks(self, status=None, limit=10):
        """Get tasks from database"""
        cursor = self.conn.cursor()
        
        if status:
            cursor.execute(
                "SELECT id, description, due_date, status, created_at FROM tasks WHERE status = ? ORDER BY created_at DESC LIMIT ?",
                (status, limit)
            )
        else:
            cursor.execute(
                "SELECT id, description, due_date, status, created_at FROM tasks ORDER BY created_at DESC LIMIT ?",
                (limit,)
            )
            
        return cursor.fetchall()
    
    def backup(self, backup_path):
        """Create a backup of the database"""
        # Close current connection to ensure all data is written
        self.conn.close()
        
        # Create backup
        shutil.copy2(self.db_path, backup_path)
        
        # Reopen connection
        self.conn = sqlite3.connect(self.db_path)
        
        self.logger.info(f"Database backed up to {backup_path}")
        return backup_path
    
    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None