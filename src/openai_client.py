#!/usr/bin/env python3
"""
Simple OpenAI client for audio transcription using Whisper API.
"""

import logging
import tempfile
import wave
from typing import Optional, Callable
from openai import OpenAI

from config import config

logger = logging.getLogger(__name__)


class OpenAITranscriptionClient:
    """Simple client for OpenAI Whisper transcription API."""

    def __init__(self, on_transcription: Optional[Callable[[str], None]] = None):
        """
        Initialize the OpenAI transcription client.

        Args:
            on_transcription: Callback function that receives transcription text.
        """
        self.on_transcription = on_transcription
        self.client = OpenAI(api_key=config.openai_api_key)
        self.audio_buffer = []
        self.temp_file = None
        logger.info("OpenAI Whisper client initialized")

    def start_recording(self):
        """Start a new recording session."""
        self.audio_buffer.clear()
        logger.info("Started new recording session")

    def add_audio_chunk(self, audio_data: bytes):
        """
        Add audio chunk to buffer.

        Args:
            audio_data: PCM16 audio data bytes
        """
        self.audio_buffer.append(audio_data)

    def transcribe_audio(self) -> Optional[str]:
        """
        Transcribe the buffered audio using OpenAI Whisper API.

        Returns:
            Transcribed text or None if error
        """
        if not self.audio_buffer:
            logger.warning("No audio data to transcribe")
            return None

        try:
            # Combine all audio chunks
            audio_data = b''.join(self.audio_buffer)
            logger.info(f"Transcribing {len(audio_data)} bytes of audio")

            # Create temporary WAV file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
                self.temp_file = temp_wav.name

                # Write WAV file
                with wave.open(temp_wav.name, 'wb') as wav_file:
                    wav_file.setnchannels(config.audio_channels)
                    wav_file.setsampwidth(2)  # 16-bit = 2 bytes
                    wav_file.setframerate(config.audio_sample_rate)
                    wav_file.writeframes(audio_data)

                logger.info(f"Created temporary WAV file: {temp_wav.name}")

            # Transcribe using OpenAI Whisper API
            with open(self.temp_file, 'rb') as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text"
                )

            # Clean up temp file
            import os
            os.unlink(self.temp_file)
            self.temp_file = None

            logger.info(f"Transcription successful: {transcript}")

            # Call callback if provided
            if self.on_transcription and transcript:
                self.on_transcription(transcript.strip())

            return transcript.strip()

        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            # Clean up temp file on error
            if self.temp_file:
                try:
                    import os
                    os.unlink(self.temp_file)
                except:
                    pass
                self.temp_file = None
            return None
        finally:
            # Clear buffer
            self.audio_buffer.clear()


if __name__ == "__main__":
    # Test the client
    logging.basicConfig(level=logging.INFO)

    def on_transcription(text):
        print(f"\n*** TRANSCRIPTION: {text} ***\n")

    client = OpenAITranscriptionClient(on_transcription=on_transcription)
    client.start_recording()

    # Simulate adding audio (in real use, this would be actual audio data)
    # For testing, you would need actual PCM audio data
    print("OpenAI Whisper client test complete")
