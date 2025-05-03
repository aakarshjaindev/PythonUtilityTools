import tkinter as tk
from tkinter import ttk
import datetime
import pytz
import threading
import time
import json
import os
import argparse
from functools import partial

class GlobalTimeApp:
    def __init__(self, root=None):
        # Default cities and timezones
        self.default_cities = [
            {"name": "New York", "timezone": "America/New_York", "color": "#3498db", "favorite": True},
            {"name": "London", "timezone": "Europe/London", "color": "#e74c3c", "favorite": True},
            {"name": "Tokyo", "timezone": "Asia/Tokyo", "color": "#2ecc71", "favorite": True},
            {"name": "Sydney", "timezone": "Australia/Sydney", "color": "#f39c12", "favorite": True},
            {"name": "Los Angeles", "timezone": "America/Los_Angeles", "color": "#9b59b6", "favorite": True},
            {"name": "Paris", "timezone": "Europe/Paris", "color": "#1abc9c", "favorite": False},
            {"name": "Dubai", "timezone": "Asia/Dubai", "color": "#d35400", "favorite": False},
            {"name": "Beijing", "timezone": "Asia/Shanghai", "color": "#c0392b", "favorite": False},
            {"name": "Moscow", "timezone": "Europe/Moscow", "color": "#7f8c8d", "favorite": False},
            {"name": "São Paulo", "timezone": "America/Sao_Paulo", "color": "#27ae60", "favorite": False}
        ]
        
        # Settings file
        self.config_dir = "global_time_config"
        os.makedirs(self.config_dir, exist_ok=True)
        self.config_file = os.path.join(self.config_dir, "settings.json")
        
        # Load settings or use defaults
        self.cities = self.load_settings()
        
        # For time update thread
        self.running = False
        self.update_thread = None
        
        # Set up UI if root is provided
        self.root = root
        if root:
            self.setup_ui()
    
    def load_settings(self):
        """Load settings from file or use defaults if file doesn't exist"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                print("Error loading settings, using defaults")
                return self.default_cities
        else:
            # Save default settings
            self.save_settings(self.default_cities)
            return self.default_cities
    
    def save_settings(self, cities=None):
        """Save current settings to file"""
        if cities is None:
            cities = self.cities
            
        try:
            with open(self.config_file, 'w') as f:
                json.dump(cities, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def setup_ui(self):
        """Set up the user interface"""
        self.root.title("Global Time Dashboard")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Style configuration
        style = ttk.Style()
        style.configure("Title.TLabel", font=("Arial", 20, "bold"))
        style.configure("City.TLabel", font=("Arial", 14))
        style.configure("Time.TLabel", font=("Arial", 18, "bold"))
        style.configure("Date.TLabel", font=("Arial", 12))
        
        # Title
        title_label = ttk.Label(main_frame, text="Global Time Dashboard", style="Title.TLabel")
        title_label.pack(pady=(0, 20))
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Main tab
        main_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(main_tab, text="Time Display")
        
        # Meeting Planner tab
        meeting_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(meeting_tab, text="Meeting Planner")
        
        # Settings tab
        settings_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(settings_tab, text="Settings")
        
        # Set up time display in main tab
        self.setup_time_display(main_tab)
        
        # Set up meeting planner
        self.setup_meeting_planner(meeting_tab)
        
        # Set up settings tab
        self.setup_settings(settings_tab)
        
        # Start time update thread
        self.running = True
        self.update_thread = threading.Thread(target=self.update_time_thread)
        self.update_thread.daemon = True
        self.update_thread.start()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def setup_time_display(self, parent):
        """Set up time display area"""
        # Filter to show only favorite cities
        favorite_cities = [city for city in self.cities if city.get("favorite", False)]
        
        # Create time frames for each city
        self.time_frames = []
        
        # Create time display area with scrollbar if needed
        display_canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=display_canvas.yview)
        scrollable_frame = ttk.Frame(display_canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: display_canvas.configure(
                scrollregion=display_canvas.bbox("all")
            )
        )
        
        display_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        display_canvas.configure(yscrollcommand=scrollbar.set)
        
        display_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create time displays for each favorite city
        for i, city in enumerate(favorite_cities):
            frame = ttk.Frame(scrollable_frame, padding=10)
            frame.pack(fill=tk.X, pady=5)
            
            # City name with colored indicator
            city_frame = ttk.Frame(frame)
            city_frame.pack(fill=tk.X)
            
            color_indicator = tk.Canvas(city_frame, width=15, height=15, highlightthickness=0)
            color_indicator.create_oval(0, 0, 15, 15, fill=city.get("color", "#cccccc"), outline="")
            color_indicator.pack(side=tk.LEFT, padx=(0, 5))
            
            city_label = ttk.Label(city_frame, text=city["name"], style="City.TLabel")
            city_label.pack(side=tk.LEFT)
            
            # Time and date labels
            time_label = ttk.Label(frame, text="", style="Time.TLabel")
            time_label.pack(fill=tk.X, pady=(5, 0))
            
            date_label = ttk.Label(frame, text="", style="Date.TLabel")
            date_label.pack(fill=tk.X)
            
            # Store references for updating
            self.time_frames.append({
                "city": city,
                "time_label": time_label,
                "date_label": date_label
            })
            
            # Add separator except for last item
            if i < len(favorite_cities) - 1:
                ttk.Separator(scrollable_frame, orient="horizontal").pack(fill=tk.X, pady=10)
    
    def setup_meeting_planner(self, parent):
        """Set up meeting planner tab"""
        # Top frame for meeting time selection
        top_frame = ttk.Frame(parent)
        top_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Meeting date selection
        date_frame = ttk.Frame(top_frame)
        date_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Label(date_frame, text="Meeting Date:").grid(row=0, column=0, sticky=tk.W)
        
        # Date spinners
        self.meeting_year = tk.StringVar(value=str(datetime.datetime.now().year))
        self.meeting_month = tk.StringVar(value=str(datetime.datetime.now().month))
        self.meeting_day = tk.StringVar(value=str(datetime.datetime.now().day))
        
        year_spinner = ttk.Spinbox(date_frame, from_=2022, to=2030, textvariable=self.meeting_year, width=5)
        month_spinner = ttk.Spinbox(date_frame, from_=1, to=12, textvariable=self.meeting_month, width=3)
        day_spinner = ttk.Spinbox(date_frame, from_=1, to=31, textvariable=self.meeting_day, width=3)
        
        year_spinner.grid(row=0, column=1, padx=2)
        ttk.Label(date_frame, text="-").grid(row=0, column=2)
        month_spinner.grid(row=0, column=3, padx=2)
        ttk.Label(date_frame, text="-").grid(row=0, column=4)
        day_spinner.grid(row=0, column=5, padx=2)
        
        # Time selection frame
        time_frame = ttk.Frame(top_frame)
        time_frame.pack(side=tk.LEFT)
        
        ttk.Label(time_frame, text="Meeting Time:").grid(row=0, column=0, sticky=tk.W)
        
        # Time spinners
        self.meeting_hour = tk.StringVar(value="9")
        self.meeting_minute = tk.StringVar(value="0")
        
        hour_spinner = ttk.Spinbox(time_frame, from_=0, to=23, textvariable=self.meeting_hour, width=3)
        minute_spinner = ttk.Spinbox(time_frame, from_=0, to=59, textvariable=self.meeting_minute, width=3)
        
        hour_spinner.grid(row=0, column=1, padx=2)
        ttk.Label(time_frame, text=":").grid(row=0, column=2)
        minute_spinner.grid(row=0, column=3, padx=2)
        
        # Timezone selection
        tz_frame = ttk.Frame(top_frame)
        tz_frame.pack(side=tk.LEFT, padx=20)
        
        ttk.Label(tz_frame, text="Base Timezone:").grid(row=0, column=0, sticky=tk.W)
        
        # Create dropdown for timezone selection
        self.base_timezone = tk.StringVar()
        timezone_dropdown = ttk.Combobox(tz_frame, textvariable=self.base_timezone, state="readonly", width=20)
        timezone_dropdown.grid(row=0, column=1, padx=5)
        
        # Populate dropdown with cities
        timezone_dropdown['values'] = [city["name"] for city in self.cities]
        timezone_dropdown.current(0)  # Set default to first city
        
        # Calculate button
        calc_button = ttk.Button(top_frame, text="Calculate Meeting Times", command=self.calculate_meeting_times)
        calc_button.pack(side=tk.LEFT, padx=20)
        
        # Results area
        results_frame = ttk.LabelFrame(parent, text="Meeting Times Across Timezones")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create scrollable area for results
        result_canvas = tk.Canvas(results_frame)
        result_scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=result_canvas.yview)
        self.meeting_results_frame = ttk.Frame(result_canvas)
        
        self.meeting_results_frame.bind(
            "<Configure>",
            lambda e: result_canvas.configure(
                scrollregion=result_canvas.bbox("all")
            )
        )
        
        result_canvas.create_window((0, 0), window=self.meeting_results_frame, anchor="nw")
        result_canvas.configure(yscrollcommand=result_scrollbar.set)
        
        result_canvas.pack(side="left", fill="both", expand=True)
        result_scrollbar.pack(side="right", fill="y")
        
        # Add placeholder text
        ttk.Label(self.meeting_results_frame, text="Select meeting time and click Calculate").pack(pady=20)
    
    def calculate_meeting_times(self):
        """Calculate and display meeting times across all timezones"""
        # Clear previous results
        for widget in self.meeting_results_frame.winfo_children():
            widget.destroy()
            
        try:
            # Get selected date and time
            year = int(self.meeting_year.get())
            month = int(self.meeting_month.get())
            day = int(self.meeting_day.get())
            hour = int(self.meeting_hour.get())
            minute = int(self.meeting_minute.get())
            
            # Find the selected base timezone
            base_city_name = self.base_timezone.get()
            base_city = next((city for city in self.cities if city["name"] == base_city_name), None)
            
            if not base_city:
                raise ValueError("Base city not found")
                
            # Create datetime in the base timezone
            base_tz = pytz.timezone(base_city["timezone"])
            meeting_datetime = base_tz.localize(datetime.datetime(year, month, day, hour, minute))
            
            # Display title with meeting info
            title = f"Meeting at {meeting_datetime.strftime('%Y-%m-%d %H:%M')} {base_city_name} time"
            ttk.Label(self.meeting_results_frame, text=title, font=("Arial", 12, "bold")).pack(pady=(10, 20))
            
            # Create a frame for the results grid
            grid_frame = ttk.Frame(self.meeting_results_frame)
            grid_frame.pack(fill=tk.BOTH, expand=True)
            
            # Column headers
            ttk.Label(grid_frame, text="City", font=("Arial", 11, "bold")).grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
            ttk.Label(grid_frame, text="Date", font=("Arial", 11, "bold")).grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)
            ttk.Label(grid_frame, text="Time", font=("Arial", 11, "bold")).grid(row=0, column=2, padx=10, pady=5, sticky=tk.W)
            ttk.Label(grid_frame, text="Working Hours?", font=("Arial", 11, "bold")).grid(row=0, column=3, padx=10, pady=5, sticky=tk.W)
            
            ttk.Separator(grid_frame, orient='horizontal').grid(row=1, column=0, columnspan=4, sticky='ew', pady=5)
            
            # Calculate and display time for each city
            for i, city in enumerate(self.cities):
                city_tz = pytz.timezone(city["timezone"])
                local_time = meeting_datetime.astimezone(city_tz)
                
                # Check if within working hours (9 AM to 5 PM)
                hour = local_time.hour
                is_working_hours = 9 <= hour < 17
                is_weekend = local_time.weekday() >= 5  # 5 = Saturday, 6 = Sunday
                
                # Display city
                ttk.Label(grid_frame, text=city["name"]).grid(row=i+2, column=0, padx=10, pady=5, sticky=tk.W)
                
                # Display date
                date_str = local_time.strftime("%Y-%m-%d")
                ttk.Label(grid_frame, text=date_str).grid(row=i+2, column=1, padx=10, pady=5, sticky=tk.W)
                
                # Display time
                time_str = local_time.strftime("%H:%M")
                ttk.Label(grid_frame, text=time_str).grid(row=i+2, column=2, padx=10, pady=5, sticky=tk.W)
                
                # Display if during working hours
                if is_weekend:
                    status = "Weekend"
                    color = "#e74c3c"  # Red
                elif is_working_hours:
                    status = "Working Hours"
                    color = "#2ecc71"  # Green
                else:
                    status = "After Hours"
                    color = "#f39c12"  # Yellow/Orange
                
                status_label = ttk.Label(grid_frame, text=status)
                status_label.grid(row=i+2, column=3, padx=10, pady=5, sticky=tk.W)
                
                # Add visual indicator of status
                # Using Canvas for a colored circle since ttk doesn't support backgroundColor
                indicator = tk.Canvas(grid_frame, width=12, height=12, highlightthickness=0)
                indicator.create_oval(0, 0, 12, 12, fill=color, outline="")
                indicator.grid(row=i+2, column=4, padx=5, pady=5)
                
        except Exception as e:
            error_label = ttk.Label(self.meeting_results_frame, 
                                   text=f"Error calculating meeting times: {str(e)}", 
                                   foreground="red")
            error_label.pack(pady=20)
    
    def setup_settings(self, parent):
        """Set up settings tab"""
        # Instructions
        ttk.Label(parent, text="Customize cities and timezones").pack(anchor=tk.W, pady=(0, 10))
        
        # Create scrollable frame for city settings
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        settings_frame = ttk.Frame(canvas)
        
        settings_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        
        canvas.create_window((0, 0), window=settings_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Column headers
        headers_frame = ttk.Frame(settings_frame)
        headers_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(headers_frame, text="Favorite", width=8).pack(side=tk.LEFT, padx=5)
        ttk.Label(headers_frame, text="City Name", width=15).pack(side=tk.LEFT, padx=5)
        ttk.Label(headers_frame, text="Timezone", width=20).pack(side=tk.LEFT, padx=5)
        ttk.Label(headers_frame, text="Display Color", width=15).pack(side=tk.LEFT, padx=5)
        
        ttk.Separator(settings_frame, orient='horizontal').pack(fill=tk.X, pady=5)
        
        # City settings
        self.city_vars = []
        for i, city in enumerate(self.cities):
            city_frame = ttk.Frame(settings_frame)
            city_frame.pack(fill=tk.X, pady=2)
            
            # Favorite checkbox
            fav_var = tk.BooleanVar(value=city.get("favorite", False))
            fav_check = ttk.Checkbutton(city_frame, variable=fav_var)
            fav_check.pack(side=tk.LEFT, padx=5)
            
            # City name entry
            name_var = tk.StringVar(value=city["name"])
            name_entry = ttk.Entry(city_frame, textvariable=name_var, width=15)
            name_entry.pack(side=tk.LEFT, padx=5)
            
            # Timezone selection (read-only dropdown)
            tz_var = tk.StringVar(value=city["timezone"])
            tz_dropdown = ttk.Combobox(city_frame, textvariable=tz_var, width=20)
            tz_dropdown['values'] = sorted(pytz.all_timezones)
            tz_dropdown.pack(side=tk.LEFT, padx=5)
            
            # Color selection (using simple dropdown for common colors)
            colors = {
                "Blue": "#3498db", 
                "Red": "#e74c3c", 
                "Green": "#2ecc71", 
                "Orange": "#f39c12", 
                "Purple": "#9b59b6", 
                "Teal": "#1abc9c", 
                "Dark Orange": "#d35400", 
                "Dark Red": "#c0392b", 
                "Gray": "#7f8c8d", 
                "Dark Green": "#27ae60"
            }
            
            color_var = tk.StringVar()
            # Find color name by its hex value
            for color_name, hex_code in colors.items():
                if hex_code == city.get("color"):
                    color_var.set(color_name)
                    break
            else:
                color_var.set("Blue")  # default
                
            color_dropdown = ttk.Combobox(city_frame, textvariable=color_var, width=15)
            color_dropdown['values'] = list(colors.keys())
            color_dropdown.pack(side=tk.LEFT, padx=5)
            
            # Delete button
            delete_btn = ttk.Button(city_frame, text="X", width=3,
                                    command=partial(self.delete_city, i))
            delete_btn.pack(side=tk.LEFT, padx=5)
            
            # Store variables
            self.city_vars.append({
                "favorite": fav_var,
                "name": name_var,
                "timezone": tz_var,
                "color": color_var,
                "colors_dict": colors,
                "row": i
            })
        
        # Add new city button
        add_frame = ttk.Frame(settings_frame)
        add_frame.pack(fill=tk.X, pady=10)
        
        add_btn = ttk.Button(add_frame, text="Add New City", command=self.add_city)
        add_btn.pack(side=tk.LEFT, padx=5)
        
        # Save settings button
        save_btn = ttk.Button(settings_frame, text="Save Settings", command=self.save_settings_from_ui)
        save_btn.pack(pady=20)
        
    def delete_city(self, index):
        """Delete a city from settings"""
        if len(self.city_vars) > 1:  # Prevent deleting all cities
            # Prepare to delete from GUI list
            del self.city_vars[index]
            
            # Rebuild the settings tab
            self.save_settings_from_ui()
            
            # Rebuild settings tab to reflect changes
            self.refresh_settings_tab()
        else:
            from tkinter import messagebox
            messagebox.showwarning("Cannot Delete", "You must keep at least one city.")
    
    def add_city(self):
        """Add a new city to settings"""
        # Add a new default city
        new_city = {
            "name": "New City",
            "timezone": "UTC",
            "color": "#3498db",
            "favorite": False
        }
        
        # Add to in-memory cities
        self.cities.append(new_city)
        
        # Refresh UI
        self.refresh_settings_tab()
    
    def save_settings_from_ui(self):
        """Save settings from UI elements"""
        updated_cities = []
        
        for i, vars in enumerate(self.city_vars):
            color_name = vars["color"].get()
            color_hex = vars["colors_dict"].get(color_name, "#3498db")
            
            city = {
                "name": vars["name"].get(),
                "timezone": vars["timezone"].get(),
                "color": color_hex,
                "favorite": vars["favorite"].get()
            }
            updated_cities.append(city)
            
        # Update settings
        self.cities = updated_cities
        self.save_settings(updated_cities)
        
        # Refresh time display
        self.refresh_time_display()
    
    def refresh_settings_tab(self):
        """Refresh the settings tab to reflect current settings"""
        # Find and destroy the settings tab
        for i in range(self.notebook.index("end")):
            if self.notebook.tab(i, "text") == "Settings":
                settings_tab = self.notebook.winfo_children()[i]
                settings_tab.destroy()
                
                # Create new settings tab
                new_settings_tab = ttk.Frame(self.notebook, padding=10)
                self.notebook.insert(i, new_settings_tab, text="Settings")
                
                # Set up the tab
                self.setup_settings(new_settings_tab)
                
                # Switch to the new tab
                self.notebook.select(i)
                
                break
    
    def refresh_time_display(self):
        """Refresh the main time display"""
        # Find and destroy the main tab
        for i in range(self.notebook.index("end")):
            if self.notebook.tab(i, "text") == "Time Display":
                main_tab = self.notebook.winfo_children()[i]
                main_tab.destroy()
                
                # Create new main tab
                new_main_tab = ttk.Frame(self.notebook, padding=10)
                self.notebook.insert(i, new_main_tab, text="Time Display")
                
                # Set up the tab
                self.setup_time_display(new_main_tab)
                
                # Switch back to where we were
                break
    
    def update_time(self):
        """Update all time displays with current time"""
        for frame in self.time_frames:
            city = frame["city"]
            tz = pytz.timezone(city["timezone"])
            now = datetime.datetime.now(tz)
            
            # Update time display
            frame["time_label"].config(text=now.strftime("%H:%M:%S"))
            frame["date_label"].config(text=now.strftime("%Y-%m-%d (%A)"))
    
    def update_time_thread(self):
        """Thread function to update time continuously"""
        while self.running:
            try:
                self.root.after(0, self.update_time)
                time.sleep(1)
            except:
                # Handle case where window was closed
                break
    
    def on_closing(self):
        """Handle window closing"""
        self.running = False
        if self.update_thread:
            self.update_thread.join(0.1)  # Give thread time to clean up
        self.root.destroy()
    
    def run(self):
        """Run the application"""
        if not self.root:
            self.root = tk.Tk()
            self.setup_ui()
        self.root.mainloop()

def parse_arguments():
    parser = argparse.ArgumentParser(description="Global Time Dashboard")
    parser.add_argument('--cli', action='store_true', help="Show times in command line instead of GUI")
    return parser.parse_args()

def display_cli_times(app):
    """Display current times in command line interface"""
    print("\n=== GLOBAL TIME DASHBOARD ===")
    print(f"Current local time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    for city in app.cities:
        if city.get("favorite", True):  # Show favorites by default
            tz = pytz.timezone(city["timezone"])
            now = datetime.datetime.now(tz)
            print(f"{city['name']:15} {now.strftime('%Y-%m-%d %H:%M:%S')} ({tz.zone})")
    
    print("\nUse --gui to launch the graphical interface")

if __name__ == "__main__":
    args = parse_arguments()
    
    app = GlobalTimeApp()
    
    if args.cli:
        display_cli_times(app)
    else:
        app.run() 