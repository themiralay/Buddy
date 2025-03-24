import logging
import json
import threading
import time
from typing import Dict, Any, Optional

class WhatsAppBot:
    """WhatsApp integration for ICEx Buddy."""
    
    def __init__(self, assistant, config_path: Optional[str] = None):
        """Initialize the WhatsApp integration.
        
        Args:
            assistant: The personal assistant instance
            config_path: Path to WhatsApp configuration file
        """
        self.assistant = assistant
        self.config_path = config_path
        self.logger = logging.getLogger("assistant.whatsapp")
        self.running = False
        
        # Load configuration
        self.config = self._load_config()
        
        try:
            # Check if required libraries are available
            # This is a simplified implementation - in a real project,
            # you would use a proper WhatsApp Business API client or library
            import requests
            self.requests = requests
            
            self.logger.info("WhatsApp integration initialized")
        except ImportError:
            self.logger.error("requests package not installed. Install with: pip install requests")
            raise
    
    def _load_config(self) -> Dict[str, Any]:
        """Load WhatsApp configuration from file."""
        if not self.config_path:
            self.logger.warning("WhatsApp config path not provided, using defaults")
            return self._get_default_config()
            
        try:
            with open(self.config_path, 'r') as file:
                config = json.load(file)
                
            self.logger.info(f"Loaded WhatsApp configuration from {self.config_path}")
            return config
            
        except Exception as e:
            self.logger.error(f"Error loading WhatsApp config: {str(e)}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default WhatsApp configuration."""
        return {
            "api_url": "https://api.whatsapp.com/v1/messages",
            "phone_number_id": "your_phone_number_id",
            "access_token": "your_access_token",
            "verify_token": "your_verify_token",
            "webhook_url": "https://your-webhook-url.com/whatsapp",
            "poll_interval": 5  # seconds
        }
    
    def _process_message(self, sender_id: str, message_text: str) -> str:
        """Process a message from WhatsApp.
        
        Args:
            sender_id: Sender's WhatsApp ID
            message_text: Message text
            
        Returns:
            Response text
        """
        # Process with assistant
        response = self.assistant.process_message(
            message=message_text,
            user_id=sender_id,
            include_voice=False
        )
        
        # Return just the text response
        return response["text"]
    
    def _send_message(self, recipient_id: str, message: str) -> bool:
        """Send a message to WhatsApp.
        
        Args:
            recipient_id: Recipient's WhatsApp ID
            message: Message to send
            
        Returns:
            True if successful
        """
        # This is a placeholder implementation
        # In a real implementation, you would use the WhatsApp Business API
        try:
            headers = {
                "Authorization": f"Bearer {self.config.get('access_token')}",
                "Content-Type": "application/json"
            }
            
            data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": recipient_id,
                "type": "text",
                "text": {
                    "body": message
                }
            }
            
            url = self.config.get("api_url")
            response = self.requests.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                return True
            else:
                self.logger.error(f"Error sending WhatsApp message: {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error in WhatsApp API call: {str(e)}")
            return False
    
    def _poll_messages(self):
        """Poll for new messages (simplified implementation)."""
        # This is a placeholder - in a real implementation,
        # you would set up a webhook receiver or use a proper client library
        while self.running:
            try:
                # This would be replaced with actual polling logic or webhook handling
                self.logger.debug("Polling for WhatsApp messages...")
                # Simulate checking for messages
                time.sleep(self.config.get("poll_interval", 5))
            except Exception as e:
                self.logger.error(f"Error polling WhatsApp messages: {str(e)}")
                time.sleep(10)  # Longer delay after error
    
    def run(self):
        """Run the WhatsApp integration in a separate thread."""
        self.logger.info("Starting WhatsApp integration")
        self.running = True
        
        polling_thread = threading.Thread(target=self._poll_messages)
        polling_thread.daemon = True
        polling_thread.start()
    
    def shutdown(self):
        """Shutdown the WhatsApp integration."""
        self.logger.info("Shutting down WhatsApp integration")
        self.running = False