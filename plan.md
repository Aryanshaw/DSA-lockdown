## Section 1 — Script Implementation

#### 1.1 Project Structure
```
dsalock/
  main.py          ← entry point
  config.json      ← settings
  enforcer.py      ← tab + app monitoring loop
  timer.py         ← session countdown
  notifier.py      ← mac notifications
  unlock.py        ← normal unlock after session ends
  emergency.py     ← emergency exit, run manually from terminal
  shame.log        ← auto-generated, logs every emergency exit
  secret.hash      ← hashed passphrase for emergency exit
```

---

#### 1.2 Startup Flow (`main.py`)

same as before:

```
1. read config.json
2. open Chrome fullscreen, navigate to leetcode.com
3. start enforcer loop (background thread)
4. start timer countdown (background thread)
5. block main thread until timer signals done
6. call unlock()
```

---

#### 1.3 Enforcer Loop (`enforcer.py`)

same algorithm as before, no changes:

```
every 2 seconds:
  → get active Chrome tab URL
  → if not in allowed_domains → redirect to leetcode
  → get frontmost app
  → if not in allowed_apps → bring Chrome to front
```

---

#### 1.4 Timer (`timer.py`)

same as before. notifications at 30 min and 10 min remaining. sets `stop_event` when done.

---

#### 1.5 Normal Unlock (`unlock.py`)

called automatically when timer finishes:

```
1. stop enforcer loop via stop_event
2. exit Chrome fullscreen
3. send notification "Session complete. You're free."
4. exit script
```

---

#### 1.6 Emergency Exit (`emergency.py`) ← updated

this is a **completely separate script** you run manually from terminal when you need out fast:

```
algorithm:
  1. prompt for passphrase
  2. hash the input and compare against secret.hash
  3. if wrong → print "Wrong passphrase" and exit (script does nothing)
  4. if correct:
       → write timestamp + reason to shame.log
       → kill the main dsalock process (find by name using psutil)
       → exit Chrome fullscreen
       → done
```

```python
# emergency.py
import hashlib, subprocess, datetime, psutil

def emergency_unlock():
    stored_hash = open("secret.hash").read().strip()
    attempt = input("Passphrase: ")
    attempt_hash = hashlib.sha256(attempt.encode()).hexdigest()

    if attempt_hash != stored_hash:
        print("Wrong. Get back to work.")
        return

    # log the shame
    with open("shame.log", "a") as f:
        f.write(f"{datetime.datetime.now()} — emergency exit triggered\n")

    # kill main.py process
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        if 'main.py' in ' '.join(proc.info['cmdline'] or []):
            proc.kill()
            break

    # exit chrome fullscreen
    subprocess.run(['osascript', '-e', '''
        tell application "Google Chrome"
            tell application "System Events"
                key code 53
            end tell
        end tell
    '''])

    print("Unlocked. Hope it was worth it.")

emergency_unlock()
```

to use it during an emergency:
```bash
cd ~/dsalock && python3 emergency.py
# type passphrase → instant exit
```

takes about 10 seconds total. fast enough for real emergencies.

---

#### 1.7 Config (`config.json`)

simplified, no off days:

```json
{
  "duration_minutes": 120,
  "start_hour": 9,
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

---

#### 1.8 Passphrase Setup (one time)

run this once when setting up:

```bash
python3 -c "
import hashlib
p = input('Set emergency passphrase: ')
h = hashlib.sha256(p.encode()).hexdigest()
open('secret.hash', 'w').write(h)
print('Saved.')
"
```

pick something you'll remember easily but wouldn't type by accident. something like a phrase, not a single word.

---

### Section 2 — macOS Permission Layer

no changes here. same as before:

**Accessibility:**
```
System Settings → Privacy & Security → Accessibility → add Terminal → ON
```

**Automation:**
```
System Settings → Privacy & Security → Automation
→ Terminal → enable Google Chrome + System Events
```

**Trigger permissions manually before first run:**
```bash
osascript -e 'tell application "Google Chrome" to activate'
osascript -e 'tell application "System Events" to name of first application process whose frontmost is true'
```

---

### Section 3 — launchd Setup

plist file, fires at 9am every day:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.dsalock</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/YOU/dsalock/main.py</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>9</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>/Users/YOU/dsalock/logs.txt</string>
    <key>StandardErrorPath</key>
    <string>/Users/YOU/dsalock/error.txt</string>
</dict>
</plist>
```

load once:
```bash
launchctl load ~/Library/LaunchAgents/com.dsalock.plist
```

to update the time later just edit the plist and:
```bash
launchctl unload ~/Library/LaunchAgents/com.dsalock.plist
launchctl load ~/Library/LaunchAgents/com.dsalock.plist
```

---

### Section 4 — Verification Steps

same as before, in order:

**4.1 — test AppleScript standalone**
```bash
osascript -e 'tell application "Google Chrome" to open location "https://leetcode.com"'
osascript -e 'tell application "Google Chrome" to get URL of active tab of front window'
osascript -e 'tell application "System Events" to name of first application process whose frontmost is true'
osascript -e 'tell application "Google Chrome" to activate'
```
all four must work cleanly.

**4.2 — test enforcer in isolation**
```python
# run test_enforcer.py
# open youtube, watch if URL gets detected
# switch to finder, watch if app switch gets detected
```

**4.3 — test redirect**
```python
from enforcer import redirect_active_tab
redirect_active_tab("https://leetcode.com")
# run while youtube is open, should snap back
```

**4.4 — full integration test at 1 minute**
```
set duration_minutes to 1
run python3 main.py
checklist:
  → chrome opened and went to leetcode ✓
  → fullscreen ✓
  → youtube tab → redirected within 2 sec ✓
  → switched to finder → chrome came back ✓
  → after 60 sec → notification + script exited ✓
```

**4.5 — test emergency exit**
```bash
# while main.py is running
cd ~/dsalock && python3 emergency.py
# type wrong passphrase → should do nothing
# type correct passphrase → should kill session instantly
# check shame.log → entry should be there
```

**4.6 — test launchd**
```bash
# manually trigger it without waiting for 9am
launchctl start com.dsalock
# verify main.py is running
ps aux | grep main.py
# check logs.txt for output
```

---
