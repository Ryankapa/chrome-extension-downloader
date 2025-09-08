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
import urllib3
from crx_utils import ChromeWebStoreURLBuilder

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class AutoExtensionDownloader:
    def __init__(self):
        self.url_builder = ChromeWebStoreURLBuilder()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://chrome.google.com",
            "Accept": "application/octet-stream,application/x-chrome-extension,*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
    
    def download_and_convert(self, extension_id, output_filename=None, cleanup=True):
        """
        Download CRX file, convert to ZIP, and optionally clean up
        
        Args:
            extension_id (str): Chrome extension ID
            output_filename (str): Output ZIP filename (optional)
            cleanup (bool): Whether to delete the CRX file after conversion
        
        Returns:
            str: Path to the final ZIP file
        """
        try:
            # Generate download URL
            download_url = self.url_builder.to_cws_url(extension_id)
            print(f"Extension ID: {extension_id}")
            print(f"Download URL: {download_url}")
            
            # Generate filenames
            if not output_filename:
                output_filename = f"{extension_id}.zip"
            
            crx_filename = f"{extension_id}.crx"
            
            # Download CRX file
            print(f"Downloading CRX file: {crx_filename}")
            crx_data = self._download_crx(download_url)
            
            if not crx_data:
                raise ValueError("Failed to download CRX file")
            
            # Save CRX file temporarily
            with open(crx_filename, 'wb') as f:
                f.write(crx_data)
            
            print(f"CRX file saved: {crx_filename} ({self._format_size(len(crx_data))})")
            
            # Convert to ZIP
            print(f"Converting to ZIP: {output_filename}")
            zip_file = self.url_builder.crx_to_zip(crx_data, output_filename)
            
            # Clean up CRX file if requested
            if cleanup:
                print(f"Cleaning up CRX file: {crx_filename}")
                os.remove(crx_filename)
                print("CRX file deleted")
            
            print(f"\n✅ Success! Extension downloaded and converted to: {zip_file}")
            return zip_file
            
        except Exception as e:
            # Clean up CRX file on error if it exists
            crx_filename = f"{extension_id}.crx"
            if os.path.exists(crx_filename):
                print(f"Cleaning up CRX file after error: {crx_filename}")
                os.remove(crx_filename)
            raise e
    
    def _download_crx(self, download_url):
        """Download CRX file from URL"""
        try:
            response = requests.get(download_url, headers=self.headers, stream=True, verify=False)
            
            if response.status_code != 200:
                raise ValueError(f"HTTP Error {response.status_code}: {response.reason}")
            
            # Check content type
            content_type = response.headers.get('content-type', '').lower()
            if 'text/html' in content_type:
                print("Warning: Received HTML instead of CRX file.")
                print("Response content preview:", response.text[:200])
                return None
            
            # Get file size if available
            content_length = response.headers.get('content-length')
            if content_length:
                file_size = int(content_length)
                print(f"File size: {self._format_size(file_size)}")
            
            # Download the file
            downloaded_bytes = 0
            crx_data = b''
            
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    crx_data += chunk
                    downloaded_bytes += len(chunk)
                    if content_length:
                        progress = (downloaded_bytes / file_size) * 100
                        print(f"\rDownloading... {progress:.1f}%", end='', flush=True)
            
            print(f"\nDownload completed: {self._format_size(downloaded_bytes)}")
            return crx_data
            
        except Exception as e:
            print(f"Error downloading: {e}")
            return None
    
    def _format_size(self, size_bytes):
        """Format file size in human readable format"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def main():
    parser = argparse.ArgumentParser(
        description='Chrome Extension Downloader - MAIN SCRIPT - Downloads CRX, converts to ZIP, and cleans up automatically',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download and convert extension:
  python chrome_extension_downloader.py gppongmhjkpfnbhagpmjfkannfbllamg
  
  # With custom output filename:
  python chrome_extension_downloader.py gppongmhjkpfnbhagpmjfkannfbllamg --output wappalyzer.zip
  
  # With full output path:
  python chrome_extension_downloader.py gppongmhjkpfnbhagpmjfkannfbllamg --output-path "C:\\Users\\test\\Desktop\\wappalyzer.zip"
  
  # Keep CRX file (don't delete):
  python chrome_extension_downloader.py gppongmhjkpfnbhagpmjfkannfbllamg --keep-crx
        """
    )
    
    parser.add_argument('extension_id', help='Chrome extension ID (32 characters)')
    parser.add_argument('--output', '-o', help='Output ZIP filename (default: extension_id.zip)')
    parser.add_argument('--output-path', '-p', help='Full output path including filename (e.g., C:\\Users\\test\\Desktop\\file.zip)')
    parser.add_argument('--keep-crx', action='store_true', help='Keep the CRX file after conversion (default: delete)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed information')
    
    args = parser.parse_args()
    
    # Validate extension ID format
    if not re.match(r'^[a-p]{32}$', args.extension_id):
        print(f"Error: Invalid extension ID format: {args.extension_id}")
        print("Extension ID must be exactly 32 characters (a-p only)")
        return 1
    
    try:
        # Create downloader
        downloader = AutoExtensionDownloader()
        
        if args.verbose:
            print("Automated Chrome Extension Downloader")
            print("=" * 50)
            print(f"Extension ID: {args.extension_id}")
            if args.output_path:
                print(f"Output path: {args.output_path}")
            elif args.output:
                print(f"Output file: {args.output}")
            else:
                print(f"Output file: {args.extension_id + '.zip'}")
            print(f"Keep CRX: {args.keep_crx}")
            print("-" * 50)
        
        # Determine output filename
        output_filename = None
        if args.output_path:
            output_filename = args.output_path
        elif args.output:
            output_filename = args.output
        
        # Download and convert
        zip_file = downloader.download_and_convert(
            args.extension_id, 
            output_filename, 
            cleanup=not args.keep_crx
        )
        
        print(f"\n🎉 All done! Extension ready: {zip_file}")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    return 0


if __name__ == '__main__':
    import re
    sys.exit(main())
