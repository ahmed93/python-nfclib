#!/usr/bin/env python3
"""
Interactive NFC Terminal Application

This script provides a command-line interface for interacting with NFC tags
using the NFC Library.
"""
import logging
import sys
import time
import argparse
from nfc_library import create_nfc_library

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

# ANSI colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header():
    """Print a nice header for the application."""
    header = f"""
{Colors.BLUE}{Colors.BOLD}╔════════════════════════════════════════╗
║             NFC TERMINAL             ║
╚════════════════════════════════════════╝{Colors.END}
    """
    print(header)

def print_status(message, status_type="info"):
    """Print a formatted status message."""
    if status_type == "success":
        print(f"{Colors.GREEN}✓ {message}{Colors.END}")
    elif status_type == "error":
        print(f"{Colors.RED}✗ {message}{Colors.END}")
    elif status_type == "warning":
        print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")
    else:
        print(f"{Colors.BLUE}ℹ {message}{Colors.END}")

def select_device(nfc_lib):
    """Allow user to select an NFC device if multiple are available."""
    devices = nfc_lib.devices()
    
    if not devices:
        print_status("No NFC devices found. Please connect an NFC reader.", "error")
        return None
    
    if len(devices) == 1:
        print_status(f"Using device: {devices[0]}")
        return devices[0]
    
    print(f"{Colors.BLUE}Available devices:{Colors.END}")
    for i, device_id in enumerate(devices):
        print(f"{i+1}. {device_id}")
    
    while True:
        try:
            choice = int(input("Select device (number): "))
            if 1 <= choice <= len(devices):
                return devices[choice-1]
            else:
                print_status("Invalid selection. Please try again.", "warning")
        except ValueError:
            print_status("Please enter a number.", "warning")

def write_text(nfc_lib, device_id):
    """Write a text message to an NFC tag."""
    text = input("Enter the text message to write: ")
    
    if not text:
        print_status("Empty message. Operation cancelled.", "warning")
        return
    
    try:
        print_status("Please place a tag on the reader...", "info")
        nfc_lib.write(device_id, text)
        print_status("Text message written successfully!", "success")
    except Exception as e:
        print_status(f"Error writing to tag: {e}", "error")

def write_url(nfc_lib, device_id):
    """Write a URL to an NFC tag."""
    url = input("Enter the URL to write: ")
    
    if not url:
        print_status("Empty URL. Operation cancelled.", "warning")
        return
    
    # Add http:// prefix if missing
    if not url.startswith(("http://", "https://", "ftp://")):
        url = "https://" + url
        print_status(f"URL automatically updated to: {url}", "info")
    
    try:
        print_status("Please place a tag on the reader...", "info")
        nfc_lib.write(device_id, {"type": "uri", "value": url})
        print_status("URL written successfully!", "success")
    except Exception as e:
        print_status(f"Error writing to tag: {e}", "error")

def write_business_card(nfc_lib, device_id):
    """Write a virtual business card (multiple records) to an NFC tag."""
    print(f"{Colors.BOLD}Enter your contact information:{Colors.END}")
    name = input("Name: ")
    email = input("Email: ")
    phone = input("Phone (optional): ")
    website = input("Website (optional): ")
    
    if not name or not email:
        print_status("Name and email are required. Operation cancelled.", "warning")
        return
    
    # Create contact information text
    contact_info = f"Name: {name}\nEmail: {email}"
    if phone:
        contact_info += f"\nPhone: {phone}"
    
    # Create record list
    records = [{"type": "text", "value": contact_info}]
    
    # Add website if provided
    if website:
        if not website.startswith(("http://", "https://")):
            website = "https://" + website
        records.append({"type": "uri", "value": website})
    
    try:
        print_status("Please place a tag on the reader...", "info")
        nfc_lib.write(device_id, records)
        print_status("Business card written successfully!", "success")
    except Exception as e:
        print_status(f"Error writing to tag: {e}", "error")

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Interactive NFC Terminal Application')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    args = parser.parse_args()
    
    # Set debug level if requested
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    print_header()
    
    # Create NFC library instance
    nfc_lib = create_nfc_library()
    
    # Select device
    device_id = select_device(nfc_lib)
    if not device_id:
        return
    
    try:
        while True:
            print(f"\n{Colors.BOLD}Available operations:{Colors.END}")
            print("1. Write text message")
            print("2. Write URL")
            print("3. Write business card")
            print("4. Change device")
            print("0. Exit")
            
            choice = input("\nSelect an operation (number): ")
            
            if choice == "1":
                write_text(nfc_lib, device_id)
            elif choice == "2":
                write_url(nfc_lib, device_id)
            elif choice == "3":
                write_business_card(nfc_lib, device_id)
            elif choice == "4":
                device_id = select_device(nfc_lib)
                if not device_id:
                    break
            elif choice == "0":
                print_status("Exiting. Thank you for using NFC Terminal!", "info")
                break
            else:
                print_status("Invalid selection. Please try again.", "warning")
            
            # Add a small delay for better UX
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\n")
        print_status("Operation interrupted. Exiting.", "warning")
    finally:
        # Always stop the library to clean up resources
        nfc_lib.stop()

if __name__ == "__main__":
    main()