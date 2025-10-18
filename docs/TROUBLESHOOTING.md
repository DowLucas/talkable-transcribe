# Troubleshooting Guide

## Service Issues

### Service won't start - "Can't connect to display" error

**Symptoms:**
```
ImportError: this platform is not supported: ('failed to acquire X connection: Can't connect to display ":0"
```

**Solution:**
The systemd service file needs to properly integrate with the graphical session. Make sure your `transcribe.service` file uses:

```ini
[Unit]
PartOf=graphical-session.target

[Install]
WantedBy=graphical-session.target
```

NOT `default.target`. The service needs to be part of the graphical session to access X11/Wayland.

**Steps to fix:**
```bash
# Update the service file
cp transcribe.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user restart transcribe.service
```

### Service won't start - PyGObject import error

**Symptoms:**
```
ModuleNotFoundError: No module named 'gi'
```

**Solution:**
PyGObject must be installed via system packages and the virtual environment needs `--system-site-packages`:

```bash
# Install system package
sudo apt install python3-gi

# Recreate venv with system site packages
rm -rf venv
python3 -m venv --system-site-packages venv
source venv/bin/activate
pip install -r requirements.txt
```

### ALSA/JACK warnings in logs

**Symptoms:**
```
ALSA lib pcm_dmix.c:1000:(snd_pcm_dmix_open) unable to open slave
jack server is not running or cannot be started
```

**Solution:**
These warnings are **normal** and can be ignored. PyAudio checks multiple audio backends (JACK, ALSA, PulseAudio) and will use whichever is available. The application will still work fine.

## Audio Issues

### No audio device found

**Check available devices:**
```bash
source venv/bin/activate
python audio_recorder.py
```

This will list all available audio input devices.

**Solution:**
- Ensure microphone is plugged in
- Check system audio settings
- Try selecting a different device in the code if needed

### Recording is silent

**Check microphone permissions:**
```bash
# Test recording with arecord
arecord -d 3 test.wav
aplay test.wav
rm test.wav
```

If this doesn't work, your microphone isn't working at the system level.

## Hotkey Issues

### Hotkey not detected (Wayland)

**Check session type:**
```bash
echo $XDG_SESSION_TYPE
```

**If Wayland:**
- Hotkey detection has limitations on Wayland
- Consider switching to X11 session
- Or run the app manually in your user session (not as systemd service)

**Workaround - Run manually:**
```bash
source venv/bin/activate
python transcribe_app.py
```

### Hotkey conflicts with system shortcuts

**Change the hotkey:**
Edit `.env`:
```bash
HOTKEY_KEY=t  # Use Ctrl+Shift+T instead
```

Then restart:
```bash
systemctl --user restart transcribe.service
```

## OpenAI API Issues

### Invalid API key error

**Verify API key:**
```bash
cat .env | grep OPENAI_API_KEY
```

**Test API key:**
```bash
source venv/bin/activate
python -c "from openai import OpenAI; client = OpenAI(); print('API key valid!')"
```

### Connection timeout

**Check internet:**
```bash
ping -c 3 api.openai.com
```

**Check firewall:**
WebSocket connections on port 443 must be allowed.

### Quota exceeded

**Solution:**
- Check your OpenAI account usage
- Add billing information at https://platform.openai.com/account/billing
- Ensure you have credit available

## Clipboard/Paste Issues

### Text not pasting automatically

**Check xdotool:**
```bash
which xdotool
xdotool key ctrl+shift+v  # Should paste clipboard
```

**Install if missing:**
```bash
sudo apt install xdotool
```

### Clipboard access fails

**Test clipboard:**
```bash
source venv/bin/activate
python -c "import pyperclip; pyperclip.copy('test'); print(pyperclip.paste())"
```

## GTK/GUI Issues

### No system tray icon

**Check AppIndicator support:**
```bash
dpkg -l | grep appindicator3
```

**Install if missing:**
```bash
sudo apt install gir1.2-appindicator3-0.1
```

**For GNOME Shell users:**
Install AppIndicator extension:
```bash
sudo apt install gnome-shell-extension-appindicator
gnome-extensions enable appindicatorsupport@rgcjonas.gmail.com
```

## Debugging Commands

### View live logs
```bash
journalctl --user -u transcribe.service -f
```

### Check service status
```bash
systemctl --user status transcribe.service
```

### Test individual components
```bash
./test_components.sh
```

### Run in debug mode
Edit `.env`:
```bash
LOG_LEVEL=DEBUG
```

Then restart:
```bash
systemctl --user restart transcribe.service
journalctl --user -u transcribe.service -f
```

### Test audio recording manually
```bash
source venv/bin/activate
python audio_recorder.py
```

### Test OpenAI connection
```bash
source venv/bin/activate
python openai_client.py
```

### Test hotkey detection
```bash
source venv/bin/activate
python hotkey_handler.py
```

## Getting Help

1. **Check logs first:**
   ```bash
   journalctl --user -u transcribe.service --since "1 hour ago"
   ```

2. **Run manually to see errors:**
   ```bash
   systemctl --user stop transcribe.service
   source venv/bin/activate
   python transcribe_app.py
   ```

3. **Verify all dependencies:**
   ```bash
   ./install.sh  # Re-run installation
   ```

4. **Check system requirements:**
   - Ubuntu 20.04+ or Debian-based Linux
   - Python 3.8+
   - X11 session (Wayland has limitations)
   - Working microphone
   - Internet connection

## Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `OPENAI_API_KEY not set` | Missing API key | Edit `.env` and add key |
| `Can't connect to display` | Wrong systemd target | Use `graphical-session.target` |
| `No module named 'gi'` | PyGObject not installed | Install `python3-gi` system package |
| `Audio device not found` | No microphone | Check microphone connection |
| `Connection refused` | No internet | Check network connection |
| `xdotool: command not found` | xdotool not installed | `sudo apt install xdotool` |

## Performance Issues

### High CPU usage

**Check logs for errors:**
```bash
journalctl --user -u transcribe.service | grep ERROR
```

**Reduce log level:**
Edit `.env`:
```bash
LOG_LEVEL=WARNING
```

### Memory leaks

**Restart service periodically:**
```bash
systemctl --user restart transcribe.service
```

Or add to service file:
```ini
RuntimeMaxSec=86400  # Restart after 24 hours
```

## Reinstallation

If all else fails, completely reinstall:

```bash
# Stop and remove service
systemctl --user stop transcribe.service
systemctl --user disable transcribe.service
rm ~/.config/systemd/user/transcribe.service
systemctl --user daemon-reload

# Remove virtual environment
cd ~/dev/transcribe
rm -rf venv

# Reinstall
./install.sh

# Reconfigure
nano .env  # Add API key

# Start service
systemctl --user enable transcribe.service
systemctl --user start transcribe.service
```

## Still Having Issues?

1. Check the main `README.md` for basic usage
2. Review `PROJECT_SUMMARY.md` for architecture details
3. Run components individually using `test_components.sh`
4. Check OpenAI status: https://status.openai.com/
5. Ensure you're on Ubuntu 22.04+ with X11 (not Wayland)
