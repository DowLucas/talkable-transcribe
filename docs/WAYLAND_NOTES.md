## Wayland Compatibility Notes

### The Issue

You're currently running **GNOME on Wayland**. Wayland has security restrictions that prevent background services (systemd) from capturing global hotkeys. This is by design for security reasons.

### Your Options

#### Option 1: Run Manually (Quick Solution)

Instead of using the systemd service, run the app directly in your user session:

```bash
cd ~/dev/transcribe
./run.sh
```

This will:
- Stop the systemd service
- Run the app in your current session
- Allow hotkey detection to work properly
- Show the system tray icon

**Pros:**
✅ Works immediately
✅ Hotkeys work properly
✅ Easy to start/stop

**Cons:**
❌ Need to run manually each time
❌ Closes when you close the terminal (unless you use `nohup` or background it)

#### Option 2: Switch to X11 (Recommended for Best Experience)

Log out and select **"Ubuntu on Xorg"** at the login screen, then log back in.

After logging in with X11:
```bash
systemctl --user restart transcribe.service
```

**Pros:**
✅ Hotkeys work perfectly
✅ Runs as background service
✅ Auto-starts on login
✅ Most reliable option

**Cons:**
❌ Need to use X11 instead of Wayland

#### Option 3: Create Desktop Launcher (Compromise)

Create an auto-start entry that runs the app in your session:

```bash
mkdir -p ~/.config/autostart
cat > ~/.config/autostart/transcribe.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=Voice Transcription
Comment=Voice transcription with OpenAI
Exec=/home/lucas/dev/transcribe/venv/bin/python /home/lucas/dev/transcribe/transcribe_app.py
Icon=audio-input-microphone
Terminal=false
X-GNOME-Autostart-enabled=true
EOF
```

Disable the systemd service:
```bash
systemctl --user disable transcribe.service
systemctl --user stop transcribe.service
```

**Pros:**
✅ Auto-starts on login
✅ Hotkeys work
✅ No need to switch to X11

**Cons:**
❌ Runs in user session (not as clean as systemd)
❌ Less control over service management

### Current Status

Your setup:
- **Desktop**: GNOME
- **Display Server**: Wayland
- **System Tray Icon**: ✅ Working (you can see it)
- **Global Hotkeys**: ❌ Blocked by Wayland security

### Quick Test

To verify hotkeys work when running manually:

1. Stop the service:
   ```bash
   systemctl --user stop transcribe.service
   ```

2. Run manually:
   ```bash
   cd ~/dev/transcribe
   ./run.sh
   ```

3. Try pressing **RCtrl + Left Arrow**

You should see log messages like:
```
INFO - Hotkey pressed
INFO - Starting recording
```

### Recommendation

For the best experience with this application, I recommend **switching to X11** at login. This is the most reliable way to use global hotkeys with background services.

Alternatively, if you prefer to stay on Wayland, use **`./run.sh`** to run the app manually whenever you need it.

### Why This Happens

Wayland's security model prevents applications from:
- Capturing global keyboard input (unless running in your active session)
- Screen recording without permission
- Injecting keyboard events in some cases

This is intentional for security, but it limits the functionality of tools like this transcription app that need global hotkey access.

X11 doesn't have these restrictions, which is why the app works perfectly there.
