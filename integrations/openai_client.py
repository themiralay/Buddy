import os
import logging
from typing import List, Dict, Any, Optional
import openai

# Global client instance
_client = None

def get_openai_client():
    """Get a global OpenAI client instance."""
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        _client = openai.OpenAI(api_key=api_key)
    return _client

class OpenAIClient:
    """Client for OpenAI API requests."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4-turbo-preview"):
        """Initialize the OpenAI client.
        
        Args:
            api_key: OpenAI API key (defaults to environment variable)
            model: Model to use for completions
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not provided and not found in environment variables")
            
        self.model = model
        self.client = openai.OpenAI(api_key=self.api_key)
        self.logger = logging.getLogger("assistant.openai")
        
        self.logger.info(f"OpenAI client initialized with model: {model}")
    
    def chat_completion(self, system_message: str, messages: List[Dict[str, str]]) -> str:
        """Generate a chat completion.
        
        Args:
            system_message: System message providing instructions
            messages: List of message objects with role and content
            
        Returns:
            Generated response text
        """
        try:
            # Prepend the system message
            all_messages = [{"role": "system", "content": system_message}]
            all_messages.extend(messages)
            
            self.logger.debug(f"Sending chat completion request with {len(all_messages)} messages")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=all_messages,
                temperature=0.7,
                max_tokens=1000,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            self.logger.error(f"Error in chat completion: {str(e)}")
            return f"I'm sorry, I encountered an error: {str(e)}"
    
    def generate_embeddings(self, text: str) -> List[float]:
        """Generate embeddings for text.
        
        Args:
            text: Text to generate embeddings for
            
        Returns:
            List of embedding values
        """
        try:
            response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            self.logger.error(f"Error generating embeddings: {str(e)}")
            raise