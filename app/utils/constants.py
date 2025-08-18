"""
Application constants and enumerations.
"""

# Database constants
DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "admin123"

# Dental chart constants
QUADRANTS = {
    'upper_right': 'Upper Right',
    'upper_left': 'Upper Left', 
    'lower_right': 'Lower Right',
    'lower_left': 'Lower Left'
}

TEETH_PER_QUADRANT = 8

TOOTH_STATUS = {
    'normal': 'Normal',
    'treated': 'Treated',
    'selected': 'Selected',
    'missing': 'Missing',
    'problematic': 'Problematic'
}

# UI constants
COLORS = {
    'primary': '#3498DB',
    'secondary': '#2C3E50',
    'success': '#4CAF50',
    'warning': '#FFC107',
    'danger': '#E74C3C',
    'info': '#17A2B8',
    'light': '#F8F9FA',
    'dark': '#343A40'
}

# Date formats
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DISPLAY_DATE_FORMAT = "%B %d, %Y"
DISPLAY_DATETIME_FORMAT = "%B %d, %Y at %I:%M %p"

# File extensions
EXPORT_FORMATS = {
    'csv': 'Comma Separated Values (*.csv)',
    'json': 'JSON Files (*.json)',
    'xlsx': 'Excel Files (*.xlsx)'
}

# Validation constants
MAX_NAME_LENGTH = 255
MAX_PHONE_LENGTH = 20
MAX_EMAIL_LENGTH = 255
MIN_PASSWORD_LENGTH = 6

# Patient ID format
PATIENT_ID_PREFIX = "P"
PATIENT_ID_LENGTH = 6  # e.g., P00001
