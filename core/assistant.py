"""
Core PersonalAssistant class that coordinates all system components.
"""
import os
import logging
import datetime
from core.context_manager import ContextManager
from core.response_generator import ResponseGenerator
from core.profile_manager import ProfileManager
from core.task_scheduler import TaskScheduler
from core.emotion_analyzer import EmotionAnalyzer
from memory.database import Database
from memory.vector_store import VectorStore
from utils.config_loader import load_config

class PersonalAssistant:
    """Human-like personal AI assistant with integrated memory system"""
    
    def __init__(self, config_path=None):
        """Initialize the personal assistant"""
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing Personal Assistant")
        
        # Load configuration
        self.config = load_config(config_path)
        
        # Initialize database and vector store
        db_path = self.config["paths"]["database"]
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db = Database(db_path)
        
        vector_path = self.config["paths"]["vector_store"]
        os.makedirs(vector_path, exist_ok=True)
        self.vector_store = VectorStore(vector_path)
        
        # Initialize core components
        self.profile_manager = ProfileManager(self.db)
        self.context_manager = ContextManager(self.db, self.vector_store)
        self.response_generator = ResponseGenerator(
            self.context_manager, 
            self.profile_manager,
            self.config["llm"]
        )
        self.task_scheduler = TaskScheduler(self.db)
        self.emotion_analyzer = EmotionAnalyzer()
        
        # Load user profile
        self.user_profile = self.profile_manager.get_profile()
        
        self.logger.info("Personal Assistant initialized successfully")
    
    def process_input(self, user_input, input_type="text"):
        """Process user input and generate response"""
        self.logger.debug(f"Processing input: {user_input[:50]}...")
        
        # Analyze emotion in the input
        emotion = self.emotion_analyzer.analyze(user_input)
        
        # Get context for the current conversation
        context = self.context_manager.get_context(user_input)
        
        # Generate response
        start_time = datetime.datetime.now()
        response = self.response_generator.generate(user_input, context, emotion)
        end_time = datetime.datetime.now()
        
        # Log performance metrics
        processing_time = (end_time - start_time).total_seconds()
        self.logger.debug(f"Response generated in {processing_time:.2f} seconds")
        
        # Update conversation memory
        self.context_manager.update_memory(user_input, response, emotion)
        
        # Extract tasks or reminders
        tasks = self.response_generator.extract_tasks(user_input, response)
        if tasks:
            for task in tasks:
                self.task_scheduler.add_task(task)
        
        # Periodically update user profile (every 5 conversations)
        conversation_count = self.db.get_conversation_count()
        if conversation_count % 5 == 0:
            recent_conversations = self.db.get_recent_conversations(10)
            profile_updates = self.profile_manager.extract_profile_info(recent_conversations)
            if profile_updates:
                self.profile_manager.update_profile(profile_updates)
                self.user_profile = self.profile_manager.get_profile()
        
        return response
    
    def add_note(self, title, content, category="general"):
        """Add a user note"""
        return self.db.add_note(title, content, category)
    
    def get_notes(self, category=None, limit=10):
        """Get user notes"""
        return self.db.get_notes(category, limit)
    
    def create_backup(self):
        """Create a backup of the system data"""
        backup_dir = self.config["paths"]["backups"]
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_dir, f"backup_{timestamp}.db")
        
        return self.db.backup(backup_path)
    
    def run_interactive(self):
        """Run in interactive console mode"""
        from rich.console import Console
        from rich.markdown import Markdown
        
        console = Console()
        console.print(f"[bold green]{self.config['system']['name']} v{self.config['system']['version']}[/bold green]")
        console.print("[italic]Type 'exit' to end the session, 'help' for commands.[/italic]\n")
        
        while True:
            try:
                user_input = input("\nYou: ")
                
                if user_input.lower() == "exit":
                    console.print("[yellow]Goodbye![/yellow]")
                    break
                
                if user_input.lower() == "help":
                    console.print(Markdown("""
                    # Available Commands
                    - `exit`: End the session
                    - `help`: Show this help message
                    - `backup`: Create a system backup
                    - `notes list [category]`: List your notes
                    - `note add <title> <content>`: Add a new note
                    """))
                    continue
                
                if user_input.lower() == "backup":
                    backup_path = self.create_backup()
                    console.print(f"[green]Backup created at: {backup_path}[/green]")
                    continue
                
                if user_input.lower().startswith("notes list"):
                    parts = user_input.split(" ", 2)
                    category = parts[2] if len(parts) > 2 else None
                    notes = self.get_notes(category)
                    
                    if not notes:
                        console.print("[yellow]No notes found.[/yellow]")
                    else:
                        for note in notes:
                            console.print(f"[bold]{note[1]}[/bold] ({note[3]})")
                            console.print(f"{note[2]}")
                            console.print("---")
                    continue
                
                if user_input.lower().startswith("note add "):
                    parts = user_input[9:].split(" ", 1)
                    if len(parts) < 2:
                        console.print("[red]Usage: note add <title> <content>[/red]")
                        continue
                        
                    title, content = parts
                    note_id = self.add_note(title, content)
                    console.print(f"[green]Note added with ID: {note_id}[/green]")
                    continue
                
                # Process normal input
                response = self.process_input(user_input)
                console.print(f"\n[cyan]Assistant:[/cyan] {response}")
                
            except KeyboardInterrupt:
                console.print("\n[yellow]Interrupted by user.[/yellow]")
                break
                
            except Exception as e:
                self.logger.error(f"Error in interactive mode: {e}", exc_info=True)
                console.print(f"[red]An error occurred: {str(e)}[/red]")
    
    def close(self):
        """Release resources"""
        self.logger.info("Closing Personal Assistant resources")
        if hasattr(self, 'db') and self.db:
            self.db.close()
        if hasattr(self, 'vector_store') and self.vector_store:
            self.vector_store.close()