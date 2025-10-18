#!/usr/bin/env python3
"""
Main application for voice transcription with global hotkey.
"""

# asyncio not needed for simple API
import logging
import signal
import sys
import threading
import subprocess
from typing import Optional

from config import config
from audio_recorder import AudioRecorder
from openai_client import OpenAITranscriptionClient
from gui_indicator import RecordingIndicator
from hotkey_handler import HotkeyHandler, XDoToolPaste

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.log_level.upper(), logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class TranscribeApp:
    """Main application class."""

    def __init__(self):
        """Initialize the transcription application."""
        self.is_running = False
        self.is_recording = False

        # Components
        self.indicator: Optional[RecordingIndicator] = None
        self.hotkey_handler: Optional[HotkeyHandler] = None
        self.audio_recorder: Optional[AudioRecorder] = None
        self.openai_client: Optional[OpenAITranscriptionClient] = None


        logger.info("TranscribeApp initialized")

    def setup(self) -> bool:
        """
        Set up all components.

        Returns:
            True if setup successful, False otherwise.
        """
        logger.info("Setting up application...")

        # Validate configuration
        if not config.validate():
            logger.error("Configuration validation failed")
            return False

        # Initialize GUI indicator
        try:
            self.indicator = RecordingIndicator(on_quit_callback=self.stop)
            self.indicator.run_in_thread()
            logger.info("GUI indicator initialized")
        except Exception as e:
            logger.error(f"Failed to initialize GUI indicator: {e}")
            return False

        # Initialize OpenAI client
        try:
            self.openai_client = OpenAITranscriptionClient(
                on_transcription=self._on_transcription_received
            )
            logger.info("OpenAI client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            return False

        # Initialize audio recorder
        try:
            self.audio_recorder = AudioRecorder(
                audio_callback=self._on_audio_chunk
            )
            logger.info("Audio recorder initialized")

            # Log device info
            device_info = self.audio_recorder.get_device_info()
            if device_info:
                logger.info(f"Using audio device: {device_info.get('name', 'Unknown')}")

        except Exception as e:
            logger.error(f"Failed to initialize audio recorder: {e}")
            return False

        # Initialize hotkey handler
        try:
            self.hotkey_handler = HotkeyHandler(
                on_press_callback=self._on_hotkey_press,
                on_release_callback=self._on_hotkey_release
            )
            self.hotkey_handler.start()
            logger.info(f"Hotkey handler started: {config.get_hotkey_description()}")
        except Exception as e:
            logger.error(f"Failed to initialize hotkey handler: {e}")
            return False

        logger.info("Application setup complete")
        return True


    def _on_hotkey_press(self) -> None:
        """Callback when hotkey is pressed (start recording)."""
        logger.info("Hotkey pressed - starting recording")

        if self.is_recording:
            logger.warning("Already recording, ignoring hotkey press")
            return

        # Start recording
        self._start_recording()

    def _on_hotkey_release(self) -> None:
        """Callback when hotkey is released (stop recording)."""
        logger.info("Hotkey released - stopping recording")

        if not self.is_recording:
            logger.warning("Not recording, ignoring hotkey release")
            return

        # Stop recording
        self._stop_recording()

    def _start_recording(self) -> None:
        """Start recording audio."""
        try:
            self.is_recording = True

            # Update indicator
            if self.indicator:
                self.indicator.set_recording(True)

            # Start new recording session
            self.openai_client.start_recording()

            # Start audio recording
            if not self.audio_recorder.start_recording():
                logger.error("Failed to start audio recording")
                self.indicator.set_error("Recording failed")
                self.is_recording = False
                return

            logger.info("Recording started successfully")

        except Exception as e:
            logger.error(f"Error starting recording: {e}")
            if self.indicator:
                self.indicator.set_error(str(e))
            self.is_recording = False

    def _stop_recording(self) -> None:
        """Stop recording audio and request transcription."""
        try:
            # Stop audio recording
            self.audio_recorder.stop_recording()

            # Update indicator
            if self.indicator:
                self.indicator.set_transcribing()

            logger.info("Recording stopped, transcribing...")

            # Transcribe in a separate thread to avoid blocking
            def transcribe_thread():
                try:
                    self.openai_client.transcribe_audio()
                except Exception as e:
                    logger.error(f"Error in transcription thread: {e}")
                    if self.indicator:
                        self.indicator.set_error("Transcription failed")

            threading.Thread(target=transcribe_thread, daemon=True).start()

        except Exception as e:
            logger.error(f"Error stopping recording: {e}")
            if self.indicator:
                self.indicator.set_error(str(e))
        finally:
            self.is_recording = False

    def _on_audio_chunk(self, audio_data: bytes) -> None:
        """
        Callback when audio chunk is received from recorder.

        Args:
            audio_data: PCM16 audio data bytes
        """
        if not self.is_recording:
            return

        # Add to OpenAI client buffer
        self.openai_client.add_audio_chunk(audio_data)

    def _on_transcription_received(self, text: str) -> None:
        """
        Callback when transcription is received from OpenAI.

        Args:
            text: Transcribed text
        """
        logger.info(f"Transcription received: {text}")

        try:
            # Copy to clipboard using xclip directly
            process = subprocess.Popen(
                ['xclip', '-selection', 'clipboard'],
                stdin=subprocess.PIPE,
                env={'DISPLAY': ':0'}
            )
            process.communicate(input=text.encode('utf-8'))
            logger.info("Transcription copied to clipboard")

            # Simulate Ctrl+Shift+V to paste
            XDoToolPaste.paste()

            # Update indicator
            if self.indicator:
                self.indicator.set_ready()

        except Exception as e:
            logger.error(f"Error handling transcription: {e}")
            if self.indicator:
                self.indicator.set_error("Paste failed")

    def run(self) -> None:
        """Run the application."""
        self.is_running = True
        logger.info(f"Application running. Press {config.get_hotkey_description()} to record.")

        # Set up signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        try:
            # Keep the main thread alive
            while self.is_running:
                import time
                time.sleep(1)

        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")

        finally:
            self.stop()

    def stop(self) -> None:
        """Stop the application and clean up resources."""
        if not self.is_running:
            return

        logger.info("Stopping application...")
        self.is_running = False

        # Stop hotkey handler
        if self.hotkey_handler:
            self.hotkey_handler.stop()

        # Stop recording if active
        if self.is_recording and self.audio_recorder:
            self.audio_recorder.stop_recording()


        # Stop GUI
        if self.indicator:
            self.indicator.quit()

        logger.info("Application stopped")

    def _signal_handler(self, signum, frame) -> None:
        """
        Handle system signals.

        Args:
            signum: Signal number
            frame: Current stack frame
        """
        logger.info(f"Received signal {signum}")
        self.stop()
        sys.exit(0)


def main():
    """Main entry point."""
    logger.info("Starting Voice Transcription Application")
    logger.info(f"OpenAI Model: {config.model}")
    logger.info(f"Hotkey: {config.get_hotkey_description()}")

    app = TranscribeApp()

    if not app.setup():
        logger.error("Application setup failed")
        sys.exit(1)

    try:
        app.run()
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
