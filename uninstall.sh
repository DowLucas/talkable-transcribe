#!/bin/bash

# Uninstallation script for Voice Transcription Application

set -e  # Exit on error

echo "========================================="
echo "Voice Transcription Application Uninstaller"
echo "========================================="
echo ""

# Stop and disable service
echo "Stopping and disabling systemd service..."
systemctl --user stop transcribe.service 2>/dev/null || true
systemctl --user disable transcribe.service 2>/dev/null || true

# Remove service file
echo "Removing service file..."
rm -f ~/.config/systemd/user/transcribe.service

# Reload systemd
systemctl --user daemon-reload

echo ""
echo "Service removed successfully."
echo ""
echo "Note: The application files in $(pwd) have NOT been deleted."
echo "If you want to remove them, run: rm -rf $(pwd)"
echo ""
echo "========================================="
echo "Uninstallation Complete!"
echo "========================================="
