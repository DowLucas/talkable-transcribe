#!/usr/bin/env python3
"""
GTK GUI indicator for recording status.
"""

import logging
import gi

gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')

from gi.repository import Gtk, AppIndicator3, GLib
import threading

logger = logging.getLogger(__name__)


class RecordingIndicator:
    """System tray indicator for recording status."""

    def __init__(self, on_quit_callback=None):
        """
        Initialize the recording indicator.

        Args:
            on_quit_callback: Optional callback function to call when quitting.
        """
        self.on_quit_callback = on_quit_callback
        self.is_recording = False

        # Create indicator
        self.indicator = AppIndicator3.Indicator.new(
            "transcribe-indicator",
            "audio-input-microphone-symbolic",  # Default icon
            AppIndicator3.IndicatorCategory.APPLICATION_STATUS
        )

        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        self.indicator.set_title("Voice Transcription")

        # Create menu
        self.menu = Gtk.Menu()

        # Status item
        self.status_item = Gtk.MenuItem(label="Ready")
        self.status_item.set_sensitive(False)
        self.menu.append(self.status_item)

        # Separator
        separator = Gtk.SeparatorMenuItem()
        self.menu.append(separator)

        # Hotkey info item
        from config import config
        hotkey_info = Gtk.MenuItem(label=f"Hotkey: {config.get_hotkey_description()}")
        hotkey_info.set_sensitive(False)
        self.menu.append(hotkey_info)

        # Another separator
        separator2 = Gtk.SeparatorMenuItem()
        self.menu.append(separator2)

        # Quit item
        quit_item = Gtk.MenuItem(label="Quit")
        quit_item.connect("activate", self._on_quit)
        self.menu.append(quit_item)

        self.menu.show_all()
        self.indicator.set_menu(self.menu)

        logger.info("Recording indicator initialized")

    def set_recording(self, recording: bool) -> None:
        """
        Update the indicator to show recording status.

        Args:
            recording: True if recording, False otherwise.
        """
        self.is_recording = recording

        if recording:
            self.indicator.set_icon("media-record")
            self.status_item.set_label("🔴 Recording...")
            logger.info("Indicator: Recording started")
        else:
            self.indicator.set_icon("audio-input-microphone-symbolic")
            self.status_item.set_label("Ready")
            logger.info("Indicator: Recording stopped")

    def set_transcribing(self) -> None:
        """Update the indicator to show transcribing status."""
        self.indicator.set_icon("emblem-synchronizing")
        self.status_item.set_label("⏳ Transcribing...")
        logger.info("Indicator: Transcribing")

    def set_ready(self) -> None:
        """Update the indicator to show ready status."""
        self.indicator.set_icon("audio-input-microphone-symbolic")
        self.status_item.set_label("Ready")
        logger.info("Indicator: Ready")

    def set_error(self, message: str) -> None:
        """
        Update the indicator to show error status.

        Args:
            message: Error message to display
        """
        self.indicator.set_icon("dialog-error")
        self.status_item.set_label(f"❌ Error: {message}")
        logger.error(f"Indicator: Error - {message}")

    def _on_quit(self, widget) -> None:
        """Handle quit menu item click."""
        logger.info("Quit requested from indicator menu")
        if self.on_quit_callback:
            self.on_quit_callback()
        Gtk.main_quit()

    def run(self) -> None:
        """Run the GTK main loop."""
        logger.info("Starting GTK main loop")
        Gtk.main()

    def run_in_thread(self) -> threading.Thread:
        """
        Run the GTK main loop in a separate thread.

        Returns:
            The thread object
        """
        thread = threading.Thread(target=self.run, daemon=True)
        thread.start()
        logger.info("GTK main loop started in separate thread")
        return thread

    @staticmethod
    def quit() -> None:
        """Quit the GTK main loop."""
        GLib.idle_add(Gtk.main_quit)


class RecordingWindow:
    """Optional overlay window to show recording status."""

    def __init__(self):
        """Initialize the recording window."""
        self.window = Gtk.Window(title="Recording")
        self.window.set_decorated(False)
        self.window.set_keep_above(True)
        self.window.set_default_size(200, 60)
        self.window.set_position(Gtk.WindowPosition.CENTER)

        # Make it semi-transparent
        self.window.set_opacity(0.9)

        # Add label
        self.label = Gtk.Label()
        self.label.set_markup("<span size='large' weight='bold'>🔴 Recording...</span>")

        # Add to window
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        box.set_margin_top(10)
        box.set_margin_bottom(10)
        box.set_margin_start(10)
        box.set_margin_end(10)
        box.pack_start(self.label, True, True, 0)

        self.window.add(box)

        # Connect close event
        self.window.connect("delete-event", self._on_close)

    def show(self) -> None:
        """Show the recording window."""
        GLib.idle_add(self._show_window)

    def _show_window(self) -> None:
        """Show the window (must be called from GTK main thread)."""
        self.window.show_all()

    def hide(self) -> None:
        """Hide the recording window."""
        GLib.idle_add(self._hide_window)

    def _hide_window(self) -> None:
        """Hide the window (must be called from GTK main thread)."""
        self.window.hide()

    def _on_close(self, widget, event) -> bool:
        """Handle window close event."""
        # Prevent closing, just hide instead
        self.hide()
        return True


if __name__ == "__main__":
    # Test the indicator
    logging.basicConfig(level=logging.INFO)

    def on_quit():
        print("Quit callback called")

    indicator = RecordingIndicator(on_quit_callback=on_quit)

    # Test status changes
    import time
    import threading

    def test_statuses():
        time.sleep(2)
        indicator.set_recording(True)
        time.sleep(2)
        indicator.set_transcribing()
        time.sleep(2)
        indicator.set_ready()
        time.sleep(2)
        indicator.set_error("Test error")
        time.sleep(2)
        indicator.set_ready()

    test_thread = threading.Thread(target=test_statuses, daemon=True)
    test_thread.start()

    print("Running indicator test. Check system tray. Will auto-cycle through states.")
    indicator.run()
