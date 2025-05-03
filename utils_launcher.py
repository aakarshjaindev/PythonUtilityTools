#!/usr/bin/env python
"""
Python Utilities Launcher
------------------------
This script provides a simple launcher for all the Python utilities in this collection.
It displays a menu of available utilities and launches the selected one.
"""

import os
import sys
import subprocess
import importlib.util
import platform

# Define available utilities and their descriptions
UTILITIES = [
    {
        "name": "Pomodoro Timer",
        "file": "pomodoro_timer.py",
        "description": "Productivity timer with focus tracking and statistics",
        "requirements": ["tkinter", "matplotlib", "plyer"]
    },
    {
        "name": "Login Camera",
        "file": "login_camera.py",
        "description": "Capture webcam photos on login for security",
        "requirements": ["cv2"]
    },
    {
        "name": "Keyboard Activity Monitor",
        "file": "keyboard_monitor.py",
        "description": "Track and analyze keyboard usage patterns",
        "requirements": ["pynput", "matplotlib", "pandas"]
    },
    {
        "name": "Global Time Dashboard",
        "file": "global_time.py",
        "description": "Display and manage times across different time zones",
        "requirements": ["pytz", "tkinter"]
    },
    {
        "name": "PDF Tools",
        "file": "pdf_tools.py",
        "description": "Tools for working with PDF files",
        "requirements": ["PyPDF2"]
    }
]

def clear_screen():
    """Clear the terminal screen"""
    # Check the operating system
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

def print_colored(text, color="white"):
    """Print colored text"""
    colors = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
        "white": "\033[97m",
        "reset": "\033[0m"
    }
    
    # Only use colors on compatible terminals
    if sys.platform == "win32" and not os.environ.get("TERM"):
        print(text)
    else:
        print(f"{colors.get(color, colors['white'])}{text}{colors['reset']}")

def check_dependencies(requirements):
    """Check if the required modules are installed"""
    missing = []
    for module in requirements:
        if not importlib.util.find_spec(module):
            missing.append(module)
    return missing

def print_header():
    """Print the application header"""
    clear_screen()
    print_colored("==================================", "blue")
    print_colored("   PYTHON UTILITIES LAUNCHER", "cyan")
    print_colored("==================================", "blue")
    print_colored("A collection of useful Python utilities for everyday tasks\n", "green")

def print_menu():
    """Print the available utilities menu"""
    print_colored("Available utilities:", "yellow")
    
    for i, utility in enumerate(UTILITIES, 1):
        # Check if the utility file exists
        file_exists = os.path.exists(utility["file"])
        status = "✓" if file_exists else "✗"
        status_color = "green" if file_exists else "red"
        
        print_colored(f"{i}. [{status}] {utility['name']}", "cyan")
        print_colored(f"   {utility['description']}", "white")
        
        if not file_exists:
            print_colored(f"   File not found: {utility['file']}", "red")
        
        print()
    
    print_colored("0. Exit", "magenta")
    print()

def run_utility(utility):
    """Run the selected utility"""
    # Check if the utility file exists
    if not os.path.exists(utility["file"]):
        print_colored(f"Error: {utility['file']} not found!", "red")
        input("Press Enter to continue...")
        return False
    
    # Check dependencies
    missing_deps = check_dependencies(utility["requirements"])
    if missing_deps:
        print_colored(f"Error: Missing dependencies: {', '.join(missing_deps)}", "red")
        print_colored("Please install the required dependencies:", "yellow")
        print_colored(f"pip install {' '.join(missing_deps)}", "green")
        input("Press Enter to continue...")
        return False
    
    # Run the utility
    print_colored(f"Running {utility['name']}...\n", "green")
    
    try:
        if platform.system() == "Windows":
            subprocess.run(["python", utility["file"]])
        else:
            subprocess.run(["python3", utility["file"]])
        return True
    except Exception as e:
        print_colored(f"Error running {utility['name']}: {e}", "red")
        input("Press Enter to continue...")
        return False

def main():
    """Main function"""
    while True:
        print_header()
        print_menu()
        
        choice = input("Select an option (0-5): ")
        
        if choice == "0":
            print_colored("Goodbye!", "green")
            break
            
        try:
            choice = int(choice)
            if 1 <= choice <= len(UTILITIES):
                run_utility(UTILITIES[choice - 1])
            else:
                print_colored("Invalid choice. Please try again.", "red")
                input("Press Enter to continue...")
        except ValueError:
            print_colored("Invalid input. Please enter a number.", "red")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main() 