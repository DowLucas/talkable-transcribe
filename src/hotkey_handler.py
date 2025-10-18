#!/usr/bin/env python3
"""
Global hotkey handler for recording toggle.
"""

import logging
from typing import Callable, Optional
from pynput import keyboard
from pynput.keyboard import Key, KeyCode

from config import config

logger = logging.getLogger(__name__)


class HotkeyHandler:
    """Handles global hotkey registration and detection."""

    def __init__(
        self,
        on_press_callback: Optional[Callable[[], None]] = None,
        on_release_callback: Optional[Callable[[], None]] = None
    ):
        """
        Initialize the hotkey handler.

        Args:
            on_press_callback: Callback when hotkey is pressed
            on_release_callback: Callback when hotkey is released
        """
        self.on_press_callback = on_press_callback
        self.on_release_callback = on_release_callback

        # Parse hotkey configuration
        self.hotkey_key = config.hotkey_key.lower()
        self.requires_ctrl = config.hotkey_ctrl
        self.requires_shift = config.hotkey_shift

        # Check if specific left/right modifiers are required
        self.requires_ctrl_r = getattr(config, 'hotkey_ctrl_r', False)
        self.requires_shift_r = getattr(config, 'hotkey_shift_r', False)

        # Map special key names to pynput Key objects
        self.special_key_map = {
            'left': Key.left,
            'right': Key.right,
            'up': Key.up,
            'down': Key.down,
            'space': Key.space,
            'enter': Key.enter,
            'tab': Key.tab,
            'esc': Key.esc,
            'backspace': Key.backspace,
        }

        # Get the actual key object if it's a special key
        self.hotkey_key_obj = self.special_key_map.get(self.hotkey_key, None)

        # Track current pressed keys
        self.current_keys = set()
        self.hotkey_pressed = False

        # Keyboard listener
        self.listener: Optional[keyboard.Listener] = None

        logger.info(f"Hotkey handler initialized: {config.get_hotkey_description()}")

    def start(self) -> bool:
        """
        Start listening for hotkey presses.

        Returns:
            True if started successfully, False otherwise.
        """
        if self.listener is not None:
            logger.warning("Hotkey listener already running")
            return False

        try:
            self.listener = keyboard.Listener(
                on_press=self._on_press,
                on_release=self._on_release
            )
            self.listener.start()
            logger.info("Hotkey listener started")
            return True

        except Exception as e:
            logger.error(f"Failed to start hotkey listener: {e}")
            return False

    def stop(self) -> None:
        """Stop listening for hotkey presses."""
        if self.listener is None:
            logger.warning("Hotkey listener not running")
            return

        try:
            self.listener.stop()
            self.listener = None
            logger.info("Hotkey listener stopped")
        except Exception as e:
            logger.error(f"Error stopping hotkey listener: {e}")

    def _on_press(self, key) -> None:
        """
        Handle key press event.

        Args:
            key: The key that was pressed
        """
        try:
            # Add key to current pressed keys
            if isinstance(key, Key):
                self.current_keys.add(key)
                logger.debug(f"Key pressed: {key} (special key)")
            elif isinstance(key, KeyCode):
                if key.char:
                    self.current_keys.add(key.char.lower())
                    logger.debug(f"Key pressed: {key.char} (character)")

            # Debug: Show all currently pressed keys
            logger.debug(f"Currently pressed keys: {self.current_keys}")

            # Debug: Show what we're looking for
            if not self.hotkey_pressed:
                logger.debug(f"Looking for: Ctrl={self.requires_ctrl} (R={self.requires_ctrl_r}), "
                           f"Shift={self.requires_shift} (R={self.requires_shift_r}), "
                           f"Key={self.hotkey_key}/{self.hotkey_key_obj}")

            # Check if hotkey combination is pressed
            if not self.hotkey_pressed and self._is_hotkey_pressed():
                self.hotkey_pressed = True
                logger.info("🎤 HOTKEY PRESSED - Starting recording!")
                if self.on_press_callback:
                    self.on_press_callback()

        except Exception as e:
            logger.error(f"Error in key press handler: {e}")

    def _on_release(self, key) -> None:
        """
        Handle key release event.

        Args:
            key: The key that was released
        """
        try:
            # Remove key from current pressed keys
            if isinstance(key, Key):
                self.current_keys.discard(key)
                logger.debug(f"Key released: {key} (special key)")
            elif isinstance(key, KeyCode):
                if key.char:
                    self.current_keys.discard(key.char.lower())
                    logger.debug(f"Key released: {key.char} (character)")

            # Debug: Show all currently pressed keys after release
            logger.debug(f"After release, pressed keys: {self.current_keys}")

            # Check if hotkey was released
            if self.hotkey_pressed and not self._is_hotkey_pressed():
                self.hotkey_pressed = False
                logger.info("🛑 HOTKEY RELEASED - Stopping recording!")
                if self.on_release_callback:
                    self.on_release_callback()

        except Exception as e:
            logger.error(f"Error in key release handler: {e}")

    def _is_hotkey_pressed(self) -> bool:
        """
        Check if the hotkey combination is currently pressed.

        Returns:
            True if hotkey is pressed, False otherwise.
        """
        # Check modifier keys
        if self.requires_ctrl:
            # If specifically right Ctrl is required
            if self.requires_ctrl_r:
                if Key.ctrl_r not in self.current_keys:
                    return False
            else:
                # Accept either left or right Ctrl
                if not (Key.ctrl_l in self.current_keys or Key.ctrl_r in self.current_keys):
                    return False

        if self.requires_shift:
            # If specifically right Shift is required
            if self.requires_shift_r:
                if Key.shift_r not in self.current_keys:
                    return False
            else:
                # Accept either left or right Shift
                if not (Key.shift_l in self.current_keys or Key.shift_r in self.current_keys):
                    return False

        # Check main key (could be special key or regular character)
        if self.hotkey_key_obj:
            # Special key (like arrow keys)
            if self.hotkey_key_obj not in self.current_keys:
                return False
        else:
            # Regular character key
            if self.hotkey_key not in self.current_keys:
                return False

        return True


class XDoToolPaste:
    """Utility class for simulating Ctrl+Shift+V using xdotool."""

    @staticmethod
    def paste() -> bool:
        """
        Simulate Ctrl+Shift+V keypress.

        Returns:
            True if successful, False otherwise.
        """
        import subprocess

        try:
            # Use xdotool to simulate keypress
            # First, give the user a small delay to release the hotkey
            import time
            time.sleep(0.1)

            # Simulate Ctrl+Shift+V
            result = subprocess.run(
                ['xdotool', 'key', 'ctrl+shift+v'],
                capture_output=True,
                text=True,
                timeout=2
            )

            if result.returncode == 0:
                logger.info("Successfully simulated Ctrl+Shift+V")
                return True
            else:
                logger.error(f"xdotool failed: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            logger.error("xdotool command timed out")
            return False
        except FileNotFoundError:
            logger.error("xdotool not found. Please install it: sudo apt install xdotool")
            return False
        except Exception as e:
            logger.error(f"Error simulating paste: {e}")
            return False


if __name__ == "__main__":
    # Test the hotkey handler
    logging.basicConfig(level=logging.INFO)

    def on_press():
        print("\n*** HOTKEY PRESSED - Recording should start ***\n")

    def on_release():
        print("\n*** HOTKEY RELEASED - Recording should stop ***\n")

    handler = HotkeyHandler(
        on_press_callback=on_press,
        on_release_callback=on_release
    )

    print(f"Press {config.get_hotkey_description()} to test hotkey detection")
    print("Press Ctrl+C to exit")

    handler.start()

    try:
        # Keep the program running
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping...")
        handler.stop()
