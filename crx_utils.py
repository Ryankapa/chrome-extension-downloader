#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Chrome Web Store URL Constructor
"""

import argparse
import urllib.parse
import re
import platform
import sys
import struct
import zipfile
import os

class ChromeWebStoreURLBuilder:
    def __init__(self):
        # Get platform information similar to getPlatformInfoFallback()
        self.platform_info = self._detect_platform_info()
        
        # Default values based on crxviewer implementation
        self.default_options = {
            'os': self.platform_info['os'],
            'arch': self.platform_info['arch'],
            'nacl_arch': self.platform_info['nacl_arch'],
            'prodversion': self._get_chrome_version(),
            'xid': None  # Extension ID - must be provided
        }
    
    def _detect_platform_info(self):
        """
        Detect platform information similar to getPlatformInfoFallback() in crxviewer.js
        """
        system = platform.system().lower()
        machine = platform.machine().lower()
        
        # OS detection
        if system == 'darwin':
            os_name = 'mac'
        elif system == 'windows':
            os_name = 'win'
        elif system == 'linux':
            os_name = 'linux'
        else:
            os_name = 'linux'  # Default fallback
        
        # Architecture detection
        if 'arm' in machine:
            arch = 'arm'
        elif '64' in machine or 'amd64' in machine or 'x86_64' in machine:
            arch = 'x86-64'
        else:
            arch = 'x86-32'
        
        return {
            'os': os_name,
            'arch': arch,
            'nacl_arch': arch
        }
    
    def _get_chrome_version(self):
        """
        Get Chrome version, using a high version number as fallback
        """
        # Use a high version number to avoid 204 responses
        return '9999.0.9999.0'
    
    def _is_chrome_not_chromium(self):
        """
        Weak detection of whether the user is using Chrome instead of Chromium
        """
        # In Python, we can't easily detect this, so default to chromiumcrx
        return False
    
    def get_cws_option(self, option_name):
        """Get Chrome Web Store option value"""
        return self.default_options.get(option_name, '')
    
    def to_cws_url(self, extension_id, **kwargs):
        """
        Construct Chrome Web Store download URL
        
        Args:
            extension_id (str): The Chrome extension ID
            **kwargs: Optional parameters to override defaults
                - os: Operating system
                - arch: Architecture  
                - nacl_arch: Native Client architecture
                - prodversion: Chrome product version
        
        Returns:
            str: Complete Chrome Web Store download URL
        """
        # Validate extension ID format (32 characters, a-p)
        if not re.match(r'^[a-p]{32}$', extension_id):
            raise ValueError(f"Invalid extension ID format: {extension_id}")
        
        # Update default options with any provided kwargs
        options = self.default_options.copy()
        options.update(kwargs)
        options['xid'] = extension_id
        
        # Determine product ID based on Chrome vs Chromium detection
        product_id = 'chromecrx' if self._is_chrome_not_chromium() else 'chromiumcrx'
        
        # Build the URL following the exact pattern from cws_pattern.js
        url = 'https://clients2.google.com/service/update2/crx?response=redirect'
        url += '&os=' + options['os']
        url += '&arch=' + options['arch']
        url += '&os_arch=' + options['arch']  # crbug.com/709147 - should be archName of chrome.system.cpu.getInfo
        url += '&nacl_arch=' + options['nacl_arch']
        url += '&prod=' + product_id
        url += '&prodchannel=unknown'  # Channel is "unknown" on Chromium, so using "unknown" will probably be fine for everyone
        url += '&prodversion=' + options['prodversion']
        url += '&acceptformat=crx2,crx3'
        url += '&x=id%3D' + options['xid']
        url += '%26uc'
        
        return url
    
    def crx_to_zip(self, crx_data, output_filename=None):
        """
        Convert CRX file data to ZIP format
        
        Args:
            crx_data (bytes): Raw CRX file data
            output_filename (str): Output ZIP filename (optional)
        
        Returns:
            str: Path to the created ZIP file
        """
        if not output_filename:
            output_filename = "extension.zip"
        
        try:
            # Check if it's already a ZIP file (starts with PK signature)
            if len(crx_data) >= 4 and crx_data[:4] == b'PK\x03\x04':
                print("Input is already a ZIP file")
                with open(output_filename, 'wb') as f:
                    f.write(crx_data)
                return output_filename
            
            # Check CRX magic number "Cr24" (67, 114, 50, 52)
            if len(crx_data) < 8 or crx_data[:4] != b'Cr24':
                # Try to find ZIP signature within the data
                zip_data = self._find_zip_in_data(crx_data)
                if zip_data:
                    with open(output_filename, 'wb') as f:
                        f.write(zip_data)
                    return output_filename
                else:
                    raise ValueError("Invalid CRX file: Does not start with Cr24")
            
            # Parse CRX version (byte 4)
            version = crx_data[4]
            if version not in [2, 3]:
                raise ValueError(f"Unexpected CRX format version: {version}")
            
            print(f"CRX Version: {version}")
            
            zip_start_offset = 0
            if version == 2:
                # CRX2 format
                zip_start_offset = self._parse_crx2_header(crx_data)
            else:
                # CRX3 format  
                zip_start_offset = self._parse_crx3_header(crx_data)
            
            if zip_start_offset >= len(crx_data):
                raise ValueError("CRX file appears to be corrupted")
            
            # Extract ZIP data
            zip_data = crx_data[zip_start_offset:]
            
            # Check for nested CRX (Opera addons sometimes do this)
            if (version == 3 and len(zip_data) >= 4 and 
                zip_data[:4] == b'Cr24'):
                print("Found nested CRX, extracting inner ZIP...")
                return self.crx_to_zip(zip_data, output_filename)
            
            # Write ZIP file
            with open(output_filename, 'wb') as f:
                f.write(zip_data)
            
            # Verify it's a valid ZIP file
            try:
                with zipfile.ZipFile(output_filename, 'r') as zf:
                    file_list = zf.namelist()
                    print(f"Successfully converted to ZIP with {len(file_list)} files")
                    print("Files in extension:")
                    for file_name in file_list[:10]:  # Show first 10 files
                        print(f"  - {file_name}")
                    if len(file_list) > 10:
                        print(f"  ... and {len(file_list) - 10} more files")
            except zipfile.BadZipFile:
                print("Warning: Created file doesn't appear to be a valid ZIP file")
            
            file_size = os.path.getsize(output_filename)
            print(f"ZIP file size: {self._format_size(file_size)}")
            
            return output_filename
            
        except Exception as e:
            raise ValueError(f"Error converting CRX to ZIP: {e}")
    
    def _parse_crx2_header(self, crx_data):
        """Parse CRX2 header and return ZIP start offset"""
        if len(crx_data) < 16:
            raise ValueError("CRX2 file too small")
        
        # CRX2: Magic(4) + Version(4) + PubKeyLen(4) + SigLen(4)
        pubkey_length = struct.unpack('<I', crx_data[8:12])[0]
        sig_length = struct.unpack('<I', crx_data[12:16])[0]
        
        print(f"CRX2 - Public key length: {pubkey_length}")
        print(f"CRX2 - Signature length: {sig_length}")
        
        # Validate lengths
        if pubkey_length > 10000 or sig_length > 10000:
            print("Warning: Unusual key/signature lengths, searching for ZIP signature...")
            return self._find_zip_offset(crx_data)
        
        return 16 + pubkey_length + sig_length
    
    def _parse_crx3_header(self, crx_data):
        """Parse CRX3 header and return ZIP start offset"""
        if len(crx_data) < 12:
            raise ValueError("CRX3 file too small")
        
        # CRX3: Magic(4) + Version(4) + HeaderLen(4)
        header_length = struct.unpack('<I', crx_data[8:12])[0]
        
        print(f"CRX3 - Header length: {header_length}")
        
        # Validate header length
        if header_length > 10000:
            print("Warning: Unusual header length, searching for ZIP signature...")
            return self._find_zip_offset(crx_data)
        
        return 12 + header_length
    
    def _find_zip_in_data(self, data):
        """Find ZIP signature within data"""
        # ZIP files start with PK signature (0x504B)
        zip_signatures = [b'PK\x03\x04', b'PK\x05\x06', b'PK\x07\x08']
        
        for sig in zip_signatures:
            pos = data.find(sig)
            if pos != -1:
                print(f"Found ZIP signature at position {pos}")
                return data[pos:]
        
        return None
    
    def _find_zip_offset(self, crx_data):
        """Find ZIP data offset by searching for ZIP signature"""
        zip_data = self._find_zip_in_data(crx_data)
        if zip_data:
            return len(crx_data) - len(zip_data)
        else:
            raise ValueError("No ZIP signature found in CRX file")
    
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
    
    def parse_chrome_store_url(self, chrome_store_url):
        """
        Extract extension ID from Chrome Web Store URL
        
        Args:
            chrome_store_url (str): Full Chrome Web Store URL
            
        Returns:
            str: Extension ID
        """
        try:
            parsed = urllib.parse.urlparse(chrome_store_url)
            if parsed.netloc != "chrome.google.com":
                raise ValueError("Not a valid Chrome Web Store URL")
            
            path_parts = parsed.path.split("/")
            if not (len(path_parts) == 4 and parsed.path.startswith("/webstore/detail/")):
                raise ValueError("Not a valid Chrome Web Store URL format")
            
            return path_parts[-1]  # Extension ID is the last part
            
        except Exception as e:
            raise ValueError(f"Error parsing URL: {e}")


def main():
    parser = argparse.ArgumentParser(
        description='Construct Chrome Web Store download URLs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # From extension ID:
  python crx_utils.py --id gppongmhjkpfnbhagpmjfkannfbllamg
  
  # From Chrome Web Store URL:
  python crx_utils.py --url "https://chrome.google.com/webstore/detail/extension-name/gppongmhjkpfnbhagpmjfkannfbllamg"
  
  # Convert CRX file to ZIP:
  python crx_utils.py --convert extension.crx
  
  # With custom parameters:
  python crx_utils.py --id gppongmhjkpfnbhagpmjfkannfbllamg --os linux --arch x64 --prodversion 119.0.6045.105
        """
    )
    
    # Input options (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--id', help='Chrome extension ID')
    input_group.add_argument('--url', help='Full Chrome Web Store URL')
    input_group.add_argument('--convert', help='Convert existing CRX file to ZIP')
    
    # Optional parameters
    parser.add_argument('--os', 
                       choices=['win', 'mac', 'linux', 'cros', 'openbsd', 'android'],
                       help='Operating system (auto-detected if not specified)')
    parser.add_argument('--arch',
                       choices=['arm', 'x86-64', 'x86-32'],
                       help='Architecture (auto-detected if not specified)')
    parser.add_argument('--nacl-arch',
                       choices=['arm', 'x86-64', 'x86-32'],
                       help='Native Client architecture (auto-detected if not specified)')
    parser.add_argument('--prodversion', default='9999.0.9999.0',
                       help='Chrome product version (default: 9999.0.9999.0 to avoid 204 responses)')
    parser.add_argument('--product', choices=['chromecrx', 'chromiumcrx'], default='chromiumcrx',
                       help='Product type (default: chromiumcrx)')
    
    # Output options
    parser.add_argument('--decode', action='store_true',
                       help='URL decode the final URL for readability')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Show detailed information')
    
    args = parser.parse_args()
    
    # Create URL builder
    builder = ChromeWebStoreURLBuilder()
    
    try:
        # Handle CRX to ZIP conversion
        if args.convert:
            if not os.path.exists(args.convert):
                print(f"Error: CRX file '{args.convert}' not found", file=sys.stderr)
                return 1
            
            print(f"Converting CRX file: {args.convert}")
            with open(args.convert, 'rb') as f:
                crx_data = f.read()
            
            # Generate output filename
            base_name = os.path.splitext(args.convert)[0]
            output_filename = f"{base_name}.zip"
            
            # Convert to ZIP
            zip_file = builder.crx_to_zip(crx_data, output_filename)
            print(f"\nSuccess! Converted to: {zip_file}")
            return 0
        
        # Get extension ID
        if args.id:
            extension_id = args.id
        else:
            extension_id = builder.parse_chrome_store_url(args.url)
        
        # Build URL with custom parameters
        url_kwargs = {}
        if args.os:
            url_kwargs['os'] = args.os
        if args.arch:
            url_kwargs['arch'] = args.arch
        if args.nacl_arch:
            url_kwargs['nacl_arch'] = args.nacl_arch
        if args.prodversion:
            url_kwargs['prodversion'] = args.prodversion
        
        url = builder.to_cws_url(extension_id, **url_kwargs)
        
        # Output results
        if args.verbose:
            print("Chrome Web Store URL Builder")
            print("=" * 50)
            print(f"Extension ID: {extension_id}")
            print(f"OS: {args.os or builder.default_options['os']} (auto-detected: {builder.default_options['os']})")
            print(f"Architecture: {args.arch or builder.default_options['arch']} (auto-detected: {builder.default_options['arch']})")
            print(f"NaCl Architecture: {args.nacl_arch or builder.default_options['nacl_arch']} (auto-detected: {builder.default_options['nacl_arch']})")
            print(f"Chrome Version: {args.prodversion}")
            print(f"Product: {args.product}")
            print("-" * 50)
        
        if args.decode:
            decoded_url = urllib.parse.unquote(url)
            print("Decoded URL:")
            print(decoded_url)
            print("\nEncoded URL:")
            print(url)
        else:
            print(url)
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
