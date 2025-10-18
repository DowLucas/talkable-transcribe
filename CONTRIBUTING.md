# Contributing to Voice Transcription

First off, thank you for considering contributing to Voice Transcription! It's people like you that make this tool better for everyone.

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When creating a bug report, include as many details as possible:

**Bug Report Template:**
- **OS Version**: Ubuntu 22.04, etc.
- **Python Version**: `python3 --version`
- **Display Server**: X11 or Wayland (`echo $XDG_SESSION_TYPE`)
- **Steps to Reproduce**: Clear steps to reproduce the behavior
- **Expected Behavior**: What you expected to happen
- **Actual Behavior**: What actually happened
- **Logs**: Output from `journalctl --user -u transcribe.service`

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Clear Description**: Describe the enhancement in detail
- **Use Case**: Explain why this would be useful
- **Alternatives**: Describe alternatives you've considered
- **Additional Context**: Add any other context or screenshots

### Pull Requests

1. **Fork the Repository**
   ```bash
   git clone git@github.com:DowLucas/talkable-transcribe.git
   cd talkable-transcribe
   ```

2. **Create a Branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **Make Your Changes**
   - Follow the existing code style
   - Add comments for complex logic
   - Update documentation as needed

4. **Test Your Changes**
   ```bash
   # Run the app manually
   source venv/bin/activate
   python transcribe_app.py

   # Test individual components
   ./test_components.sh
   ```

5. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "Add amazing feature"
   ```

6. **Push to Your Fork**
   ```bash
   git push origin feature/amazing-feature
   ```

7. **Open a Pull Request**
   - Provide a clear description of the changes
   - Reference any related issues
   - Include screenshots/GIFs if applicable

## Development Setup

### Prerequisites

```bash
# System dependencies
sudo apt install python3-venv python3-pip python3-gi \
    gir1.2-gtk-3.0 gir1.2-appindicator3-0.1 \
    portaudio19-dev xdotool xclip xsel

# Clone and setup
git clone git@github.com:DowLucas/talkable-transcribe.git
cd talkable-transcribe
./install.sh
```

### Project Structure

```
talkable-transcribe/
├── transcribe_app.py      # Main application
├── config.py              # Configuration management
├── audio_recorder.py      # Audio capture
├── openai_client.py       # OpenAI API client
├── gui_indicator.py       # GTK system tray
├── hotkey_handler.py      # Global hotkeys
├── install.sh             # Installation script
├── transcribe.service     # Systemd service
├── .env.example           # Configuration template
├── requirements.txt       # Python dependencies
└── README.md             # Documentation
```

### Code Style

- **Python**: Follow PEP 8 guidelines
- **Comments**: Add docstrings for all functions and classes
- **Logging**: Use appropriate log levels (DEBUG, INFO, WARNING, ERROR)
- **Type Hints**: Use type hints where applicable

Example:

```python
def my_function(param: str) -> bool:
    """
    Brief description of function.

    Args:
        param: Description of parameter

    Returns:
        Description of return value
    """
    logger.info(f"Function called with {param}")
    return True
```

### Testing

Currently, the project uses manual testing. We welcome contributions for automated tests!

**Manual Testing Checklist:**
- [ ] Hotkey detection works
- [ ] Audio recording captures sound
- [ ] Transcription is accurate
- [ ] Clipboard copy works
- [ ] Auto-paste functions correctly
- [ ] System tray indicator updates properly
- [ ] Service starts/stops cleanly

## Areas for Contribution

We especially welcome contributions in these areas:

### High Priority
- [ ] Automated testing framework
- [ ] Wayland support improvements
- [ ] Better error handling and recovery
- [ ] Multi-language support
- [ ] Performance optimizations

### Medium Priority
- [ ] GUI configuration panel
- [ ] Transcription history/logging
- [ ] Custom vocabulary support
- [ ] Alternative TTS engines
- [ ] Windows/macOS support

### Documentation
- [ ] Video tutorials
- [ ] More troubleshooting guides
- [ ] API documentation
- [ ] Architecture diagrams

## Questions?

Feel free to:
- Open a [Discussion](https://github.com/DowLucas/talkable-transcribe/discussions)
- Create an [Issue](https://github.com/DowLucas/talkable-transcribe/issues)
- Reach out to the maintainers

## Recognition

Contributors will be recognized in:
- README.md Contributors section
- Release notes
- Project documentation

Thank you for contributing! 🎉
