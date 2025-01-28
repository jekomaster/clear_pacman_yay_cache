import subprocess

def send_notification(title, message, icon_path=None, pacman_after=None, yay_after=None, pacman_space_freed=None, yay_space_freed=None):
    # Check if the space freed values are None and set them to 0.0 if so
    if pacman_space_freed is None:
        pacman_space_freed = 0.0
    if yay_space_freed is None:
        yay_space_freed = 0.0

    message = f"Disk usage after cleanup:\nPacman Cache After Cleanup: {pacman_after}\nYAY Cache After Cleanup: {yay_after}\nTotal Space Freed: {pacman_space_freed + yay_space_freed:.2f} GB"

    command = ["dunstify", "-u", "normal", title, message]
    
    if icon_path:
        command.extend(["-i", icon_path])

    subprocess.run(command)
