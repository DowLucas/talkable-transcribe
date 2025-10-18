# Quick Reference Card

## Installation (First Time Only)

```bash
./install.sh
nano .env  # Add your OpenAI API key
systemctl --user enable transcribe.service
systemctl --user start transcribe.service
```

## Daily Usage

**Press and hold** `Ctrl+Shift+R` → **Speak** → **Release**

The transcribed text will automatically paste where your cursor is.

## Common Commands

| Action | Command |
|--------|---------|
| Check if running | `systemctl --user status transcribe.service` |
| View logs | `journalctl --user -u transcribe.service -f` |
| Restart service | `systemctl --user restart transcribe.service` |
| Stop service | `systemctl --user stop transcribe.service` |
| Start service | `systemctl --user start transcribe.service` |
| Test manually | `source venv/bin/activate && python transcribe_app.py` |
| Test components | `./test_components.sh` |

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Service won't start | Check logs: `journalctl --user -u transcribe.service` |
| No API key error | Edit `.env` file and add your OpenAI API key |
| Hotkey not working | Make sure you're using X11 (not Wayland) |
| No audio device | Check: `python audio_recorder.py` |
| Auto-paste fails | Install: `sudo apt install xdotool` |

## File Locations

| File | Purpose |
|------|---------|
| `~/.config/systemd/user/transcribe.service` | Service definition |
| `~/dev/transcribe/.env` | API key and configuration |
| `~/dev/transcribe/venv/` | Python virtual environment |

## Configuration (.env)

```bash
OPENAI_API_KEY=sk-...              # Your API key (required)
AUDIO_SAMPLE_RATE=24000            # 24kHz for gpt-4o-transcribe
HOTKEY_KEY=r                       # Main key (with Ctrl+Shift)
LOG_LEVEL=INFO                     # DEBUG, INFO, WARNING, ERROR
```

## Costs (Approximate)

- $0.006 per minute of audio
- $0.36 per hour
- ~$1.80/month for 10 min/day usage

## System Requirements

- Ubuntu 20.04+ (or Debian-based Linux)
- Python 3.8+
- Internet connection
- Microphone
- X11 display server (not Wayland)

## Support

1. Check `README.md` for detailed documentation
2. View `PROJECT_SUMMARY.md` for technical details
3. Check logs: `journalctl --user -u transcribe.service`
4. Test components: `./test_components.sh`

## Uninstall

```bash
./uninstall.sh
cd .. && rm -rf transcribe/
```

---

**Version**: 1.0.0
**License**: MIT
**Model**: OpenAI GPT-4o-Transcribe
