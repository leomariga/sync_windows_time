# Windows Time Sync Tool 🕒

A reliable Python tool that synchronizes your Windows system clock with precise NTP servers. Say goodbye to Windows' built-in sync failures!

## Why This Exists

Let's be honest - Windows time synchronization can be frustratingly unreliable. After being consistently annoyed by my system clock drifting and the built-in sync failing repeatedly, I decided to take matters into my own hands. This simple tool was born from that frustration.

## Features

- Connects to multiple reliable NTP servers (time.google.com, time.windows.com, time.nist.gov)
- Falls back to alternative servers if one fails
- Shows time difference between your system and the NTP server
- Automatically updates your system time with administrator privileges
- Easy to run with the included batch file

## Requirements

- Windows OS
- Python 3.x
- Administrator privileges (for setting the system time)

## Usage

### One-time Sync

1. Right-click on `run_sync_admin.bat` and select "Run as administrator"
2. The script will automatically:
   - Connect to available NTP servers
   - Display the time difference
   - Update your system time

That's it! Your system clock is now accurate.

### Auto-run at Windows Startup

To automatically sync your clock every time Windows starts:

1. Press `Win + R` to open the Run dialog
2. Type `shell:startup` and press Enter
3. Create a shortcut to `run_sync_admin.bat` in this folder
   - Right-click in the Startup folder → New → Shortcut
   - Browse to the location of `run_sync_admin.bat` and select it
   - Click Next and Finish

Alternatively, you can set up a scheduled task:

1. Open Task Scheduler (search for it in the Start menu)
2. Create a Basic Task
   - Set trigger to "When I log on"
   - Action: Start a program
   - Program/script: Select the full path to `run_sync_admin.bat`
   - Select "Run with highest privileges"

## How It Works

The script connects to NTP servers using the UDP protocol, retrieves the current accurate time, and uses Windows commands to update your system clock. All operations require administrator privileges since changing system time is a protected operation.

## License

Feel free to use, modify, and distribute this code however you like!

## Contributions

Found a bug or want to improve something? Pull requests are welcome! 
