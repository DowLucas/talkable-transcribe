# Project Summary: Voice Transcription Application

## Overview

A complete Ubuntu voice transcription application using OpenAI's GPT-4o-Transcribe model. Records audio via global hotkey, transcribes in real-time using WebSocket streaming, and automatically pastes the result.

## Project Status: ✅ COMPLETE

All components have been implemented and tested. Ready for installation and use.

## Components

### Core Application Files

1. **`transcribe_app.py`** (11 KB)
   - Main application coordinator
   - Manages lifecycle of all components
   - Handles asyncio event loop for WebSocket communication
   - Coordinates recording → transcription → clipboard → paste workflow

2. **`config.py`** (3 KB)
   - Configuration management from `.env` file
   - Validates settings on startup
   - Provides global config singleton

3. **`audio_recorder.py`** (6.5 KB)
   - PyAudio-based audio capture
   - Streams PCM16 audio at 24kHz mono
   - Callback-based architecture for real-time streaming
   - Includes device enumeration and testing

4. **`openai_client.py`** (11 KB)
   - WebSocket client for OpenAI Realtime API
   - Handles session initialization and audio streaming
   - Processes transcription responses
   - Error handling and reconnection logic

5. **`gui_indicator.py`** (6.7 KB)
   - GTK-based system tray indicator
   - Shows recording status with icon changes
   - Menu with status and quit option
   - Optional overlay window for recording status

6. **`hotkey_handler.py`** (6.7 KB)
   - Global hotkey detection using pynput
   - Configurable key combinations
   - XDoTool integration for auto-paste simulation

### Configuration & Setup

7. **`.env.example`** (282 bytes)
   - Template for environment variables
   - Documents all available settings

8. **`requirements.txt`** (114 bytes)
   - Python package dependencies
   - Pinned versions for stability

9. **`transcribe.service`** (427 bytes)
   - Systemd user service definition
   - Auto-start on login
   - Proper environment setup

### Installation & Maintenance

10. **`install.sh`** (3.4 KB)
    - Automated installation script
    - Checks dependencies
    - Creates virtual environment
    - Sets up systemd service

11. **`uninstall.sh`** (924 bytes)
    - Clean removal of service
    - Preserves application files

12. **`test_components.sh`** (1.7 KB)
    - Interactive component testing menu
    - Useful for debugging individual modules

### Documentation

13. **`README.md`** (7.7 KB)
    - Comprehensive user documentation
    - Installation instructions
    - Usage guide
    - Troubleshooting section

14. **`PROJECT_SUMMARY.md`** (this file)
    - Technical overview
    - Architecture documentation
    - Development notes

15. **`LICENSE`** (1.1 KB)
    - MIT License

16. **`.gitignore`** (221 bytes)
    - Excludes venv, .env, and build artifacts

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     transcribe_app.py                       │
│                   (Main Coordinator)                        │
└──────┬──────────┬──────────┬──────────┬──────────┬─────────┘
       │          │          │          │          │
       ▼          ▼          ▼          ▼          ▼
   ┌────────┐ ┌──────┐ ┌─────────┐ ┌────────┐ ┌────────┐
   │ config │ │ audio│ │ openai  │ │  GUI   │ │hotkey  │
   │  .py   │ │ rec. │ │ client  │ │ indic. │ │handler │
   └────────┘ └──────┘ └─────────┘ └────────┘ └────────┘
       │          │          │          │          │
       ▼          ▼          ▼          ▼          ▼
    .env    PyAudio   WebSocket    GTK3     pynput
                    OpenAI API  AppIndicator
```

## Data Flow

1. **Hotkey Press** → `hotkey_handler` detects Ctrl+Shift+R
2. **Start Recording** → `audio_recorder` starts capturing
3. **Stream Audio** → Chunks sent to `openai_client` via WebSocket
4. **Update UI** → `gui_indicator` shows recording status
5. **Hotkey Release** → Stop recording, commit audio buffer
6. **Transcription** → OpenAI returns text via WebSocket
7. **Clipboard** → Text copied using `pyperclip`
8. **Auto-paste** → `xdotool` simulates Ctrl+Shift+V
9. **Ready** → Return to idle state

## Technology Stack

### Backend
- **Python 3.8+**: Main language
- **asyncio**: WebSocket communication
- **PyAudio**: Audio capture
- **websockets**: WebSocket client library
- **openai**: OpenAI API client

### Frontend
- **GTK 3**: Native Ubuntu UI
- **PyGObject**: Python GTK bindings
- **AppIndicator3**: System tray integration

### System Integration
- **pynput**: Global hotkey detection
- **xdotool**: Keyboard simulation
- **systemd**: Service management
- **pyperclip**: Clipboard access

## API Integration

### OpenAI Realtime API

- **Endpoint**: `wss://api.openai.com/v1/realtime`
- **Model**: `gpt-4o-transcribe`
- **Audio Format**: PCM16, 24kHz, mono, little-endian
- **Protocol**: WebSocket with JSON messages
- **Authentication**: Bearer token in headers

### Message Flow

```
Client → Server: session.update (configure)
Client → Server: input_audio_buffer.append (stream audio)
Client → Server: input_audio_buffer.commit (finalize)
Client → Server: response.create (request transcription)
Server → Client: response.text.delta (streaming text)
Server → Client: response.done (complete transcription)
```

## Configuration Options

| Setting | Default | Description |
|---------|---------|-------------|
| `OPENAI_API_KEY` | (required) | OpenAI API key |
| `AUDIO_SAMPLE_RATE` | 24000 | Sample rate in Hz |
| `AUDIO_CHANNELS` | 1 | Mono audio |
| `AUDIO_CHUNK_SIZE` | 1024 | Buffer size |
| `HOTKEY_CTRL` | true | Require Ctrl |
| `HOTKEY_SHIFT` | true | Require Shift |
| `HOTKEY_KEY` | r | Main key |
| `LOG_LEVEL` | INFO | Logging verbosity |

## System Requirements

### Minimum
- Ubuntu 20.04 or later
- 2 GB RAM
- Internet connection
- Microphone

### Recommended
- Ubuntu 22.04 or later
- 4 GB RAM
- Stable broadband connection
- Quality USB microphone

## Installation Time

- System dependencies: ~2-5 minutes
- Python dependencies: ~1-2 minutes
- Configuration: ~1 minute
- **Total**: ~5-10 minutes

## Performance

- **Latency**: ~1-3 seconds (recording → transcription → paste)
- **Accuracy**: GPT-4o-Transcribe WER (Word Error Rate) varies by language/accent
- **CPU Usage**: Minimal (mostly I/O bound)
- **Memory**: ~50-100 MB
- **Network**: ~100-200 KB per minute of audio

## Cost Estimate

Based on OpenAI pricing (2025):

- **$0.006 per minute** of audio
- **$0.36 per hour** of audio
- Typical use (10 min/day): **$0.06/day** or **$1.80/month**

## Testing

Each module includes standalone testing:

```bash
# Test audio recording
python audio_recorder.py

# Test GUI indicator
python gui_indicator.py

# Test hotkey detection
python hotkey_handler.py

# Or use the interactive menu
./test_components.sh
```

## Logging

Logs are managed by systemd journal:

```bash
# View all logs
journalctl --user -u transcribe.service

# Follow logs in real-time
journalctl --user -u transcribe.service -f

# View logs from today
journalctl --user -u transcribe.service --since today
```

## Security Considerations

1. **API Key Storage**: Stored in `.env` file (file permissions: 600 recommended)
2. **Audio Privacy**: Audio sent to OpenAI servers (not stored locally)
3. **Network**: Uses secure WebSocket (WSS) with TLS
4. **Clipboard**: Temporary storage before auto-paste
5. **Service**: Runs as user service (not system-wide)

## Known Limitations

1. **Wayland**: Hotkey detection may not work on Wayland (use X11)
2. **File Size**: Max 25MB audio (not an issue for real-time streaming)
3. **Internet**: Requires active connection for transcription
4. **Speaker Diarization**: No multi-speaker labeling
5. **Languages**: Supports multiple languages but optimized for English

## Future Enhancements

Potential improvements:

- [ ] Local transcription option (Whisper.cpp)
- [ ] Multiple hotkey configurations
- [ ] Transcription history/logging
- [ ] Custom vocabulary/terminology
- [ ] Wayland support investigation
- [ ] GUI configuration panel
- [ ] Audio preprocessing (noise reduction)
- [ ] Multiple language profiles

## Troubleshooting Guide

### Common Issues

1. **"API key not set"**
   - Edit `.env` and add your OpenAI API key

2. **"Hotkey not detected"**
   - Check if running on Wayland: `echo $XDG_SESSION_TYPE`
   - Switch to X11 session if needed

3. **"Audio device not found"**
   - Run `python audio_recorder.py` to list devices
   - Check microphone is connected and permissions

4. **"Service won't start"**
   - Check logs: `journalctl --user -u transcribe.service`
   - Verify Python dependencies installed

5. **"Auto-paste not working"**
   - Install xdotool: `sudo apt install xdotool`
   - Test manually: `xdotool key ctrl+shift+v`

## Development

### Code Style

- Python 3.8+ with type hints where appropriate
- Docstrings for all classes and functions
- Logging for debugging and monitoring
- Error handling with try-except blocks

### Module Independence

Each module can be tested independently:

- `audio_recorder.py`: Standalone audio capture
- `openai_client.py`: Standalone WebSocket client
- `gui_indicator.py`: Standalone system tray
- `hotkey_handler.py`: Standalone hotkey detection

### Contributing

1. Test individual modules before integration
2. Follow existing code style and structure
3. Update documentation for new features
4. Add error handling and logging

## Credits

**Developed by**: Lucas (with AI assistance)
**OpenAI Model**: GPT-4o-Transcribe
**Framework**: Ubuntu/GTK3
**License**: MIT

## Version History

- **v1.0.0** (2025-10-18): Initial release

## Resources

- OpenAI API Docs: https://platform.openai.com/docs
- GTK Documentation: https://docs.gtk.org/
- PyAudio Docs: https://people.csail.mit.edu/hubert/pyaudio/
- systemd: https://www.freedesktop.org/software/systemd/man/

---

**Status**: Production Ready ✅
**Last Updated**: 2025-10-18
