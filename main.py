import json
import threading
import subprocess
import time

from enforcer import enforcer, open_leetcode
from timer import timer
from unlock import unlock
from keyblock import key_blocker_loop

# activate Chrome
def activate_chrome():
    subprocess.run([
        "osascript", "-e",
        'tell application "Google Chrome" to activate'
    ])

def main():
    """
    1. read config.json
    2. open Chrome fullscreen, navigate to leetcode.com
    3. start enforcer loop (background thread)
    4. start timer countdown (background thread)
    5. block main thread until timer signals done
    6. call unlock()
    """
    # read config.json
    with open("config.json", "r") as f:
        config = json.load(f)

    stop_event = threading.Event()
    
    # open Chrome fullscreen, navigate to leetcode.com
    open_leetcode()
    activate_chrome()
    time.sleep(1)
    # only enter fullscreen if not already in it (check menu item label)
    subprocess.run([
        "osascript", "-e",
        '''tell application "System Events"
            tell process "Google Chrome"
                set viewMenu to menu "View" of menu bar 1
                if exists menu item "Enter Full Screen" of viewMenu then
                    click menu item "Enter Full Screen" of viewMenu
                end if
            end tell
        end tell'''
    ])
    time.sleep(1)
    # start key blocker (background thread)
    keyblock_thread = threading.Thread(target=key_blocker_loop, args=(stop_event,), daemon=True)
    keyblock_thread.start()
    # start enforcer loop (background thread)
    enforcer_thread = threading.Thread(target=enforcer , args=(config, stop_event,))
    enforcer_thread.start()
    # start timer countdown (background thread)
    timer_thread = threading.Thread(target=timer, args=(config["duration_minutes"], stop_event,))
    timer_thread.start()
    # block main thread until timer signals done
    timer_thread.join()
    # call unlock()
    unlock()

if __name__ == "__main__":
    main()