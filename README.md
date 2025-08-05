# 🚀 Windows2Go

[![Version](https://img.shields.io/badge/version-3.0.0-blue.svg)](https://github.com/user/windows-togo-creator)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)
[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/)

![Application logo](https://github.com/LMLK-seal/Windows2Go/blob/main/Logo.png?raw=true)

> 💾 Windows2Go is a comprehensive, professional-grade application for creating portable, bootable Windows2Go installations on USB drives.
- This was successfully tested on a SanDisk Cruzer Blade 16GB drive using Windows 11. Performance can be better with a higher-spec USB drive and ports that support USB 3.1 or 3.2.
---

## 📋 Table of Contents

- [🎯 Features](#-features)
- [⚠️ Important Disclaimers](#️-important-disclaimers)
- [📋 Prerequisites](#-prerequisites)
- [⚡ Installation](#-installation)
- [🖥️ Usage](#️-usage)
- [🔧 Technical Details](#-technical-details)
- [📸 Screenshots](#-screenshots)
- [🛠️ Troubleshooting](#️-troubleshooting)
- [📝 License](#-license)
- [🤝 Contributing](#-contributing)

---

## 🎯 Features

### ✨ Core Functionality
- 🖱️ **Intuitive GUI** - Modern, dark-themed interface built with CustomTkinter
- 💾 **USB Drive Detection** - Automatic detection and listing of connected USB drives
- 📀 **ISO Validation** - Built-in validation for Windows ISO files
- 🔄 **Real-time Progress** - Live progress tracking with detailed logging
- ⚙️ **Smart Configuration** - Automatic settings persistence between sessions

### 🛡️ Safety Features
- 🔒 **Administrator Rights Verification** - Ensures proper permissions before execution
- ⚠️ **Multiple Warning Systems** - Clear warnings before destructive operations
- 🛑 **Emergency Stop Function** - Ability to cancel operations mid-process
- 🧹 **Automatic Cleanup** - Temporary files are automatically removed

### 🔧 Technical Capabilities
- 💿 **Professional Image Application** - Uses Microsoft DISM for Windows image deployment
- 🥾 **Dual Boot Support** - Creates boot files compatible with both BIOS and UEFI systems
- 📦 **Efficient Extraction** - 7-Zip integration for fast ISO extraction
- 💻 **Windows To Go Optimization** - Specialized for portable Windows installations

---

## 📊 Screenshot
![Screenshot](https://github.com/LMLK-seal/Windows2Go/blob/main/screenshot.png?raw=true)

## ⚠️ Important Disclaimers

### 🚨 **CRITICAL WARNING**

This tool directly manipulates disk drives and can cause **PERMANENT DATA LOSS**. Please read carefully:

- ❌ **All data on the target USB drive will be completely destroyed**
- ⚡ **A mistake can result in data loss on ANY connected drive**
- 🔧 **This creates a NON-OFFICIAL Windows To Go environment**
- 📊 **Performance and compatibility may vary**
- 🛡️ **Use at your own risk - no warranties provided**

### 🎯 **Use Cases**
- System recovery and troubleshooting
- Portable workstation environments
- Testing and development scenarios
- Emergency boot scenarios

---

## 📋 Prerequisites

### 🖥️ **System Requirements**
- **Operating System**: Windows 10 Pro/Enterprise or Windows 11 Pro/Enterprise [official website](https://www.microsoft.com/en-us/software-download/windows11)
- **Privileges**: Administrator rights required
- **Architecture**: 64-bit Windows installation
- **Memory**: Minimum 4GB RAM recommended
- **Storage**: At least 10GB free space for temporary files

### 🛠️ **Required Dependencies**

#### **7-Zip Command Line Tools** (Required)
- Download 7-Zip from [official website](https://www.7-zip.org/)
- Ensure `7z.exe` and `7z.dll` are in the same directory as the application
- Version 19.00 or later recommended

##### 📦 **How to Extract the 7z.exe Files:**
1. **Download the Stable Installer (23.01 x64):** Go to the [7-Zip Download Page](https://www.7-zip.org/) and download the very first link: **"Download .exe 64-bit Windows x64"**
   - Direct link: [`7z2301-x64.exe`](https://www.7-zip.org/a/7z2301-x64.exe)
2. **⚠️ Do NOT run the installer.** Instead, **right-click** on the downloaded `.exe` file
3. From the context menu, choose **7-Zip → Open archive**
4. A 7-Zip window will open. Inside, you will see `7z.exe` and `7z.dll`
5. Select **both** `7z.exe` and `7z.dll` and drag them into your Windows2Go project folder

> 💡 **Note**: If you don't have 7-Zip installed yet, you can use WinRAR or extract the files using PowerShell: `Expand-Archive -Path "7z2301-x64.exe" -DestinationPath "extracted"`

#### **Python Libraries**
```bash
pip install customtkinter psutil pillow pywin32
```

#### **Windows Tools** (Built-in)
- ✅ DISM (Deployment Image Servicing and Management)
- ✅ BCDBoot (Boot Configuration Data Boot)
- ✅ DiskPart (Disk Partitioning Utility)
- ✅ WMIC (Windows Management Instrumentation)

### 💿 **Compatible Windows ISOs**
- Windows 10 (all editions)
- Windows 11 (all editions)
- Windows Server 2019/2022
- Other Windows versions may work but are not tested

---

## ⚡ Installation

### 📥 **Method 1: Direct Download**
1. Download the windows2Go program.
2. Extract to your desired directory
3. Ensure 7-Zip command line tools are in the same directory
4. Run as Administrator

### 🐍 **Method 2: From Source**
```bash
# Clone the repository
git clone https://github.com/LMLK-seal/windows2Go.git
cd Windows2Go

# Install Python dependencies
pip install customtkinter psutil pillow pywin32

# Download 7-Zip command line tools
# Place 7z.exe and 7z.dll in the project directory

# Run the application
python Windows2Go.py
```

### 📦 **Method 3: Portable Installation**
1. Create a dedicated folder (e.g., `C:\windows2Go`)
2. Place all files in this folder
3. Create a desktop shortcut with "Run as administrator" enabled

---

## 🖥️ Usage

### 🚀 **Quick Start Guide**

#### **Step 1: Launch Application**
- Right-click on `Windows2Go.py` → "Run as administrator"
- Or use the provided batch file if available

#### **Step 2: Select Windows ISO** 📀
- Click **Browse** to select your Windows ISO file
- The application will validate the file size and format
- Supported formats: `.iso` files only

#### **Step 3: Choose Target USB Drive** 💾
- Click **Refresh** to scan for USB drives
- Select your target USB drive from the dropdown
- ⚠️ **WARNING**: All data will be permanently destroyed!

#### **Step 4: Configure Options** ⚙️
- **Partition Scheme**: MBR (currently the only supported option)
- **File System**: NTFS (recommended for Windows To Go)

#### **Step 5: Create Windows To Go Drive** 🚀
- Click **"CREATE WINDOWS TO GO DRIVE"**
- Confirm the final warning dialog
- Monitor progress through the real-time log

### ⏱️ **Expected Timeline**
- **Phase 1**: ISO Extraction (2-5 minutes)
- **Phase 2**: USB Drive Preparation (1-2 minutes)
- **Phase 3**: Windows Image Application (15-45 minutes) *longest phase*
- **Phase 4**: Boot File Creation (1-2 minutes)

**Total Time**: 20-55 minutes depending on hardware and ISO size

---

## 🔧 Technical Details

### 🏗️ **Architecture Overview**
```
Windows To Go Creator
├── 🖼️ GUI Layer (CustomTkinter)
├── 🔧 Core Logic (Threading)
├── 💾 Disk Operations (Windows APIs)
├── 📦 Image Processing (DISM)
└── 🥾 Boot Creation (BCDBoot)
```

### 🔄 **Process Flow**
1. **Validation**: ISO file and USB drive verification
2. **Extraction**: 7-Zip extracts ISO contents to temporary directory
3. **Preparation**: DiskPart formats USB drive with NTFS
4. **Application**: DISM applies Windows image to USB drive
5. **Bootloader**: BCDBoot creates boot files for BIOS/UEFI compatibility
6. **Cleanup**: Temporary files are automatically removed

### 📁 **File Structure**
```
Windows-ToGo-Creator/
├── Windows2Go.py              # Main application
├── 7z.exe                     # 7-Zip executable
├── 7z.dll                     # 7-Zip library
├── windows_togo_config.json   # Configuration file (auto-generated)
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

### 🔧 **Configuration Options**
The application automatically saves settings in `windows_togo_config.json`:
```json
{
    "last_iso_path": "C:/path/to/windows.iso",
    "partition_scheme": "MBR",
    "file_system": "NTFS"
}
```

---

## 📸 Screenshots

### 🖥️ **Main Interface**
*Modern, dark-themed interface with clear step-by-step workflow*

### 📊 **Progress Tracking**
*Real-time progress bars and detailed logging for transparency*

### ⚠️ **Safety Warnings**
*Multiple confirmation dialogs to prevent accidental data loss*

---

## 🛠️ Troubleshooting

### ❌ **Common Issues**

#### **"Administrator Rights Required"**
- **Solution**: Always run the application as Administrator
- Right-click → "Run as administrator"

#### **"7z.exe not found"**
- **Solution**: Download 7-Zip command line tools
- Place `7z.exe` and `7z.dll` in the application directory

#### **"No USB drives detected"**
- **Solution**: 
  - Ensure USB drive is properly connected
  - Try a different USB port
  - Click the "Refresh" button
  - Check if the drive appears in Windows Disk Management

#### **"USB drive is too small"**
- **Solution**: Use a larger USB drive
- Minimum recommended: 32GB for Windows 10/11
- The drive must be larger than the ISO file + additional space for Windows To Go

#### **Installation fails during image application**
- **Cause**: Corrupted ISO file or insufficient space
- **Solution**: 
  - Verify ISO file integrity
  - Try a different USB drive
  - Ensure stable USB connection

### 🔍 **Advanced Troubleshooting**

#### **Enable Detailed Logging**
The application automatically logs all operations. Check the log panel for detailed error messages.

#### **Manual Cleanup**
If the application crashes, manually delete temporary directories:
- Check `%TEMP%` for folders starting with `win-togo-`

#### **DISM Errors**
- Ensure Windows 10/11 Pro or Enterprise
- Run `DISM /Online /Cleanup-Image /RestoreHealth` as administrator
- Restart and try again

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### 📄 **Third-Party Licenses**
- **7-Zip**: GNU LGPL license
- **CustomTkinter**: MIT License
- **Windows APIs**: Microsoft License Terms

---

## 🤝 Contributing

We welcome contributions! Please see our [contributing guidelines](CONTRIBUTING.md) for details.

### 🐛 **Reporting Issues**
- Use the GitHub issue tracker
- Include detailed system information
- Provide log output when possible
- Describe steps to reproduce

### 💡 **Feature Requests**
- Check existing issues first
- Provide clear use case descriptions
- Consider backward compatibility

---

## 📞 Support

- 📚 **Documentation**: Check this README and inline code comments
- 🐛 **Bug Reports**: Use GitHub Issues
- 💬 **Discussions**: Use GitHub Discussions for general questions
- ⭐ **Show Support**: Star the repository if you find it helpful

---

## 🏆 Acknowledgments

- Microsoft for DISM, BCDBoot, and DiskPart utilities
- 7-Zip project for compression/extraction capabilities
- CustomTkinter community for the modern GUI framework
- Contributors and beta testers

---

<div align="center">

**⚡ Made with ❤️ for the Windows community ⚡**

![Windows2Go](https://img.shields.io/badge/Windows2Go-blue?style=for-the-badge&logo=windows&logoColor=white)

</div>
