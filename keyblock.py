import Quartz
from notifier import notify

# macOS virtual keycodes
KEY_Q = 12
KEY_W = 13

def key_blocker_loop(stop_event):
    """
    Intercepts Cmd+Q and Cmd+W system-wide while session is active.
    Suppresses the event and sends a shame notification instead.
    Requires Accessibility permission for the terminal running this script.
    """
    def callback(proxy, event_type, event, refcon):
        if event_type == Quartz.kCGEventKeyDown:
            flags = Quartz.CGEventGetFlags(event)
            keycode = Quartz.CGEventGetIntegerValueField(event, Quartz.kCGKeyboardEventKeycode)
            cmd_down = bool(flags & Quartz.kCGEventFlagMaskCommand)

            if cmd_down and keycode in (KEY_Q, KEY_W):
                notify("DSA Lock", "Study u asshole, dont you want to go to Google?")
                return None  # suppress the event

        return event

    tap = Quartz.CGEventTapCreate(
        Quartz.kCGSessionEventTap,
        Quartz.kCGHeadInsertEventTap,
        Quartz.kCGEventTapOptionDefault,
        Quartz.CGEventMaskBit(Quartz.kCGEventKeyDown),
        callback,
        None
    )

    if tap is None:
        print("[keyblock] Failed to create event tap. Go to System Settings → Privacy & Security → Accessibility and enable Terminal.")
        return

    source = Quartz.CFMachPortCreateRunLoopSource(None, tap, 0)
    Quartz.CFRunLoopAddSource(Quartz.CFRunLoopGetCurrent(), source, Quartz.kCFRunLoopDefaultMode)
    Quartz.CGEventTapEnable(tap, True)

    # run in 1-second ticks so we can check stop_event cleanly
    while not stop_event.is_set():
        Quartz.CFRunLoopRunInMode(Quartz.kCFRunLoopDefaultMode, 1.0, False)

    Quartz.CGEventTapEnable(tap, False)
