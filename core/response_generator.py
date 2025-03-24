"""
Generates responses using LLM integration.
"""
import logging
import json
from integrations.openai_client import OpenAIClient

class ResponseGenerator:
    """Generates assistant responses using LLM"""
    
    def __init__(self, context_manager, profile_manager, llm_config):
        """Initialize response generator"""
        self.logger = logging.getLogger(__name__)
        self.context_manager = context_manager
        self.profile_manager = profile_manager
        self.llm_config = llm_config
        self.openai = OpenAIClient()
    
    def generate(self, user_input, context, emotion=None):
        """Generate a response to user input"""
        # Prepare the messages for the API
        messages = [
            {"role": "system", "content": self.llm_config.get("system_prompt", "")}
        ]
        
        # Add user profile
        user_profile = self.profile_manager.get_profile()
        if user_profile:
            profile_str = json.dumps(user_profile, indent=2)
            messages.append({
                "role": "system", 
                "content": f"User profile information:\n{profile_str}"
            })
        
        # Add current datetime
        if "current_datetime" in context:
            messages.append({
                "role": "system", 
                "content": f"Current date and time: {context['current_datetime']}"
            })
        
        # Add recent conversation history
        if context.get("recent_conversations"):
            recent_convs = []
            for conv in context["recent_conversations"]:
                recent_convs.append(f"User: {conv['user_input']}")
                recent_convs.append(f"Assistant: {conv['assistant_response']}")
            
            recent_history = "\n".join(recent_convs)
            messages.append({
                "role": "system", 
                "content": f"Recent conversation history:\n{recent_history}"
            })
        
        # Add relevant past memories
        if context.get("relevant_memories"):
            relevant_memories = []
            for memory in context["relevant_memories"]:
                relevant_memories.append(memory["content"])
            
            memories_text = "\n---\n".join(relevant_memories)
            messages.append({
                "role": "system", 
                "content": f"Relevant past conversations:\n{memories_text}"
            })
        
        # Add user emotion if available
        if emotion:
            messages.append({
                "role": "system", 
                "content": f"User's current emotional state appears to be: {emotion}"
            })
        
        # Add the user's message
        messages.append({"role": "user", "content": user_input})
        
        # Generate response
        try:
            response = self.openai.chat_completion(
                messages=messages,
                model=self.llm_config.get("default_model", "gpt-4-turbo"),
                temperature=self.llm_config.get("temperature", 0.7),
                max_tokens=self.llm_config.get("max_tokens", 1024)
            )
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error generating response: {e}", exc_info=True)
            # Use fallback model if configured
            if "fallback_model" in self.llm_config:
                try:
                    self.logger.info(f"Trying fallback model: {self.llm_config['fallback_model']}")
                    response = self.openai.chat_completion(
                        messages=messages,
                        model=self.llm_config.get("fallback_model"),
                        temperature=self.llm_config.get("temperature", 0.7),
                        max_tokens=self.llm_config.get("max_tokens", 1024)
                    )
                    return response
                except Exception as e2:
                    self.logger.error(f"Error with fallback model: {e2}", exc_info=True)
            
            return "I'm sorry, I'm having trouble generating a response right now. Could you try again?"
    
    def extract_tasks(self, user_input, assistant_response):
        """Extract tasks or reminders from the conversation"""
        prompt = f"""
        Identify any action items, tasks, or commitments made in this conversation.
        Format as a JSON list of objects with 'task', 'due_date' (if specified), and 'for_whom'.
        Return an empty list if none found.
        
        User: {user_input}
        Assistant: {assistant_response}
        """
        
        try:
            response = self.openai.complete(
                system_message="Extract action items from text",
                user_message=prompt,
                temperature=0.1,
                max_tokens=500
            )
            
            content = response.strip()
            
            # Extract JSON list
            if "[" in content and "]" in content:
                start = content.find("[")
                end = content.rfind("]") + 1
                json_str = content[start:end]
                return json.loads(json_str)
            return []
        except Exception as e:
            self.logger.error(f"Error extracting tasks: {e}", exc_info=True)
            return []