import logging
import asyncio
import threading
from typing import Optional

class DiscordBot:
    """Discord bot integration for ICEx Buddy."""
    
    def __init__(self, assistant, token: Optional[str] = None):
        """Initialize the Discord bot.
        
        Args:
            assistant: The personal assistant instance
            token: Discord bot token
        """
        self.assistant = assistant
        self.token = token
        self.logger = logging.getLogger("assistant.discord")
        
        if not self.token:
            self.logger.error("Discord bot token not provided")
            raise ValueError("Discord bot token is required")
        
        try:
            import discord
            from discord.ext import commands
            
            # Set up intents
            intents = discord.Intents.default()
            intents.message_content = True
            intents.messages = True
            
            # Create bot
            self.bot = commands.Bot(command_prefix="!", intents=intents)
            
            # Register events and commands
            self._setup_events()
            self._setup_commands()
            
            self.logger.info("Discord bot initialized")
            
        except ImportError:
            self.logger.error("discord.py package not installed. Install with: pip install discord.py")
            raise
    
    def _setup_events(self):
        """Set up Discord bot events."""
        @self.bot.event
        async def on_ready():
            self.logger.info(f"Discord bot logged in as {self.bot.user}")
            await self.bot.change_presence(activity=discord.Activity(
                type=discord.ActivityType.listening, 
                name="your questions"
            ))
        
        @self.bot.event
        async def on_message(message):
            # Don't respond to bot's own messages
            if message.author == self.bot.user:
                return
            
            # Don't process commands here to avoid double processing
            if message.content.startswith(self.bot.command_prefix):
                await self.bot.process_commands(message)
                return
            
            # Only respond to DMs and mentions
            is_dm = isinstance(message.channel, discord.DMChannel)
            is_mentioned = self.bot.user in message.mentions
            
            if is_dm or is_mentioned:
                # Remove the mention from the message if present
                content = message.content
                if is_mentioned:
                    content = content.replace(f"<@{self.bot.user.id}>", "").strip()
                
                # Indicate typing
                async with message.channel.typing():
                    # Process with assistant
                    user_id = str(message.author.id)
                    response = self.assistant.process_message(
                        message=content,
                        user_id=user_id,
                        include_voice=False
                    )
                    
                    # Send response
                    await message.reply(response["text"])
                    
                    # Notify if tasks were extracted
                    if response.get("tasks_extracted", 0) > 0:
                        await message.channel.send(
                            f"📋 I've added {response['tasks_extracted']} task(s) to your list.\n"
                            "You can view them with !tasks"
                        )
    
    def _setup_commands(self):
        """Set up Discord bot commands."""
        @self.bot.command(name="help", description="Show help information")
        async def help_command(ctx):
            embed = discord.Embed(
                title="ICEx Buddy Help",
                description="I'm your personal AI assistant!",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="Commands",
                value=(
                    "!help - Show this help message\n"
                    "!tasks - Show your current tasks\n"
                ),
                inline=False
            )
            
            embed.add_field(
                name="How to use",
                value=(
                    "1. Mention me in a channel (@ICEx Buddy)\n"
                    "2. Send me direct messages\n"
                    "3. I can remind you of tasks - just ask!"
                ),
                inline=False
            )
            
            await ctx.send(embed=embed)
        
        @self.bot.command(name="tasks", description="Show your current tasks")
        async def tasks_command(ctx):
            user_id = str(ctx.author.id)
            
            # Get tasks from assistant
            tasks = self.assistant.get_user_tasks(user_id)
            
            if not tasks:
                await ctx.send("You don't have any tasks yet. Ask me to remind you of something!")
                return
            
            # Create embed for tasks
            embed = discord.Embed(
                title="Your Tasks",
                description="Here are your current tasks:",
                color=discord.Color.green()
            )
            
            for i, task in enumerate(tasks, 1):
                status_emoji = "✅" if task.get("status") == "completed" else "⏳"
                task_desc = f"{status_emoji} {task.get('description')}"
                
                task_details = ""
                if task.get("due_date"):
                    task_details += f"Due: {task.get('due_date')}\n"
                task_details += f"Status: {task.get('status', 'pending')}"
                
                embed.add_field(
                    name=f"Task {i}",
                    value=f"{task_desc}\n{task_details}",
                    inline=False
                )
            
            await ctx.send(embed=embed)
    
    def run(self):
        """Run the Discord bot in a separate thread."""
        def _run_bot():
            self.logger.info("Starting Discord bot")
            asyncio.run(self.bot.start(self.token))
        
        bot_thread = threading.Thread(target=_run_bot)
        bot_thread.daemon = True
        bot_thread.start()
    
    def shutdown(self):
        """Shutdown the Discord bot."""
        self.logger.info("Shutting down Discord bot")
        if hasattr(self, 'bot') and self.bot:
            asyncio.run(self.bot.close())