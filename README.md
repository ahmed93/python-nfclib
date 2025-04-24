# Python NFC Library

A high-level Python wrapper library for interacting with NFC (Near Field Communication) devices and tags on Linux systems (including Raspberry Pi) with a focus on reliability and ease of use.

## Architecture

This library serves as a simplified abstraction layer over lower-level NFC libraries:

```
Your Application
       ↓
Python NFC Library (this library)
       ↓
 nfcpy and ndef libraries
       ↓
   NFC Hardware
```

By wrapping the more complex nfcpy library, we provide a cleaner, more developer-friendly API that handles common edge cases, errors, and configuration while maintaining the full power of the underlying libraries.

## Features

-   **Simplified API**: Abstracts away hardware-specific details while maintaining full functionality
-   Automatic device detection for ACR122U NFC readers
-   Clean, high-level interface for reading and writing NDEF messages to NFC tags
-   Support for various NDEF record types (Text, URI)
-   Built-in error handling for hardware timeouts and failures
-   Configurable timeouts, retries, and validation
-   Comprehensive logging
-   Thread-safe operations

## Installation

### Prerequisites

This library requires the following dependencies:

-   Linux operating system (including Raspberry Pi)
-   Python 3.9+
-   nfcpy
-   ndef

Install dependencies using pip:

```bash
pip install nfcpy ndef
```

### Installation

```bash
# Using pip
pip install python-nfc-library

# Manual installation
git clone https://github.com/yourusername/python-nfc-library.git
cd python-nfc-library
pip install -e .
```

## Quick Start

```python
from nfc_library import create_nfc_library

# Create an instance of the library
nfc_lib = create_nfc_library()

# Get available devices
devices = nfc_lib.devices()
print(f"Available devices: {devices}")

# Write a text message to a tag
if devices:
    try:
        # Simple text message
        nfc_lib.write(devices[0], "Hello, NFC!")

        # URI message
        nfc_lib.write(devices[0], {"type": "uri", "value": "https://example.com"})

        # Multiple records
        message = [
            {"type": "text", "value": "Hello, NFC!"},
            {"type": "uri", "value": "https://example.com"}
        ]
        nfc_lib.write(devices[0], message)

    except Exception as e:
        print(f"Error writing to tag: {e}")
    finally:
        nfc_lib.stop()
```

## Configuration

The library can be configured using a JSON configuration file. By default, it looks for a file named `config.json` in the current directory.

### Configuration Options

```json
{
	"devices": [
		{
			"id": "reader_1",
			"path": "usb:123:456",
			"description": "ACR122U NFC Reader"
		}
	],
	"lock_on_write": false,
	"validate_writes": true,
	"retry_count": 3,
	"retry_delay": 0.5,
	"timeout": 5.0
}
```

| Option            | Description                                | Default       |
| ----------------- | ------------------------------------------ | ------------- |
| `devices`         | List of NFC devices                        | Auto-detected |
| `lock_on_write`   | Whether to lock tags after writing         | `false`       |
| `validate_writes` | Validate written data matches the original | `true`        |
| `retry_count`     | Number of retries for operations           | `3`           |
| `retry_delay`     | Delay between retries (seconds)            | `0.5`         |
| `timeout`         | Timeout for operations (seconds)           | `5.0`         |

If no configuration file is found, the library will use default values and attempt to auto-detect devices.

## API Reference

### `create_nfc_library(config_path="config.json", logger=None)`

Creates and returns a new instance of the NFC library.

**Parameters:**

-   `config_path` (str): Path to the configuration file
-   `logger` (logging.Logger, optional): Custom logger instance

**Returns:**

-   `NFCLibrary`: A new library instance

### `NFCLibrary.devices()`

Returns a list of available device IDs.

**Returns:**

-   `List[str]`: List of device IDs

### `NFCLibrary.write(device_id, message)`

Writes an NDEF message to a tag and returns immediately after a successful write.

**Parameters:**

-   `device_id` (str): The ID of the device to use
-   `message` (Union[str, Dict, List]): The message to write, which can be:
    -   A string for a simple text message
    -   A dictionary with 'type' and 'value' keys for a single record
    -   A list of dictionaries for multiple records

**Returns:**

-   `bool`: True if successful

**Raises:**

-   `ValueError`: If the device ID is invalid or the message format is incorrect
-   `Exception`: If no tag is detected within the timeout period

### `NFCLibrary.stop()`

Stops all active NFC connections.

## Message Formats

The library supports three formats for messages:

### Simple Text

```python
message = "Hello, NFC!"
```

### Single Record (Dictionary)

```python
message = {
    "type": "text",  # or "uri"
    "value": "Hello, NFC!"  # or "https://example.com" for URI
}
```

### Multiple Records (List of Dictionaries)

```python
message = [
    {
        "type": "text",
        "value": "Hello, NFC!"
    },
    {
        "type": "uri",
        "value": "https://example.com"
    }
]
```

## Logging

The library uses Python's built-in logging module and leverages the default root logger. This makes it easy to integrate with your existing logging configuration. You can configure the root logger or provide a custom logger:

```python
import logging

# Configure the root logger (applies to all modules using the default logger)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='nfc.log'
)

# Create the library (will use the configured root logger)
nfc_lib = create_nfc_library()

# Or use a custom logger if needed
custom_logger = logging.getLogger("my_nfc_app")
custom_logger.setLevel(logging.DEBUG)
custom_logger.addHandler(logging.FileHandler("custom_nfc.log"))
nfc_lib = create_nfc_library(logger=custom_logger)
```

## Troubleshooting

### Device Detection Issues

If the library cannot detect your NFC reader:

1. Ensure the device is properly connected
2. Run `lsusb` to check if the device is recognized by the system
3. Make sure you have the necessary permissions to access USB devices
4. Try manually configuring the device in the configuration file

### Tag Reading/Writing Issues

1. Make sure the tag is compatible with NDEF
2. Keep the tag still over the reader during operations
3. Increase the timeout value in the configuration
4. Check the logs for detailed error messages

### Test Failures During Publishing

If you're experiencing test failures during the publishing process, the most common issues are:

1. **Missing hardware**: CI environments may not have NFC readers attached

    - Solution: Add a mock mode for tests that doesn't require physical hardware
    - Example: Add `MOCK_MODE=True` environment variable detection in tests

2. **Permissions issues**: CI runners may not have proper USB access permissions

    - Solution: Ensure tests can be run with a `--no-hardware` flag that skips hardware-dependent tests

3. **Timing issues**: Hardware operations might timeout in constrained CI environments
    - Solution: Increase timeouts specifically in test mode

To address these, add this to your test suite:

```python
import os
import pytest

# Skip hardware tests when running in CI
SKIP_HARDWARE_TESTS = os.environ.get('SKIP_HARDWARE_TESTS', 'False').lower() in ('true', '1', 't')

@pytest.mark.skipif(SKIP_HARDWARE_TESTS, reason="Skipping hardware tests in CI environment")
class TestHardwareOperations(unittest.TestCase):
    # Hardware-dependent tests here
```

Then in your CI configuration, set `SKIP_HARDWARE_TESTS=True`.

## License

[MIT License](LICENSE)

## Contributions

Contributions are welcome! Please feel free to submit a Pull Request.
