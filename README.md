# Python Utility Tools

A collection of useful Python utilities for everyday tasks.

## Quick Start

The easiest way to get started is to use the setup script and utility launcher:

```bash
# Set up the environment and install dependencies
python setup.py

# Launch the utilities menu
python utils_launcher.py
```

## Setup Instructions

### 1. Create a Virtual Environment (recommended)

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

For specific utilities, you may need to uncomment the relevant dependencies in the requirements.txt file.

## Utility Launcher

The `utils_launcher.py` script provides a simple menu interface to launch any of the utilities:

```bash
python utils_launcher.py
```

This will display an interactive menu of all available utilities, check for dependencies, and launch your selection.

## Available Utilities

### Pomodoro Timer (`pomodoro_timer.py`)

A productivity tool implementing the Pomodoro Technique with focus tracking and statistics.

**Features:**
- Customizable work and break durations
- Desktop notifications
- Focus tracking with visualization
- Weekly statistics report

**Dependencies:**
- tkinter (built-in with most Python installations)
- matplotlib
- plyer (for notifications)

**Usage:**
```bash
python pomodoro_timer.py
```

### Login Camera (`login_camera.py`)

A security tool that captures a photo using your webcam when someone logs into your computer.

**Features:**
- Automatically takes and saves photos with timestamps
- Optional email notifications with captured images
- Configurable settings (webcam index, capture delay, etc.)
- Test mode for ensuring proper setup

**Dependencies:**
- opencv-python (for webcam access)
- smtplib (built-in for email functionality)

**Usage:**
```bash
# Normal usage (capture on login)
python login_camera.py

# Generate configuration file and exit
python login_camera.py --setup

# Test camera without sending email
python login_camera.py --test
```

### Keyboard Activity Monitor (`keyboard_monitor.py`)

Tracks and analyzes your keyboard usage patterns without recording the actual keys pressed.

**Features:**
- Records keypress statistics over time
- Graphical visualization of activity by hour
- Generates text reports of usage patterns
- Can run silently in the background

**Dependencies:**
- pynput (for keyboard monitoring)
- pandas (for data handling)
- matplotlib (for visualization)
- tkinter (for GUI)

**Usage:**
```bash
# Launch GUI interface
python keyboard_monitor.py --gui

# Start monitoring in background
python keyboard_monitor.py --start

# Stop monitoring
python keyboard_monitor.py --stop

# Generate activity report
python keyboard_monitor.py --report
```

### Global Time Dashboard (`global_time.py`)

Display and manage times across different time zones with an intuitive interface.

**Features:**
- Real-time display of current time in multiple cities
- Meeting planner tool to check working hours across time zones
- Customizable city list with color coding
- Both GUI and CLI interfaces

**Dependencies:**
- pytz (for timezone handling)
- tkinter (for GUI)

**Usage:**
```bash
# Launch GUI dashboard
python global_time.py

# Show times in command line
python global_time.py --cli
```

### PDF Tools (`pdf_tools.py`)

A set of tools for working with PDF files without requiring external software.

**Features:**
- Merge multiple PDFs into a single file
- Split a PDF into individual page files
- Extract specific pages from a PDF
- Extract text content from PDF files

**Dependencies:**
- PyPDF2 (for PDF manipulation)

**Usage:**
```bash
# Merge multiple PDFs
python pdf_tools.py merge file1.pdf file2.pdf file3.pdf -o merged.pdf

# Split a PDF into individual pages
python pdf_tools.py split document.pdf -o output_folder

# Extract specific pages
python pdf_tools.py extract document.pdf "1,3,5-7" -o extracted.pdf

# Extract text from a PDF
python pdf_tools.py text document.pdf -o document_text.txt
```

## Installation Troubleshooting

### Common Issues:

1. **Missing tkinter:**
   - Windows: Reinstall Python with the "tcl/tk and IDLE" option checked
   - Linux: `sudo apt-get install python3-tk` (Ubuntu/Debian)
   - macOS: Use the Python.org installer which includes tkinter

2. **Matplotlib errors:**
   - Make sure you have a C++ compiler installed if building from source
   - On Windows, use `pip install matplotlib` directly instead of building

3. **Notification issues:**
   - The app will fall back to tkinter message boxes if plyer isn't installed correctly
   - On Linux, make sure you have a notification daemon running

4. **Webcam access issues:**
   - Make sure your webcam is not being used by another application
   - On Linux, you may need to install v4l2 (`sudo apt-get install v4l-utils`)
   - On macOS, ensure your application has camera permissions in System Preferences

5. **Keyboard monitoring issues:**
   - On macOS, you may need to grant accessibility permissions
   - On Linux, the pynput library may require X server (`sudo apt-get install python3-xlib`)

### Virtual Environment Tips:

- Always use a virtual environment to avoid conflicts with system packages
- If you see "command not found" errors with pip or python, make sure your virtual environment is activated
- Use `pip list` to verify installed packages
