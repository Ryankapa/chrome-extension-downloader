# Chrome Extension Downloader - API Documentation

## Overview

The Chrome Extension Downloader is a comprehensive Python tool for downloading Chrome extensions from the Chrome Web Store, converting them from CRX to ZIP format, and managing downloads with advanced features like batch processing, caching, and configuration management.

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Configuration](#configuration)
4. [API Reference](#api-reference)
5. [Command Line Interface](#command-line-interface)
6. [Examples](#examples)
7. [Error Handling](#error-handling)
8. [Advanced Features](#advanced-features)

## Installation

### From Source
```bash
git clone https://github.com/your-username/chrome-extension-downloader.git
cd chrome-extension-downloader
pip install -r requirements.txt
```

### As Package (when published to PyPI)
```bash
pip install chrome-extension-downloader
```

## Quick Start

### Basic Usage
```python
from chrome_extension_downloader import AutoExtensionDownloader

# Create downloader instance
downloader = AutoExtensionDownloader()

# Download single extension
result = downloader.download_and_convert("gppongmhjkpfnbhagpmjfkannfbllamg")
print(f"Downloaded to: {result}")
```

### Command Line
```bash
# Download single extension
python chrome_extension_downloader.py gppongmhjkpfnbhagpmjfkannfbllamg

# Download multiple extensions
python chrome_extension_downloader.py --batch gppongmhjkpfnbhagpmjfkannfbllamg nkeimhogjdpnpccoofpliimaahmaaome

# Interactive mode
python chrome_extension_downloader.py --interactive
```

## Configuration

### Configuration File Structure

The tool uses a JSON configuration file (`config.json`) with the following structure:

```json
{
  "download": {
    "max_file_size_mb": 100,
    "timeout_seconds": 30,
    "retry_attempts": 3,
    "retry_delay_seconds": 2,
    "verify_ssl": true,
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
  },
  "output": {
    "default_directory": "./downloads",
    "auto_cleanup": true,
    "create_subdirectories": true
  },
  "performance": {
    "max_concurrent_downloads": 3,
    "chunk_size": 8192,
    "enable_caching": true,
    "cache_directory": "./cache"
  },
  "security": {
    "validate_extension_id": true,
    "check_file_integrity": true,
    "rate_limit_delay": 1.0
  }
}
```

### Configuration Options

#### Download Settings
- `max_file_size_mb`: Maximum file size in MB (default: 100)
- `timeout_seconds`: Request timeout in seconds (default: 30)
- `retry_attempts`: Number of retry attempts (default: 3)
- `retry_delay_seconds`: Delay between retries (default: 2)
- `verify_ssl`: Enable SSL certificate verification (default: true)
- `user_agent`: HTTP User-Agent string

#### Output Settings
- `default_directory`: Default download directory (default: "./downloads")
- `auto_cleanup`: Automatically delete CRX files after conversion (default: true)
- `create_subdirectories`: Create subdirectories for organization (default: true)

#### Performance Settings
- `max_concurrent_downloads`: Maximum concurrent downloads (default: 3)
- `chunk_size`: Download chunk size in bytes (default: 8192)
- `enable_caching`: Enable download caching (default: true)
- `cache_directory`: Cache directory path (default: "./cache")

#### Security Settings
- `validate_extension_id`: Validate extension ID format (default: true)
- `check_file_integrity`: Verify ZIP file integrity (default: true)
- `rate_limit_delay`: Delay between requests in seconds (default: 1.0)

## API Reference

### Config Class

#### `Config(config_file: str = "config.json")`

Configuration management class.

**Parameters:**
- `config_file`: Path to configuration file

**Methods:**
- `load_config() -> Dict[str, Any]`: Load configuration from file
- `save_config()`: Save current configuration to file
- `_merge_configs(default: Dict, user: Dict) -> Dict`: Merge user config with defaults

### AutoExtensionDownloader Class

#### `AutoExtensionDownloader(config: Optional[Config] = None)`

Main downloader class.

**Parameters:**
- `config`: Configuration instance (optional)

**Methods:**

##### `validate_extension_id(extension_id: str) -> bool`

Validate Chrome extension ID format.

**Parameters:**
- `extension_id`: Extension ID to validate

**Returns:**
- `bool`: True if valid, False otherwise

##### `get_extension_metadata(extension_id: str) -> Dict[str, Any]`

Get extension metadata from Chrome Web Store.

**Parameters:**
- `extension_id`: Extension ID

**Returns:**
- `Dict[str, Any]`: Metadata dictionary with keys: id, name, version, description

##### `download_and_convert(extension_id: str, output_filename: Optional[str] = None, cleanup: bool = True, show_progress: bool = True) -> str`

Download CRX file, convert to ZIP, and optionally clean up.

**Parameters:**
- `extension_id`: Chrome extension ID
- `output_filename`: Output ZIP filename (optional)
- `cleanup`: Whether to delete the CRX file after conversion
- `show_progress`: Whether to show download progress

**Returns:**
- `str`: Path to the final ZIP file

**Raises:**
- `ValueError`: If extension ID is invalid or download fails
- `FileNotFoundError`: If output directory doesn't exist

##### `download_multiple(extension_ids: List[str], output_dir: Optional[str] = None, max_workers: Optional[int] = None) -> Dict[str, str]`

Download multiple extensions concurrently.

**Parameters:**
- `extension_ids`: List of Chrome extension IDs
- `output_dir`: Output directory (optional)
- `max_workers`: Maximum concurrent downloads (optional)

**Returns:**
- `Dict[str, str]`: Mapping of extension_id to output_file_path

##### `download_from_file(file_path: str, output_dir: Optional[str] = None) -> Dict[str, str]`

Download extensions from a text file containing extension IDs.

**Parameters:**
- `file_path`: Path to file containing extension IDs (one per line)
- `output_dir`: Output directory (optional)

**Returns:**
- `Dict[str, str]`: Mapping of extension_id to output_file_path

**Raises:**
- `FileNotFoundError`: If file doesn't exist
- `ValueError`: If file can't be read

### ChromeWebStoreURLBuilder Class

#### `ChromeWebStoreURLBuilder()`

URL builder for Chrome Web Store downloads.

**Methods:**

##### `to_cws_url(extension_id: str, **kwargs) -> str`

Construct Chrome Web Store download URL.

**Parameters:**
- `extension_id`: The Chrome extension ID
- `**kwargs`: Optional parameters (os, arch, nacl_arch, prodversion)

**Returns:**
- `str`: Complete Chrome Web Store download URL

##### `crx_to_zip(crx_data: bytes, output_filename: Optional[str] = None) -> str`

Convert CRX file data to ZIP format.

**Parameters:**
- `crx_data`: Raw CRX file data
- `output_filename`: Output ZIP filename (optional)

**Returns:**
- `str`: Path to the created ZIP file

##### `parse_chrome_store_url(chrome_store_url: str) -> str`

Extract extension ID from Chrome Web Store URL.

**Parameters:**
- `chrome_store_url`: Full Chrome Web Store URL

**Returns:**
- `str`: Extension ID

## Command Line Interface

### Basic Commands

```bash
# Download single extension
python chrome_extension_downloader.py <extension_id>

# Download with custom output
python chrome_extension_downloader.py <extension_id> --output <filename>

# Download to specific directory
python chrome_extension_downloader.py <extension_id> --output-dir <directory>
```

### Batch Operations

```bash
# Download multiple extensions
python chrome_extension_downloader.py --batch <id1> <id2> <id3>

# Download from file
python chrome_extension_downloader.py --from-file <file_path>
```

### Interactive Mode

```bash
# Run interactive mode
python chrome_extension_downloader.py --interactive
```

### Configuration

```bash
# Create sample config
python chrome_extension_downloader.py --create-config

# Use custom config file
python chrome_extension_downloader.py <extension_id> --config <config_file>
```

### Performance Options

```bash
# Set maximum concurrent downloads
python chrome_extension_downloader.py --batch <id1> <id2> --max-workers 5

# Disable progress indicators
python chrome_extension_downloader.py <extension_id> --no-progress
```

### Logging Options

```bash
# Verbose output
python chrome_extension_downloader.py <extension_id> --verbose

# Quiet mode
python chrome_extension_downloader.py <extension_id> --quiet

# Set log level
python chrome_extension_downloader.py <extension_id> --log-level DEBUG
```

## Examples

### Python API Examples

#### Basic Download
```python
from chrome_extension_downloader import AutoExtensionDownloader

downloader = AutoExtensionDownloader()
result = downloader.download_and_convert("gppongmhjkpfnbhagpmjfkannfbllamg")
print(f"Downloaded: {result}")
```

#### Batch Download
```python
from chrome_extension_downloader import AutoExtensionDownloader

downloader = AutoExtensionDownloader()
extension_ids = [
    "gppongmhjkpfnbhagpmjfkannfbllamg",
    "nkeimhogjdpnpccoofpliimaahmaaome"
]
results = downloader.download_multiple(extension_ids)
print(f"Downloaded {len(results)} extensions")
```

#### Custom Configuration
```python
from chrome_extension_downloader import AutoExtensionDownloader, Config

# Create custom config
config = Config("my_config.json")
config.config["download"]["max_file_size_mb"] = 200
config.config["performance"]["max_concurrent_downloads"] = 5
config.save_config()

# Use custom config
downloader = AutoExtensionDownloader(config)
```

#### Download from File
```python
from chrome_extension_downloader import AutoExtensionDownloader

downloader = AutoExtensionDownloader()
results = downloader.download_from_file("extensions.txt")
print(f"Downloaded {len(results)} extensions from file")
```

### Command Line Examples

#### Single Extension
```bash
# Basic download
python chrome_extension_downloader.py gppongmhjkpfnbhagpmjfkannfbllamg

# With custom name
python chrome_extension_downloader.py gppongmhjkpfnbhagpmjfkannfbllamg --output wappalyzer.zip

# To specific directory
python chrome_extension_downloader.py gppongmhjkpfnbhagpmjfkannfbllamg --output-dir /path/to/downloads
```

#### Batch Operations
```bash
# Multiple extensions
python chrome_extension_downloader.py --batch gppongmhjkpfnbhagpmjfkannfbllamg nkeimhogjdpnpccoofpliimaahmaaome

# From file
python chrome_extension_downloader.py --from-file extensions.txt

# With custom output directory
python chrome_extension_downloader.py --batch <id1> <id2> --output-dir /path/to/downloads
```

#### Advanced Usage
```bash
# High performance batch download
python chrome_extension_downloader.py --batch <id1> <id2> <id3> --max-workers 10 --no-progress

# Debug mode
python chrome_extension_downloader.py <extension_id> --verbose --log-level DEBUG

# Disable SSL verification (not recommended)
python chrome_extension_downloader.py <extension_id> --no-ssl-verify
```

## Error Handling

### Common Exceptions

#### `ValueError`
- Invalid extension ID format
- Download failure
- File size exceeds limit

#### `FileNotFoundError`
- Output directory doesn't exist
- Extension list file not found

#### `requests.exceptions.RequestException`
- Network connectivity issues
- HTTP errors (404, 500, etc.)
- Timeout errors

### Error Handling Example
```python
from chrome_extension_downloader import AutoExtensionDownloader
import logging

downloader = AutoExtensionDownloader()

try:
    result = downloader.download_and_convert("invalid_id")
except ValueError as e:
    print(f"Validation error: {e}")
except FileNotFoundError as e:
    print(f"File error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Advanced Features

### Caching
The tool includes a built-in caching system to avoid re-downloading the same extensions:

```python
# Enable caching (default)
config = Config()
config.config["performance"]["enable_caching"] = True
downloader = AutoExtensionDownloader(config)
```

### Rate Limiting
Built-in rate limiting to respect server resources:

```python
config = Config()
config.config["security"]["rate_limit_delay"] = 2.0  # 2 second delay
downloader = AutoExtensionDownloader(config)
```

### Progress Tracking
Real-time download progress with file size information:

```python
# Enable progress (default)
result = downloader.download_and_convert("extension_id", show_progress=True)

# Disable progress
result = downloader.download_and_convert("extension_id", show_progress=False)
```

### Logging
Comprehensive logging system with multiple levels:

```python
import logging

# Set log level
logging.getLogger().setLevel(logging.DEBUG)

# Logs are written to both console and file
# File: chrome_extension_downloader.log
```

### Extension List Files
Support for extension list files with comments:

```
# This is a comment
gppongmhjkpfnbhagpmjfkannfbllamg
nkeimhogjdpnpccoofpliimaahmaaome

# Another comment
abcdefghijklmnopqrstuvwxyzabcdef
```

## Troubleshooting

### Common Issues

1. **HTTP 204: No Content**
   - Extension may not be available for download
   - Try a different extension or check if it's a Chrome App

2. **SSL Certificate Errors**
   - Enable SSL verification in config
   - Check network/firewall settings

3. **Invalid Extension ID**
   - Extension ID must be exactly 32 characters (a-p only)
   - Check the URL format from Chrome Web Store

4. **Download Timeouts**
   - Increase timeout in configuration
   - Check network connectivity

5. **File Size Limits**
   - Increase max_file_size_mb in configuration
   - Check available disk space

### Debug Mode
Enable debug logging for detailed troubleshooting:

```bash
python chrome_extension_downloader.py <extension_id> --verbose --log-level DEBUG
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
