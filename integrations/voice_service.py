import logging
import tempfile
import os
from typing import Optional, Union, Dict, Any

class VoiceService:
    """Service for text-to-speech and speech-to-text functionality."""
    
    def __init__(self, tts_provider: str = "openai", stt_provider: str = "openai"):
        """Initialize the voice service.
        
        Args:
            tts_provider: Provider for text-to-speech ('openai', 'elevenlabs', 'local')
            stt_provider: Provider for speech-to-text ('openai', 'whisper', 'local')
        """
        self.tts_provider = tts_provider
        self.stt_provider = stt_provider
        self.logger = logging.getLogger("assistant.voice")
        
        # Initialize appropriate clients based on providers
        self._init_tts_client()
        self._init_stt_client()
        
        self.logger.info(f"Voice service initialized with TTS: {tts_provider}, STT: {stt_provider}")
    
    def _init_tts_client(self):
        """Initialize the appropriate TTS client based on provider."""
        if self.tts_provider == "openai":
            # Import here to avoid circular imports
            from integrations.openai_client import OpenAIClient
            # We'll use the existing OpenAI client from other modules
            self.tts_client = "openai"
        elif self.tts_provider == "elevenlabs":
            try:
                import elevenlabs
                self.tts_client = "elevenlabs"
            except ImportError:
                self.logger.error("ElevenLabs package not installed. Falling back to OpenAI.")
                self.tts_provider = "openai"
                self.tts_client = "openai"
        else:
            # Default to OpenAI if provider not recognized
            self.tts_provider = "openai"
            self.tts_client = "openai"
            
    def _init_stt_client(self):
        """Initialize the appropriate STT client based on provider."""
        if self.stt_provider == "openai":
            # Will use OpenAI's Whisper API
            self.stt_client = "openai"
        elif self.stt_provider == "whisper":
            try:
                import whisper
                self.stt_client = whisper.load_model("base")
            except ImportError:
                self.logger.error("Local Whisper package not installed. Falling back to OpenAI.")
                self.stt_provider = "openai"
                self.stt_client = "openai"
        else:
            # Default to OpenAI if provider not recognized
            self.stt_provider = "openai"
            self.stt_client = "openai"
    
    def text_to_speech(self, text: str, voice: str = "alloy") -> bytes:
        """Convert text to speech.
        
        Args:
            text: Text to convert to speech
            voice: Voice ID or name to use
            
        Returns:
            Audio data as bytes
        """
        self.logger.debug(f"Converting to speech: {text[:50]}...")
        
        if self.tts_provider == "openai":
            from integrations.openai_client import get_openai_client
            client = get_openai_client()
            
            try:
                response = client.audio.speech.create(
                    model="tts-1",
                    voice=voice,
                    input=text
                )
                return response.content
            except Exception as e:
                self.logger.error(f"Error in TTS: {str(e)}")
                return b""
                
        elif self.tts_provider == "elevenlabs":
            import elevenlabs
            
            try:
                audio = elevenlabs.generate(
                    text=text,
                    voice=voice
                )
                return audio
            except Exception as e:
                self.logger.error(f"Error in ElevenLabs TTS: {str(e)}")
                return b""
        else:
            self.logger.warning(f"Unsupported TTS provider: {self.tts_provider}")
            return b""
    
    def speech_to_text(self, audio_data: bytes) -> str:
        """Convert speech to text.
        
        Args:
            audio_data: Audio data as bytes
            
        Returns:
            Transcribed text
        """
        self.logger.debug("Converting speech to text...")
        
        if self.stt_provider == "openai":
            from integrations.openai_client import get_openai_client
            client = get_openai_client()
            
            # Save audio data to a temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            temp_file.write(audio_data)
            temp_file.close()
            
            try:
                with open(temp_file.name, "rb") as audio_file:
                    transcript = client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file
                    )
                os.unlink(temp_file.name)
                return transcript.text
            except Exception as e:
                self.logger.error(f"Error in STT: {str(e)}")
                os.unlink(temp_file.name)
                return ""
                
        elif self.stt_provider == "whisper":
            # Save audio data to a temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            temp_file.write(audio_data)
            temp_file.close()
            
            try:
                result = self.stt_client.transcribe(temp_file.name)
                os.unlink(temp_file.name)
                return result["text"]
            except Exception as e:
                self.logger.error(f"Error in Whisper STT: {str(e)}")
                os.unlink(temp_file.name)
                return ""
        else:
            self.logger.warning(f"Unsupported STT provider: {self.stt_provider}")
            return ""