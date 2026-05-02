import subprocess
from notifier import notify

def unlock():
    """
    exit Chrome fullscreen, send completion notification, exit script.
    """
    # only exit fullscreen if currently in it
    subprocess.run([
        "osascript", "-e",
        '''tell application "System Events"
            tell process "Google Chrome"
                set viewMenu to menu "View" of menu bar 1
                if exists menu item "Exit Full Screen" of viewMenu then
                    click menu item "Exit Full Screen" of viewMenu
                end if
            end tell
        end tell'''
    ])

    notify("DSA Lock", "Session complete. You're free.")
