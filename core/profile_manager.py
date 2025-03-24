import logging
from typing import Dict, Optional, Any

from memory.database import Database

class ProfileManager:
    """Builds and maintains user profiles based on interactions."""
    
    def __init__(self, database: Database):
        """Initialize the profile manager.
        
        Args:
            database: Database for storing user profiles
        """
        self.database = database
        self.logger = logging.getLogger("assistant.profile")
    
    def get_profile(self, user_id: str) -> Dict[str, Any]:
        """Get the user profile, creating a new one if it doesn't exist.
        
        Args:
            user_id: Identifier for the user
            
        Returns:
            User profile as a dictionary
        """
        profile = self.database.get_user_profile(user_id)
        
        if not profile:
            # Create a new profile
            self.logger.info(f"Creating new profile for user {user_id}")
            profile = {
                "user_id": user_id,
                "preferences": {},
                "interests": [],
                "interaction_stats": {
                    "total_messages": 0,
                    "first_interaction": self.database.get_timestamp()
                }
            }
            self.database.store_user_profile(user_id, profile)
        
        return profile
    
    def update_profile(self, user_id: str, message: str, response: str) -> None:
        """Update the user profile based on the latest interaction.
        
        Args:
            user_id: Identifier for the user
            message: The user's message
            response: The assistant's response
        """
        profile = self.get_profile(user_id)
        
        # Update basic interaction stats
        if "interaction_stats" not in profile:
            profile["interaction_stats"] = {}
        
        profile["interaction_stats"]["total_messages"] = profile["interaction_stats"].get("total_messages", 0) + 1
        profile["interaction_stats"]["last_interaction"] = self.database.get_timestamp()
        
        # Extract potential interests and preferences (simplified approach)
        self._extract_interests(profile, message)
        self._extract_preferences(profile, message)
        
        # Store updated profile
        self.database.store_user_profile(user_id, profile)
        self.logger.debug(f"Updated profile for user {user_id}")
    
    def _extract_interests(self, profile: Dict[str, Any], message: str) -> None:
        """Extract potential interests from user messages.
        
        Args:
            profile: The user profile to update
            message: The user's message
        """
        # This is a simplified approach - in a real system, you'd use NLP or LLMs
        # to extract interests more intelligently
        
        if "interests" not in profile:
            profile["interests"] = []
            
        # For simplicity, we're just looking for "I like X" or "I love X" patterns
        lower_message = message.lower()
        interest_indicators = ["i like ", "i love ", "i enjoy ", "fan of "]
        
        for indicator in interest_indicators:
            if indicator in lower_message:
                start_idx = lower_message.find(indicator) + len(indicator)
                end_idx = lower_message.find(".", start_idx)
                if end_idx == -1:
                    end_idx = len(lower_message)
                
                potential_interest = lower_message[start_idx:end_idx].strip()
                if potential_interest and len(potential_interest) < 50:  # Reasonable length check
                    if potential_interest not in profile["interests"]:
                        profile["interests"].append(potential_interest)
                        self.logger.debug(f"Extracted interest: {potential_interest}")
    
    def _extract_preferences(self, profile: Dict[str, Any], message: str) -> None:
        """Extract potential preferences from user messages.
        
        Args:
            profile: The user profile to update
            message: The user's message
        """
        # Again, simplified approach
        if "preferences" not in profile:
            profile["preferences"] = {}
            
        # Very basic preference extraction
        preference_indicators = {
            "response_length": ["be brief", "keep it short", "detailed response", "elaborate"],
            "formality": ["formal", "informal", "casual", "professional"],
            "humor": ["be funny", "humor", "joke", "serious"]
        }
        
        lower_message = message.lower()
        
        for category, phrases in preference_indicators.items():
            for phrase in phrases:
                if phrase in lower_message:
                    if category == "response_length":
                        if "brief" in phrase or "short" in phrase:
                            profile["preferences"][category] = "concise"
                        else:
                            profile["preferences"][category] = "detailed"
                    elif category == "formality":
                        if "informal" in phrase or "casual" in phrase:
                            profile["preferences"][category] = "informal"
                        else:
                            profile["preferences"][category] = "formal"
                    elif category == "humor":
                        if "funny" in phrase or "humor" in phrase or "joke" in phrase:
                            profile["preferences"][category] = "humorous"
                        else:
                            profile["preferences"][category] = "serious"