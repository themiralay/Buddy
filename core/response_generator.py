import logging
from typing import Dict, Any, Optional

from integrations.openai_client import OpenAIClient

class ResponseGenerator:
    """Generates responses using AI models."""
    
    def __init__(self, ai_client: OpenAIClient):
        """Initialize the response generator.
        
        Args:
            ai_client: Client for AI model API
        """
        self.ai_client = ai_client
        self.logger = logging.getLogger("assistant.response")
    
    def generate(self, message: str, context: Dict[str, Any], user_profile: Dict[str, Any]) -> str:
        """Generate a response using the AI model.
        
        Args:
            message: The user's message
            context: Conversation context and history
            user_profile: The user's profile information
            
        Returns:
            Generated response text
        """
        # Create system message with context and profile information
        system_message = self._create_system_message(context, user_profile)
        
        # Build conversation history for the AI
        conversation = self._build_conversation_history(context)
        
        # Add current message
        conversation.append({"role": "user", "content": message})
        
        # Generate response
        self.logger.debug("Generating response with AI model")
        response = self.ai_client.chat_completion(
            system_message=system_message,
            messages=conversation
        )
        
        return response
    
    def _create_system_message(self, context: Dict[str, Any], user_profile: Dict[str, Any]) -> str:
        """Create a system message with instructions for the AI.
        
        Args:
            context: Conversation context
            user_profile: User profile information
            
        Returns:
            Formatted system message
        """
        # Start with basic instructions
        system_message = "You are ICEx Buddy, a helpful and intelligent personal assistant. "
        
        # Add profile-based customization
        if user_profile:
            if "preferences" in user_profile:
                prefs = user_profile["preferences"]
                
                if "response_length" in prefs:
                    if prefs["response_length"] == "concise":
                        system_message += "Keep your responses brief and to the point. "
                    else:
                        system_message += "Provide detailed and thorough responses. "
                        
                if "formality" in prefs:
                    if prefs["formality"] == "informal":
                        system_message += "Use a casual, friendly tone. "
                    else:
                        system_message += "Maintain a professional tone. "
                        
                if "humor" in prefs:
                    if prefs["humor"] == "humorous":
                        system_message += "Include appropriate humor in your responses. "
                    else:
                        system_message += "Maintain a serious demeanor. "
            
            if "interests" in user_profile and user_profile["interests"]:
                interests = ", ".join(user_profile["interests"][:5])  # Limit to 5 interests
                system_message += f"The user has expressed interest in: {interests}. "
        
        # Add memory instructions
        system_message += (
            "You have access to conversation history to provide continuity. "
            "Reference relevant past interactions when helpful. "
            "Always be helpful, accurate, and respectful."
        )
        
        return system_message
    
    def _build_conversation_history(self, context: Dict[str, Any]) -> list:
        """Build conversation history from context for the AI.
        
        Args:
            context: Conversation context with history
            
        Returns:
            List of messages in format for AI completion
        """
        conversation = []
        
        # Add recent history
        if "recent_history" in context:
            for entry in context["recent_history"]:
                conversation.append({"role": "user", "content": entry.get("user", "")})
                conversation.append({"role": "assistant", "content": entry.get("assistant", "")})
        
        # Add relevant history - only if significantly different from recent history
        if "relevant_history" in context:
            for entry in context["relevant_history"]:
                # Skip if this exact exchange is already in the conversation
                if any(msg["role"] == "user" and msg["content"] == entry.get("user", "") for msg in conversation):
                    continue
                    
                # Add a marker to indicate this is from previous relevant conversations
                user_content = f"[From previous conversation] {entry.get('user', '')}"
                assistant_content = entry.get('assistant', '')
                
                conversation.append({"role": "user", "content": user_content})
                conversation.append({"role": "assistant", "content": assistant_content})
        
        return conversation