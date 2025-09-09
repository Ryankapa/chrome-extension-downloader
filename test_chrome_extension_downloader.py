#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test suite for Chrome Extension Downloader
"""

import unittest
import tempfile
import os
import json
import shutil
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from chrome_extension_downloader import AutoExtensionDownloader, Config
from crx_utils import ChromeWebStoreURLBuilder


class TestConfig(unittest.TestCase):
    """Test configuration management"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "test_config.json")
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_default_config(self):
        """Test default configuration creation"""
        config = Config(self.config_file)
        
        # Check that default config has all required sections
        self.assertIn("download", config.config)
        self.assertIn("output", config.config)
        self.assertIn("performance", config.config)
        self.assertIn("security", config.config)
        
        # Check specific default values
        self.assertTrue(config.config["download"]["verify_ssl"])
        self.assertEqual(config.config["performance"]["max_concurrent_downloads"], 3)
        self.assertEqual(config.config["output"]["default_directory"], "./downloads")
    
    def test_config_save_load(self):
        """Test saving and loading configuration"""
        config = Config(self.config_file)
        config.config["download"]["max_file_size_mb"] = 200
        
        # Save config
        config.save_config()
        self.assertTrue(os.path.exists(self.config_file))
        
        # Load config
        new_config = Config(self.config_file)
        self.assertEqual(new_config.config["download"]["max_file_size_mb"], 200)
    
    def test_config_merge(self):
        """Test configuration merging with defaults"""
        # Create partial config file
        partial_config = {
            "download": {
                "max_file_size_mb": 150
            }
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(partial_config, f)
        
        config = Config(self.config_file)
        
        # Should have custom value
        self.assertEqual(config.config["download"]["max_file_size_mb"], 150)
        # Should have default values for other settings
        self.assertTrue(config.config["download"]["verify_ssl"])
        self.assertEqual(config.config["performance"]["max_concurrent_downloads"], 3)


class TestAutoExtensionDownloader(unittest.TestCase):
    """Test the main downloader class"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "test_config.json")
        self.config = Config(self.config_file)
        self.downloader = AutoExtensionDownloader(self.config)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_validate_extension_id(self):
        """Test extension ID validation"""
        # Valid IDs
        valid_ids = [
            "gppongmhjkpfnbhagpmjfkannfbllamg",
            "abcdefghijklmnopqrstuvwxyzabcdef"
        ]
        
        for ext_id in valid_ids:
            self.assertTrue(self.downloader.validate_extension_id(ext_id))
        
        # Invalid IDs
        invalid_ids = [
            "gppongmhjkpfnbhagpmjfkannfbllam",  # Too short
            "gppongmhjkpfnbhagpmjfkannfbllamgg",  # Too long
            "gppongmhjkpfnbhagpmjfkannfbllamz",  # Invalid character 'z'
            "12345678901234567890123456789012",  # Numbers instead of letters
            "",  # Empty string
            None  # None value
        ]
        
        for ext_id in invalid_ids:
            self.assertFalse(self.downloader.validate_extension_id(ext_id))
    
    def test_get_extension_metadata(self):
        """Test extension metadata retrieval"""
        ext_id = "gppongmhjkpfnbhagpmjfkannfbllamg"
        
        with patch.object(self.downloader.session, 'get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            metadata = self.downloader.get_extension_metadata(ext_id)
            
            self.assertEqual(metadata["id"], ext_id)
            self.assertIn("name", metadata)
            self.assertIn("version", metadata)
            self.assertIn("description", metadata)
    
    def test_format_size(self):
        """Test file size formatting"""
        self.assertEqual(self.downloader._format_size(1023), "1023 B")
        self.assertEqual(self.downloader._format_size(1024), "1.0 KB")
        self.assertEqual(self.downloader._format_size(1024 * 1024), "1.0 MB")
        self.assertEqual(self.downloader._format_size(1024 * 1024 * 1024), "1.0 GB")
    
    @patch('chrome_extension_downloader.AutoExtensionDownloader._download_crx')
    @patch('chrome_extension_downloader.ChromeWebStoreURLBuilder.crx_to_zip')
    def test_download_and_convert_success(self, mock_crx_to_zip, mock_download_crx):
        """Test successful download and conversion"""
        ext_id = "gppongmhjkpfnbhagpmjfkannfbllamg"
        mock_crx_data = b"fake_crx_data"
        mock_zip_file = "test_extension.zip"
        
        mock_download_crx.return_value = mock_crx_data
        mock_crx_to_zip.return_value = mock_zip_file
        
        result = self.downloader.download_and_convert(ext_id)
        
        self.assertEqual(result, mock_zip_file)
        mock_download_crx.assert_called_once()
        mock_crx_to_zip.assert_called_once_with(mock_crx_data, unittest.mock.ANY)
    
    def test_download_and_convert_invalid_id(self):
        """Test download with invalid extension ID"""
        invalid_id = "invalid_id"
        
        with self.assertRaises(ValueError):
            self.downloader.download_and_convert(invalid_id)
    
    @patch('chrome_extension_downloader.AutoExtensionDownloader._download_crx')
    def test_download_and_convert_download_failure(self, mock_download_crx):
        """Test download failure handling"""
        ext_id = "gppongmhjkpfnbhagpmjfkannfbllamg"
        mock_download_crx.return_value = None
        
        with self.assertRaises(ValueError):
            self.downloader.download_and_convert(ext_id)
    
    def test_download_multiple_validation(self):
        """Test batch download with invalid IDs"""
        invalid_ids = ["invalid1", "gppongmhjkpfnbhagpmjfkannfbllamg", "invalid2"]
        
        with self.assertRaises(ValueError):
            self.downloader.download_multiple(invalid_ids)
    
    def test_download_from_file_nonexistent(self):
        """Test download from non-existent file"""
        with self.assertRaises(FileNotFoundError):
            self.downloader.download_from_file("nonexistent.txt")
    
    def test_download_from_file_empty(self):
        """Test download from empty file"""
        empty_file = os.path.join(self.temp_dir, "empty.txt")
        with open(empty_file, 'w') as f:
            pass
        
        result = self.downloader.download_from_file(empty_file)
        self.assertEqual(result, {})


class TestChromeWebStoreURLBuilder(unittest.TestCase):
    """Test the URL builder utility"""
    
    def setUp(self):
        self.builder = ChromeWebStoreURLBuilder()
    
    def test_validate_extension_id(self):
        """Test extension ID validation in URL builder"""
        # Valid ID
        valid_id = "gppongmhjkpfnbhagpmjfkannfbllamg"
        url = self.builder.to_cws_url(valid_id)
        self.assertIn(valid_id, url)
        
        # Invalid ID
        invalid_id = "invalid_id"
        with self.assertRaises(ValueError):
            self.builder.to_cws_url(invalid_id)
    
    def test_parse_chrome_store_url(self):
        """Test parsing Chrome Web Store URLs"""
        valid_url = "https://chrome.google.com/webstore/detail/wappalyzer-technology-profiler/gppongmhjkpfnbhagpmjfkannfbllamg"
        ext_id = self.builder.parse_chrome_store_url(valid_url)
        self.assertEqual(ext_id, "gppongmhjkpfnbhagpmjfkannfbllamg")
        
        # Invalid URL
        invalid_url = "https://example.com/not-chrome-store"
        with self.assertRaises(ValueError):
            self.builder.parse_chrome_store_url(invalid_url)
    
    def test_crx_to_zip_already_zip(self):
        """Test CRX to ZIP conversion when input is already ZIP"""
        zip_data = b'PK\x03\x04fake_zip_data'
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
        temp_file.close()
        
        try:
            result = self.builder.crx_to_zip(zip_data, temp_file.name)
            self.assertEqual(result, temp_file.name)
        finally:
            os.unlink(temp_file.name)
    
    def test_crx_to_zip_invalid_crx(self):
        """Test CRX to ZIP conversion with invalid CRX data"""
        invalid_data = b'invalid_crx_data'
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
        temp_file.close()
        
        try:
            with self.assertRaises(ValueError):
                self.builder.crx_to_zip(invalid_data, temp_file.name)
        finally:
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)


class TestIntegration(unittest.TestCase):
    """Integration tests"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "test_config.json")
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_config_and_downloader_integration(self):
        """Test that config and downloader work together"""
        config = Config(self.config_file)
        config.config["output"]["default_directory"] = self.temp_dir
        
        downloader = AutoExtensionDownloader(config)
        
        # Verify config was applied
        self.assertEqual(downloader.config.config["output"]["default_directory"], self.temp_dir)
    
    def test_extension_list_file_creation(self):
        """Test creating and using extension list file"""
        ext_list_file = os.path.join(self.temp_dir, "extensions.txt")
        
        # Create extension list file
        with open(ext_list_file, 'w') as f:
            f.write("gppongmhjkpfnbhagpmjfkannfbllamg\n")
            f.write("# This is a comment\n")
            f.write("nkeimhogjdpnpccoofpliimaahmaaome\n")
            f.write("\n")  # Empty line
        
        config = Config(self.config_file)
        downloader = AutoExtensionDownloader(config)
        
        # Test reading the file
        with patch.object(downloader, 'download_multiple') as mock_download:
            mock_download.return_value = {}
            downloader.download_from_file(ext_list_file)
            
            # Should have called download_multiple with 2 valid IDs
            mock_download.assert_called_once()
            args, kwargs = mock_download.call_args
            self.assertEqual(len(args[0]), 2)


if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestConfig))
    test_suite.addTest(unittest.makeSuite(TestAutoExtensionDownloader))
    test_suite.addTest(unittest.makeSuite(TestChromeWebStoreURLBuilder))
    test_suite.addTest(unittest.makeSuite(TestIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
