# NFC Library

A high-level wrapper for NFC operations that simplifies working with NFC readers and tags.

## Overview

This library provides an easy-to-use interface for NFC (Near Field Communication) operations, specifically designed to simplify tag reading and writing. It wraps the lower-level nfcpy and ndef libraries to provide a more user-friendly experience with robust error handling, automatic device detection, and configurable settings.

## Features

-   **Auto-detection** of NFC readers (specifically ACR122U devices)
-   **Simple write** operations with built-in validation
-   **Robust error handling** with timeouts and retries
-   **Comprehensive logging** for debugging
-   **Configuration** via JSON file
-   **Thread-safe** operations
-   **Terminal application** for interactive use

## Installation

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Ensure you have the appropriate drivers for your NFC reader devices.
    - For ACR122U readers on Linux, ensure pcscd service is running:
        ```bash
        sudo apt-get install pcscd
        sudo systemctl start pcscd
        sudo systemctl enable pcscd
        ```

## Usage

### Library Usage

```python
import logging
from nfc_library import create_nfc_library

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nfc_app")

# Create an NFC library instance with auto-detection
nfc_lib = create_nfc_library(logger=logger)

# Get available devices
devices = nfc_lib.devices()
if devices:
    # Write a simple text message to the first detected device
    try:
        nfc_lib.write(devices[0], "Hello, NFC World!")
        logger.info("Write successful!")
    except Exception as e:
        logger.error(f"Write failed: {e}")
else:
    logger.error("No NFC devices detected")

# Clean up resources
nfc_lib.stop()
```

### Terminal Application

The package includes a simple terminal application (`nfc_terminal.py`) to interact with NFC tags without writing code:

```bash
# Run the terminal application
python nfc_terminal.py

# With debug logging enabled
python nfc_terminal.py --debug
```

The terminal application provides options to:

-   Write text messages to tags
-   Write URLs to tags
-   Write contact information (with optional website link)

### Advanced Usage: Multiple Record Types

```python
# Create a multi-record message
message = [
    {"type": "text", "value": "Product: Super Widget"},
    {"type": "uri", "value": "https://example.com/products/123"}
]

# Write to the device
nfc_lib.write(device_id, message)
```

## Configuration

The library can be configured using a JSON file. Default location is `config.json` in the working directory.

Example configuration:

```json
{
	"devices": [
		{
			"id": "main_reader",
			"path": "usb:072f:2200",
			"description": "ACR122U at reception desk"
		}
	],
	"lock_on_write": false,
	"validate_writes": true,
	"retry_count": 3,
	"retry_delay": 0.5,
	"timeout": 5.0
}
```

### Configuration Options

-   `devices`: Array of configured NFC devices
    -   `id`: Unique identifier for the device
    -   `path`: Path to the device (usually USB path)
    -   `description`: Human-readable description
-   `lock_on_write`: Whether to lock tags after writing
-   `validate_writes`: Whether to validate data after writing
-   `retry_count`: Number of retries for failed operations
-   `retry_delay`: Delay between retries (seconds)
-   `timeout`: Operation timeout (seconds)

If no configuration file is found, the library will attempt to auto-detect connected NFC readers.

## Supported NFC Operations

Currently, the library supports:

-   Writing Text records to NFC tags
-   Writing URI records to NFC tags
-   Writing multiple records of different types
-   Automatic validation of written data

## Supported Devices

The auto-detection feature is configured to detect ACR122U NFC readers. Other devices may be manually specified in the configuration file.

## Troubleshooting

### Common Issues

1. **Device not detected**

    - Ensure the device is properly connected
    - Check that pcscd service is running (Linux)
    - Try unplugging and reconnecting the device

2. **Permission issues**

    - Ensure your user has permissions to access USB devices
    - On Linux, you may need to add udev rules for your device

3. **Tag write failures**
    - Ensure the tag is NFC Forum Type compatible
    - Check that the tag has sufficient memory for your data
    - Hold the tag steady against the reader during operation

### Debug Logging

To enable debug logging for troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("nfc_app")
nfc_lib = create_nfc_library(logger=logger)
```

You can also run the terminal application with debug logging:

```bash
python nfc_terminal.py --debug
```

## License

[MIT License](LICENSE)

## Contributions

Contributions are welcome! Please feel free to submit a Pull Request.
