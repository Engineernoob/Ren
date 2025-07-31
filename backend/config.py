# config.py
# Centralized configuration management for Ren voice assistant

import os
from typing import Optional
from dotenv import load_dotenv

class Config:
    """Configuration class for managing environment variables and settings."""

    def __init__(self):
        self.load_environment()

    def load_environment(self):
        """Load environment variables with fallback defaults."""
        load_dotenv()

        # ElevenLabs API Configuration
        self.ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
        self.ELEVEN_VOICE_ID = os.getenv('ELEVEN_VOICE_ID')

        # Whisper Configuration
        self.WHISPER_MODEL = os.getenv('WHISPER_MODEL', 'base')

        # Audio Configuration
        self.AUDIO_SAMPLE_RATE = int(os.getenv('AUDIO_SAMPLE_RATE', '16000'))
        self.AUDIO_DURATION = int(os.getenv('AUDIO_DURATION', '4'))

        # Agent Configuration
        self.MEMORY_THRESHOLD = int(os.getenv('MEMORY_THRESHOLD', '20'))
        self.AGENT_NAME = os.getenv('AGENT_NAME', 'Ren')
        self.AGENT_PERSONALITY = os.getenv('AGENT_PERSONALITY', 'calm, introspective, articulate — poetic when needed, with quiet authority')

        # Background task manager toggle
        self.ENABLE_BACKGROUND_TASKS = os.getenv('ENABLE_BACKGROUND_TASKS', 'true').lower() == 'true'

        # LLM configuration
        self.OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama3')
        self.OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')  # fallback

    def validate_required_config(self) -> list:
        """Validate that required configuration is present."""
        missing = []

        if not self.ELEVENLABS_API_KEY:
            missing.append('ELEVENLABS_API_KEY')
        if not self.ELEVEN_VOICE_ID:
            missing.append('ELEVEN_VOICE_ID')

        return missing

    def is_voice_enabled(self) -> bool:
        """Check if voice functionality is properly configured."""
        return bool(self.ELEVENLABS_API_KEY and self.ELEVEN_VOICE_ID)

    def debug_summary(self) -> dict:
        """Return summarized config for logging/debugging."""
        return {
            "voice_enabled": self.is_voice_enabled(),
            "agent_name": self.AGENT_NAME,
            "personality": self.AGENT_PERSONALITY,
            "memory_threshold": self.MEMORY_THRESHOLD,
            "background_tasks": self.ENABLE_BACKGROUND_TASKS,
            "whisper_model": self.WHISPER_MODEL,
            "ollama_model": self.OLLAMA_MODEL,
            "openrouter_fallback": bool(self.OPENROUTER_API_KEY),
        }

# Global configuration instance
config = Config()
