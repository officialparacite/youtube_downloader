# YouTube Video and Audio Downloader

A simple GUI-based tool for downloading YouTube videos and audio in various formats.

## Key Features
- **Download YouTube videos** in multiple formats (currently supports WEBM).
- **Extract audio** in MP3 format (other formats may be added in future updates).
- **Select video quality** (720p, 1080p, etc.).
- **User-friendly GUI** interface for easy operation.

## Build Instructions
To build the project on your local machine, follow these steps:

1. Clone the repository to your local machine.
2. Install the necessary dependencies:
   ```bash
   pip install pyinstaller
   ```
3. Compile the tool using PyInstaller:
   ```bash
   pyinstaller youtube_downloader.spec
   ```

## Pre-built Windows Executable
If you prefer not to build the project yourself, you can find the pre-built Windows executable in the `dist` folder.

**Note:** Some antivirus software may flag the `.exe` file as a false positive. If this occurs, please add the `.exe` to your antivirus exclusion list to avoid blocking it.

---

Feel free to contribute or open an issue for any bugs or feature requests.