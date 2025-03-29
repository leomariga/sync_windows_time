import socket
import struct
import subprocess
import datetime
import sys
import time
import locale
import os

def get_ntp_time(server):
    """Get time from the specified NTP server using raw sockets."""
    # NTP server port
    port = 123
    # NTP request packet format (according to the protocol)
    # https://tools.ietf.org/html/rfc5905
    # First byte: Leap (2 bits), Version (3 bits), Mode (3 bits)
    # 00 011 011 = 0x1B (no leap warning, version 3, client mode)
    ntp_packet = bytearray(48)
    ntp_packet[0] = 0x1B  # Set version and mode
    
    try:
        # Create a UDP socket and set timeout
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client.settimeout(5)
        
        # Get IP address for the NTP server
        addr = socket.gethostbyname(server)
        
        # Send the NTP packet
        client.sendto(ntp_packet, (addr, port))
        
        # Receive response
        msg, _ = client.recvfrom(1024)
        
        # Close the socket
        client.close()
        
        # Extract timestamp from the response
        # The transmit timestamp is at offset 40
        # Format: 64-bit timestamp (32 bits for seconds, 32 bits for fraction)
        transmit_time = struct.unpack('!12I', msg)[10]
        
        # NTP timestamps start from 1900-01-01, while Unix timestamps start from 1970-01-01
        # The difference is 2208988800 seconds
        ntp_epoch_offset = 2208988800
        
        # Convert NTP timestamp to Unix timestamp
        tx_time = transmit_time - ntp_epoch_offset
        
        return tx_time
    except Exception as e:
        print(f"Error connecting to {server}: {e}")
        return None

def get_system_date_format():
    """Detect the system's date format."""
    try:
        # Try to get date format using PowerShell
        result = subprocess.run(
            ['powershell', '-command', 
             "(Get-Culture).DateTimeFormat.ShortDatePattern"],
            capture_output=True, text=True, check=True
        )
        date_format = result.stdout.strip()
        
        # Convert .NET format to strftime format
        # Most common patterns:
        # MM/dd/yyyy -> %m/%d/%y (US)
        # dd/MM/yyyy -> %d/%m/%y (UK/Europe)
        # yyyy/MM/dd -> %y/%m/%d (East Asia)
        
        # Simple conversion for the most common cases
        date_format = date_format.replace('yyyy', '%Y')
        date_format = date_format.replace('yy', '%y')
        date_format = date_format.replace('MM', '%m')
        date_format = date_format.replace('M', '%m')
        date_format = date_format.replace('dd', '%d')
        date_format = date_format.replace('d', '%d')
        
        return date_format
    except Exception:
        # Fallback to a simple check based on locale
        try:
            # Get the locale's date representation
            locale.setlocale(locale.LC_TIME, '')
            date_format = locale.nl_langinfo(locale.D_FMT)
            return date_format
        except Exception:
            # Final fallback - use a heuristic based on country code
            try:
                country = os.environ.get('COUNTRY', '')
                if country in ['US', 'PH', 'CA']:
                    return '%m-%d-%y'  # MM-DD-YY (US style)
                else:
                    return '%d-%m-%y'  # DD-MM-YY (most other countries)
            except:
                # Default to DD-MM-YY as it's the most widely used
                return '%d-%m-%y'

def set_windows_time(timestamp):
    """Set the Windows system time using the timestamp."""
    # Convert Unix timestamp to datetime
    dt = datetime.datetime.fromtimestamp(timestamp)
    
    try:
        # Use Windows time command to set the system time
        subprocess.run(["cmd", "/c", f"time {dt.strftime('%H:%M:%S')}"], check=True)
        
        # For Windows date command, always use dd-mm-yy format with dashes
        # This is what the Windows cmd expects when prompting "Digite a nova data: (dd-mm-aa)"
        cmd_date_format = dt.strftime('%d-%m-%y')
        
        print(f"Using Windows date format: {cmd_date_format}")
        subprocess.run(["cmd", "/c", f"date {cmd_date_format}"], check=True)
        print(f"System time successfully updated to: {dt}")
        return True
    except subprocess.SubprocessError as e:
        print(f"Error setting system time: {e}")
        return False

def main():
    # List of available NTP servers
    servers = [
        "time.google.com",
        "time.windows.com",
        "time.nist.gov"
    ]
    
    print("Windows Time Synchronization Tool")
    print("=================================")
    
    # Try each server in sequence until one works
    ntp_time = None
    successful_server = None
    
    for server in servers:
        print(f"Connecting to {server}...")
        ntp_time = get_ntp_time(server)
        
        if ntp_time is not None:
            successful_server = server
            print(f"Successfully connected to {server}")
            break
        
        print(f"Failed to connect to {server}, trying next server...\n")
    
    # If all servers failed
    if ntp_time is None:
        print("Failed to connect to any NTP server. Please check your internet connection and try again later.")
        return
    
    # Display current and new time
    current_time = datetime.datetime.now()
    new_time = datetime.datetime.fromtimestamp(ntp_time)
    
    print(f"\nCurrent system time: {current_time}")
    print(f"NTP server time:     {new_time} (from {successful_server})")
    print(f"Time difference:     {abs((new_time - current_time).total_seconds())} seconds")
    
    # Automatically proceed with the update without asking
    print("\nAutomatically updating system time...")
    print("Note: This operation requires administrator privileges.")
    
    # Set the system time
    if set_windows_time(ntp_time):
        print("Time synchronization completed successfully.")
    else:
        print("Time synchronization failed. Please run as administrator and try again.")

if __name__ == "__main__":
    main()
