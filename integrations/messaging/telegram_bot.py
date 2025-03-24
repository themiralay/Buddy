import logging
import asyncio
import threading
from typing import Optional

class TelegramBot:
    """Telegram bot integration for ICEx Buddy."""
    
    def __init__(self, assistant, token: Optional[str] = None):
        """Initialize the Telegram bot.
        
        Args:
            assistant: The personal assistant instance
            token: Telegram bot token
        """
        self.assistant = assistant
        self.token = token
        self.logger = logging.getLogger("assistant.telegram")
        
        if not self.token:
            self.logger.error("Telegram bot token not provided")
            raise ValueError("Telegram bot token is required")
        
        try:
            from telegram import Update
            from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
            
            self.bot_app = Application.builder().token(self.token).build()
            
            # Register handlers
            self.bot_app.add_handler(CommandHandler("start", self._start_command))
            self.bot_app.add_handler(CommandHandler("help", self._help_command))
            self.bot_app.add_handler(CommandHandler("tasks", self._tasks_command))
            self.bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_message))
            
            self.logger.info("Telegram bot initialized")
            
        except ImportError:
            self.logger.error("python-telegram-bot package not installed. Install with: pip install python-telegram-bot")
            raise
    
    async def _start_command(self, update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        """Handle /start command."""
        await update.message.reply_text(
            "👋 Hello! I'm ICEx Buddy, your personal AI assistant.\n\n"
            "You can ask me questions, request information, or even ask me to remind you of tasks!\n\n"
            "Type /help to see available commands."
        )
    
    async def _help_command(self, update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        """Handle /help command."""
        await update.message.reply_text(
            "🔍 ICEx Buddy Help:\n\n"
            "/start - Start the conversation\n"
            "/help - Show this help message\n"
            "/tasks - Show your current tasks\n\n"
            "You can also just chat with me normally or ask me to remind you of things!"
        )
    
    async def _tasks_command(self, update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        """Handle /tasks command."""
        user_id = str(update.effective_user.id)
        
        # Get tasks from assistant
        tasks = self.assistant.get_user_tasks(user_id)
        
        if not tasks:
            await update.message.reply_text("You don't have any tasks yet. Ask me to remind you of something!")
            return
        
        # Format tasks list
        tasks_text = "📋 Your Tasks:\n\n"
        for i, task in enumerate(tasks, 1):
            status_emoji = "✅" if task.get("status") == "completed" else "⏳"
            tasks_text += f"{i}. {status_emoji} {task.get('description')}\n"
            if task.get("due_date"):
                tasks_text += f"   Due: {task.get('due_date')}\n"
            tasks_text += f"   Status: {task.get('status', 'pending')}\n\n"
        
        await update.message.reply_text(tasks_text)
    
    async def _handle_message(self, update: 'Update', context: 'ContextTypes.DEFAULT_TYPE'):
        """Handle user messages."""
        user_id = str(update.effective_user.id)
        message_text = update.message.text
        
        # Indicate typing
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        # Process the message with the assistant
        response = self.assistant.process_message(
            message=message_text,
            user_id=user_id,
            include_voice=False
        )
        
        # Send the response
        await update.message.reply_text(response["text"])
        
        # Notify if tasks were extracted
        if response.get("tasks_extracted", 0) > 0:
            await update.message.reply_text(
                f"📋 I've added {response['tasks_extracted']} task(s) to your list.\n"
                "You can view them with /tasks"
            )
    
    def run(self):
        """Run the Telegram bot in a separate thread."""
        def _run_bot():
            self.logger.info("Starting Telegram bot")
            asyncio.run(self.bot_app.run_polling())
        
        bot_thread = threading.Thread(target=_run_bot)
        bot_thread.daemon = True
        bot_thread.start()
    
    def shutdown(self):
        """Shutdown the Telegram bot."""
        self.logger.info("Shutting down Telegram bot")
        # Stop polling
        if hasattr(self, 'bot_app') and self.bot_app:
            asyncio.run(self.bot_app.stop())