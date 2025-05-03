import tkinter as tk
from tkinter import ttk, messagebox
import time
import json
import os
import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from threading import Thread
import csv

# Try to import the notification library, with graceful fallback
try:
    from plyer import notification
except ImportError:
    # Define a fallback notification function if plyer isn't installed
    def show_notification(title, message):
        messagebox.showinfo(title, message)
else:
    # Use plyer's notification if available
    def show_notification(title, message):
        notification.notify(
            title=title,
            message=message,
            app_name="Pomodoro Timer",
            timeout=10
        )

class PomodoroTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("Pomodoro Timer")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # Default settings
        self.work_minutes = 25
        self.short_break_minutes = 5
        self.long_break_minutes = 15
        self.pomodoro_count = 0
        self.max_pomodoros = 4
        
        # Timer state
        self.running = False
        self.time_left = self.work_minutes * 60
        self.mode = "Work"
        self.timer_thread = None
        
        # Focus tracking data
        self.today_focus_minutes = 0
        self.focus_sessions = []
        self.data_file = "pomodoro_data.csv"
        self.load_data()
        
        # UI elements
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Style
        style = ttk.Style()
        style.configure("Timer.TLabel", font=("Arial", 48))
        style.configure("Mode.TLabel", font=("Arial", 18))
        style.configure("Stats.TLabel", font=("Arial", 12))
        
        # Timer display
        self.timer_display = ttk.Label(main_frame, text="25:00", style="Timer.TLabel")
        self.timer_display.pack(pady=20)
        
        # Mode label
        self.mode_label = ttk.Label(main_frame, text="Work Time", style="Mode.TLabel")
        self.mode_label.pack(pady=5)
        
        # Buttons frame
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=20)
        
        # Control buttons
        self.start_btn = ttk.Button(btn_frame, text="Start", command=self.start_timer, width=10)
        self.start_btn.grid(row=0, column=0, padx=5)
        
        self.pause_btn = ttk.Button(btn_frame, text="Pause", command=self.pause_timer, width=10, state=tk.DISABLED)
        self.pause_btn.grid(row=0, column=1, padx=5)
        
        self.reset_btn = ttk.Button(btn_frame, text="Reset", command=self.reset_timer, width=10)
        self.reset_btn.grid(row=0, column=2, padx=5)
        
        # Settings frame
        settings_frame = ttk.LabelFrame(main_frame, text="Settings")
        settings_frame.pack(fill=tk.X, pady=10)
        
        # Work duration setting
        ttk.Label(settings_frame, text="Work Duration (min):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.work_spinbox = ttk.Spinbox(settings_frame, from_=1, to=60, width=5, command=self.update_settings)
        self.work_spinbox.grid(row=0, column=1, padx=5, pady=5)
        self.work_spinbox.set(self.work_minutes)
        
        # Short break duration setting
        ttk.Label(settings_frame, text="Short Break (min):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.short_break_spinbox = ttk.Spinbox(settings_frame, from_=1, to=30, width=5, command=self.update_settings)
        self.short_break_spinbox.grid(row=1, column=1, padx=5, pady=5)
        self.short_break_spinbox.set(self.short_break_minutes)
        
        # Long break duration setting
        ttk.Label(settings_frame, text="Long Break (min):").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.long_break_spinbox = ttk.Spinbox(settings_frame, from_=1, to=60, width=5, command=self.update_settings)
        self.long_break_spinbox.grid(row=2, column=1, padx=5, pady=5)
        self.long_break_spinbox.set(self.long_break_minutes)
        
        # Focus statistics frame
        stats_frame = ttk.LabelFrame(main_frame, text="Focus Statistics")
        stats_frame.pack(fill=tk.X, pady=10)
        
        # Today's stats
        self.today_stats_label = ttk.Label(stats_frame, text=f"Today's Focus: {self.today_focus_minutes} minutes", style="Stats.TLabel")
        self.today_stats_label.pack(pady=5)
        
        # Visualization button
        self.viz_btn = ttk.Button(stats_frame, text="Show Weekly Report", command=self.show_visualization)
        self.viz_btn.pack(pady=5)
    
    def update_settings(self):
        # Update timer settings from spinboxes
        try:
            self.work_minutes = int(self.work_spinbox.get())
            self.short_break_minutes = int(self.short_break_spinbox.get())
            self.long_break_minutes = int(self.long_break_spinbox.get())
            
            # Update display if timer is not running
            if not self.running:
                self.time_left = self.work_minutes * 60
                self.update_timer_display()
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for timer durations.")
    
    def format_time(self, seconds):
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def update_timer_display(self):
        self.timer_display.config(text=self.format_time(self.time_left))
        
    def start_timer(self):
        if not self.running:
            self.running = True
            self.start_btn.config(state=tk.DISABLED)
            self.pause_btn.config(state=tk.NORMAL)
            
            # Start timer in a separate thread
            self.timer_thread = Thread(target=self.run_timer)
            self.timer_thread.daemon = True
            self.timer_thread.start()
    
    def pause_timer(self):
        self.running = False
        self.start_btn.config(state=tk.NORMAL)
        self.pause_btn.config(state=tk.DISABLED)
    
    def reset_timer(self):
        self.running = False
        self.mode = "Work"
        self.time_left = self.work_minutes * 60
        self.pomodoro_count = 0
        self.update_timer_display()
        self.mode_label.config(text="Work Time")
        self.start_btn.config(state=tk.NORMAL)
        self.pause_btn.config(state=tk.DISABLED)
    
    def run_timer(self):
        start_time = None
        if self.mode == "Work":
            start_time = time.time()
            
        while self.running and self.time_left > 0:
            self.time_left -= 1
            self.root.after(0, self.update_timer_display)
            time.sleep(1)
            
        # If timer completed naturally (not paused)
        if self.running and self.time_left <= 0:
            # Record focus session if it was work time
            if self.mode == "Work" and start_time is not None:
                focus_duration = (time.time() - start_time) / 60  # in minutes
                self.today_focus_minutes += int(focus_duration)
                self.focus_sessions.append({
                    'date': datetime.datetime.now().strftime('%Y-%m-%d'),
                    'start_time': datetime.datetime.fromtimestamp(start_time).strftime('%H:%M'),
                    'duration_minutes': int(focus_duration)
                })
                self.save_data()
                self.today_stats_label.config(text=f"Today's Focus: {self.today_focus_minutes} minutes")
            
            # Determine next timer mode
            self.switch_mode()
            
            # Notify user
            message = "Time's up! "
            if self.mode == "Work":
                message += "Focus time starts now."
            else:
                message += f"{self.mode} time starts now."
            
            self.root.after(0, lambda: show_notification("Pomodoro Timer", message))
            
            # Start next timer period automatically
            self.root.after(1000, self.start_timer)
    
    def switch_mode(self):
        if self.mode == "Work":
            self.pomodoro_count += 1
            
            if self.pomodoro_count % self.max_pomodoros == 0:
                self.mode = "Long Break"
                self.time_left = self.long_break_minutes * 60
                self.mode_label.config(text="Long Break")
            else:
                self.mode = "Short Break"
                self.time_left = self.short_break_minutes * 60
                self.mode_label.config(text="Short Break")
        else:
            self.mode = "Work"
            self.time_left = self.work_minutes * 60
            self.mode_label.config(text="Work Time")
            
        self.update_timer_display()
    
    def load_data(self):
        # Create the data file if it doesn't exist
        if not os.path.exists(self.data_file):
            with open(self.data_file, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['date', 'start_time', 'duration_minutes'])
            return
            
        # Load existing data
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        self.focus_sessions = []
        
        with open(self.data_file, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                self.focus_sessions.append(row)
                # Calculate today's total
                if row['date'] == today:
                    self.today_focus_minutes += int(row['duration_minutes'])
    
    def save_data(self):
        # Write all sessions to CSV
        with open(self.data_file, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['date', 'start_time', 'duration_minutes'])
            writer.writeheader()
            for session in self.focus_sessions:
                writer.writerow(session)
    
    def show_visualization(self):
        # Create a new window for visualization
        viz_window = tk.Toplevel(self.root)
        viz_window.title("Weekly Focus Report")
        viz_window.geometry("800x600")
        
        # Get the last 7 days of data
        today = datetime.datetime.now().date()
        dates = [(today - datetime.timedelta(days=i)).strftime('%Y-%m-%d') for i in range(6, -1, -1)]
        
        # Calculate daily totals
        daily_totals = {date: 0 for date in dates}
        
        for session in self.focus_sessions:
            if session['date'] in daily_totals:
                daily_totals[session['date']] += int(session['duration_minutes'])
        
        # Create figure and plot
        fig, ax = plt.Figure(figsize=(8, 5), dpi=100)
        ax = fig.add_subplot(111)
        
        # Format x-axis dates to be more readable (just show day of week)
        display_dates = []
        for date_str in dates:
            dt = datetime.datetime.strptime(date_str, '%Y-%m-%d')
            display_dates.append(dt.strftime('%a'))
        
        # Plot bar chart
        bars = ax.bar(display_dates, [daily_totals[date] for date in dates])
        
        # Add data labels on top of bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f"{int(height)}" if height > 0 else "0",
                    ha='center', va='bottom')
        
        # Customize the plot
        ax.set_ylabel('Focus Minutes')
        ax.set_title('Daily Focus Time (Last 7 Days)')
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Create canvas
        canvas = FigureCanvasTkAgg(fig, master=viz_window)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        
        # Add statistics text
        total_focus = sum(daily_totals.values())
        avg_daily = total_focus / 7
        
        stats_text = ttk.Label(viz_window, 
                              text=f"Total focus time: {total_focus} minutes ({total_focus/60:.1f} hours)\n"
                                   f"Daily average: {avg_daily:.1f} minutes")
        stats_text.pack(pady=10)
        
        # Close button
        close_btn = ttk.Button(viz_window, text="Close", command=viz_window.destroy)
        close_btn.pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = PomodoroTimer(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (app.running and app.pause_timer(), root.destroy()))
    root.mainloop() 