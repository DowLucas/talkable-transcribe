#!/bin/bash

# Test script for individual components

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Activate virtual environment
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found. Run ./install.sh first."
    exit 1
fi

source venv/bin/activate

echo "========================================="
echo "Voice Transcription Component Tests"
echo "========================================="
echo ""

PS3='Select a component to test: '
options=("Audio Recorder" "GUI Indicator" "Hotkey Handler" "Full Application" "Quit")

select opt in "${options[@]}"
do
    case $opt in
        "Audio Recorder")
            echo ""
            echo "Testing Audio Recorder..."
            echo "This will record for 3 seconds and show audio device info."
            echo ""
            python src/audio_recorder.py
            ;;
        "GUI Indicator")
            echo ""
            echo "Testing GUI Indicator..."
            echo "Check your system tray. The indicator will cycle through states."
            echo "Press Ctrl+C to exit."
            echo ""
            python src/gui_indicator.py
            ;;
        "Hotkey Handler")
            echo ""
            echo "Testing Hotkey Handler..."
            echo "Press Ctrl+Shift+R to test hotkey detection."
            echo "Press Ctrl+C to exit."
            echo ""
            python src/hotkey_handler.py
            ;;
        "Full Application")
            echo ""
            echo "Running Full Application..."
            echo "Press Ctrl+Shift+R to record, release to transcribe."
            echo "Make sure you have set your OpenAI API key in .env file."
            echo "Press Ctrl+C to exit."
            echo ""
            python main.py
            ;;
        "Quit")
            echo "Exiting..."
            break
            ;;
        *) echo "Invalid option $REPLY";;
    esac

    echo ""
    echo "Test completed. Select another test or quit."
    echo ""
done

deactivate
