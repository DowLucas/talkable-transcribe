#!/usr/bin/env python3
"""
Audio recording module for real-time audio capture and streaming.
"""

import logging
import threading
import queue
import struct
from typing import Optional, Callable
import pyaudio

from config import config

logger = logging.getLogger(__name__)


class AudioRecorder:
    """Handles audio recording from the default input device."""

    def __init__(self, audio_callback: Optional[Callable[[bytes], None]] = None):
        """
        Initialize the audio recorder.

        Args:
            audio_callback: Optional callback function that receives audio chunks as bytes.
        """
        self.audio_callback = audio_callback
        self.is_recording = False
        self.audio_queue = queue.Queue()
        self.stream: Optional[pyaudio.Stream] = None
        self.pyaudio_instance: Optional[pyaudio.PyAudio] = None

        # Audio format settings for OpenAI gpt-4o-transcribe
        # Must be: 16-bit PCM, 24kHz, mono, little-endian
        self.sample_rate = config.audio_sample_rate
        self.channels = config.audio_channels
        self.chunk_size = config.audio_chunk_size
        self.format = pyaudio.paInt16  # 16-bit PCM

    def start_recording(self) -> bool:
        """
        Start recording audio.

        Returns:
            True if recording started successfully, False otherwise.
        """
        if self.is_recording:
            logger.warning("Already recording")
            return False

        try:
            self.pyaudio_instance = pyaudio.PyAudio()

            # Open audio stream
            self.stream = self.pyaudio_instance.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size,
                stream_callback=self._audio_stream_callback,
                start=False
            )

            self.is_recording = True
            self.stream.start_stream()
            logger.info(f"Started recording: {self.sample_rate}Hz, {self.channels} channel(s), {self.chunk_size} chunk size")
            return True

        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
            self.cleanup()
            return False

    def stop_recording(self) -> None:
        """Stop recording audio."""
        if not self.is_recording:
            logger.warning("Not currently recording")
            return

        logger.info("Stopping recording")
        self.is_recording = False

        if self.stream:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except Exception as e:
                logger.error(f"Error closing stream: {e}")
            finally:
                self.stream = None

        self.cleanup()

    def cleanup(self) -> None:
        """Clean up PyAudio resources."""
        if self.pyaudio_instance:
            try:
                self.pyaudio_instance.terminate()
            except Exception as e:
                logger.error(f"Error terminating PyAudio: {e}")
            finally:
                self.pyaudio_instance = None

    def _audio_stream_callback(self, in_data, frame_count, time_info, status):
        """
        Callback function for audio stream.

        Args:
            in_data: Audio data bytes
            frame_count: Number of frames
            time_info: Time information
            status: Stream status

        Returns:
            Tuple of (None, continue_flag)
        """
        if status:
            logger.warning(f"Audio stream status: {status}")

        if self.is_recording and in_data:
            # Convert to PCM16 if needed
            audio_data = self._process_audio_data(in_data)

            # Call the callback if provided
            if self.audio_callback:
                try:
                    self.audio_callback(audio_data)
                except Exception as e:
                    logger.error(f"Error in audio callback: {e}")

        return (None, pyaudio.paContinue)

    def _process_audio_data(self, audio_data: bytes) -> bytes:
        """
        Process audio data to ensure it's in the correct format.

        Args:
            audio_data: Raw audio data

        Returns:
            Processed audio data in PCM16 format
        """
        # Audio is already in paInt16 format from PyAudio
        # Just ensure it's little-endian (which is the default on most systems)
        return audio_data

    def get_device_info(self) -> dict:
        """
        Get information about the default input device.

        Returns:
            Dictionary with device information
        """
        try:
            p = pyaudio.PyAudio()
            default_device = p.get_default_input_device_info()
            p.terminate()
            return default_device
        except Exception as e:
            logger.error(f"Error getting device info: {e}")
            return {}

    def list_devices(self) -> list:
        """
        List all available audio input devices.

        Returns:
            List of device information dictionaries
        """
        devices = []
        try:
            p = pyaudio.PyAudio()
            for i in range(p.get_device_count()):
                device_info = p.get_device_info_by_index(i)
                if device_info['maxInputChannels'] > 0:
                    devices.append({
                        'index': i,
                        'name': device_info['name'],
                        'channels': device_info['maxInputChannels'],
                        'sample_rate': device_info['defaultSampleRate']
                    })
            p.terminate()
        except Exception as e:
            logger.error(f"Error listing devices: {e}")

        return devices


if __name__ == "__main__":
    # Test the audio recorder
    logging.basicConfig(level=logging.INFO)

    def test_callback(audio_data):
        print(f"Received audio chunk: {len(audio_data)} bytes")

    recorder = AudioRecorder(audio_callback=test_callback)

    print("\nAvailable input devices:")
    for device in recorder.list_devices():
        print(f"  [{device['index']}] {device['name']} - {device['channels']} channels @ {device['sample_rate']} Hz")

    print("\nDefault input device:")
    default = recorder.get_device_info()
    if default:
        print(f"  {default.get('name', 'Unknown')}")

    print("\nTesting recording for 3 seconds...")
    recorder.start_recording()

    import time
    time.sleep(3)

    recorder.stop_recording()
    print("Recording test complete!")
