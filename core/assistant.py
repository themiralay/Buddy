"""
Core Assistant module for ICEx Buddy
"""
import time
from typing import Dict, Any, List, Optional
import traceback

from core.config import Config
from llm.manager import LLMManager
from memory.manager import MemoryManager
from skills.registry import SkillRegistry
from utils.logger import get_logger

logger = get_logger("assistant")

class Assistant:
    """
    Main assistant class that coordinates all components.
    """
    
    def __init__(self, config: Config):
        """
        Initialize the assistant.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.name = config.get("assistant.name", "ICEx Buddy")
        self.version = config.get("assistant.version", "1.0.0")
        
        # Initialize components
        logger.info("Initializing LLM manager")
        self.llm_manager = LLMManager(config)
        
        logger.info("Initializing memory manager")
        self.memory_manager = MemoryManager(config)
        
        logger.info("Initializing skill registry")
        self.skill_registry = SkillRegistry(config)
        
        # Load system prompt
        self.system_prompt = config.get("assistant.system_prompt", 
            f"You are {self.name}, a helpful AI assistant. " +
            "Answer questions accurately and concisely.")
            
        logger.info(f"Assistant initialized: {self.name} v{self.version}")
    
    def process_message(self, message: str, context: Dict[str, Any] = None) -> str:
        """
        Process a user message and generate a response.
        
        Args:
            message: User's message
            context: Additional context information
            
        Returns:
            Assistant's response
        """
        if context is None:
            context = {}
            
        user_id = context.get("username", "user")
        start_time = time.time()
        
        logger.info(f"Processing message from {user_id}: {message[:50]}...")
        
        try:
            # Store message in memory
            self.memory_manager.add_message(user_id, "user", message)
            
            # Check if any skill can handle this message
            skill = self.skill_registry.get_skill_for_message(message, context)
            
            if skill:
                logger.info(f"Handling message with skill: {skill.__class__.__name__}")
                response = skill.handle(message, context)
            else:
                # Get conversation history
                conversation = self.memory_manager.get_conversation(
                    user_id, 
                    limit=self.config.get("memory.context_limit", 10)
                )
                
                # Generate response using LLM
                response = self.llm_manager.generate_response(
                    message, 
                    conversation=conversation,
                    system_prompt=self.system_prompt,
                    context=context
                )
            
            # Store response in memory
            self.memory_manager.add_message(user_id, "assistant", response)
            
            elapsed_time = time.time() - start_time
            logger.info(f"Response generated in {elapsed_time:.2f}s: {response[:50]}...")
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            logger.debug(traceback.format_exc())
            return f"I'm sorry, I encountered an error while processing your message: {str(e)}"
    
    def reset_conversation(self, user_id: str) -> None:
        """
        Reset conversation history for a user.
        
        Args:
            user_id: User identifier
        """
        logger.info(f"Resetting conversation for user: {user_id}")
        self.memory_manager.clear_conversation(user_id)