"""
Main application entry point.
"""
import sys
import logging
import traceback
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

from .database.database import db_manager
from .ui.login_dialog import LoginDialog
from .ui.main_window import MainWindow
from .config import APP_NAME, LOG_LEVEL, LOG_FORMAT, LOG_FILE
from .utils.error_handler import error_handler
from .utils.performance import performance_monitor, optimize_application_performance


def setup_logging():
    """Set up application logging."""
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL),
        format=LOG_FORMAT,
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler(sys.stdout)
        ]
    )


def handle_exception(exc_type, exc_value, exc_traceback):
    """Global exception handler."""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    # Log the exception
    logging.critical("Uncaught exception:", exc_info=(exc_type, exc_value, exc_traceback))
    
    # Handle with error handler
    error_handler.handle_error(
        exc_value, 
        "An unexpected error occurred in the application",
        severity=error_handler.ErrorSeverity.CRITICAL
    )


class DentalManagementApp:
    """Main application class."""
    
    def __init__(self):
        self.app = None
        self.main_window = None
        
    def run(self):
        """Run the application."""
        # Set up logging and global exception handler
        setup_logging()
        sys.excepthook = handle_exception
        
        logger = logging.getLogger(__name__)
        logger.info(f"Starting {APP_NAME}...")
        
        try:
            # Create Qt application
            self.app = QApplication(sys.argv)
            self.app.setApplicationName(APP_NAME)
            self.app.setOrganizationName("Dental Solutions")

            # Apply stylesheet
            stylesheet_path = Path(__file__).parent / "ui" / "resources" / "style.qss"
            if stylesheet_path.exists():
                with open(stylesheet_path, "r") as f:
                    self.app.setStyleSheet(f.read())
                logger.info(f"Stylesheet applied: {stylesheet_path}")
            else:
                logger.warning(f"Stylesheet not found: {stylesheet_path}")
            
            # Set application icon
            icon_path = Path(__file__).parent / "icon" / "logo.png"
            if icon_path.exists():
                self.app.setWindowIcon(QIcon(str(icon_path)))
                logger.info(f"Application icon set: {icon_path}")
            else:
                logger.warning(f"Application icon not found: {icon_path}")
            
            # Run initial performance optimization
            logger.info("Running startup optimizations...")
            optimize_application_performance()
            
            # Initialize database
            logger.info("Initializing database...")
            if not db_manager.initialize_database():
                error_handler.handle_known_error(
                    'database_connection',
                    "Failed to initialize database",
                    parent=None
                )
                return 1
            
            # Show login dialog
            logger.info("Showing login dialog...")
            login_dialog = LoginDialog()
            
            if login_dialog.exec() == LoginDialog.Accepted:
                # Login successful, show main window
                logger.info("Login successful, showing main window...")
                self.main_window = MainWindow()
                self.main_window.show()
                
                # Start event loop
                return self.app.exec()
            else:
                # Login cancelled or failed
                logger.info("Login cancelled or failed")
                return 0
                
        except Exception as e:
            logger.error(f"Application error: {str(e)}")
            if self.app:
                QMessageBox.critical(
                    None,
                    "Application Error",
                    f"An unexpected error occurred:\n{str(e)}"
                )
            return 1
        
        finally:
            # Clean up
            if db_manager:
                db_manager.close()
            logger.info("Application shutdown complete")


def main():
    """Main entry point."""
    app = DentalManagementApp()
    sys.exit(app.run())


if __name__ == "__main__":
    main()
