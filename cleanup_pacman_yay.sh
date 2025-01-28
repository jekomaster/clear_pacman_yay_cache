#!/bin/bash
# Script to clean Pacman cache and orphaned packages, with space summary

# Define the cache directories
PACMAN_CACHE_DIR="/var/cache/pacman/pkg"
YAY_CACHE_DIR="$HOME/.cache/yay"

# Function to get disk usage before and after cleaning
get_disk_usage() {
    if [ $(id -u) -eq 0 ]; then
        du -sh $1 | awk '{print $1}'
    else
        sudo du -sh $1 | awk '{print $1}'
    fi
}

# Get disk usage before cleaning
echo "Disk usage before cleanup:"
PACMAN_BEFORE=$(get_disk_usage $PACMAN_CACHE_DIR)
YAY_BEFORE=$(get_disk_usage $YAY_CACHE_DIR)

echo "Pacman Cache Before Cleanup: $PACMAN_BEFORE"
echo "YAY Cache Before Cleanup: $YAY_BEFORE"

# Clean Pacman cache (remove old versions, keep only the latest ones)
echo "Cleaning Pacman cache..."
sudo pacman -Sc --noconfirm

# Clean Yay cache (remove old versions of AUR packages)
echo "Cleaning YAY cache..."
yay -Sc --noconfirm

# Clean orphaned packages (installed by Pacman)
echo "Removing orphaned packages installed by Pacman..."
PACMAN_ORPHANS=$(pacman -Qdtq)
if [ -n "$PACMAN_ORPHANS" ]; then
    sudo pacman -Rns $(pacman -Qdtq) --noconfirm
else
    echo "No orphaned packages found in Pacman."
fi

# Clean orphaned AUR packages (installed by Yay)
echo "Removing orphaned AUR packages..."
YAY_ORPHANS=$(yay -Qdtq)
if [ -n "$YAY_ORPHANS" ]; then
    yay -Rns $(yay -Qdtq) --noconfirm
else
    echo "No orphaned packages found in Yay."
fi

# Get disk usage after cleaning
echo "Disk usage after cleanup:"
PACMAN_AFTER=$(get_disk_usage $PACMAN_CACHE_DIR)
YAY_AFTER=$(get_disk_usage $YAY_CACHE_DIR)

echo "Pacman Cache After Cleanup: $PACMAN_AFTER"
echo "YAY Cache After Cleanup: $YAY_AFTER"

# Calculate space freed
PACMAN_SPACE_FREED=$(echo $PACMAN_BEFORE $PACMAN_AFTER | awk '{print $1-$2}')
YAY_SPACE_FREED=$(echo $YAY_BEFORE $YAY_AFTER | awk '{print $1-$2}')

# Display space freed
echo "Space freed in Pacman Cache: $PACMAN_SPACE_FREED"
echo "Space freed in YAY Cache: $YAY_SPACE_FREED"

echo "Cleanup complete!"
