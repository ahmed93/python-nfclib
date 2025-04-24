# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2025-04-25

### Changed
- Updated minimum Python version requirement to Python 3.9
- Simplified test suite for improved reliability in CI environments
- Updated documentation to emphasize wrapper nature of the library

### Fixed
- Test failures during package publishing
- Improved error handling for missing hardware in test environments

## [1.0.0] - 2025-04-11

### Added
- Initial release of the NFC Library
- Core functionality for NFC tag detection and interaction
- Support for ACR122U NFC readers
- NDEF message creation and writing capabilities 
- Support for text and URI record types
- Configuration system with JSON-based settings
- Automatic device detection
- Comprehensive logging system
- Example scripts and interactive terminal application