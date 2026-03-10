# AdBlocker using Hosts File

![icon](icon.png)

## Overview

This project provides a comprehensive solution to block advertisements across various platforms (Mac, Windows, Linux, and Android) by leveraging the hosts file. The hosts file is used to map hostnames to IP addresses and can be manipulated to redirect ad-serving domains to a non-existent IP, effectively blocking ads.

## Features

- Aggregates hosts from 204+ authoritative sources
- Blocks ads, trackers, malware, phishing, and adult content
- Regular expression and wildcard support
- Automatic deduplication
- Platform-specific deployment scripts
- Supports multiple blocklist categories
- Auto-run check (24-hour throttle)
- Resume capability for interrupted downloads

## Blocklist Categories

| Category | Description |
|----------|-------------|
| Ads & Trackers | Main advertising domains |
| Malware | Known malicious websites |
| Phishing | Fraud and scam sites |
| Social Media | Optional social network blocking |
| Adult | Sexual content filtering |
| Gambling | Casino and betting sites |
| Piracy | Torrent and streaming sites |
| Telemetry | Device tracking domains |

## Supported Platforms

- macOS
- Windows
- Linux
- Android

## Quick Start

### 1. Generate Hosts File

```bash
# Install dependencies
pip install requests tldextract

# Run the aggregator
python3 aggregator.py
```

This will download and merge all blocklists into a single `hosts` file.

### 2. Install on Your Device

Navigate to the appropriate directory for your platform:

| Platform | Script | Command |
|----------|--------|---------|
| Linux | `scripts/block_ads_linux.sh` | `sudo ./block_ads_linux.sh` |
| macOS | `scripts/block_ads_mac.sh` | `sudo ./block_ads_mac.sh` |
| Windows | `scripts/block_ads_windows.bat` | Run as Administrator |
| Android | `android-scripts/README.md` | See instructions |

### 3. Apply Changes

After running the script, restart your device or networking service:

**Linux:**
```bash
sudo systemctl restart systemd-resolved
```

**macOS:**
```bash
sudo dscacheutil -flushcache
sudo killall -HUP mDNSResponder
```

**Windows:**
```cmd
ipconfig /flushdns
```

## Usage

### Pre-requisites

- Python 3.7+
- `requests` library
- `tldextract` library

### Running the Aggregator

The aggregator will:
1. Read source URLs from `sources.txt`
2. Download each blocklist in parallel
3. Parse and extract domains
4. Remove duplicates
5. Generate a unified `hosts` file

```bash
python3 aggregator.py
```

### Resuming Downloads

The aggregator saves progress to `cache/state.json`. If interrupted, simply run again to resume from where it left off.

### Auto-Run Check

The aggregator checks when it was last run:
- If more than 24 hours since last run: automatically processes all URLs
- If less than 24 hours: prompts you to confirm before running again

## Configuration

### Adding Custom Sources

Edit `sources.txt` and add your blocklist URLs (one per line, lines starting with `#` are comments):

```
# My custom blocklist
https://example.com/my-blocklist.txt
```

### Supported Source Formats

- Standard hosts file format (`0.0.0.0 domain.com`)
- AdBlock-style domain lists
- Plain domain lists (one per line)

## Statistics

| Metric | Value |
|--------|-------|
| Sources | 204 blocklists |
| Unique Domains | 10,036,528 |
| Output File Size | 270 MB |
| Last Updated | March 10, 2026 |

## Troubleshooting

### Ads Still Showing

1. Clear your browser cache
2. Flush DNS cache (commands above)
3. Restart your device
4. Check if your browser has built-in ad blocking

### Script Errors

- Ensure you run with appropriate permissions (sudo for system hosts)
- Verify the `hosts` file exists before running deployment scripts
- Check that Python dependencies are installed

## Contribution

Contributions are welcome! If you have improvements or additional scripts for other platforms, feel free to fork this repository and submit a pull request.

## Disclaimer

Blocking ads using the hosts file can impact the functionality of certain websites and services. Use this script responsibly and be aware of potential side effects. The maintainers of this repository are not responsible for any adverse effects on your system.

This project is provided for educational and informational purposes only. Use it at your own risk.

## License

This project is licensed under the [MIT License](LICENSE).
