"""
Startup optimization script for faster application launch.
"""

import sys
import os
from pathlib import Path

def optimize_python_startup():
    """Optimize Python startup performance."""
    # Disable bytecode generation for faster startup
    sys.dont_write_bytecode = True
    
    # Set PYTHONOPTIMIZE for better performance
    os.environ['PYTHONOPTIMIZE'] = '1'
    
    # Disable Python debug mode
    os.environ['PYTHONDEBUG'] = '0'
    
    # Set application to run with high priority
    try:
        import psutil
        import os
        process = psutil.Process(os.getpid())
        process.nice(psutil.HIGH_PRIORITY_CLASS)
    except ImportError:
        pass  # psutil not available

def optimize_qt_startup():
    """Optimize Qt startup performance."""
    # Set Qt environment variables for better performance
    os.environ['QT_QUICK_CONTROLS_STYLE'] = 'Fusion'
    os.environ['QT_SCALE_FACTOR_ROUNDING_POLICY'] = 'RoundPreferFloor'
    
    # Disable Qt accessibility for faster startup
    os.environ['QT_ACCESSIBILITY'] = '0'
    
    # Enable Qt performance optimizations
    os.environ['QT_OPENGL'] = 'software'  # Use software rendering for compatibility

# Apply optimizations
optimize_python_startup()
optimize_qt_startup()
