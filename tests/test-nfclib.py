import unittest
from unittest.mock import patch, MagicMock
import logging
import json
import os
import tempfile

from nfc_library import create_nfc_library, NFCLibrary


class TestNFCLibrary(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        # Create a logger that doesn't output anything
        self.logger = logging.getLogger("test_logger")
        self.logger.setLevel(logging.CRITICAL)
        
        # Create a temporary config file
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_path = os.path.join(self.temp_dir.name, "test_config.json")
        self.test_config = {
            "devices": [
                {
                    "id": "test_device_1",
                    "path": "usb:123:456",
                    "description": "Test NFC Reader"
                }
            ],
            "lock_on_write": False,
            "validate_writes": True,
            "retry_count": 3,
            "retry_delay": 0.5,
            "timeout": 1.0
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(self.test_config, f)
    
    def tearDown(self):
        """Tear down test fixtures"""
        self.temp_dir.cleanup()
    
    @patch('nfc_library.nfc_library.nfc')
    def test_initialization(self, mock_nfc):
        """Test library initialization with config file"""
        lib = NFCLibrary(self.config_path, self.logger)
        self.assertEqual(lib.config["devices"][0]["id"], "test_device_1")
        self.assertEqual(lib.active_device_id, None)
        self.assertEqual(lib.active_clf, None)
        self.assertFalse(lib.is_connection_active)
    
    @patch('nfc_library.nfc_library.nfc')
    def test_default_config(self, mock_nfc):
        """Test library uses default config when file not found"""
        non_existent_path = os.path.join(self.temp_dir.name, "nonexistent.json")
        lib = NFCLibrary(non_existent_path, self.logger)
        self.assertEqual(lib.config["devices"], [])
        self.assertEqual(lib.config["retry_count"], 3)
    
    @patch('nfc_library.nfc_library.nfc')
    def test_devices_method(self, mock_nfc):
        """Test devices() returns correct list of device IDs"""
        lib = NFCLibrary(self.config_path, self.logger)
        devices = lib.devices()
        self.assertEqual(devices, ["test_device_1"])
    
    @patch('nfc_library.nfc_library.subprocess')
    @patch('nfc_library.nfc_library.nfc')
    def test_auto_scan_devices(self, mock_nfc, mock_subprocess):
        """Test auto-scanning for devices"""
        # Set up mock for subprocess.run to return ACR122U device info
        mock_process = MagicMock()
        mock_process.stdout = "Bus 001 Device 002: ID 072f:2200 Advanced Card Systems, Ltd ACR122U"
        mock_subprocess.run.return_value = mock_process
        
        # Create empty config
        empty_config = {
            "devices": [],
            "lock_on_write": False,
            "validate_writes": True,
            "retry_count": 3,
            "retry_delay": 0.5,
            "timeout": 1.0
        }
        
        empty_config_path = os.path.join(self.temp_dir.name, "empty_config.json")
        with open(empty_config_path, 'w') as f:
            json.dump(empty_config, f)
        
        # Initialize library with empty config - should trigger auto-scan
        with patch('nfc_library.nfc_library.re.match') as mock_match:
            # Mock the regex match
            mock_match_obj = MagicMock()
            mock_match_obj.groups.return_value = ("001", "002")
            mock_match.return_value = mock_match_obj
            
            lib = NFCLibrary(empty_config_path, self.logger)
            
            # Verify a device was auto-detected
            self.assertEqual(len(lib.config["devices"]), 1)
            self.assertTrue(lib.config["devices"][0]["id"].startswith("device_"))
            self.assertEqual(lib.config["devices"][0]["path"], "usb:001:002")
    
    @patch('nfc_library.nfc_library.nfc')
    def test_create_ndef_message_text(self, mock_nfc):
        """Test creating NDEF message from text string"""
        lib = NFCLibrary(self.config_path, self.logger)
        
        with patch('nfc_library.nfc_library.ndef.TextRecord') as mock_text_record:
            mock_text_record.return_value = MagicMock()
            
            result = lib._create_ndef_message("Hello, NFC!")
            
            # Verify TextRecord was called with the correct text
            mock_text_record.assert_called_once_with("Hello, NFC!")
            # Verify result is a list containing the record
            self.assertEqual(len(result), 1)
    
    @patch('nfc_library.nfc_library.nfc')
    def test_create_ndef_message_uri(self, mock_nfc):
        """Test creating NDEF message from URI dict"""
        lib = NFCLibrary(self.config_path, self.logger)
        
        with patch('nfc_library.nfc_library.ndef.UriRecord') as mock_uri_record:
            mock_uri_record.return_value = MagicMock()
            
            result = lib._create_ndef_message({"type": "uri", "value": "https://example.com"})
            
            # Verify UriRecord was called with the correct URI
            mock_uri_record.assert_called_once_with("https://example.com")
            # Verify result is a list containing the record
            self.assertEqual(len(result), 1)
    
    @patch('nfc_library.nfc_library.nfc')
    def test_factory_function(self, mock_nfc):
        """Test the create_nfc_library factory function"""
        with patch('nfc_library.nfc_library.NFCLibrary') as mock_nfc_lib:
            mock_nfc_lib.return_value = MagicMock()
            
            lib = create_nfc_library("custom_config.json", self.logger)
            
            # Verify NFCLibrary was instantiated with the correct parameters
            mock_nfc_lib.assert_called_once_with("custom_config.json", self.logger)


if __name__ == '__main__':
    unittest.main()