import nfc
import ndef
import subprocess
import re
import json
import time
import os
import logging
import threading
from typing import List, Dict, Any, Optional, Union, Tuple, cast


class NFCLibrary:
    def __init__(self, config_path: str, logger: Optional[logging.Logger] = None):
        # Set up logging
        self.logger = logger or self._setup_default_logger()
        self.logger.info("Initializing NFC Library")
        self.config = self._load_config(config_path)
        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug(f"Loaded configuration: {self.config}")
        self.active_device_id = None
        self.active_clf = None
        self.is_connection_active = False
        self._tag_found = False
        self._reader_lock = threading.Lock()
        
        # Initialize devices
        if not self.config["devices"]:
            self.logger.info("No devices configured, performing auto-scan")
            self._auto_scan_devices()
            self.logger.info(f"Auto-scan found {len(self.config['devices'])} devices")
    
    def _setup_default_logger(self) -> logging.Logger:
        logger = logging.getLogger("nfc_library")
        logger.setLevel(logging.INFO)
        
        # Create console handler
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(handler)
        
        return logger
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        if not os.path.exists(config_path):
            self.logger.warning(f"Configuration file {config_path} not found. Using default configuration.")
            # Create default configuration
            default_config = {
                "devices": [],
                "lock_on_write": False,
                "validate_writes": True,
                "retry_count": 3,
                "retry_delay": 0.5,
                "timeout": 5.0
            }
            return default_config
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                self.logger.info(f"Successfully loaded configuration from {config_path}")
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse configuration file: {e}")
            raise
        
        # Ensure all required fields exist
        required_fields = [
            "devices", "lock_on_write", "validate_writes", 
            "retry_count", "retry_delay", "timeout"
        ]
        
        for field in required_fields:
            if field not in config:
                if field == "devices":
                    config[field] = []
                elif field == "lock_on_write":
                    config[field] = False
                elif field == "validate_writes":
                    config[field] = True
                elif field == "retry_count":
                    config[field] = 3
                elif field == "retry_delay":
                    config[field] = 0.5
                elif field == "timeout":
                    config[field] = 5.0
                self.logger.warning(f"Missing required field '{field}' in config. Using default value: {config[field]}")
        
        return config
    
    def _auto_scan_devices(self) -> None:
        self.logger.info("Starting automatic device scan")
        try:
            result = subprocess.run(["lsusb"], capture_output=True, text=True)
            device_id = 1
            
            for line in result.stdout.strip().split("\n"):
                if "072f:2200" in line:  # Match ACR122U
                    match = re.match(r"Bus (\d{3}) Device (\d{3})", line)
                    if match:
                        bus, dev = match.groups()
                        path = f"usb:{bus}:{dev}"
                        
                        # Create a unique ID for the device
                        device_id_str = f"device_{device_id}"
                        device_id += 1
                        
                        # Add the device to the configuration
                        device_info = {
                            "id": device_id_str,
                            "path": path,
                            "description": "ACR122U NFC Reader (Auto-detected)"
                        }
                        self.config["devices"].append(device_info)
                        self.logger.info(f"Detected device: {device_info}")
        except Exception as e:
            self.logger.error(f"Error during device scan: {e}")
            raise
    
    def devices(self) -> List[str]:
        device_ids = [device["id"] for device in self.config["devices"]]
        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug(f"Available devices: {device_ids}")
        return device_ids
    
    def _find_device_path(self, device_id: str) -> Optional[str]:
        for device in self.config["devices"]:
            if device["id"] == device_id:
                if self.logger.isEnabledFor(logging.DEBUG):
                    self.logger.debug(f"Found path for device {device_id}: {device['path']}")
                return device["path"]
        self.logger.warning(f"No path found for device ID: {device_id}")
        return None
    
    def _ensure_device_active(self, device_id: str) -> bool:
        # If this device is already active, nothing to do
        if self.active_device_id == device_id and self.active_clf is not None and self.is_connection_active:
            if self.logger.isEnabledFor(logging.DEBUG):
                self.logger.debug(f"Device {device_id} is already active")
            return True
            
        # If a different device is active, close it
        if self.active_clf is not None:
            self.logger.info(f"Closing currently active device {self.active_device_id}")
            try:
                self.active_clf.close()
            except Exception as e:
                self.logger.error(f"Error closing device {self.active_device_id}: {e}")
            finally:
                self.active_clf = None
                self.active_device_id = None
                self.is_connection_active = False
        
        # Get the path for the new device
        device_path = self._find_device_path(device_id)
        if not device_path:
            self.logger.error(f"Invalid device ID: {device_id}")
            return False
            
        # Open the new device with manual timeout
        try:
            self.logger.info(f"Opening connection to device {device_id} at {device_path}")
            
            # Use threading to implement timeout
            result = {"clf": None, "success": False, "error": None}
            
            def open_device():
                try:
                    result["clf"] = nfc.ContactlessFrontend(device_path)
                    result["success"] = True
                except Exception as e:
                    result["error"] = e
            
            thread = threading.Thread(target=open_device)
            thread.daemon = True
            thread.start()
            thread.join(timeout=self.config["timeout"])
            
            if not result["success"]:
                if thread.is_alive():
                    self.logger.error(f"Timeout while opening device {device_id}")
                    return False
                elif result["error"]:
                    self.logger.error(f"Error opening device {device_id}: {result['error']}")
                    return False
            
            self.active_clf = result["clf"]
            self.active_device_id = device_id
            self.is_connection_active = True
            return True
        except Exception as e:
            self.logger.error(f"Error opening device {device_id}: {e}")
            return False
    
    def _create_ndef_message(self, message: Union[str, Dict, List]) -> Any:
        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug(f"Creating NDEF message from: {message}")
        
        if isinstance(message, str):
            # Simple text message
            if self.logger.isEnabledFor(logging.DEBUG):
                self.logger.debug("Creating text record from string")
            record = ndef.TextRecord(message)
            return [record]
        
        elif isinstance(message, dict):
            # Single record with type specification
            if "type" not in message or "value" not in message:
                self.logger.error("Dictionary message missing required 'type' or 'value' keys")
                raise ValueError("Dictionary message must have 'type' and 'value' keys")
            
            if message["type"] == "text":
                if self.logger.isEnabledFor(logging.DEBUG):
                    self.logger.debug(f"Creating text record: {message['value']}")
                record = ndef.TextRecord(message["value"])
                return [record]
            elif message["type"] == "uri":
                if self.logger.isEnabledFor(logging.DEBUG):
                    self.logger.debug(f"Creating URI record: {message['value']}")
                record = ndef.UriRecord(message["value"])
                return [record]
            else:
                self.logger.error(f"Unsupported record type: {message['type']}")
                raise ValueError(f"Unsupported record type: {message['type']}")
        
        elif isinstance(message, list):
            # Multiple records
            if self.logger.isEnabledFor(logging.DEBUG):
                self.logger.debug(f"Creating {len(message)} records from list")
            records = []
            for i, record in enumerate(message):
                if not isinstance(record, dict) or "type" not in record or "value" not in record:
                    self.logger.error(f"Record {i} in list is invalid")
                    raise ValueError("Each record in the list must be a dictionary with 'type' and 'value' keys")
                
                if record["type"] == "text":
                    if self.logger.isEnabledFor(logging.DEBUG):
                        self.logger.debug(f"Creating text record {i}: {record['value']}")
                    records.append(ndef.TextRecord(record["value"]))
                elif record["type"] == "uri":
                    if self.logger.isEnabledFor(logging.DEBUG):
                        self.logger.debug(f"Creating URI record {i}: {record['value']}")
                    records.append(ndef.UriRecord(record["value"]))
                else:
                    self.logger.error(f"Unsupported record type in record {i}: {record['type']}")
                    raise ValueError(f"Unsupported record type: {record['type']}")
            
            return records
        
        else:
            self.logger.error(f"Unsupported message type: {type(message)}")
            raise ValueError("Message must be a string, dictionary, or list of records")
    
    def _validate_write(self, tag, ndef_message: List) -> bool:
        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug("Validating tag write")
        
        if not tag.ndef:
            self.logger.error("Validation failed: Tag doesn't support NDEF")
            return False
        
        # Compare the written message with the original
        original_records = ndef_message
        written_records = tag.ndef.records
        
        if len(original_records) != len(written_records):
            self.logger.error(f"Validation failed: Record count mismatch - original: {len(original_records)}, written: {len(written_records)}")
            return False
        
        for i, (orig, written) in enumerate(zip(original_records, written_records)):
            if orig.type != written.type or orig.data != written.data:
                self.logger.error(f"Validation failed: Record {i} data mismatch")
                return False
        
        self.logger.info("Write validation successful")
        return True
    
    def write(self, device_id: str, message: Union[str, Dict, List]) -> bool:
        """
        Write an NDEF message to a tag using the specified device.
        Returns control immediately after successful write.
        """
        self.logger.info(f"Writing to device {device_id}")
        
        # Reset the reader first to clear any lingering RF field state
        self._reset_reader(device_id)
        
        # Ensure the device is active
        if not self._ensure_device_active(device_id):
            raise ValueError(f"Failed to activate device {device_id}")
        
        # Prepare the NDEF message
        ndef_message = self._create_ndef_message(message)
        
        # Use a threading lock to prevent concurrent tag detection
        with self._reader_lock:
            # Clear any previous detection state
            self._tag_found = False
            write_success = False
            
            # Use an event to signal when writing is complete
            write_completed = threading.Event()
            
            # Define the on-connect callback with better state management
            def on_tag_connect(tag):
                nonlocal write_success
                
                # Skip if we already processed a tag in this operation
                if self._tag_found:
                    return True
                
                self._tag_found = True
                self.logger.info(f"Tag detected - UID: {tag.identifier.hex().upper()}")
                
                try:
                    if not tag.ndef or not tag.ndef.is_writeable:
                        return True
                    
                    # Write the message
                    self.logger.info("Writing NDEF message to tag")
                    tag.ndef.records = ndef_message
                    
                    # Validate if needed
                    if self.config["validate_writes"]:
                        if not self._validate_write(tag, ndef_message):
                            return True
                    
                    self.logger.info("Tag write successful")
                    write_success = True
                    
                    # Signal completion and force termination
                    write_completed.set()
                    
                except Exception as e:
                    self.logger.error(f"Error during tag operation: {e}")
                
                return True
                
            # Start tag detection
            try:
                # Use direct connect rather than threading to avoid race conditions
                self.active_clf.connect(
                    rdwr={'on-connect': on_tag_connect},
                    terminate=lambda: write_completed.is_set() or not self.is_connection_active
                )
            except Exception as e:
                self.logger.error(f"Connection error: {e}")
                
            if write_success:
                self.logger.info("Returning control after successful write")
                
                # Force field off immediately to prepare for next tag
                self._force_field_off()
                
                return True
                
            raise Exception("No tag detected within timeout period")

    def _reset_reader(self, device_id):
        """
        Force a complete reset of the NFC reader to clear any lingering RF field state.
        """
        # If this device is active, close it first
        if self.active_clf is not None:
            try:
                self.active_clf.close()
            except Exception:
                pass
            self.active_clf = None
            self.active_device_id = None
            self.is_connection_active = False
            
        # Small delay to ensure hardware reset
        time.sleep(0.05)
        
    def _force_field_off(self):
        """
        Force the RF field to turn off.
        """
        # For ACR122U readers, sending specific direct commands can force field off
        # This requires pyscard integration
        try:
            if self.active_clf and hasattr(self.active_clf, 'device'):
                # This will depend on your specific NFC library implementation
                # For ACR122U with pyscard:
                # self.active_clf.device.transmit([0xFF, 0x00, 0x00, 0x00, 0x00])
                pass
        except:
            pass

    def stop(self) -> None:
        """
        Stop all active NFC connections.
        """
        if self.active_clf is not None:
            self.logger.info(f"Closing device {self.active_device_id}")
            try:
                self.active_clf.close()
            except Exception as e:
                self.logger.error(f"Error closing device {self.active_device_id}: {e}")
            finally:
                self.active_clf = None
                self.active_device_id = None
                self.is_connection_active = False
        else:
            if self.logger.isEnabledFor(logging.DEBUG):
                self.logger.debug("No active device to close")


def create_nfc_library(config_path: str = "config.json", logger: Optional[logging.Logger] = None) -> NFCLibrary:
    return NFCLibrary(config_path, logger)