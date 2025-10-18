# 🎤 Talkable Transcription

**Talk naturally, transcribe instantly.**

Voice-to-text for Ubuntu using OpenAI Whisper. Press a hotkey, speak, and get instant transcription.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## Quick Start

```bash
git clone git@github.com:DowLucas/talkable-transcribe.git
cd talkable-transcribe
./install.sh
```

Edit `.env` to add your OpenAI API key, then:

```bash
systemctl --user enable transcribe.service
systemctl --user start transcribe.service
```

## Usage

1. Press and hold `Right Ctrl + Left Arrow`
2. Speak
3. Release - text auto-pastes at cursor

## Requirements

- Ubuntu 20.04+ (X11, not Wayland)
- Python 3.8+
- OpenAI API key
- Microphone

## Configuration

Edit `.env`:

```bash
OPENAI_API_KEY=your_key_here
HOTKEY_CTRL=true
HOTKEY_KEY=left    # or: right, up, down, space, etc.
```

## Commands

```bash
systemctl --user status transcribe.service    # Check status
journalctl --user -u transcribe.service -f    # View logs
systemctl --user restart transcribe.service   # Restart
```

## Troubleshooting

**Hotkeys not working?** Switch to X11 (not Wayland)
**Service won't start?** Check logs: `journalctl --user -u transcribe.service`
**Clipboard issues?** Install: `sudo apt install xclip xsel`

See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for more.

## Cost

~$0.006/minute via OpenAI Whisper API

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md)

## License

MIT License - see [LICENSE](LICENSE)
