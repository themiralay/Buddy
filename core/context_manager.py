import logging
from typing import Dict, List, Optional, Any

from memory.database import Database
from memory.vector_store import VectorStore
from utils.token_counter import count_tokens

class ContextManager:
    """Manages conversation context and history."""
    
    def __init__(self, vector_store: VectorStore, database: Database, max_context_tokens: int = 4000):
        """Initialize the context manager.
        
        Args:
            vector_store: Vector store for semantic search
            database: Database for storing conversations
            max_context_tokens: Maximum number of tokens for context
        """
        self.vector_store = vector_store
        self.database = database
        self.max_context_tokens = max_context_tokens
        self.logger = logging.getLogger("assistant.context")
        
    def get_context(self, user_id: str, current_message: str) -> Dict[str, Any]:
        """Get the context for the current conversation.
        
        Args:
            user_id: Identifier for the user
            current_message: The current message being processed
            
        Returns:
            Dictionary containing conversation history and relevant context
        """
        # Get recent conversations from database
        recent_history = self.database.get_recent_conversations(user_id, limit=10)
        
        # Perform semantic search for relevant past conversations
        relevant_history = self.vector_store.search(current_message, limit=5)
        
        # Combine and format the context
        formatted_history = self._format_conversations(recent_history)
        formatted_relevant = self._format_conversations(relevant_history)
        
        # Ensure we don't exceed token limit
        combined_context = self._trim_to_token_limit(formatted_history, formatted_relevant)
        
        return {
            "recent_history": combined_context["recent_history"],
            "relevant_history": combined_context["relevant_history"],
            "timestamp": combined_context.get("timestamp")
        }
    
    def update_memory(self, user_id: str, message: str, response: str) -> None:
        """Update memory with the new conversation.
        
        Args:
            user_id: Identifier for the user
            message: The user's message
            response: The assistant's response
        """
        # Store in database
        conversation_id = self.database.store_conversation(
            user_id=user_id,
            message=message,
            response=response
        )
        
        # Store in vector database for semantic search
        self.vector_store.add_text(
            text=f"User: {message}\nAssistant: {response}",
            metadata={
                "user_id": user_id,
                "conversation_id": conversation_id,
                "timestamp": self.database.get_timestamp()
            }
        )
        
        self.logger.debug(f"Updated memory for user {user_id}, conversation_id: {conversation_id}")
    
    def _format_conversations(self, conversations: List[Dict]) -> List[Dict]:
        """Format conversations for context inclusion.
        
        Args:
            conversations: List of conversation dictionaries
            
        Returns:
            Formatted list of conversations
        """
        formatted = []
        for conv in conversations:
            formatted.append({
                "user": conv.get("message", ""),
                "assistant": conv.get("response", ""),
                "timestamp": conv.get("timestamp", "")
            })
        return formatted
    
    def _trim_to_token_limit(self, recent_history: List[Dict], relevant_history: List[Dict]) -> Dict:
        """Trim context to fit within token limit.
        
        Args:
            recent_history: Recent conversation history
            relevant_history: Semantically relevant history
            
        Returns:
            Trimmed context dictionary
        """
        # Start with most relevant conversations
        result = {"recent_history": [], "relevant_history": []}
        token_count = 0
        
        # First add relevant history
        for conv in relevant_history:
            conv_tokens = count_tokens(f"User: {conv.get('user')}\nAssistant: {conv.get('assistant')}")
            if token_count + conv_tokens <= self.max_context_tokens:
                result["relevant_history"].append(conv)
                token_count += conv_tokens
            else:
                break
                
        # Then add recent history if there's space
        for conv in recent_history:
            conv_tokens = count_tokens(f"User: {conv.get('user')}\nAssistant: {conv.get('assistant')}")
            if token_count + conv_tokens <= self.max_context_tokens:
                result["recent_history"].append(conv)
                token_count += conv_tokens
            else:
                break
        
        self.logger.debug(f"Context built with {token_count} tokens, {len(result['recent_history'])} recent and {len(result['relevant_history'])} relevant conversations")
        return result