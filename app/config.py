"""
Configuration settings for the Dental Practice Management System.
"""
import os
from pathlib import Path

# Application Information
APP_NAME = "Yashoda Dental Clinic"
APP_VERSION = "1.0.0"
ORGANIZATION = "Yashoda Dental Clinic"

# Database Configuration
DATABASE_NAME = "dental_practice.db"
DATABASE_PATH = Path(__file__).parent.parent / "data" / DATABASE_NAME

# Ensure data directory exists
DATABASE_PATH.parent.mkdir(exist_ok=True)

# UI Configuration
WINDOW_MIN_WIDTH = 1024
WINDOW_MIN_HEIGHT = 600
WINDOW_DEFAULT_WIDTH = 1400
WINDOW_DEFAULT_HEIGHT = 900

# Authentication Configuration
SESSION_TIMEOUT = 3600  # 1 hour in seconds
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION = 300  # 5 minutes in seconds

# Dental Chart Configuration
QUADRANTS = {
    'upper_right': 'Upper Right',
    'upper_left': 'Upper Left',
    'lower_right': 'Lower Right',
    'lower_left': 'Lower Left'
}
TEETH_PER_QUADRANT = 7

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = Path(__file__).parent.parent / "logs" / "dental_app.log"

# Ensure logs directory exists
LOG_FILE.parent.mkdir(exist_ok=True)
