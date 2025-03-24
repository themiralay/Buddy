import cmd
import os
import sys
import time
import logging
from typing import Optional

from core.assistant import PersonalAssistant

class CLIInterface(cmd.Cmd):
    """Command-line interface for the ICEx Buddy assistant."""
    
    intro = """
    ╔═══════════════════════════════════════════╗
    ║                ICEx Buddy                 ║
    ║      Your Personal AI Assistant CLI       ║
    ╚═══════════════════════════════════════════╝
    
    Type 'help' for available commands.
    Start chatting by simply typing your message.
    """
    prompt = '📝 You: '
    
    def __init__(self, assistant: PersonalAssistant):
        """Initialize the CLI interface.
        
        Args:
            assistant: The personal assistant instance
        """
        super().__init__()
        self.assistant = assistant
        self.logger = logging.getLogger("assistant.cli")
        self.user_id = os.getenv("USER_ID", "cli_user")
        self.voice_enabled = self.assistant.voice_enabled
    
    def default(self, line: str):
        """Handle any input that's not a command as a message to the assistant.
        
        Args:
            line: User input
        """
        if not line.strip():
            return
            
        try:
            # Process the message
            response = self.assistant.process_message(
                message=line,
                user_id=self.user_id,
                include_voice=False
            )
            
            # Print the response with a typing effect
            print("\n🤖 ICEx Buddy: ", end="", flush=True)
            self._type_effect(response["text"])
            print("\n")
            
            # Mention if tasks were extracted
            if response.get("tasks_extracted", 0) > 0:
                print(f"📋 {response['tasks_extracted']} task(s) added to your list.\n")
                
        except Exception as e:
            self.logger.error(f"Error processing message: {str(e)}")
            print("\n❌ Sorry, I encountered an error while processing your message.")
    
    def do_tasks(self, arg):
        """Show your current tasks."""
        status = None
        if arg:
            status = arg.strip().lower()
            if status not in ["pending", "completed", "all"]:
                print("Invalid status. Use 'pending', 'completed', or 'all'.")
                return
        
        try:
            if status == "all" or not status:
                tasks = self.assistant.get_user_tasks(self.user_id)
            else:
                tasks = self.assistant.task_manager.get_tasks_for_user(
                    user_id=self.user_id,
                    status=status
                )
            
            if not tasks:
                print("📋 No tasks found.")
                return
                
            print("\n📋 Your Tasks:")
            print("═════════════════════════════════════════════")
            
            for i, task in enumerate(tasks, 1):
                status_symbol = "✅" if task.get("status") == "completed" else "⏳"
                print(f"{i}. {status_symbol} {task.get('description')}")
                if task.get("due_date"):
                    print(f"   Due: {task.get('due_date')}")
                print(f"   Status: {task.get('status', 'pending')}")
                print("─────────────────────────────────────────────")
                
            print()
            
        except Exception as e:
            self.logger.error(f"Error retrieving tasks: {str(e)}")
            print("❌ Sorry, I encountered an error while retrieving your tasks.")
    
    def do_complete(self, arg):
        """Mark a task as completed. Usage: complete <task_id>"""
        try:
            task_id = int(arg.strip())
            success = self.assistant.task_manager.update_task_status(task_id, "completed")
            
            if success:
                print(f"✅ Task {task_id} marked as completed.")
            else:
                print(f"❌ Task {task_id} not found.")
                
        except ValueError:
            print("❌ Please provide a valid task ID.")
        except Exception as e:
            self.logger.error(f"Error completing task: {str(e)}")
            print("❌ Sorry, I encountered an error while updating the task.")
    
    def do_voice(self, arg):
        """Record audio and send it to the assistant (if voice is enabled)."""
        if not self.voice_enabled:
            print("❌ Voice functionality is not enabled.")
            return
            
        try:
            import sounddevice as sd
            import soundfile as sf
            import tempfile
            
            print("🎤 Recording... (Press Ctrl+C to stop)")
            
            # Record audio
            sample_rate = 44100
            duration = 10  # seconds
            recording = sd.rec(int(duration * sample_rate), 
                              samplerate=sample_rate, 
                              channels=1)
            
            # Wait for recording to complete or user to interrupt
            try:
                sd.wait()
            except KeyboardInterrupt:
                print("\n⏹️ Recording stopped.")
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                sf.write(temp_file.name, recording, sample_rate)
                
                # Read the file as bytes
                with open(temp_file.name, "rb") as audio_file:
                    audio_data = audio_file.read()
                
                # Process the voice
                print("🔄 Processing your voice message...")
                response = self.assistant.process_voice(audio_data, self.user_id)
                
                # Display results
                if "error" in response:
                    print(f"❌ {response['error']}")
                else:
                    print("\n🤖 ICEx Buddy: ", end="", flush=True)
                    self._type_effect(response["text"])
                    print("\n")
                
                # Clean up
                os.unlink(temp_file.name)
                
        except ImportError:
            print("❌ Voice recording requires the 'sounddevice' and 'soundfile' packages.")
            print("Install them with: pip install sounddevice soundfile")
        except Exception as e:
            self.logger.error(f"Error in voice processing: {str(e)}")
            print(f"❌ Error: {str(e)}")
    
    def do_exit(self, arg):
        """Exit the CLI."""
        print("\n👋 Goodbye! Thank you for using ICEx Buddy.")
        return True
        
    def do_quit(self, arg):
        """Exit the CLI."""
        return self.do_exit(arg)
        
    def do_EOF(self, arg):
        """Handle Ctrl+D to exit."""
        print()  # Add a newline
        return self.do_exit(arg)
    
    def _type_effect(self, text: str, delay: float = 0.01):
        """Create a typing effect for text output.
        
        Args:
            text: Text to display
            delay: Delay between characters in seconds
        """
        for char in text:
            print(char, end="", flush=True)
            time.sleep(delay)
    
    def run(self):
        """Start the CLI interface."""
        self.logger.info("Starting CLI interface")
        self.cmdloop()