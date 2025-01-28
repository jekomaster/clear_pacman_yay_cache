import os
import subprocess
from notification import send_notification  # Import the function from notification.py

# Function to get disk usage before and after cleaning
def get_disk_usage(path):
    if os.geteuid() == 0:  # Check if running as root
        return subprocess.check_output(['du', '-sh', path]).split()[0].decode('utf-8')
    else:
        return subprocess.check_output(['sudo', 'du', '-sh', path]).split()[0].decode('utf-8')

# Function to convert human-readable size to float (for space freed calculation)
def convert_to_float(size_str):
    size, unit = size_str[:-1], size_str[-1]
    size = float(size)
    if unit == 'M':
        return size / 1024  # Convert to GB if size is in MB
    elif unit == 'K':
        return size / 1048576  # Convert to GB if size is in KB
    return size  # Assume it's already in GB if it's in 'G'

# Define cache directories
pacman_cache_dir = '/var/cache/pacman/pkg'
yay_cache_dir = os.path.expanduser('~/.cache/yay')

# Get disk usage before cleaning
print("Disk usage before cleanup:")
pacman_before = get_disk_usage(pacman_cache_dir)
yay_before = get_disk_usage(yay_cache_dir)

print(f"Pacman Cache Before Cleanup: {pacman_before}")
print(f"YAY Cache Before Cleanup: {yay_before}")

# Clean Pacman cache (remove old versions, keep only the latest ones)
print("Cleaning Pacman cache...")
subprocess.run(['sudo', 'pacman', '-Sc', '--noconfirm'])

# Clean Yay cache (remove old versions of AUR packages)
print("Cleaning YAY cache...")
subprocess.run(['yay', '-Sc', '--noconfirm'])

# Clean orphaned packages (installed by Pacman)
print("Removing orphaned packages installed by Pacman...")
pacman_orphans = subprocess.check_output(['pacman', '-Qdtq']).decode('utf-8').strip()
if pacman_orphans:
    subprocess.run(['sudo', 'pacman', '-Rns', pacman_orphans, '--noconfirm'])
else:
    print("No orphaned packages found in Pacman.")

# Clean orphaned AUR packages (installed by Yay)
print("Removing orphaned AUR packages...")
yay_orphans = subprocess.check_output(['yay', '-Qdtq']).decode('utf-8').strip()
if yay_orphans:
    subprocess.run(['yay', '-Rns', yay_orphans, '--noconfirm'])
else:
    print("No orphaned packages found in Yay.")

# Get disk usage after cleaning
print("Disk usage after cleanup:")
pacman_after = get_disk_usage(pacman_cache_dir)
yay_after = get_disk_usage(yay_cache_dir)

print(f"Pacman Cache After Cleanup: {pacman_after}")
print(f"YAY Cache After Cleanup: {yay_after}")

# Convert and calculate space freed in GB
pacman_space_freed = convert_to_float(pacman_before) - convert_to_float(pacman_after)
yay_space_freed = convert_to_float(yay_before) - convert_to_float(yay_after)

# Display space freed
print(f"Space freed in Pacman Cache: {pacman_space_freed:.2f} GB")
print(f"Space freed in YAY Cache: {yay_space_freed:.2f} GB")

# Format the message for the notification
message = f"""
Disk usage after cleanup:
Pacman Cache After Cleanup: {pacman_after}
YAY Cache After Cleanup: {yay_after}
Space freed in Pacman Cache: {pacman_space_freed:.2f} GB
Space freed in YAY Cache: {yay_space_freed:.2f} GB
Cleanup complete!
"""

# Send a notification about the cleanup with the formatted message
send_notification("Cleanup Complete", message, "/home/craftworkson/cleanup_pac&yay_cache/ghosty.ico")

print("Cleanup complete!")
