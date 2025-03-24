"""
Token counting utilities for LLM context management.
"""
import logging
import tiktoken

def count_tokens(text, model="gpt-4"):
    """Count the number of tokens in a text string"""
    try:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except Exception as e:
        logging.getLogger(__name__).warning(f"Error counting tokens: {e}")
        # Fallback to approximate counting (4 chars ~= 1 token)
        return len(text) // 4