@echo off
:: Block Ads Script for Windows
:: Run as Administrator

set HOSTS_FILE=%SystemRoot%\System32\drivers\etc\hosts
set BACKUP_FILE=%SystemRoot%\System32\drivers\etc\hosts.backup.%DATE:~-4%%DATE:~4,2%%DATE:~7,2%
set SCRIPT_DIR=%~dp0
set HOSTS_SOURCE=%SCRIPT_DIR%..\hosts

if not exist "%HOSTS_SOURCE%" (
    echo Error: hosts file not found at %HOSTS_SOURCE%
    echo Please run aggregator.py first
    pause
    exit /b 1
)

echo Backing up current hosts file...
copy /Y "%HOSTS_FILE%" "%BACKUP_FILE%"

echo Updating hosts file...
type "%HOSTS_SOURCE%" >> "%HOSTS_FILE%"

echo.
echo Hosts file updated successfully!
echo Total entries: findstr /C:"0.0.0.0" "%HOSTS_FILE%" ^| find /C /V ""

echo.
echo Flushing DNS cache...
ipconfig /flushdns >nul

echo Done! You may need to restart your browser.
pause
