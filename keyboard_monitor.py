from pynput import keyboard
import time
import datetime
import os
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk
import threading
import atexit
import argparse

class KeyboardMonitor:
    """
    Manages keyboard event listening, logging, and the Tkinter GUI for display.
    """
    def __init__(self, log_dir="keyboard_logs"):
        """
        Initializes the KeyboardMonitor.

        Sets up logging directories, loads existing data for the current day (or creates a new log structure),
        and registers a function to save data upon program exit.

        Args:
            log_dir (str, optional): The directory where log files will be stored.
                                     Defaults to "keyboard_logs".
        """
        # Create logging directories
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Current date for logging
        self.today = datetime.datetime.now().strftime("%Y-%m-%d") # Get current date for log file naming
        self.log_file = os.path.join(self.log_dir, f"keyboard_log_{self.today}.json") # Construct full log file path
        
        # Load existing data or create new log structure
        self.data = self.load_data() # Load data or initialize new structure
        
        # For keyboard monitoring
        self.listener = None  # pynput keyboard listener instance
        self.is_running = False  # Flag to indicate if monitoring is active
        self.start_time = None  # Timestamp when monitoring started (not currently used in this snippet but good for context)
        
        # For GUI
        self.root = None  # Tkinter root window (will be set if GUI is used)
        self.stats_thread = None  # Thread for updating GUI statistics (if GUI is used)
        
        # Make sure to save when the program exits
        atexit.register(self.save_data)  # Ensure data is saved when the program exits gracefully
        
    def load_data(self):
        """
        Loads keyboard activity data for the current day from a JSON file.
        If the file doesn't exist or is corrupted, it initializes a new data structure.

        The data structure includes:
        - "hourly_counts": A dictionary mapping each hour (0-23) to keystroke counts.
        - "total_count": Total keystrokes for the day.
        - "start_time": ISO format timestamp of when logging for this data structure began.
        - "keystrokes": A list of ISO format timestamps for each keystroke (actual keys are not logged).

        Returns:
            dict: The loaded or newly initialized data.
        """
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'r') as f:
                    data = json.load(f)
                    
                # Make sure the structure is valid
                if all(k in data for k in ["hourly_counts", "total_count", "start_time", "keystrokes"]):
                    return data
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON from {self.log_file}: {e}. A new log file will be created.")
            except Exception as e:
                print(f"Error loading data from {self.log_file}: {e}. A new log file will be created.")
                # If any other error, create new data structure
        
        # Create new data structure
        return {
            "hourly_counts": {str(i): 0 for i in range(24)},  # Initialize counts for each hour of the day (0-23)
            "total_count": 0,  # Total keystrokes for this session/day
            "start_time": datetime.datetime.now().isoformat(),  # Record when this log structure was created
            "keystrokes": []  # List to store timestamps of keystrokes (actual keys are not recorded for privacy)
        }
        
    def save_data(self):
        """
        Saves the current keyboard activity data (self.data) to the JSON log file.
        This is typically called periodically and upon program exit.
        """
        if self.data:
            try:
                with open(self.log_file, 'w') as f:
                    json.dump(self.data, f, indent=2)
                print(f"Data saved to {self.log_file}")
            except IOError as e:
                print(f"Error writing data to {self.log_file}: {e}")
            except Exception as e:
                print(f"An unexpected error occurred while saving data to {self.log_file}: {e}")
                
    def on_press(self, key):
        """
        Callback function triggered by the pynput listener whenever a key is pressed.

        Updates the keystroke counts (total and hourly) and records the timestamp of the press.
        It does NOT record the actual key pressed to maintain privacy.
        Periodically saves data and triggers a GUI update if the GUI is active.

        Args:
            key: The key object from pynput (not used to store the actual key).
        """
        # Record the current time
        current_time = datetime.datetime.now() # Get the precise time of the key press
        hour = current_time.hour # Extract the hour for hourly counting
        
        # Update counters without recording the actual key
        self.data["total_count"] += 1
        self.data["hourly_counts"][str(hour)] = self.data["hourly_counts"].get(str(hour), 0) + 1 # Increment count for the current hour
        
        # Add timestamp to keystrokes list (without the actual key pressed)
        self.data["keystrokes"].append(current_time.isoformat()) # Add timestamp to the list of keystrokes
        
        # Save data periodically (every 100 keystrokes)
        # Periodically save data to disk to prevent data loss (e.g., every 100 keystrokes)
        if self.data["total_count"] % 100 == 0:
            self.save_data()
            # If the GUI is running, generate a custom event to trigger a stats update.
            # This is a way to communicate from this (potentially non-GUI) thread to the GUI thread.
            if self.root and self.root.winfo_exists(): # Check if GUI root window exists
                self.root.event_generate("<<UpdateStats>>", when="tail") # Generate event for GUI to handle
    
    def start_monitoring(self):
        """
        Starts the keyboard monitoring process if it's not already running.
        Initializes and starts the pynput keyboard listener in a separate thread.
        """
        if not self.is_running:
            self.is_running = True
            self.start_time = datetime.datetime.now()
            
            # Start listener in a non-blocking way
            self.listener = keyboard.Listener(on_press=self.on_press)
            self.listener.start()
            
            print("Keyboard monitoring started.")
            
    def stop_monitoring(self):
        """Stops the keyboard monitoring process if it's currently running.

        Stops the pynput listener and saves the current data before exiting.
        """
        if self.is_running:
            self.is_running = False
            
            if self.listener:
                self.listener.stop()
                self.listener = None
                
            self.save_data()
            print("Keyboard monitoring stopped.")
            
    def get_stats(self):
        """Calculates various statistics from the collected keystroke data.

        Returns:
            dict: A dictionary containing statistics like total keystrokes,
                  hourly counts, peak hour, session duration, and keystrokes per minute.
        """
        stats = {}
        
        # Calculate total keystrokes
        stats["total_keystrokes"] = self.data["total_count"]
        
        # Calculate keystrokes per hour
        hourly_counts = {int(h): c for h, c in self.data["hourly_counts"].items()}
        stats["hourly_counts"] = hourly_counts
        
        # Find peak hour
        if hourly_counts:
            stats["peak_hour"] = max(hourly_counts.items(), key=lambda x: x[1])
        else:
            stats["peak_hour"] = (0, 0)
            
        # Calculate session duration
        start_time = datetime.datetime.fromisoformat(self.data["start_time"])
        end_time = datetime.datetime.now()
        duration = (end_time - start_time).total_seconds() / 3600  # in hours
        stats["duration_hours"] = duration
        
        # Calculate keystrokes per minute (if duration > 0)
        if duration > 0:
            stats["keystrokes_per_minute"] = stats["total_keystrokes"] / (duration * 60)
        else:
            stats["keystrokes_per_minute"] = 0
            
        return stats
        
    def create_gui(self):
        """Creates and configures the main graphical user interface (GUI) for the application.

        Sets up the window, frames, labels for statistics, control buttons, and the plot area.
        Binds a custom event for updating stats from other threads.
        """
        self.root = tk.Tk()
        self.root.title("Keyboard Activity Monitor")
        self.root.geometry("800x600")
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Style configuration
        style = ttk.Style()
        style.configure("Title.TLabel", font=("Arial", 16, "bold"))
        style.configure("Stat.TLabel", font=("Arial", 12))
        
        # Title
        title_label = ttk.Label(main_frame, text="Keyboard Activity Monitor", style="Title.TLabel")
        title_label.pack(pady=10)
        
        # Stats frame
        stats_frame = ttk.LabelFrame(main_frame, text="Statistics")
        stats_frame.pack(fill=tk.X, pady=10)
        
        # Statistics labels
        self.total_keystrokes_label = ttk.Label(stats_frame, text="Total Keystrokes: 0", style="Stat.TLabel")
        self.total_keystrokes_label.pack(anchor="w", padx=10, pady=5)
        
        self.keystrokes_per_minute_label = ttk.Label(stats_frame, text="Keystrokes Per Minute: 0.0", style="Stat.TLabel")
        self.keystrokes_per_minute_label.pack(anchor="w", padx=10, pady=5)
        
        self.peak_hour_label = ttk.Label(stats_frame, text="Peak Hour: N/A", style="Stat.TLabel")
        self.peak_hour_label.pack(anchor="w", padx=10, pady=5)
        
        self.duration_label = ttk.Label(stats_frame, text="Monitoring Duration: 0 hours", style="Stat.TLabel")
        self.duration_label.pack(anchor="w", padx=10, pady=5)
        
        # Create a frame for the plot
        self.plot_frame = ttk.Frame(main_frame)
        self.plot_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Control frame
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=10)
        
        # Control buttons
        self.start_button = ttk.Button(control_frame, text="Start Monitoring", command=self.start_from_gui)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(control_frame, text="Stop Monitoring", command=self.stop_from_gui)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        self.stop_button.config(state=tk.DISABLED)
        
        self.refresh_button = ttk.Button(control_frame, text="Refresh Stats", command=self.update_stats_display)
        self.refresh_button.pack(side=tk.LEFT, padx=5)
        
        # Bind custom event for updating stats
        self.root.bind("<<UpdateStats>>", lambda e: self.update_stats_display())
        
        # Create initial plot
        self.create_plot()
        
    def start_from_gui(self):
        """Handles the 'Start Monitoring' button click in the GUI.

        Disables the start button, enables the stop button, starts the actual monitoring,
        and launches a separate thread for periodic statistics updates in the GUI.
        """
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.start_monitoring()
        
        # Start updating stats periodically
        self.stats_thread = threading.Thread(target=self.periodic_stats_update)
        self.stats_thread.daemon = True
        self.stats_thread.start()
        
    def stop_from_gui(self):
        """Handles the 'Stop Monitoring' button click in the GUI.

        Enables the start button, disables the stop button, and stops the monitoring process.
        """
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.stop_monitoring()
        
    def periodic_stats_update(self):
        """Periodically triggers a GUI update to refresh the displayed statistics.

        This function runs in a separate thread and generates a custom event
        to safely update the GUI from a non-GUI thread.
        It continues as long as monitoring is active and the GUI window exists.
        """
        while self.is_running and self.root and self.root.winfo_exists():
            self.root.event_generate("<<UpdateStats>>", when="tail")
            time.sleep(5)  # Update every 5 seconds
            
    def update_stats_display(self):
        """Updates the statistics labels and the plot in the GUI.

        Fetches the latest statistics using `get_stats` and updates the corresponding
        Tkinter labels and redraws the hourly keystroke plot.
        """
        stats = self.get_stats()
        
        # Update labels
        self.total_keystrokes_label.config(text=f"Total Keystrokes: {stats['total_keystrokes']}")
        self.keystrokes_per_minute_label.config(text=f"Keystrokes Per Minute: {stats['keystrokes_per_minute']:.1f}")
        
        peak_hour, peak_count = stats["peak_hour"]
        peak_time = f"{peak_hour:02d}:00 - {peak_hour+1:02d}:00" if peak_count > 0 else "N/A"
        self.peak_hour_label.config(text=f"Peak Hour: {peak_time} ({peak_count} keystrokes)")
        
        self.duration_label.config(text=f"Monitoring Duration: {stats['duration_hours']:.2f} hours")
        
        # Update plot
        self.create_plot()
        
    def create_plot(self):
        """Creates or updates the Matplotlib bar chart showing keystrokes per hour.

        Clears the previous plot, fetches current hourly data, and renders a new bar chart.
        Highlights the current hour's bar in a different color.
        The plot is embedded into the Tkinter GUI using `FigureCanvasTkAgg`.
        """
        # Clear the plot frame
        for widget in self.plot_frame.winfo_children():
            widget.destroy()
            
        # Get hourly data
        stats = self.get_stats()
        hourly_counts = stats["hourly_counts"]
        
        # Create a new figure
        fig, ax = plt.subplots(figsize=(8, 4))
        
        # Plot data
        hours = list(range(24))
        counts = [hourly_counts.get(h, 0) for h in hours]
        bars = ax.bar(hours, counts, color='steelblue')
        
        # Add labels and formatting
        ax.set_xlabel('Hour of Day')
        ax.set_ylabel('Keystrokes')
        ax.set_title('Keystrokes by Hour of Day')
        ax.set_xticks(range(0, 24, 2))
        ax.set_xticklabels([f'{h:02d}:00' for h in range(0, 24, 2)])
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Highlight the current hour
        current_hour = datetime.datetime.now().hour
        if 0 <= current_hour < 24:
            bars[current_hour].set_color('red')
        
        # Create canvas
        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def run_gui(self):
        """Initializes and runs the Tkinter GUI application.

        Calls `create_gui` to build the interface, performs an initial stats update,
        sets up the window closing protocol, and starts the Tkinter main event loop.
        """
        self.create_gui()
        self.update_stats_display()  # Initial update
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
        
    def on_closing(self):
        """Handles the event when the GUI window is closed.

        Ensures that monitoring is stopped (if running) and data is saved
        before the application exits and the Tkinter window is destroyed.
        """
        if self.is_running:
            self.stop_monitoring()
        self.save_data()
        self.root.destroy()
        
    def generate_report(self, output_file=None):
        """Generates a text-based summary report of the keyboard activity.

        Args:
            output_file (str, optional): The path to save the report. 
                                         Defaults to a timestamped file in the log directory.

        Returns:
            str: The path to the generated report file.
        """
        stats = self.get_stats()
        
        if not output_file:
            output_file = os.path.join(self.log_dir, f"keyboard_report_{self.today}.txt")
            
        with open(output_file, 'w') as f:
            f.write("===== Keyboard Activity Report =====\n\n")
            f.write(f"Date: {self.today}\n")
            f.write(f"Monitoring Start Time: {self.data['start_time']}\n")
            f.write(f"Monitoring Duration: {stats['duration_hours']:.2f} hours\n\n")
            
            f.write("--- Statistics ---\n")
            f.write(f"Total Keystrokes: {stats['total_keystrokes']}\n")
            f.write(f"Average Keystrokes Per Minute: {stats['keystrokes_per_minute']:.1f}\n")
            
            peak_hour, peak_count = stats["peak_hour"]
            peak_time = f"{peak_hour:02d}:00 - {peak_hour+1:02d}:00" if peak_count > 0 else "N/A"
            f.write(f"Peak Activity Hour: {peak_time} ({peak_count} keystrokes)\n\n")
            
            f.write("--- Hourly Breakdown ---\n")
            for hour in range(24):
                count = stats["hourly_counts"].get(hour, 0)
                f.write(f"{hour:02d}:00 - {hour+1:02d}:00: {count} keystrokes\n")
                
        print(f"Report generated: {output_file}")
        return output_file

def parse_arguments():
    """Parses command-line arguments for the application.

    Defines arguments for launching the GUI, starting/stopping monitoring in the background,
    generating a report, and specifying an output file for the report.

    Returns:
        argparse.Namespace: An object containing the parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(description="Keyboard Activity Monitor")
    parser.add_argument('--gui', action='store_true', help="Launch the graphical user interface")
    parser.add_argument('--start', action='store_true', help="Start monitoring in background")
    parser.add_argument('--stop', action='store_true', help="Stop monitoring")
    parser.add_argument('--report', action='store_true', help="Generate activity report")
    parser.add_argument('--output', help="Output file for report")
    return parser.parse_args()

if __name__ == "__main__":
    # This block executes when the script is run directly.
    args = parse_arguments() # Parse command-line arguments
    
    monitor = KeyboardMonitor() # Initialize the keyboard monitor
    
    # Handle command-line arguments to determine the mode of operation
    if args.gui:
        # Launch the graphical user interface
        print("Launching GUI...")
        monitor.run_gui()
    elif args.start:
        # Start monitoring in the background (headless mode)
        print("Starting monitoring in background...")
        monitor.start_monitoring()
        print("Keyboard monitoring is now active in the background.")
        print("To stop, run: python keyboard_monitor.py --stop")
        print("To view stats in GUI, run: python keyboard_monitor.py --gui")
    elif args.stop:
        # Stop any active monitoring process
        print("Stopping monitoring...")
        monitor.stop_monitoring()
        print("Keyboard monitoring stopped.")
    elif args.report:
        # Generate an activity report
        print("Generating activity report...")
        report_file = monitor.generate_report(args.output)
        print(f"Report successfully generated: {report_file}")
    else:
        # Default behavior: If no specific arguments are given, launch the GUI.
        print("No specific arguments provided. Launching GUI by default...")
        monitor.run_gui()