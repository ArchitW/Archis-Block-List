# Android Setup

Blocking ads on Android requires either:
1. Root access
2. Using a DNS-based ad blocker app

## Option 1: Root Users

### Using Hosts File

1. Download the `hosts` file from the repository
2. Transfer it to your Android device
3. Use a file manager with root access (like ES File Explorer or Solid Explorer)
4. Replace `/system/etc/hosts` with the downloaded file
5. Restart your device

### Using AdAway (Recommended)

1. Install [AdAway](https://f-droid.org/packages/org.adaway/) from F-Droid
2. Open the app and grant root access
3. Go to Settings > Backup and restore
4. Choose "Download hosts file"
5. Or add custom hosts sources in Settings > Lists
6. Apply the hosts file

## Option 2: Non-Root Users

### DNS-based Blockers

1. **AdGuard DNS**
   - Go to Settings > Network & Internet > Private DNS
   - Enter: `dns.adguard-dns.com`

2. **NextDNS**
   - Go to Settings > Network & Internet > Private DNS
   - Enter your NextDNS hostname

3. **Blokada** (Free, open-source)
   - Download from [Blokada.org](https://blokada.org/)
   - Works without root on Android 5.0+

### Private DNS

Many ad blockers offer DNS-over-TLS or DNS-over-HTTPS:

| Service | Private DNS Hostname |
|---------|---------------------|
| AdGuard | dns.adguard-dns.com |
| NextDNS | your-id.dns.nextdns.io |
| Control D | dns.filter-dns.com |

## Troubleshooting

- After updating hosts, restart your device
- Clear browser cache if ads still appear
- Some apps may have internal DNS that bypasses system hosts
