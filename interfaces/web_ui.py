"""
Web Interface for ICEx Buddy

This module provides a web-based user interface for interacting with the assistant.
"""
import os
import json
from typing import Dict, Any
import secrets
import logging
from datetime import datetime, timedelta

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash

from core.assistant import Assistant
from core.config import Config
from utils.logger import get_logger

logger = get_logger("web_interface")

class WebInterface:
    """Web interface for ICEx Buddy."""
    
    def __init__(self, assistant: Assistant, config: Config):
        """
        Initialize web interface.
        
        Args:
            assistant: The assistant instance
            config: Application configuration
        """
        self.assistant = assistant
        self.config = config
        self.app = Flask(__name__, 
                         template_folder=os.path.join(os.path.dirname(__file__), '..', 'templates'),
                         static_folder=os.path.join(os.path.dirname(__file__), '..', 'static'))
        
        # Configure Flask app
        self.app.config['SECRET_KEY'] = self.config.get('web.secret_key', secrets.token_hex(16))
        self.app.config['SESSION_TYPE'] = 'filesystem'
        self.app.config['SESSION_PERMANENT'] = True
        self.app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
        
        # Initialize Flask-Session
        Session(self.app)
        
        # Register routes
        self._register_routes()
        
        # Get host and port from config
        self.host = self.config.get('web.host', '127.0.0.1')
        self.port = self.config.get('web.port', 5000)
        self.debug = self.config.get('web.debug', False)
        
    def _register_routes(self):
        """Register Flask routes."""
        
        @self.app.route('/')
        def index():
            """Render main page."""
            if not session.get('authenticated', False):
                return redirect(url_for('login'))
            return render_template('index.html')
        
        @self.app.route('/login', methods=['GET', 'POST'])
        def login():
            """Handle login."""
            if request.method == 'POST':
                username = request.form.get('username')
                password = request.form.get('password')
                
                if self._validate_login(username, password):
                    session['authenticated'] = True
                    session['username'] = username
                    return redirect(url_for('index'))
                
                return render_template('login.html', error="Invalid credentials")
            
            return render_template('login.html')
        
        @self.app.route('/logout')
        def logout():
            """Handle logout."""
            session.clear()
            return redirect(url_for('login'))
        
        @self.app.route('/api/chat', methods=['POST'])
        def chat():
            """Handle chat API calls."""
            if not session.get('authenticated', False):
                return jsonify({"error": "Not authenticated"}), 401
                
            try:
                data = request.get_json()
                message = data.get('message', '')
                
                if not message.strip():
                    return jsonify({"error": "Empty message"}), 400
                
                # Process message through assistant
                context = {
                    "username": session.get('username', 'user'),
                    "timestamp": datetime.now().isoformat(),
                    "interface": "web"
                }
                
                response = self.assistant.process_message(message, context)
                
                return jsonify({
                    "response": response,
                    "timestamp": datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"Error processing chat request: {str(e)}")
                return jsonify({"error": "Internal server error"}), 500
    
    def _validate_login(self, username: str, password: str) -> bool:
        """
        Validate user login credentials.
        
        Args:
            username: Username
            password: Password
            
        Returns:
            True if credentials are valid, False otherwise
        """
        users = self.config.get('web.users', {})
        
        if username not in users:
            logger.warning(f"Login attempt with unknown username: {username}")
            return False
            
        stored_password = users[username]
        
        # Check if password is stored as hash
        if stored_password.startswith('pbkdf2:'):
            return check_password_hash(stored_password, password)
        
        # For backward compatibility, support plain text passwords
        # (but log a warning to encourage hashing)
        if stored_password == password:
            logger.warning(f"User {username} has unhashed password, consider updating")
            return True
            
        return False
    
    def start(self):
        """Start the web interface."""
        logger.info(f"Starting web interface on {self.host}:{self.port}")
        self.app.run(host=self.host, port=self.port, debug=self.debug)