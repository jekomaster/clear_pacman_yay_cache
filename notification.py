# notification.py
import subprocess

def send_notification(title, message, icon_path=None):
    command = ["dunstify", "-u", "normal", title, message]
    if icon_path:
        command.extend(["-i", icon_path])
    subprocess.run(command)
