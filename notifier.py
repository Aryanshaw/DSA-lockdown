import subprocess

def notify(title, message):
    subprocess.run([
        "osascript", "-e",
        f'display notification "{message}" with title "{title}" sound name "Ping"'
    ])
