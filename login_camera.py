import cv2
import os
import datetime
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import json
import argparse
import sys

class LoginCamera:
    """A class to capture an image from the webcam upon script execution,
    typically intended for use at login, and optionally send it via email.

    Attributes:
        storage_dir (str): Directory to store captured images.
        config_file (str): Path to the JSON configuration file.
        config (dict): Loaded configuration settings.
        camera (cv2.VideoCapture): OpenCV video capture object.
    """
    def __init__(self, config_file="login_camera_config.json"):
        """Initializes the LoginCamera instance.

        Args:
            config_file (str, optional): Path to the configuration file.
                                         Defaults to "login_camera_config.json".
        """
        # Create storage directory if it doesn't exist
        self.storage_dir = "login_captures" # Define the directory for storing images
        os.makedirs(self.storage_dir, exist_ok=True) # Create directory, ignore if already exists
        
        # Load or create configuration
        self.config_file = config_file # Store the path to the config file
        self.config = self.load_config() # Load settings from the config file
        
        # Initialize webcam (will be set up when needed)
        self.camera = None
    
    def load_config(self):
        """Loads configuration from a JSON file or creates it with default settings if not found.

        Returns:
            dict: A dictionary containing the configuration settings.
        """
        default_config = {
            "email_notification": False,
            "sender_email": "",
            "sender_password": "",
            "recipient_email": "",
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "camera_index": 0,
            "capture_delay": 2,  # seconds to wait before capturing
            "image_quality": 80   # JPEG quality (0-100)
        }
        
        # Create config file with defaults if it doesn't exist
        if not os.path.exists(self.config_file): # Check if the configuration file is present
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=4)
            print(f"Created default configuration file: {self.config_file}")
            print("Please edit this file to configure email notifications.")
            return default_config
        
        # Load existing config
        try:
            with open(self.config_file, 'r') as f: # Open the config file for reading
                config = json.load(f) # Load JSON data
                # Update with any missing keys from default config to ensure all settings are present
                for key in default_config:
                    if key not in config:
                        config[key] = default_config[key] # Add missing keys with default values
            return config
        except json.JSONDecodeError as e: # Specific exception for JSON errors
            print(f"Error decoding JSON from config file {self.config_file}: {e}")
            print("Using default configuration.")
            return default_config
        except IOError as e: # Specific exception for file I/O errors
            print(f"Error reading config file {self.config_file}: {e}")
            print("Using default configuration.")
            return default_config
        except Exception as e: # Catch any other unexpected errors
            print(f"Error loading config: {e}")
            print("Using default configuration.")
            return default_config
    
    def initialize_camera(self):
        """Initializes the webcam using the camera index from the configuration.

        Returns:
            bool: True if the camera was initialized successfully, False otherwise.
        """
        try:
            self.camera = cv2.VideoCapture(self.config["camera_index"])
            
            # Check if camera opened successfully
            if not self.camera.isOpened():
                print("Error: Could not open webcam. Please check if it's connected and not in use by another application.")
                return False
                
            return True
        except Exception as e:
            print(f"Error initializing camera: {e}")
            return False
    
    def capture_image(self):
        """Captures an image from the initialized webcam after a configured delay.

        Reads a few frames to allow the camera to adjust before capturing the final image.

        Returns:
            numpy.ndarray or None: The captured image frame as a NumPy array, 
                                   or None if capturing failed.
        """
        if not self.initialize_camera():
            return None
            
        print(f"Waiting {self.config['capture_delay']} seconds before capture...")
        time.sleep(self.config["capture_delay"])  # Wait before capture
        
        # Attempt to capture a few frames (sometimes first frames are dark or blurry)
        for _ in range(5): # Read and discard a few initial frames
            ret, frame = self.camera.read()
            if not ret: # Check if frame reading was successful
                print("Warning: Could not read initial frame from camera.")
                time.sleep(0.1) # Short pause before retrying
            
        # Capture the actual frame we'll use
        ret, frame = self.camera.read() # Read the final frame
        
        # Release the webcam to free up the resource
        if self.camera:
            self.camera.release()
        
        if not ret or frame is None: # Check if the final capture was successful
            print("Failed to capture image from webcam.")
            return None
            
        print("Image captured successfully.")
        return frame
    
    def save_image(self, frame):
        """Saves the captured image frame to the storage directory with a timestamped filename.

        Args:
            frame (numpy.ndarray): The image frame to save.

        Returns:
            str or None: The path to the saved image file, or None if saving failed.
        """
        if frame is None:
            return None
            
        # Create filename with timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{self.storage_dir}/login_{timestamp}.jpg"
        
        # Save image
        try:
            cv2.imwrite(filename, frame, [cv2.IMWRITE_JPEG_QUALITY, self.config["image_quality"]])
            print(f"Image saved: {filename}")
            return filename
        except Exception as e:
            print(f"Error saving image: {e}")
            return None
    
    def send_email_notification(self, image_path):
        """Sends an email notification with the captured image attached, if enabled and configured.

        Args:
            image_path (str): The path to the image file to attach.
        """
        if not self.config["email_notification"] or image_path is None:
            return
            
        # Check if email configuration is complete
        required_fields = ["sender_email", "sender_password", "recipient_email"]
        if any(not self.config[field] for field in required_fields):
            print("Email notification is enabled but not fully configured. Please update the config file.")
            return
            
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.config["sender_email"]
            msg['To'] = self.config["recipient_email"]
            msg['Subject'] = f"Login Alert - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            # Add message body
            body = "Someone has logged into your computer. Please see the attached image."
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach the image
            with open(image_path, 'rb') as f:
                img_data = f.read()
                image = MIMEImage(img_data, name=os.path.basename(image_path))
                msg.attach(image)
            
            # Connect to SMTP server and send the email
            with smtplib.SMTP(self.config["smtp_server"], self.config["smtp_port"]) as server:
                server.ehlo() # Greet the server
                server.starttls() # Upgrade connection to TLS
                server.ehlo() # Greet again after TLS
                server.login(self.config["sender_email"], self.config["sender_password"]) # Log in
                server.send_message(msg) # Send the email
                
            print("Email notification sent successfully.")
        except smtplib.SMTPAuthenticationError as e:
            print(f"SMTP Authentication Error: {e}. Check sender email/password and app password settings.")
        except smtplib.SMTPConnectError as e:
            print(f"SMTP Connection Error: {e}. Check SMTP server/port and network connection.")
        except Exception as e: # Catch any other email related errors
            print(f"Error sending email: {e}")
    
    def run(self):
        """The main execution method for the LoginCamera.

        Captures an image, saves it, and sends an email notification if configured.
        """
        print("Login Camera activated")
        
        # Capture image
        frame = self.capture_image()
        
        # Save image
        image_path = self.save_image(frame)
        
        # Send email notification if enabled
        if image_path and self.config["email_notification"]:
            self.send_email_notification(image_path)

def parse_arguments():
    """Parses command-line arguments for the Login Camera script.

    Returns:
        argparse.Namespace: An object containing the parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(description="Login Camera - Capture webcam image at login")
    parser.add_argument('--config', default="login_camera_config.json", 
                        help="Path to configuration file")
    parser.add_argument('--setup', action='store_true',
                        help="Generate default configuration file and exit")
    parser.add_argument('--test', action='store_true',
                        help="Test camera capture without sending email")
    return parser.parse_args()

if __name__ == "__main__":
    # This block executes when the script is run directly.
    args = parse_arguments() # Parse command-line arguments
    
    # Initialize LoginCamera with the specified or default config file
    login_camera = LoginCamera(config_file=args.config)
    
    if args.setup:
        # If --setup flag is used, generate/update config and exit
        print(f"Configuration file '{login_camera.config_file}' ensured/created.")
        print("Please review and edit this file to configure your settings, especially for email notifications.")
        sys.exit(0) # Exit after setup
        
    if args.test:
        # If --test flag is used, perform a camera test and exit
        print("Running camera test mode...")
        frame = login_camera.capture_image() # Attempt to capture an image
        if frame is not None:
            image_path = login_camera.save_image(frame) # Save the captured image
            if image_path:
                print(f"Test successful! Image saved to: {image_path}")
            else:
                print("Test failed: Image captured but could not be saved.")
            print("No email was sent as this is test mode.")
        else:
            print("Camera test failed. Please check your webcam connection and permissions.")
        sys.exit(0) # Exit after test
    
    # Default action: run the full login camera capture and notification process
    login_camera.run()