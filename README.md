# DSA Lockdown

A macOS lockdown tool to force-focus your study sessions on LeetCode. Blocks distractions, locks Chrome, and logs emergency exits.

## What It Does

1. Opens Chrome in fullscreen on your LeetCode problem list
2. Every 2 seconds:
   - Scans all open Chrome tabs → closes any not on allowed domains
   - Checks frontmost app → brings Chrome back if you switch away
3. Blocks `Cmd+Q` and `Cmd+W` system-wide (quit/close disabled)
4. Notifies at 30 min and 10 min remaining
5. Auto-unlocks when session ends

## File Structure

```
dsalock/
  main.py          ← entry point
  config.json      ← settings (duration, allowed domains)
  enforcer.py      ← tab + app monitoring loop
  timer.py         ← session countdown with milestone notifications
  notifier.py      ← macOS notifications
  unlock.py        ← auto-unlock after session ends
  keyblock.py      ← blocks Cmd+Q and Cmd+W
  emergency.py     ← manual emergency exit (run from terminal)
  set_time.sh      ← helper to reschedule daily trigger
  secret.hash      ← hashed passphrase (auto-generated on setup)
  shame.log        ← logs every emergency exit
  logs.txt         ← stdout from launchd runs
  error.txt        ← stderr from launchd runs
```

---

## Setup

### 1. Install dependencies

```bash
pip3 install psutil pyobjc-framework-Quartz
```

### 2. Set emergency passphrase (one time)

```bash
python3 -c "
import hashlib
p = input('Set passphrase: ')
open('secret.hash','w').write(hashlib.sha256(p.encode()).hexdigest())
print('Saved.')
"
```

Pick something you will remember but would never type by accident.

### 3. Configure

Edit `config.json`:

```json
{
  "duration_minutes": 120,
  "start_hour": 23,
  "allowed_domains": [
    "leetcode.com",
    "chatgpt.com",
    "neetcode.io"
  ],
  "allowed_apps": [
    "Google Chrome"
  ],
  "check_interval_seconds": 2
}
```

### 4. Grant macOS permissions

**Accessibility** — required for key blocking:
```
System Settings → Privacy & Security → Accessibility → enable Terminal
```

**Automation** — required for Chrome control:
```
System Settings → Privacy & Security → Automation
→ Terminal → enable Google Chrome + System Events
```

**Notifications** — required for timer alerts:
```
System Settings → Notifications → Script Editor → Allow Notifications ON
```

Trigger permission dialogs manually before first run:
```bash
osascript -e 'tell application "Google Chrome" to activate'
osascript -e 'tell application "System Events" to name of first application process whose frontmost is true'
```

---

## Run Manually

```bash
cd ~/path/to/dsalock
python3 main.py
```

Session runs until timer ends → Chrome exits fullscreen → notification sent → script exits.

---

## Emergency Exit

If you need out mid-session:

```bash
cd ~/path/to/dsalock && python3 emergency.py
```

- Wrong passphrase → does nothing
- Correct passphrase → kills session, exits fullscreen, logs timestamp to `shame.log`

---

## Automate with launchd (run daily at a fixed time)

### Create the plist

Save this to `~/Library/LaunchAgents/com.dsalock.plist` — replace `YOUR_USERNAME` and the path with your actual values:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.dsalock</string>
    <key>ProgramArguments</key>
    <array>
        <string>/opt/homebrew/bin/python3</string>
        <string>/Users/YOUR_USERNAME/path/to/dsalock/main.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/YOUR_USERNAME/path/to/dsalock</string>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>23</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>/Users/YOUR_USERNAME/path/to/dsalock/logs.txt</string>
    <key>StandardErrorPath</key>
    <string>/Users/YOUR_USERNAME/path/to/dsalock/error.txt</string>
    <key>RunAtLoad</key>
    <false/>
</dict>
</plist>
```

### Load it

```bash
launchctl load ~/Library/LaunchAgents/com.dsalock.plist
```

Only needed once. Persists across reboots.

### Verify it's registered

```bash
launchctl list | grep dsalock
```

### Change the time

Use the included helper — no manual plist editing needed:

```bash
chmod +x set_time.sh

./set_time.sh 23      # 11:00 PM
./set_time.sh 9 30    # 9:30 AM
./set_time.sh 20      # 8:00 PM
```

Handles plist update + reload in one command.

### Unload (disable)

```bash
launchctl unload ~/Library/LaunchAgents/com.dsalock.plist
```

### Trigger manually without waiting

```bash
launchctl start com.dsalock
```

---

## Shame Log

Every emergency exit is logged:

```
2025-05-02 23:14:32 — emergency exit triggered
```

Check it anytime:
```bash
cat shame.log
```
