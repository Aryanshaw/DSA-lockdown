import subprocess
import time

"""
every 2 seconds:
  → get all Chrome tabs
  → close any tab whose URL is not in allowed_domains
  → if no tabs left → open leetcode
  → get frontmost app
  → if not in allowed_apps → bring Chrome to front
"""

def get_all_chrome_tabs():
    """
    Returns list of (index, url) for all tabs in front window. Index is 1-based.
    """
    result = subprocess.run([
        "osascript", "-e",
        '''tell application "Google Chrome"
            set output to ""
            set tabCount to count of tabs of front window
            repeat with i from 1 to tabCount
                set tabURL to URL of tab i of front window
                set output to output & i & "|" & tabURL & "\n"
            end repeat
            return output
        end tell'''
    ], capture_output=True, text=True)

    tabs = []
    for line in result.stdout.strip().split("\n"):
        if "|" in line:
            parts = line.split("|", 1)
            try:
                tabs.append((int(parts[0].strip()), parts[1].strip()))
            except ValueError:
                pass
    return tabs

def close_tab_at_index(index):
    subprocess.run([
        "osascript", "-e",
        f'tell application "Google Chrome" to close tab {index} of front window'
    ])

def open_leetcode():
    subprocess.run([
        "osascript", "-e",
        'tell application "Google Chrome" to open location "https://leetcode.com/problem-list/plakya4j/"'
    ])

def get_frontmost_app():
    result = subprocess.run([
        "osascript", "-e",
        'tell application "System Events" to name of first application process whose frontmost is true'
    ], capture_output=True, text=True)
    return result.stdout.strip()

def bring_chrome_to_front():
    subprocess.run([
        "osascript", "-e",
        'tell application "Google Chrome" to activate'
    ])


def enforcer(config, stop_event):
    allowed_domains = config["allowed_domains"]
    allowed_apps = config["allowed_apps"]

    while not stop_event.is_set():
        time.sleep(2)

        # get all tabs, close disallowed ones
        tabs = get_all_chrome_tabs()
        disallowed = [
            (i, url) for i, url in tabs
            if not any(domain in url for domain in allowed_domains)
        ]

        # close in reverse order so indices don't shift
        for index, url in sorted(disallowed, reverse=True):
            print(f"closing disallowed tab [{index}]: {url}")
            close_tab_at_index(index)

        # if all tabs were disallowed and closed, reopen leetcode
        remaining = len(tabs) - len(disallowed)
        if remaining == 0:
            open_leetcode()

        # check frontmost app
        app = get_frontmost_app()
        print(f"{app} is frontmost")
        if not any(a in app for a in allowed_apps):
            bring_chrome_to_front()
            time.sleep(1)
