#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Chrome Extension Downloader - MAIN SCRIPT
Automated tool that downloads Chrome extensions, converts CRX to ZIP, and cleans up automatically.

This is the main script you should use for downloading Chrome extensions.
"""

import argparse
import requests
import sys
import os
import re
import urllib3
import logging
import json
import time
from pathlib import Path
from typing import Optional, List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from crx_utils import ChromeWebStoreURLBuilder

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('chrome_extension_downloader.log')
    ]
)
logger = logging.getLogger(__name__)

# Only disable SSL warnings if explicitly configured
# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Config:
    """Configuration management for the extension downloader"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.default_config = {
            "download": {
                "max_file_size_mb": 100,
                "timeout_seconds": 30,
                "retry_attempts": 3,
                "retry_delay_seconds": 2,
                "verify_ssl": True,
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            },
            "output": {
                "default_directory": "./downloads",
                "auto_cleanup": True,
                "create_subdirectories": True
            },
            "performance": {
                "max_concurrent_downloads": 3,
                "chunk_size": 8192,
                "enable_caching": True,
                "cache_directory": "./cache"
            },
            "security": {
                "validate_extension_id": True,
                "check_file_integrity": True,
                "rate_limit_delay": 1.0
            }
        }
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                # Merge with defaults for any missing keys
                return self._merge_configs(self.default_config, config)
            except Exception as e:
                logger.warning(f"Failed to load config file: {e}. Using defaults.")
        return self.default_config.copy()
    
    def _merge_configs(self, default: Dict, user: Dict) -> Dict:
        """Recursively merge user config with defaults"""
        result = default.copy()
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        return result
    
    def save_config(self):
        """Save current configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            logger.info(f"Configuration saved to {self.config_file}")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")

class AutoExtensionDownloader:
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.url_builder = ChromeWebStoreURLBuilder()
        self.session = requests.Session()
        self._setup_session()
        self.download_cache = {}
        
    def _setup_session(self):
        """Setup HTTP session with proper configuration"""
        self.session.headers.update({
            "User-Agent": self.config.config["download"]["user_agent"],
            "Referer": "https://chrome.google.com",
            "Accept": "application/octet-stream,application/x-chrome-extension,*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        })
        
        # Configure SSL verification
        verify_ssl = self.config.config["download"]["verify_ssl"]
        self.session.verify = verify_ssl
        if not verify_ssl:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            logger.warning("SSL verification disabled - this is not recommended for production use")
    
    def validate_extension_id(self, extension_id: str) -> bool:
        """Validate Chrome extension ID format"""
        if not isinstance(extension_id, str):
            return False
        return bool(re.match(r'^[a-p]{32}$', extension_id))
    
    def get_extension_metadata(self, extension_id: str) -> Dict[str, Any]:
        """Get extension metadata from Chrome Web Store"""
        try:
            # Try to get metadata from Chrome Web Store API
            metadata_url = f"https://chrome.google.com/webstore/detail/dummy/{extension_id}"
            response = self.session.get(metadata_url, timeout=self.config.config["download"]["timeout_seconds"])
            
            # This is a simplified approach - in reality, you'd need to parse the HTML
            # or use a proper Chrome Web Store API if available
            return {
                "id": extension_id,
                "name": f"Extension {extension_id}",
                "version": "Unknown",
                "description": "Metadata extraction not fully implemented"
            }
        except Exception as e:
            logger.warning(f"Failed to get metadata for {extension_id}: {e}")
            return {
                "id": extension_id,
                "name": f"Extension {extension_id}",
                "version": "Unknown",
                "description": "Metadata unavailable"
            }
    
    def download_and_convert(self, extension_id: str, output_filename: Optional[str] = None, 
                           cleanup: bool = True, show_progress: bool = True) -> str:
        """
        Download CRX file, convert to ZIP, and optionally clean up
        
        Args:
            extension_id (str): Chrome extension ID
            output_filename (str): Output ZIP filename (optional)
            cleanup (bool): Whether to delete the CRX file after conversion
            show_progress (bool): Whether to show download progress
        
        Returns:
            str: Path to the final ZIP file
            
        Raises:
            ValueError: If extension ID is invalid or download fails
            FileNotFoundError: If output directory doesn't exist
        """
        # Validate extension ID
        if self.config.config["security"]["validate_extension_id"]:
            if not self.validate_extension_id(extension_id):
                raise ValueError(f"Invalid extension ID format: {extension_id}. Must be 32 characters (a-p only)")
        
        # Get extension metadata
        metadata = self.get_extension_metadata(extension_id)
        logger.info(f"Downloading extension: {metadata['name']} ({extension_id})")
        
        try:
            # Generate download URL
            download_url = self.url_builder.to_cws_url(extension_id)
            logger.debug(f"Download URL: {download_url}")
            
            # Setup output directory
            output_dir = Path(self.config.config["output"]["default_directory"])
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate filenames
            if not output_filename:
                safe_name = "".join(c for c in metadata['name'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
                safe_name = safe_name.replace(' ', '_') if safe_name else extension_id
                output_filename = f"{safe_name}_{extension_id}.zip"
            
            # Ensure output filename has .zip extension
            if not output_filename.endswith('.zip'):
                output_filename += '.zip'
            
            output_path = output_dir / output_filename
            crx_filename = output_dir / f"{extension_id}.crx"
            
            # Check cache first
            if self.config.config["performance"]["enable_caching"]:
                cache_key = f"{extension_id}_{hash(download_url)}"
                if cache_key in self.download_cache:
                    logger.info("Using cached download")
                    crx_data = self.download_cache[cache_key]
                else:
                    crx_data = self._download_crx(download_url, show_progress)
                    if crx_data:
                        self.download_cache[cache_key] = crx_data
            else:
                crx_data = self._download_crx(download_url, show_progress)
            
            if not crx_data:
                raise ValueError("Failed to download CRX file")
            
            # Validate file size
            max_size = self.config.config["download"]["max_file_size_mb"] * 1024 * 1024
            if len(crx_data) > max_size:
                raise ValueError(f"File too large: {self._format_size(len(crx_data))} > {self._format_size(max_size)}")
            
            # Save CRX file temporarily
            with open(crx_filename, 'wb') as f:
                f.write(crx_data)
            
            logger.info(f"CRX file saved: {crx_filename} ({self._format_size(len(crx_data))})")
            
            # Convert to ZIP
            logger.info(f"Converting to ZIP: {output_path}")
            zip_file = self.url_builder.crx_to_zip(crx_data, str(output_path))
            
            # Validate ZIP file integrity
            if self.config.config["security"]["check_file_integrity"]:
                self._validate_zip_integrity(zip_file)
            
            # Clean up CRX file if requested
            if cleanup and self.config.config["output"]["auto_cleanup"]:
                logger.info(f"Cleaning up CRX file: {crx_filename}")
                os.remove(crx_filename)
                logger.info("CRX file deleted")
            
            logger.info(f"✅ Success! Extension downloaded and converted to: {zip_file}")
            return zip_file
            
        except Exception as e:
            # Clean up CRX file on error if it exists
            crx_filename = output_dir / f"{extension_id}.crx"
            if crx_filename.exists():
                logger.info(f"Cleaning up CRX file after error: {crx_filename}")
                os.remove(crx_filename)
            logger.error(f"Download failed for {extension_id}: {e}")
            raise e
    
    def _validate_zip_integrity(self, zip_file: str):
        """Validate ZIP file integrity"""
        try:
            import zipfile
            with zipfile.ZipFile(zip_file, 'r') as zf:
                # Test the ZIP file
                bad_file = zf.testzip()
                if bad_file:
                    raise ValueError(f"ZIP file integrity check failed: {bad_file}")
            logger.debug("ZIP file integrity check passed")
        except Exception as e:
            logger.error(f"ZIP integrity validation failed: {e}")
            raise
    
    def _download_crx(self, download_url: str, show_progress: bool = True) -> Optional[bytes]:
        """Download CRX file from URL with retry logic and progress indication"""
        max_retries = self.config.config["download"]["retry_attempts"]
        retry_delay = self.config.config["download"]["retry_delay_seconds"]
        timeout = self.config.config["download"]["timeout_seconds"]
        chunk_size = self.config.config["performance"]["chunk_size"]
        
        for attempt in range(max_retries):
            try:
                logger.debug(f"Download attempt {attempt + 1}/{max_retries} for {download_url}")
                
                # Rate limiting
                if attempt > 0:
                    time.sleep(retry_delay * attempt)
                
                response = self.session.get(
                    download_url, 
                    stream=True, 
                    timeout=timeout,
                    verify=self.config.config["download"]["verify_ssl"]
                )
                
                if response.status_code == 204:
                    logger.warning("HTTP 204: No Content - Extension may not be available for download")
                    return None
                elif response.status_code != 200:
                    raise ValueError(f"HTTP Error {response.status_code}: {response.reason}")
                
                # Check content type
                content_type = response.headers.get('content-type', '').lower()
                if 'text/html' in content_type:
                    logger.warning("Received HTML instead of CRX file - extension may not be available")
                    logger.debug(f"Response content preview: {response.text[:200]}")
                    return None
                
                # Get file size if available
                content_length = response.headers.get('content-length')
                file_size = int(content_length) if content_length else None
                
                if file_size:
                    logger.info(f"File size: {self._format_size(file_size)}")
                
                # Download the file with progress indication
                downloaded_bytes = 0
                crx_data = b''
                
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        crx_data += chunk
                        downloaded_bytes += len(chunk)
                        
                        if show_progress and file_size:
                            progress = (downloaded_bytes / file_size) * 100
                            print(f"\rDownloading... {progress:.1f}% ({self._format_size(downloaded_bytes)}/{self._format_size(file_size)})", 
                                  end='', flush=True)
                
                if show_progress:
                    print()  # New line after progress
                
                logger.info(f"Download completed: {self._format_size(downloaded_bytes)}")
                return crx_data
                
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout on attempt {attempt + 1}/{max_retries}")
                if attempt == max_retries - 1:
                    raise ValueError(f"Download timeout after {max_retries} attempts")
            except requests.exceptions.ConnectionError as e:
                logger.warning(f"Connection error on attempt {attempt + 1}/{max_retries}: {e}")
                if attempt == max_retries - 1:
                    raise ValueError(f"Connection failed after {max_retries} attempts: {e}")
            except Exception as e:
                logger.error(f"Download error on attempt {attempt + 1}/{max_retries}: {e}")
                if attempt == max_retries - 1:
                    raise e
        
        return None
    
    def download_multiple(self, extension_ids: List[str], output_dir: Optional[str] = None, 
                         max_workers: Optional[int] = None) -> Dict[str, str]:
        """
        Download multiple extensions concurrently
        
        Args:
            extension_ids (List[str]): List of Chrome extension IDs
            output_dir (str): Output directory (optional)
            max_workers (int): Maximum concurrent downloads (optional)
        
        Returns:
            Dict[str, str]: Mapping of extension_id to output_file_path
        """
        if not extension_ids:
            return {}
        
        # Validate all extension IDs first
        invalid_ids = [eid for eid in extension_ids if not self.validate_extension_id(eid)]
        if invalid_ids:
            raise ValueError(f"Invalid extension IDs: {invalid_ids}")
        
        # Setup output directory
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            # Temporarily update config
            original_dir = self.config.config["output"]["default_directory"]
            self.config.config["output"]["default_directory"] = str(output_path)
        
        max_workers = max_workers or self.config.config["performance"]["max_concurrent_downloads"]
        results = {}
        failed_downloads = []
        
        logger.info(f"Starting batch download of {len(extension_ids)} extensions with {max_workers} workers")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all download tasks
            future_to_id = {
                executor.submit(self.download_and_convert, ext_id, show_progress=False): ext_id 
                for ext_id in extension_ids
            }
            
            # Process completed downloads
            for future in as_completed(future_to_id):
                ext_id = future_to_id[future]
                try:
                    result = future.result()
                    results[ext_id] = result
                    logger.info(f"✅ Downloaded: {ext_id} -> {result}")
                except Exception as e:
                    failed_downloads.append((ext_id, str(e)))
                    logger.error(f"❌ Failed to download {ext_id}: {e}")
        
        # Restore original output directory
        if output_dir:
            self.config.config["output"]["default_directory"] = original_dir
        
        # Report results
        logger.info(f"Batch download completed: {len(results)} successful, {len(failed_downloads)} failed")
        if failed_downloads:
            logger.warning("Failed downloads:")
            for ext_id, error in failed_downloads:
                logger.warning(f"  - {ext_id}: {error}")
        
        return results
    
    def download_from_file(self, file_path: str, output_dir: Optional[str] = None) -> Dict[str, str]:
        """
        Download extensions from a text file containing extension IDs (one per line)
        
        Args:
            file_path (str): Path to file containing extension IDs
            output_dir (str): Output directory (optional)
        
        Returns:
            Dict[str, str]: Mapping of extension_id to output_file_path
        """
        try:
            with open(file_path, 'r') as f:
                extension_ids = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
            if not extension_ids:
                logger.warning(f"No valid extension IDs found in {file_path}")
                return {}
            
            logger.info(f"Found {len(extension_ids)} extension IDs in {file_path}")
            return self.download_multiple(extension_ids, output_dir)
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Extension list file not found: {file_path}")
        except Exception as e:
            raise ValueError(f"Error reading extension list file: {e}")
    
    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def create_sample_config():
    """Create a sample configuration file"""
    config = Config()
    config.save_config()
    print(f"Sample configuration file created: {config.config_file}")
    print("Edit this file to customize download settings.")

def interactive_mode():
    """Interactive mode for non-technical users"""
    print("🔧 Chrome Extension Downloader - Interactive Mode")
    print("=" * 50)
    
    while True:
        print("\nOptions:")
        print("1. Download single extension")
        print("2. Download multiple extensions")
        print("3. Download from file")
        print("4. Create sample config")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            extension_id = input("Enter extension ID: ").strip()
            if extension_id:
                try:
                    downloader = AutoExtensionDownloader()
                    result = downloader.download_and_convert(extension_id)
                    print(f"✅ Success! Downloaded to: {result}")
                except Exception as e:
                    print(f"❌ Error: {e}")
        
        elif choice == '2':
            print("Enter extension IDs (one per line, empty line to finish):")
            extension_ids = []
            while True:
                ext_id = input().strip()
                if not ext_id:
                    break
                extension_ids.append(ext_id)
            
            if extension_ids:
                try:
                    downloader = AutoExtensionDownloader()
                    results = downloader.download_multiple(extension_ids)
                    print(f"✅ Downloaded {len(results)} extensions successfully!")
                except Exception as e:
                    print(f"❌ Error: {e}")
        
        elif choice == '3':
            file_path = input("Enter path to file with extension IDs: ").strip()
            if file_path:
                try:
                    downloader = AutoExtensionDownloader()
                    results = downloader.download_from_file(file_path)
                    print(f"✅ Downloaded {len(results)} extensions successfully!")
                except Exception as e:
                    print(f"❌ Error: {e}")
        
        elif choice == '4':
            create_sample_config()
        
        elif choice == '5':
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice. Please try again.")

def main():
    parser = argparse.ArgumentParser(
        description='Chrome Extension Downloader - Enhanced version with batch downloads, configuration, and logging',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download single extension:
  python chrome_extension_downloader.py gppongmhjkpfnbhagpmjfkannfbllamg
  
  # Download with custom output:
  python chrome_extension_downloader.py gppongmhjkpfnbhagpmjfkannfbllamg --output wappalyzer.zip
  
  # Download multiple extensions:
  python chrome_extension_downloader.py --batch gppongmhjkpfnbhagpmjfkannfbllamg nkeimhogjdpnpccoofpliimaahmaaome
  
  # Download from file:
  python chrome_extension_downloader.py --from-file extensions.txt
  
  # Interactive mode:
  python chrome_extension_downloader.py --interactive
  
  # Create sample config:
  python chrome_extension_downloader.py --create-config
        """
    )
    
    # Input options (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument('extension_id', nargs='?', help='Chrome extension ID (32 characters)')
    input_group.add_argument('--batch', nargs='+', help='Download multiple extensions (space-separated IDs)')
    input_group.add_argument('--from-file', help='Download extensions from file (one ID per line)')
    input_group.add_argument('--interactive', action='store_true', help='Run in interactive mode')
    input_group.add_argument('--create-config', action='store_true', help='Create sample configuration file')
    
    # Output options
    parser.add_argument('--output', '-o', help='Output ZIP filename (default: auto-generated)')
    parser.add_argument('--output-dir', '-d', help='Output directory (default: ./downloads)')
    parser.add_argument('--keep-crx', action='store_true', help='Keep the CRX file after conversion (default: delete)')
    
    # Performance options
    parser.add_argument('--max-workers', type=int, help='Maximum concurrent downloads (default: 3)')
    parser.add_argument('--no-progress', action='store_true', help='Disable progress indicators')
    
    # Configuration options
    parser.add_argument('--config', help='Path to configuration file (default: config.json)')
    parser.add_argument('--no-ssl-verify', action='store_true', help='Disable SSL verification (not recommended)')
    
    # Logging options
    parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed information')
    parser.add_argument('--quiet', '-q', action='store_true', help='Suppress output except errors')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
                       default='INFO', help='Set logging level')
    
    args = parser.parse_args()
    
    # Setup logging level
    if args.quiet:
        logging.getLogger().setLevel(logging.ERROR)
    elif args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    # Handle special commands
    if args.create_config:
        create_sample_config()
        return 0
    
    if args.interactive:
        interactive_mode()
        return 0
    
    # Validate that we have some input
    if not any([args.extension_id, args.batch, args.from_file]):
        parser.print_help()
        return 1
    
    try:
        # Create configuration
        config = Config(args.config) if args.config else Config()
        
        # Override config with command line arguments
        if args.no_ssl_verify:
            config.config["download"]["verify_ssl"] = False
        if args.output_dir:
            config.config["output"]["default_directory"] = args.output_dir
        if args.max_workers:
            config.config["performance"]["max_concurrent_downloads"] = args.max_workers
        if args.keep_crx:
            config.config["output"]["auto_cleanup"] = False
        
        # Create downloader
        downloader = AutoExtensionDownloader(config)
        
        if args.verbose:
            print("🔧 Enhanced Chrome Extension Downloader")
            print("=" * 50)
            print(f"Config file: {config.config_file}")
            print(f"Output directory: {config.config['output']['default_directory']}")
            print(f"Max concurrent downloads: {config.config['performance']['max_concurrent_downloads']}")
            print(f"SSL verification: {config.config['download']['verify_ssl']}")
            print("-" * 50)
        
        # Handle different input types
        if args.extension_id:
            # Single extension download
            if not downloader.validate_extension_id(args.extension_id):
                print(f"❌ Error: Invalid extension ID format: {args.extension_id}")
                print("Extension ID must be exactly 32 characters (a-p only)")
                return 1
            
            result = downloader.download_and_convert(
                args.extension_id, 
                args.output, 
                cleanup=not args.keep_crx,
                show_progress=not args.no_progress
            )
            print(f"🎉 Success! Extension downloaded to: {result}")
            
        elif args.batch:
            # Multiple extensions download
            results = downloader.download_multiple(
                args.batch, 
                args.output_dir, 
                args.max_workers
            )
            print(f"🎉 Batch download completed: {len(results)} successful downloads")
            
        elif args.from_file:
            # Download from file
            results = downloader.download_from_file(args.from_file, args.output_dir)
            print(f"🎉 File download completed: {len(results)} successful downloads")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n⚠️ Download interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
