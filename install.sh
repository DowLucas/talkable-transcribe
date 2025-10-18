#!/bin/bash

# Installation script for Voice Transcription Application
# This script sets up the application, creates a virtual environment, and installs dependencies.

set -e  # Exit on error

echo "========================================="
echo "Voice Transcription Application Installer"
echo "========================================="
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed."
    echo "Please install Python 3: sudo apt install python3 python3-pip python3-venv"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "Found Python $PYTHON_VERSION"

# Install system dependencies
echo ""
echo "Installing system dependencies..."
echo "This will require sudo access."
echo ""

sudo apt update
sudo apt install -y \
    python3-venv \
    python3-pip \
    python3-gi \
    python3-gi-cairo \
    gir1.2-gtk-3.0 \
    gir1.2-appindicator3-0.1 \
    portaudio19-dev \
    xdotool \
    libcairo2-dev \
    libgirepository1.0-dev

echo ""
echo "System dependencies installed successfully."

# Create virtual environment with system site packages
# This allows us to use the system-installed PyGObject
echo ""
echo "Creating Python virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists. Removing old one..."
    rm -rf venv
fi

python3 -m venv --system-site-packages venv
source venv/bin/activate

echo "Virtual environment created with system site packages."

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
pip install -r requirements.txt

echo ""
echo "Python dependencies installed successfully."

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo ""
    echo "Creating .env file from template..."
    cp .env.example .env
    echo ""
    echo "IMPORTANT: Please edit .env file and add your OpenAI API key:"
    echo "  nano .env"
    echo ""
    echo "Get your API key from: https://platform.openai.com/api-keys"
    echo ""
fi

# Make scripts executable
echo ""
echo "Making scripts executable..."
chmod +x transcribe_app.py
chmod +x install.sh
chmod +x uninstall.sh 2>/dev/null || true

# Set up systemd service
echo ""
echo "Setting up systemd service..."

# Create systemd user directory if it doesn't exist
mkdir -p ~/.config/systemd/user

# Copy service file
cp transcribe.service ~/.config/systemd/user/

# Reload systemd
systemctl --user daemon-reload

echo ""
echo "========================================="
echo "Installation Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Edit the .env file and add your OpenAI API key:"
echo "   nano $SCRIPT_DIR/.env"
echo ""
echo "2. Enable and start the service:"
echo "   systemctl --user enable transcribe.service"
echo "   systemctl --user start transcribe.service"
echo ""
echo "3. To check service status:"
echo "   systemctl --user status transcribe.service"
echo ""
echo "4. To view logs:"
echo "   journalctl --user -u transcribe.service -f"
echo ""
echo "5. To test manually (without systemd):"
echo "   source $SCRIPT_DIR/venv/bin/activate"
echo "   python $SCRIPT_DIR/transcribe_app.py"
echo ""
echo "Hotkey: Ctrl+Shift+R (press and hold to record, release to transcribe)"
echo ""
echo "========================================="
