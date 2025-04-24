"""
NFC Library - A high-level Python library for NFC operations on Linux systems.
"""

__version__ = "1.0.0"

from .nfc_library import create_nfc_library, NFCLibrary

__all__ = ["create_nfc_library", "NFCLibrary"]
