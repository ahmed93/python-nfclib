#!/usr/bin/env python3
"""
Simplified NFC Terminal Application

A streamlined command-line interface for writing data to NFC tags
using the NFC Library.
"""
import logging
import sys
import argparse
from main import create_nfc_library

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

def print_colored(message, color_code):
    """Print a message with color."""
    print(f"{color_code}{message}\033[0m")

# Color codes
GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
BOLD = '\033[1m'

def print_header():
    """Print the application header."""
    print_colored("\n=== NFC TERMINAL ===\n", BOLD + BLUE)

def select_device(nfc_lib):
    """Select an NFC device from available devices."""
    devices = nfc_lib.devices()
    
    if not devices:
        print_colored("No NFC devices found. Please connect an NFC reader.", RED)
        return None
    
    if len(devices) == 1:
        print_colored(f"Using device: {devices[0]}", BLUE)
        return devices[0]
    
    print_colored("Available devices:", BLUE)
    for i, device_id in enumerate(devices):
        print(f"{i+1}. {device_id}")
    
    while True:
        try:
            choice = int(input("Select device (number): "))
            if 1 <= choice <= len(devices):
                return devices[choice-1]
            print_colored("Invalid selection. Try again.", YELLOW)
        except ValueError:
            print_colored("Please enter a number.", YELLOW)

def write_to_tag(nfc_lib, device_id, message):
    """Write a message to an NFC tag."""
    try:
        print_colored("Place a tag on the reader...", BLUE)
        nfc_lib.write(device_id, message)
        print_colored("Write successful!", GREEN)
        return True
    except Exception as e:
        print_colored(f"Error: {e}", RED)
        return False

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='NFC Terminal')
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
            print("\nOptions:")
            print("1. Write text")
            print("2. Write URL")
            print("3. Write contact info")
            print("0. Exit")
            
            choice = input("\nSelect option: ")
            
            if choice == "1":
                text = input("Enter text: ")
                if text:
                    write_to_tag(nfc_lib, device_id, text)
            
            elif choice == "2":
                url = input("Enter URL: ")
                if url:
                    # Add https:// if missing
                    if not url.startswith(("http://", "https://")):
                        url = "https://" + url
                        print_colored(f"URL updated to: {url}", BLUE)
                    write_to_tag(nfc_lib, device_id, {"type": "uri", "value": url})
            
            elif choice == "3":
                name = input("Name: ")
                email = input("Email: ")
                
                if name and email:
                    contact_info = f"Name: {name}\nEmail: {email}"
                    website = input("Website (optional): ")
                    
                    if website:
                        if not website.startswith(("http://", "https://")):
                            website = "https://" + website
                        # Create multi-record message
                        message = [
                            {"type": "text", "value": contact_info},
                            {"type": "uri", "value": website}
                        ]
                    else:
                        message = contact_info
                        
                    write_to_tag(nfc_lib, device_id, message)
                else:
                    print_colored("Name and email are required.", YELLOW)
            
            elif choice == "0":
                print_colored("Exiting NFC Terminal.", BLUE)
                break
                
            else:
                print_colored("Invalid option.", YELLOW)
    
    except KeyboardInterrupt:
        print("\n")
        print_colored("Operation interrupted.", YELLOW)
    finally:
        # Clean up resources
        nfc_lib.stop()

if __name__ == "__main__":
    main()