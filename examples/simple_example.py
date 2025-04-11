#!/usr/bin/env python3
"""
Simple example of using the NFC Library.
This script will write a text message to an NFC tag.
"""
import logging
import sys
import time
from nfc_library import create_nfc_library

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

def main():
    # Create NFC library instance
    nfc_lib = create_nfc_library()
    
    # Get available devices
    devices = nfc_lib.devices()
    
    if not devices:
        logging.error("No NFC devices found. Please connect an NFC reader.")
        return
    
    # Select the first device
    device_id = devices[0]
    logging.info(f"Using device: {device_id}")
    
    try:
        # Message to write
        message = "Hello from Python NFC Library!"
        
        # Write message to tag
        logging.info("Please place an NFC tag on the reader...")
        nfc_lib.write(device_id, message)
        logging.info("✅ Message written successfully!")
        
        # You can also write a URI
        logging.info("\nNow let's write a URL. Please place another tag (or the same tag) on the reader...")
        nfc_lib.write(device_id, {"type": "uri", "value": "https://github.com/yourusername/python-nfc-library"})
        logging.info("✅ URL written successfully!")
        
    except Exception as e:
        logging.error(f"Error: {e}")
    finally:
        # Always stop the library to clean up resources
        nfc_lib.stop()
        
if __name__ == "__main__":
    main()