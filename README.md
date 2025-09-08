# Chrome Extension Downloader

A **Python 3** tool that automatically downloads Chrome extensions from the Chrome Web Store, converts them from CRX to ZIP format, and cleans up temporary files.

## 🚀 Quick Start

### **Step 1: Install Requirements (REQUIRED FIRST)**
```bash
pip install -r requirements.txt
```

### **Step 2: Download Extension**
```bash
python chrome_extension_downloader.py gppongmhjkpfnbhagpmjfkannfbllamg
```

This single command will:
1. Download the extension as a CRX file
2. Convert it to ZIP format
3. Delete the temporary CRX file
4. Give you a ready-to-use ZIP file

## 📁 Files

- **`chrome_extension_downloader.py`** - **MAIN SCRIPT** - Automated tool that downloads extensions, converts CRX to ZIP, and cleans up files automatically
- **`crx_utils.py`** - **UTILITY LIBRARY** - Core functions for URL building and CRX conversion (used by main script)
- **`requirements.txt`** - **DEPENDENCIES** - Python packages needed to run the scripts
- **`README.md`** - **DOCUMENTATION** - This file with usage instructions

## 🛠️ Usage

### **Main Script (Automated) - RECOMMENDED**

**What it does:** Downloads extension, converts CRX to ZIP, and cleans up automatically

```bash
# Basic usage - download and convert
python chrome_extension_downloader.py gppongmhjkpfnbhagpmjfkannfbllamg

# With custom output filename
python chrome_extension_downloader.py gppongmhjkpfnbhagpmjfkannfbllamg --output wappalyzer.zip

# With full output path (including directory)
python chrome_extension_downloader.py gppongmhjkpfnbhagpmjfkannfbllamg --output-path "C:\Users\test\Desktop\wappalyzer.zip"

# Keep the CRX file (don't delete it)
python chrome_extension_downloader.py gppongmhjkpfnbhagpmjfkannfbllamg --keep-crx

# Verbose output (shows detailed progress)
python chrome_extension_downloader.py gppongmhjkpfnbhagpmjfkannfbllamg --verbose
```

### **Utility Script (Manual Operations) - ADVANCED**

**What it does:** Provides individual functions for URL generation and CRX conversion

```bash
# Generate download URL only (doesn't download)
python crx_utils.py --id gppongmhjkpfnbhagpmjfkannfbllamg

# Convert existing CRX file to ZIP
python crx_utils.py --convert extension.crx

# From Chrome Web Store URL
python crx_utils.py --url "https://chrome.google.com/webstore/detail/extension-name/gppongmhjkpfnbhagpmjfkannfbllamg"
```

## 📋 Requirements

- **Python 3.6+** (Python 2 is not supported)
- Required packages (see `requirements.txt`)

### **Installation (REQUIRED BEFORE USE)**

1. **Ensure you have Python 3.6+ installed**
   ```bash
   python --version  # Should show Python 3.x.x
   ```

2. **Clone or download** this repository

3. **Install dependencies FIRST:**
   ```bash
   pip install -r requirements.txt
   ```

   Or install manually:
   ```bash
   pip install requests urllib3
   ```

**⚠️ Important:** 
- You must have **Python 3.6+** installed
- You must install the requirements before running any scripts!

## 🔍 How to Find Extension IDs

1. Go to the Chrome Web Store
2. Find the extension you want
3. Look at the URL: `https://chrome.google.com/webstore/detail/extension-name/EXTENSION_ID`
4. The 32-character string at the end is the Extension ID

**Example:**
- URL: `https://chrome.google.com/webstore/detail/wappalyzer-technology-profiler/gppongmhjkpfnbhagpmjfkannfbllamg`
- Extension ID: `gppongmhjkpfnbhagpmjfkannfbllamg`

## ⚙️ Features

- **Automatic Download**: Downloads CRX files directly from Google's servers
- **CRX to ZIP Conversion**: Converts Chrome extension files to standard ZIP format
- **Auto Cleanup**: Removes temporary CRX files after conversion
- **Progress Indicators**: Shows download progress and file information
- **Error Handling**: Graceful error handling with cleanup
- **Platform Detection**: Auto-detects your system (Windows, macOS, Linux)
- **Multiple Formats**: Supports both CRX2 and CRX3 formats

## 🎯 Examples

### **Download Wappalyzer Extension (Complete Process)**
```bash
# Step 1: Check Python version (should be 3.6+)
python --version

# Step 2: Install requirements (if not done already)
pip install -r requirements.txt

# Step 3: Download and convert extension
python chrome_extension_downloader.py gppongmhjkpfnbhagpmjfkannfbllamg
```

### **Download with Custom Name**
```bash
python chrome_extension_downloader.py gppongmhjkpfnbhagpmjfkannfbllamg --output wappalyzer.zip
```

### **Download to Specific Directory**
```bash
python chrome_extension_downloader.py gppongmhjkpfnbhagpmjfkannfbllamg --output-path "C:\Users\test\Desktop\wappalyzer.zip"
```

### **Convert Existing CRX File**
```bash
python crx_utils.py --convert downloaded_extension.crx
```

## 🔧 Technical Details

- Uses Google's internal Chrome Web Store API
- Implements the same CRX parsing logic as the official CRX Viewer
- Handles both CRX2 and CRX3 file formats
- Supports nested CRX files (Opera addons)
- Uses high Chrome version numbers to avoid 204 responses
- Includes proper SSL handling for corporate environments

## 🚨 Troubleshooting

**"HTTP 204: No Content" Error:**
- Some extensions may not be available for direct download
- Try a different extension or check if it's a Chrome App (not extension)

**"Invalid extension ID format" Error:**
- Extension ID must be exactly 32 characters (a-p only)
- Check the URL format from Chrome Web Store

**SSL Certificate Errors:**
- The script automatically handles SSL verification issues
- If problems persist, check your network/firewall settings

## 📝 License

This tool is for educational and personal use. Please respect Chrome Web Store terms of service and extension developers' rights.

## 🤝 Contributing

Feel free to submit issues or pull requests to improve this tool.

---

**Note:** This tool replicates the functionality of the CRX Viewer extension and uses the same underlying logic for reliable CRX to ZIP conversion.
