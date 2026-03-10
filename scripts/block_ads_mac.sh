#!/bin/bash

# Block Ads Script for macOS
# This script replaces the system hosts file with the aggregated hosts file

HOSTS_FILE="/etc/hosts"
BACKUP_FILE="/etc/hosts.backup.$(date +%Y%m%d%H%M%S)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOSTS_SOURCE="${SCRIPT_DIR}/../hosts"

if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (sudo)"
    exit 1
fi

if [ ! -f "$HOSTS_SOURCE" ]; then
    echo "Error: hosts file not found at $HOSTS_SOURCE"
    echo "Please run aggregator.py first"
    exit 1
fi

echo "Backing up current hosts file to $BACKUP_FILE"
cp "$HOSTS_FILE" "$BACKUP_FILE"

echo "Updating hosts file..."
cat "$HOSTS_SOURCE" >> "$HOSTS_FILE"

echo "Hosts file updated successfully!"
echo "Total entries: $(grep -c '^0.0.0.0' "$HOSTS_FILE")"
echo ""
echo "Flushing DNS cache..."
# For macOS Monterey and later
sudo dscacheutil -flushcache 2>/dev/null
sudo killall -HUP mDNSResponder 2>/dev/null

echo "Done! You may need to restart your browser."
