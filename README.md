# Chrome Extension Downloader

A **simple Python 3.7+** tool that automatically downloads Chrome extensions from the Chrome Web Store, converts them from CRX to ZIP format, with automatic SSL bypass for better compatibility.

## ✨ Features

- 🚀 **Single & Batch Downloads**: Download one or multiple extensions simultaneously
- ⚙️ **Configuration Management**: JSON-based configuration with sensible defaults
- 🔄 **Concurrent Processing**: Multi-threaded downloads with configurable limits
- 💾 **Caching System**: Avoid re-downloading the same extensions
- 📊 **Progress Tracking**: Real-time download progress with file size information
- 🔓 **Automatic SSL Bypass**: Works in corporate environments with SSL issues
- 📝 **Comprehensive Logging**: Detailed logging with multiple levels
- 🎯 **Interactive Mode**: User-friendly interface for non-technical users

## 🚀 Quick Start

### **Step 1: Install Requirements**
```bash
pip install -r requirements.txt
```

### **Step 2: Download Extension**
```bash
# Single extension
python chrome_extension_downloader.py gppongmhjkpfnbhagpmjfkannfbllamg

# Multiple extensions
python chrome_extension_downloader.py --batch gppongmhjkpfnbhagpmjfkannfbllamg nkeimhogjdpnpccoofpliimaahmaaome

# Interactive mode
python chrome_extension_downloader.py --interactive
```

This will:
1. Download the extension(s) as CRX file(s)
2. Convert to ZIP format
3. Validate file integrity
4. Clean up temporary files
5. Provide detailed progress and logging

## 📁 Project Structure

```
chrome-extension-downloader/
├── chrome_extension_downloader.py    # Main script
├── crx_utils.py                      # Core utilities for CRX handling
├── requirements.txt                  # Python dependencies
├── config.json                       # Default configuration file
├── README.md                         # This documentation
└── LICENSE                           # MIT License
```

## 🛠️ Usage

### **Command Line Interface**

#### **Single Extension Download**
```bash
# Basic download
python chrome_extension_downloader.py gppongmhjkpfnbhagpmjfkannfbllamg

# With custom output filename
python chrome_extension_downloader.py gppongmhjkpfnbhagpmjfkannfbllamg --output wappalyzer.zip

# To specific directory
python chrome_extension_downloader.py gppongmhjkpfnbhagpmjfkannfbllamg --output-dir ./my_downloads

# Keep CRX file (don't delete)
python chrome_extension_downloader.py gppongmhjkpfnbhagpmjfkannfbllamg --keep-crx

# Verbose output
python chrome_extension_downloader.py gppongmhjkpfnbhagpmjfkannfbllamg --verbose
```

#### **Batch Downloads**
```bash
# Multiple extensions
python chrome_extension_downloader.py --batch gppongmhjkpfnbhagpmjfkannfbllamg nkeimhogjdpnpccoofpliimaahmaaome

# From file (create your own extension list)
python chrome_extension_downloader.py --from-file extensions.txt

# High performance batch download
python chrome_extension_downloader.py --batch gppongmhjkpfnbhagpmjfkannfbllamg nkeimhogjdpnpccoofpliimaahmaaome --max-workers 5
```

#### **Interactive Mode**
```bash
# User-friendly interface
python chrome_extension_downloader.py --interactive
```

#### **Configuration**
```bash
# Create sample config
python chrome_extension_downloader.py --create-config

# Use custom config
python chrome_extension_downloader.py <extension_id> --config my_config.json
```


### **Utility Script (Advanced)**

```bash
# Generate download URL only
python crx_utils.py --id gppongmhjkpfnbhagpmjfkannfbllamg

# Convert existing CRX file to ZIP
python crx_utils.py --convert extension.crx

# From Chrome Web Store URL
python crx_utils.py --url "https://chrome.google.com/webstore/detail/extension-name/gppongmhjkpfnbhagpmjfkannfbllamg"

# With custom platform settings
python crx_utils.py --id gppongmhjkpfnbhagpmjfkannfbllamg --os linux --arch x86-64 --prodversion 120.0.6099.109
```

## 📋 Requirements

- **Python 3.7+** (uses modern typing features)
- Required packages (see `requirements.txt`)

### **Installation**

#### **From Source**
```bash
# Clone repository
git clone https://github.com/your-username/chrome-extension-downloader.git
cd chrome-extension-downloader

# Install dependencies
pip install -r requirements.txt
```

#### **Simple Usage**
```bash
# Just run the script directly - no installation needed!
python chrome_extension_downloader.py <extension_id>
```

## 🔍 How to Find Extension IDs

1. Go to the Chrome Web Store
2. Find the extension you want
3. Look at the URL: `https://chrome.google.com/webstore/detail/extension-name/EXTENSION_ID`
4. The 32-character string at the end is the Extension ID

**Example:**
- URL: `https://chrome.google.com/webstore/detail/wappalyzer-technology-profiler/gppongmhjkpfnbhagpmjfkannfbllamg`
- Extension ID: `gppongmhjkpfnbhagpmjfkannfbllamg`

## ⚙️ Advanced Features

### **Download Management**
- **Automatic Download**: Downloads CRX files directly from Google's servers
- **CRX to ZIP Conversion**: Converts Chrome extension files to standard ZIP format
- **Batch Processing**: Download multiple extensions simultaneously
- **Concurrent Downloads**: Multi-threaded downloads with configurable limits
- **Caching System**: Avoid re-downloading the same extensions
- **Resume Support**: Handle interrupted downloads gracefully

### **Configuration & Customization**
- **JSON Configuration**: Comprehensive configuration management
- **Environment Detection**: Auto-detects your system (Windows, macOS, Linux)
- **Custom Output**: Flexible output directory and filename options
- **Performance Tuning**: Configurable chunk sizes, timeouts, and retry logic

### **Security & Validation**
- **Automatic SSL Bypass**: Works in corporate environments with SSL issues
- **File Validation**: Extension ID format validation
- **Integrity Checks**: ZIP file integrity verification
- **Rate Limiting**: Respectful request throttling
- **Size Limits**: Configurable file size restrictions

### **User Experience**
- **Progress Tracking**: Real-time download progress with file size information
- **Interactive Mode**: User-friendly interface for non-technical users
- **Comprehensive Logging**: Detailed logging with multiple levels
- **Error Handling**: Graceful error handling with detailed messages
- **Auto Cleanup**: Removes temporary CRX files after conversion

### **Technical Features**
- **Multiple Formats**: Supports both CRX2 and CRX3 formats
- **Platform Detection**: Auto-detects your system architecture
- **Type Hints**: Full type annotation support
- **SSL Compatibility**: Automatic SSL bypass for corporate environments

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
python chrome_extension_downloader.py gppongmhjkpfnbhagpmjfkannfbllamg --output-dir ./my_downloads
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
- SSL verification is automatically disabled for better compatibility
- The script works in corporate environments with SSL restrictions

## 📝 License

This tool is for educational and personal use. Please respect Chrome Web Store terms of service and extension developers' rights.

## 🧪 Development

This is a simple, lightweight tool focused on core functionality. For development:

1. Clone the repository
2. Install requirements: `pip install -r requirements.txt`
3. Run the script: `python chrome_extension_downloader.py <extension_id>`

## 📊 Project Status

- ✅ **Core Functionality**: Download and convert extensions
- ✅ **Batch Downloads**: Multiple extensions simultaneously  
- ✅ **Configuration System**: JSON-based configuration
- ✅ **SSL Compatibility**: Automatic SSL bypass for corporate environments
- ✅ **Performance**: Concurrent downloads, caching, streaming
- ✅ **User Experience**: Interactive mode, progress tracking, logging
- ✅ **Documentation**: Complete usage documentation

## 🤝 Contributing

We welcome contributions! 

### **Development Workflow**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test your changes
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### **Reporting Issues**
- Use the GitHub issue tracker
- Include Python version, OS, and error details
- Provide steps to reproduce the issue

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Based on the CRX Viewer extension functionality
- Uses the same underlying logic for reliable CRX to ZIP conversion
- Inspired by the Chrome Web Store's internal APIs

---

**Note:** This tool replicates and enhances the functionality of the CRX Viewer extension with modern Python features and automatic SSL bypass for better compatibility.
