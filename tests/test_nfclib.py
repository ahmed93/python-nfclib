import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Skip tests if Python version is less than 3.9
if sys.version_info < (3, 9):
    print("Skipping tests: Python 3.9 or higher is required")
    sys.exit(0)

from nfc_library import create_nfc_library, NFCLibrary

# Simple environment check to detect CI environments
RUNNING_IN_CI = os.environ.get("CI", "False").lower() == "true"


class TestNFCLibrary(unittest.TestCase):
    """Basic tests for the NFC Library that don't require hardware"""

    @patch("nfc_library.nfc_library.nfc")
    def test_library_creation(self, mock_nfc):
        """Test that the library can be created"""
        lib = create_nfc_library()
        self.assertIsInstance(lib, NFCLibrary)

    @patch("nfc_library.nfc_library.nfc")
    def test_message_creation_text(self, mock_nfc):
        """Test creating a text message"""
        lib = create_nfc_library()

        with patch("nfc_library.nfc_library.ndef.TextRecord") as mock_text_record:
            mock_text_record.return_value = "mocked_text_record"

            message = lib._create_ndef_message("Hello, NFC!")

            # Verify the method was called with the right text
            mock_text_record.assert_called_once_with("Hello, NFC!")

    @patch("nfc_library.nfc_library.nfc")
    def test_message_creation_uri(self, mock_nfc):
        """Test creating a URI message"""
        lib = create_nfc_library()

        with patch("nfc_library.nfc_library.ndef.UriRecord") as mock_uri_record:
            mock_uri_record.return_value = "mocked_uri_record"

            message = lib._create_ndef_message(
                {"type": "uri", "value": "https://example.com"}
            )

            # Verify the method was called with the right URI
            mock_uri_record.assert_called_once_with("https://example.com")

    @patch("nfc_library.nfc_library.nfc")
    def test_multi_record_message(self, mock_nfc):
        """Test creating a multi-record message"""
        lib = create_nfc_library()

        with patch("nfc_library.nfc_library.ndef.TextRecord") as mock_text_record:
            with patch("nfc_library.nfc_library.ndef.UriRecord") as mock_uri_record:
                mock_text_record.return_value = "mocked_text_record"
                mock_uri_record.return_value = "mocked_uri_record"

                message = lib._create_ndef_message(
                    [
                        {"type": "text", "value": "Hello"},
                        {"type": "uri", "value": "https://example.com"},
                    ]
                )

                # Verify both records were created
                mock_text_record.assert_called_once_with("Hello")
                mock_uri_record.assert_called_once_with("https://example.com")


# Only run this test when not in CI environment
@unittest.skipIf(RUNNING_IN_CI, "Skipping hardware test in CI environment")
class SimpleHardwareTest(unittest.TestCase):
    """A simple test that requires hardware - skipped in CI environments"""

    @patch("nfc_library.nfc_library.nfc")
    def test_basic_mock_write(self, mock_nfc):
        """Test a simple write with mocked hardware"""
        # Create a simple mock for the hardware
        mock_clf = MagicMock()
        mock_nfc.ContactlessFrontend.return_value = mock_clf

        # Make the connect method execute our on-connect callback with a mock tag
        def mock_connect(**kwargs):
            mock_tag = MagicMock()
            mock_tag.ndef = MagicMock()
            mock_tag.identifier = b"1234"

            # Call the on-connect callback with our mock tag
            if "rdwr" in kwargs and "on-connect" in kwargs["rdwr"]:
                kwargs["rdwr"]["on-connect"](mock_tag)
            return True

        mock_clf.connect = mock_connect

        # Create the library and attempt a write
        lib = create_nfc_library()

        # Mock getting a device
        with patch.object(lib, "devices", return_value=["mock_device"]):
            with patch.object(lib, "_find_device_path", return_value="usb:mock"):
                # Should return True if the write succeeded
                result = lib.write("mock_device", "Test message")
                self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
