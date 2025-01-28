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
    if not size_str:
        return None
    size, unit = size_str[:-1], size_str[-1]
    try:
        size = float(size)
    except ValueError:
        return None
    if unit == 'M':
        return size / 1024  # Convert to GB if size is in MB
    elif unit == 'K':
        return size / 1048576  # Convert to GB if size is in KB
    elif unit == 'G':
        return size  # Already in GB
    return None  # If the unit is unexpected, return None

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
subprocess.run(['sudo', 'pacman', '-Scc', '--noconfirm'])

# Clean Yay cache (remove old versions of AUR packages)
print("Cleaning YAY cache...")
subprocess.run(['yay', '-Sc', '--noconfirm'])

# Clean orphaned packages (installed by Pacman)
print("Removing orphaned packages installed by Pacman...")
pacman_orphans = subprocess.check_output(['pacman', '-Qdtq']).decode('utf-8').strip()
if pacman_orphans:
    subprocess.run(['sudo', 'pacman', '-Rns', pacman_orphans, '--noconfirm'], check=False)
else:
    print("No orphaned packages found in Pacman.")

# Clean orphaned AUR packages (installed by Yay)
print("Removing orphaned AUR packages...")
yay_orphans = subprocess.check_output(['yay', '-Qdtq']).decode('utf-8').strip()
if yay_orphans:
    subprocess.run(['yay', '-Rns', yay_orphans, '--noconfirm'], check=False)
else:
    print("No orphaned packages found in Yay.")

# Get disk usage after cleaning
print("Disk usage after cleanup:")
pacman_after = get_disk_usage(pacman_cache_dir)
yay_after = get_disk_usage(yay_cache_dir)

# Print the values for debugging
print(f"pacman_after: {pacman_after}")
print(f"yay_after: {yay_after}")

# Convert and calculate space freed in GB
pacman_space_freed = convert_to_float(pacman_before) - convert_to_float(pacman_after)
yay_space_freed = convert_to_float(yay_before) - convert_to_float(yay_after)

# Print for debugging
print(f"pacman_space_freed: {pacman_space_freed}")
print(f"yay_space_freed: {yay_space_freed}")

# Check if the conversion was successful
if pacman_space_freed is None or yay_space_freed is None:
    print("Error: Could not calculate the space freed due to invalid disk usage data.")
    pacman_space_freed = 0.0
    yay_space_freed = 0.0

# Check if any space was freed
if pacman_space_freed == 0 and yay_space_freed == 0:
    message = "No space was freed during cleanup. All caches were already up to date."
else:
    # Format the message for the notification
    message = f"""
    Disk usage after cleanup:
    Pacman Cache After Cleanup: {pacman_after}
    YAY Cache After Cleanup: {yay_after}
    Space freed in Pacman Cache: {pacman_space_freed:.2f} GB
    Space freed in YAY Cache: {yay_space_freed:.2f} GB
    Total Space Freed: {pacman_space_freed + yay_space_freed:.2f} GB
    Cleanup complete!
    """

# Full report message
full_message = f"""
Disk usage after cleanup:
Pacman Cache After Cleanup: {pacman_after}
YAY Cache After Cleanup: {yay_after}
Space freed in Pacman Cache: {pacman_space_freed:.2f} GB
Space freed in YAY Cache: {yay_space_freed:.2f} GB
Total Space Freed: {pacman_space_freed + yay_space_freed:.2f} GB
Cleanup complete!
"""

# Call send_notification with the full report message
send_notification("Cleanup Report", full_message, icon_path="/home/craftworkson/cleanup_pac/ghosty.ico", pacman_after=pacman_after, yay_after=yay_after, pacman_space_freed=pacman_space_freed, yay_space_freed=yay_space_freed)

print("Cleanup complete!")

