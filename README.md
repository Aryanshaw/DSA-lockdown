# DSA Lockdown

A macOS lockdown tool to force-focus your study sessions on LeetCode. Blocks distraction and logs emergency exits.

## What It Does

1. Opens Chrome in fullscreen at leetcode.com
2. Every 2 seconds:
   - Checks active Chrome tab → redirects if not on allowed domains
   - Checks frontmost app → brings Chrome back if you switch away
3. Blocks Cmd+Q and Cmd+W (so you can't quit or close tabs)
4. Counts down (default 120 min) → notifies at 30m and 10m remaining
5. Auto-unlocks when done

## Files

```
main.py          - entry point
config.json     - settings
enforcer.py     - tab + app monitoring
timer.py        - session countdown
unlock.py       - auto-unlock on completion
notifier.py     - macOS notifications
keyblock.py     - blocks Cmd+Q / Cmd+W
emergency.py   - manual unlock with passphrase
secret.hash    - hashed passphrase
shame.log      - logs emergency exits
```

## Setup

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install psutil

# 3. Set passphrase (one time)
python3 -c "
import hashlib
p = input('Passphrase: ')
open('secret.hash','w').write(hashlib.sha256(p.encode()).hexdigest())
"

# 4. Edit config.json (duration, allowed domains, etc.)
```

## Usage

```bash
source venv/bin/activate
python3 main.py
```

Session runs in foreground. When timer ends → Chrome exits fullscreen, notification sent, script exits.

## Emergency Unlock

If you need out during a session:

```bash
python3 emergency.py
# enter passphrase → kills session, logs to shame.log
```

Wrong passphrase does nothing.

## Required Permissions

**Accessibility** (required for keyblock.py):
```
System Settings → Privacy & Security → Accessibility
→ Enable Terminal (or your terminal app)
```

**Automation** (required for Chrome control):
```
System Settings → Privacy & Security → Automation
→ Enable Terminal → Google Chrome
→ Enable Terminal → System Events
```

**Grant permissions manually** before first run:
```bash
osascript -e 'tell application "Google Chrome" to activate'
osascript -e 'tell application "System Events" to name of first application process whose frontmost is true'
```

## Config Options (config.json)

| Key | Description |
|-----|-------------|
| `duration_minutes` | Session length (default 120) |
| `start_hour` | Not used in standalone mode |
| `allowed_domains` | Whitelisted domains (e.g., leetcode.com) |
| `allowed_apps` | Whitelisted apps (e.g., Google Chrome) |
| `check_interval_seconds` | How often to check (default 2) |
