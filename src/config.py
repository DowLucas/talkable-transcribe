#!/usr/bin/env python3
"""
Configuration management for the transcription application.
"""

import os
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class Config:
    """Application configuration."""

    def __init__(self):
        """Initialize configuration from environment variables."""
        self.load_env_file()

        # OpenAI settings
        self.openai_api_key = os.getenv('OPENAI_API_KEY', '')
        if not self.openai_api_key:
            logger.warning("OPENAI_API_KEY not set. Please set it in .env file or environment.")

        # Audio settings
        self.audio_sample_rate = int(os.getenv('AUDIO_SAMPLE_RATE', '24000'))
        self.audio_channels = int(os.getenv('AUDIO_CHANNELS', '1'))
        self.audio_chunk_size = int(os.getenv('AUDIO_CHUNK_SIZE', '1024'))

        # Hotkey settings
        self.hotkey_ctrl = os.getenv('HOTKEY_CTRL', 'true').lower() == 'true'
        self.hotkey_shift = os.getenv('HOTKEY_SHIFT', 'true').lower() == 'true'
        self.hotkey_key = os.getenv('HOTKEY_KEY', 'r').lower()

        # Specific left/right modifier requirements
        self.hotkey_ctrl_r = os.getenv('HOTKEY_CTRL_R', 'true').lower() == 'true'
        self.hotkey_shift_r = os.getenv('HOTKEY_SHIFT_R', 'true').lower() == 'true'

        # OpenAI WebSocket settings
        self.websocket_url = "wss://api.openai.com/v1/realtime"
        self.model = "gpt-4o-transcribe"

        # Logging
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')

    def load_env_file(self):
        """Load .env file if it exists."""
        env_path = Path(__file__).parent.parent / '.env'
        if env_path.exists():
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        # Only set if not already in environment
                        if key not in os.environ:
                            os.environ[key] = value
        else:
            logger.info(f".env file not found at {env_path}. Using environment variables or defaults.")

    def validate(self) -> bool:
        """Validate configuration."""
        if not self.openai_api_key:
            logger.error("OPENAI_API_KEY is required but not set.")
            return False

        if self.audio_sample_rate not in [16000, 24000, 48000]:
            logger.warning(f"Unusual sample rate: {self.audio_sample_rate}. OpenAI prefers 24000 Hz.")

        if self.audio_channels != 1:
            logger.error("Only mono audio (1 channel) is supported.")
            return False

        return True

    def get_hotkey_description(self) -> str:
        """Get human-readable hotkey description."""
        parts = []
        if self.hotkey_ctrl:
            if self.hotkey_ctrl_r:
                parts.append("RCtrl")
            else:
                parts.append("Ctrl")
        if self.hotkey_shift:
            if self.hotkey_shift_r:
                parts.append("RShift")
            else:
                parts.append("Shift")

        # Format special keys nicely
        key_display = {
            'left': 'Left Arrow',
            'right': 'Right Arrow',
            'up': 'Up Arrow',
            'down': 'Down Arrow',
            'space': 'Space',
            'enter': 'Enter',
            'tab': 'Tab',
            'esc': 'Esc',
            'backspace': 'Backspace',
        }

        key_name = key_display.get(self.hotkey_key.lower(), self.hotkey_key.upper())
        parts.append(key_name)
        return "+".join(parts)


# Global config instance
config = Config()
