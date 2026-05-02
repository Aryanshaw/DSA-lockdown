import time
from notifier import notify

def timer(duration_minutes, stop_event):
    """
    start timer countdown. notify at 30 min and 10 min remaining.
    """
    total_seconds = duration_minutes * 60
    notified_30 = False
    notified_10 = False

    for remaining in range(total_seconds, 0, -1):
        if stop_event.is_set():
            return

        minutes_left = remaining // 60

        if minutes_left == 30 and not notified_30:
            notify("DSA Lock", "30 minutes remaining.")
            notified_30 = True

        if minutes_left == 10 and not notified_10:
            notify("DSA Lock", "10 minutes remaining.")
            notified_10 = True

        time.sleep(1)

    stop_event.set()

    