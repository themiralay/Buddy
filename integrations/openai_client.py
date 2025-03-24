"""
OpenAI API client for LLM requests.
"""
import os
import logging
import openai

class OpenAIClient:
    """Client for OpenAI API requests"""
    
    def __init__(self):
        """Initialize OpenAI client"""
        self.logger = logging.getLogger(__name__)
        
        # Get API key from environment
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            self.logger.error("OpenAI API key not found in environment variables")
            raise ValueError("OpenAI API key is required")
        
        openai.api_key = api_key
    
    def chat_completion(self, messages, model="gpt-4-turbo", temperature=0.7, max_tokens=1024):
        """Generate a chat completion response"""
        try:
            response = openai.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            self.logger.error(f"Error in chat completion: {e}", exc_info=True)
            raise
    
    def complete(self, system_message, user_message, temperature=0.7, max_tokens=1024):
        """Helper for simple completion with system and user message"""
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
        
        return self.chat_completion(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
    
    def create_embedding(self, text):
        """Create an embedding vector for text"""
        try:
            response = openai.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            self.logger.error(f"Error creating embedding: {e}", exc_info=True)
            raise