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
    def __init__(self, config_file="login_camera_config.json"):
        # Create storage directory if it doesn't exist
        self.storage_dir = "login_captures"
        os.makedirs(self.storage_dir, exist_ok=True)
        
        # Load or create configuration
        self.config_file = config_file
        self.config = self.load_config()
        
        # Initialize webcam
        self.camera = None
    
    def load_config(self):
        """Load or create config file with default settings"""
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
        if not os.path.exists(self.config_file):
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=4)
            print(f"Created default configuration file: {self.config_file}")
            print("Please edit this file to configure email notifications.")
            return default_config
        
        # Load existing config
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                # Update with any missing keys from default config
                for key in default_config:
                    if key not in config:
                        config[key] = default_config[key]
            return config
        except Exception as e:
            print(f"Error loading config: {e}")
            print("Using default configuration.")
            return default_config
    
    def initialize_camera(self):
        """Initialize the webcam with error handling"""
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
        """Capture an image from the webcam"""
        if not self.initialize_camera():
            return None
            
        print(f"Waiting {self.config['capture_delay']} seconds before capture...")
        time.sleep(self.config["capture_delay"])  # Wait before capture
        
        # Attempt to capture a few frames (sometimes first frames are dark)
        for _ in range(5):
            ret, frame = self.camera.read()
            
        # Capture the actual frame we'll use
        ret, frame = self.camera.read()
        
        # Release the webcam
        self.camera.release()
        
        if not ret or frame is None:
            print("Failed to capture image")
            return None
            
        return frame
    
    def save_image(self, frame):
        """Save the captured image with timestamp"""
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
        """Send email notification with the captured image"""
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
            
            # Connect to server and send
            with smtplib.SMTP(self.config["smtp_server"], self.config["smtp_port"]) as server:
                server.starttls()
                server.login(self.config["sender_email"], self.config["sender_password"])
                server.send_message(msg)
                
            print("Email notification sent successfully")
        except Exception as e:
            print(f"Error sending email: {e}")
    
    def run(self):
        """Main function to capture login image and notify"""
        print("Login Camera activated")
        
        # Capture image
        frame = self.capture_image()
        
        # Save image
        image_path = self.save_image(frame)
        
        # Send email notification if enabled
        if image_path and self.config["email_notification"]:
            self.send_email_notification(image_path)

def parse_arguments():
    parser = argparse.ArgumentParser(description="Login Camera - Capture webcam image at login")
    parser.add_argument('--config', default="login_camera_config.json", 
                        help="Path to configuration file")
    parser.add_argument('--setup', action='store_true',
                        help="Generate default configuration file and exit")
    parser.add_argument('--test', action='store_true',
                        help="Test camera capture without sending email")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    
    login_camera = LoginCamera(config_file=args.config)
    
    if args.setup:
        print(f"Configuration file created/updated: {login_camera.config_file}")
        print("Edit this file to configure your settings and email notifications.")
        sys.exit(0)
        
    if args.test:
        print("Running camera test...")
        frame = login_camera.capture_image()
        if frame is not None:
            path = login_camera.save_image(frame)
            print(f"Test successful! Image saved to: {path}")
            print("No email was sent in test mode.")
        else:
            print("Camera test failed. Please check your webcam connection.")
        sys.exit(0)
    
    # Normal execution
    login_camera.run() 