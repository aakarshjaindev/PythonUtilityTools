#!/usr/bin/env python
"""
Python Utilities Setup Script
----------------------------
This script helps set up the environment for the Python utilities.
It checks for Python version, creates a virtual environment if needed,
and installs the required dependencies.
"""

import os
import sys
import platform
import subprocess
import venv
import argparse

def print_colored(text, color="green"):
    """Print colored text to terminal"""
    colors = {
        "green": "\033[92m",
        "yellow": "\033[93m",
        "red": "\033[91m",
        "blue": "\033[94m",
        "end": "\033[0m"
    }
    
    # On Windows, colored output might not work in some terminals
    if platform.system() == "Windows" and not os.environ.get("TERM"):
        print(text)
    else:
        print(f"{colors.get(color, colors['green'])}{text}{colors['end']}")

def check_python_version():
    """Check if Python version is compatible (>= 3.6)"""
    min_version = (3, 6)
    current_version = sys.version_info[:2]
    
    if current_version >= min_version:
        print_colored(f"✓ Python version {sys.version.split()[0]} detected (minimum required: {min_version[0]}.{min_version[1]})")
        return True
    else:
        print_colored(f"✗ Python version {current_version[0]}.{current_version[1]} is not supported. Please use Python {min_version[0]}.{min_version[1]} or higher.", "red")
        return False

def create_venv(venv_path="venv"):
    """Create a virtual environment"""
    if os.path.exists(venv_path):
        print_colored(f"! Virtual environment already exists at '{venv_path}'", "yellow")
        return True
    
    print_colored(f"Creating virtual environment in '{venv_path}'...")
    try:
        venv.create(venv_path, with_pip=True)
        print_colored("✓ Virtual environment created successfully")
        return True
    except Exception as e:
        print_colored(f"✗ Failed to create virtual environment: {e}", "red")
        return False

def get_venv_python_path(venv_path="venv"):
    """Get path to Python in the virtual environment"""
    if platform.system() == "Windows":
        return os.path.join(venv_path, "Scripts", "python.exe")
    else:
        return os.path.join(venv_path, "bin", "python")

def get_venv_pip_path(venv_path="venv"):
    """Get path to pip in the virtual environment"""
    if platform.system() == "Windows":
        return os.path.join(venv_path, "Scripts", "pip.exe")
    else:
        return os.path.join(venv_path, "bin", "pip")

def install_dependencies(venv_path="venv", requirements_file="requirements.txt"):
    """Install dependencies from requirements.txt"""
    if not os.path.exists(requirements_file):
        print_colored(f"✗ Requirements file '{requirements_file}' not found", "red")
        return False
    
    pip_path = get_venv_pip_path(venv_path)
    
    print_colored(f"Installing dependencies from '{requirements_file}'...")
    try:
        subprocess.run([pip_path, "install", "-U", "pip"], check=True)
        subprocess.run([pip_path, "install", "-r", requirements_file], check=True)
        print_colored("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print_colored(f"✗ Failed to install dependencies: {e}", "red")
        return False

def check_available_utilities():
    """Check which utility scripts are available"""
    utilities = {
        "pomodoro_timer.py": "Pomodoro Timer",
        "login_camera.py": "Login Camera",
        "keyboard_monitor.py": "Keyboard Activity Monitor",
        "global_time.py": "Global Time Dashboard",
    }
    
    print_colored("\nAvailable utilities:", "blue")
    for script, name in utilities.items():
        if os.path.exists(script):
            print_colored(f"✓ {name} ({script})", "green")
        else:
            print_colored(f"✗ {name} ({script}) - Not found", "yellow")

def print_usage_instructions(venv_path="venv"):
    """Print instructions for using the utilities"""
    activate_cmd = f"{os.path.join(venv_path, 'Scripts', 'activate')}" if platform.system() == "Windows" else f"source {os.path.join(venv_path, 'bin', 'activate')}"
    
    print_colored("\nUsage Instructions:", "blue")
    print_colored("1. Activate the virtual environment:")
    print_colored(f"   {activate_cmd}", "yellow")
    print_colored("2. Run a utility with Python, for example:")
    print_colored("   python pomodoro_timer.py", "yellow")
    print_colored("3. See README.md for detailed usage instructions for each utility.")

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Setup script for Python utilities")
    parser.add_argument("--venv-path", default="venv", help="Path for the virtual environment")
    parser.add_argument("--requirements", default="requirements.txt", help="Path to requirements file")
    parser.add_argument("--no-venv", action="store_true", help="Skip virtual environment creation")
    parser.add_argument("--no-deps", action="store_true", help="Skip dependency installation")
    return parser.parse_args()

def main():
    """Main function"""
    args = parse_arguments()
    
    print_colored("Python Utilities Setup", "blue")
    print_colored("=" * 40)
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Create virtual environment (if not skipped)
    if not args.no_venv:
        if not create_venv(args.venv_path):
            return 1
    
    # Install dependencies (if not skipped)
    if not args.no_deps and not args.no_venv:
        if not install_dependencies(args.venv_path, args.requirements):
            return 1
    
    # Check available utilities
    check_available_utilities()
    
    # Print usage instructions
    print_usage_instructions(args.venv_path)
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 