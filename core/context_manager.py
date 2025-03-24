"""
Manages conversation context and memory retrieval.
"""
import logging
import datetime
import json
from utils.token_counter import count_tokens

class ContextManager:
    """Manages conversation context and memory for the assistant"""
    
    def __init__(self, database, vector_store, max_context_tokens=4000):
        """Initialize context manager"""
        self.logger = logging.getLogger(__name__)
        self.db = database
        self.vector_store = vector_store
        self.max_context_tokens = max_context_tokens
    
    def get_context(self, query, max_recent=5, max_relevant=3):
        """
        Build context for the current conversation including:
        - Recent conversations
        - Semantically relevant past conversations
        - Current date and time
        """
        context = {
            "recent_conversations": [],
            "relevant_memories": [],
            "current_datetime": datetime.datetime.now().isoformat(),
            "token_count": 0
        }
        
        # Add recent conversations
        recent = self.db.get_recent_conversations(max_recent)
        for timestamp, user_input, assistant_response in recent:
            conversation = f"User: {user_input}\nAssistant: {assistant_response}"
            tokens = count_tokens(conversation)
            
            if context["token_count"] + tokens <= self.max_context_tokens:
                context["recent_conversations"].append({
                    "timestamp": timestamp,
                    "user_input": user_input,
                    "assistant_response": assistant_response
                })
                context["token_count"] += tokens
            else:
                break
        
        # Find semantically relevant past conversations
        if query:
            relevant_results = self.vector_store.similarity_search(query, max_relevant)
            for doc in relevant_results:
                content = doc.page_content
                tokens = count_tokens(content)
                
                if context["token_count"] + tokens <= self.max_context_tokens:
                    context["relevant_memories"].append({
                        "content": content,
                        "metadata": doc.metadata
                    })
                    context["token_count"] += tokens
                else:
                    break
        
        self.logger.debug(f"Built context with {len(context['recent_conversations'])} recent and " 
                         f"{len(context['relevant_memories'])} relevant conversations " 
                         f"({context['token_count']} tokens)")
        
        return context
    
    def update_memory(self, user_input, assistant_response, emotion=None):
        """Store conversation in both database and vector store"""
        # Add to database
        timestamp = datetime.datetime.now().isoformat()
        self.db.add_conversation(timestamp, user_input, assistant_response, emotion)
        
        # Add to vector store for semantic search
        combined_text = f"User: {user_input}\nAssistant: {assistant_response}"
        metadata = {
            "timestamp": timestamp,
            "type": "conversation"
        }
        
        if emotion:
            metadata["emotion"] = emotion
            
        self.vector_store.add_texts([combined_text], [metadata])
        
        return timestamp