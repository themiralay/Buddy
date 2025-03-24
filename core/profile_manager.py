"""
Manages user profile information.
"""
import logging
import json
import datetime
from integrations.openai_client import OpenAIClient

class ProfileManager:
    """Manages user profile data"""
    
    def __init__(self, database):
        """Initialize profile manager"""
        self.logger = logging.getLogger(__name__)
        self.db = database
        self.openai = OpenAIClient()
    
    def get_profile(self):
        """Get the current user profile"""
        profile = self.db.get_user_profile()
        
        if not profile:
            # Create default profile
            default_profile = {
                "name": "User",
                "created_at": datetime.datetime.now().isoformat(),
                "personal_info": {},
                "preferences": {},
                "interests": [],
                "important_dates": {},
                "relationships": {},
                "memories": {}
            }
            
            self.save_profile(default_profile)
            return default_profile
            
        return profile
    
    def save_profile(self, profile):
        """Save the user profile to database"""
        return self.db.save_user_profile(profile)
    
    def update_profile(self, updates):
        """Update user profile with new information"""
        current_profile = self.get_profile()
        
        # Create a deep copy of the current profile
        updated_profile = json.loads(json.dumps(current_profile))
        
        # Apply updates
        for key, value in updates.items():
            if "." in key:
                # Handle nested keys like "personal_info.birthday"
                parts = key.split(".")
                current = updated_profile
                for part in parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                current[parts[-1]] = value
            else:
                updated_profile[key] = value
        
        # Save updated profile
        self.save_profile(updated_profile)
        return updated_profile
    
    def extract_profile_info(self, conversations):
        """Extract profile information from conversations"""
        if not conversations:
            return {}
            
        # Format conversations for the prompt
        formatted_convs = []
        for conv in conversations:
            if isinstance(conv, tuple) and len(conv) >= 3:
                # If coming from database (timestamp, user_input, assistant_response)
                formatted_convs.append(f"User: {conv[1]}")
                formatted_convs.append(f"Assistant: {conv[2]}")
            elif isinstance(conv, dict):
                # If coming from context manager
                formatted_convs.append(f"User: {conv.get('user_input', '')}")
                formatted_convs.append(f"Assistant: {conv.get('assistant_response', '')}")
                
        combined_text = "\n".join(formatted_convs)
        
        prompt = f"""
        Based on the following conversation, extract any personal information about the user
        that should be remembered for future interactions. This could include preferences,
        interests, important dates, relationships, or other personal details.
        
        Return the information as a JSON object with keys representing the profile fields,
        or an empty JSON object if no relevant information is found.
        
        Example format:
        {{
            "personal_info.birthday": "April 15, 1985",
            "interests": ["hiking", "photography", "cooking"],
            "relationships.mother": "Maria"
        }}
        
        Conversation:
        {combined_text}
        """
        
        try:
            response = self.openai.complete(
                system_message="You extract user profile information from conversations.",
                user_message=prompt,
                temperature=0.2
            )
            
            content = response.strip()
            
            # Try to extract JSON from the response
            try:
                # Find JSON object in the text if it's embedded
                if "{" in content and "}" in content:
                    start = content.find("{")
                    end = content.rfind("}") + 1
                    json_str = content[start:end]
                    return json.loads(json_str)
                return {}
            except json.JSONDecodeError:
                self.logger.warning("Failed to parse profile information as JSON")
                return {}
                
        except Exception as e:
            self.logger.error(f"Error extracting profile information: {e}", exc_info=True)
            return {}