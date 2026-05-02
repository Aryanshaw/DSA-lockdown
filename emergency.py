import hashlib
import subprocess
import datetime
import psutil

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

    # exit chrome fullscreen if in it
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

    print("Unlocked. Hope it was worth it.")

emergency_unlock()
