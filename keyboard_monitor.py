import pynput
from pynput import keyboard
import time
import datetime
import os
import json
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk
import threading
import atexit
import argparse
import sys

class KeyboardMonitor:
    def __init__(self, log_dir="keyboard_logs"):
        # Create logging directories
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Current date for logging
        self.today = datetime.datetime.now().strftime("%Y-%m-%d")
        self.log_file = os.path.join(self.log_dir, f"keyboard_log_{self.today}.json")
        
        # Load existing data or create new log structure
        self.data = self.load_data()
        
        # For keyboard monitoring
        self.listener = None
        self.is_running = False
        self.start_time = None
        
        # For GUI
        self.root = None
        self.stats_thread = None
        
        # Make sure to save when the program exits
        atexit.register(self.save_data)
        
    def load_data(self):
        """Load existing data for today or create new log structure"""
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'r') as f:
                    data = json.load(f)
                    
                # Make sure the structure is valid
                if all(k in data for k in ["hourly_counts", "total_count", "start_time", "keystrokes"]):
                    return data
            except Exception as e:
                print(f"Error loading data: {e}")
                # If error, create new data structure
        
        # Create new data structure
        return {
            "hourly_counts": {str(i): 0 for i in range(24)},  # Count per hour of day
            "total_count": 0,
            "start_time": datetime.datetime.now().isoformat(),
            "keystrokes": []  # We don't record actual keys, just timestamps
        }
        
    def save_data(self):
        """Save current data to log file"""
        if self.data:
            try:
                with open(self.log_file, 'w') as f:
                    json.dump(self.data, f, indent=2)
                print(f"Data saved to {self.log_file}")
            except Exception as e:
                print(f"Error saving data: {e}")
                
    def on_press(self, key):
        """Callback function for key press events"""
        # Record the current time
        current_time = datetime.datetime.now()
        hour = current_time.hour
        
        # Update counters without recording the actual key
        self.data["total_count"] += 1
        self.data["hourly_counts"][str(hour)] = self.data["hourly_counts"].get(str(hour), 0) + 1
        
        # Add timestamp to keystrokes list (without the actual key pressed)
        self.data["keystrokes"].append(current_time.isoformat())
        
        # Save data periodically (every 100 keystrokes)
        if self.data["total_count"] % 100 == 0:
            self.save_data()
            # Also update the GUI if it's running
            if self.root and self.root.winfo_exists():
                self.root.event_generate("<<UpdateStats>>", when="tail")
    
    def start_monitoring(self):
        """Start keyboard monitoring"""
        if not self.is_running:
            self.is_running = True
            self.start_time = datetime.datetime.now()
            
            # Start listener in a non-blocking way
            self.listener = keyboard.Listener(on_press=self.on_press)
            self.listener.start()
            
            print("Keyboard monitoring started.")
            
    def stop_monitoring(self):
        """Stop keyboard monitoring"""
        if self.is_running:
            self.is_running = False
            
            if self.listener:
                self.listener.stop()
                self.listener = None
                
            self.save_data()
            print("Keyboard monitoring stopped.")
            
    def get_stats(self):
        """Calculate statistics from the collected data"""
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
        """Create a GUI for displaying statistics"""
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
        """Start monitoring from GUI button"""
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.start_monitoring()
        
        # Start updating stats periodically
        self.stats_thread = threading.Thread(target=self.periodic_stats_update)
        self.stats_thread.daemon = True
        self.stats_thread.start()
        
    def stop_from_gui(self):
        """Stop monitoring from GUI button"""
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.stop_monitoring()
        
    def periodic_stats_update(self):
        """Update stats display periodically"""
        while self.is_running and self.root and self.root.winfo_exists():
            self.root.event_generate("<<UpdateStats>>", when="tail")
            time.sleep(5)  # Update every 5 seconds
            
    def update_stats_display(self):
        """Update the stats display in the GUI"""
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
        """Create or update the hourly keystrokes plot"""
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
        """Run the GUI application"""
        self.create_gui()
        self.update_stats_display()  # Initial update
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
        
    def on_closing(self):
        """Handle window closing event"""
        if self.is_running:
            self.stop_monitoring()
        self.save_data()
        self.root.destroy()
        
    def generate_report(self, output_file=None):
        """Generate a text report of keyboard activity"""
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
    parser = argparse.ArgumentParser(description="Keyboard Activity Monitor")
    parser.add_argument('--gui', action='store_true', help="Launch the graphical user interface")
    parser.add_argument('--start', action='store_true', help="Start monitoring in background")
    parser.add_argument('--stop', action='store_true', help="Stop monitoring")
    parser.add_argument('--report', action='store_true', help="Generate activity report")
    parser.add_argument('--output', help="Output file for report")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    
    monitor = KeyboardMonitor()
    
    if args.gui:
        # Launch GUI
        monitor.run_gui()
    elif args.start:
        # Start monitoring in background
        monitor.start_monitoring()
        print("Keyboard monitoring started in background.")
        print("Use '--stop' to stop monitoring or '--gui' to view statistics.")
    elif args.stop:
        # Stop monitoring
        monitor.stop_monitoring()
    elif args.report:
        # Generate report
        monitor.generate_report(args.output)
    else:
        # If no arguments, launch GUI by default
        monitor.run_gui() 