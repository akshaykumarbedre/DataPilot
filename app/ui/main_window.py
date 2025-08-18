"""
Main application window with navigation and content areas.
"""
import logging
from PySide6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                               QStackedWidget, QLabel, QPushButton, QFrame,
                               QMenuBar, QStatusBar, QMessageBox, QSplitter)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QAction, QIcon
from pathlib import Path
from ..services.auth_service import auth_service
from ..config import APP_NAME, APP_VERSION
from .patient_management import PatientManagement
from .dashboard import Dashboard
from .dental_chart import DentalChart
from .settings import SettingsWidget
from .dialogs import ExportDialog

logger = logging.getLogger(__name__)


class CombinedHeaderNavigation(QWidget):
    """Combined header and navigation widget in a single row."""
    
    page_changed = Signal(str)
    logout_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(60)
        self.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
                border-bottom: 1px solid #E5E5E5;
              
            }
        """)
        
        self.navigation_buttons = {}
        self.current_page = 'dashboard'
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the combined header and navigation UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(15)
        
        # App title/welcome message
        self.welcome_label = QLabel()
        self.welcome_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2C3E50;")
        layout.addWidget(self.welcome_label)
        
        # Navigation buttons
        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(10)
        
        nav_items = [
            ('dashboard', 'Dashboard', '🏠'),
            ('patients', 'Patients', '👥'),
            ('examination', 'Dental Chart', '🦷'),
            ('settings', 'Settings', '⚙️')
        ]
        
        for page_name, title, icon in nav_items:
            btn = QPushButton(f"{icon} {title}")
            btn.setCheckable(True)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #2C3E50;
                    border: 2px solid transparent;
                    padding: 8px 16px;
                    border-radius: 8px;
                    font-weight: 600;
                    font-size: 14px;
                    min-width: 100px;
                }
                QPushButton:hover {
                    background-color: #F8F9FA;
                    border: 2px solid #E9ECEF;
                    color: #495057;
                }
                QPushButton:checked {
                    background-color: #007BFF;
                    border: 2px solid #007BFF;
                    color: white;
                }
            """)
            btn.clicked.connect(lambda checked, name=page_name: self._handle_navigation(name))
            self.navigation_buttons[page_name] = btn
            nav_layout.addWidget(btn)
        
        # Set dashboard as default
        self.navigation_buttons['dashboard'].setChecked(True)
        
        layout.addLayout(nav_layout)
        layout.addStretch()
        
        # User info and logout button
        user_layout = QHBoxLayout()
        user_layout.setSpacing(10)
        
        self.user_label = QLabel()
        self.user_label.setStyleSheet("font-size: 14px; color: #6C757D;")
        user_layout.addWidget(self.user_label)
        
        self.logout_btn = QPushButton("Logout")
        self.logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #DC3545;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #C82333;
                transform: translateY(-1px);
            }
        """)
        self.logout_btn.clicked.connect(self.logout_requested.emit)
        user_layout.addWidget(self.logout_btn)
        
        layout.addLayout(user_layout)
        
        self._update_user_info()
    
    def _handle_navigation(self, page_name: str):
        """Handle navigation button clicks."""
        if page_name == self.current_page:
            return
        
        self.current_page = page_name
        
        # Update button states
        for name, button in self.navigation_buttons.items():
            button.setChecked(name == page_name)
        
        # Emit page change signal
        self.page_changed.emit(page_name)
    
    def _update_user_info(self):
        """Update user information display."""
        current_user = auth_service.get_current_user()
        if current_user:
            self.welcome_label.setText(f"Yashoda Dental Clinic")
            self.welcome_label.setStyleSheet("font-weight: bold; font-size: 18px; color: #2c3e50; background-color: #f0f0f0;")
            
            self.user_label.setText(f"Logged in as: {current_user['username']}")
            self.welcome_label.setStyleSheet("background-color: #f0f0f0;")

        else:
            self.welcome_label.setText("Yashoda Dental Clinic")
            self.welcome_label.setStyleSheet("font-weight: bold; font-size: 18px; color: #2c3e50; background-color: #f0f0f0;")
            self.user_label.setText("")


class PlaceholderWidget(QWidget):
    """Placeholder widget for content areas."""
    
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        
        label = QLabel(f"{title} Content")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 24px; color: #7F8C8D;")
        layout.addWidget(label)
        
        description = QLabel(f"This will contain the {title.lower()} interface.")
        description.setAlignment(Qt.AlignCenter)
        description.setStyleSheet("font-size: 14px; color: #BDC3C7;")
        layout.addWidget(description)


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        # Set window icon
        icon_path = Path(__file__).parent.parent / "icon" / "logo.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        
        self._setup_ui()
        self._connect_signals()
        
        logger.info("Main window initialized")
    
    def _setup_ui(self):
        """Set up the main window UI."""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Combined header and navigation
        self.header_nav = CombinedHeaderNavigation()
        main_layout.addWidget(self.header_nav)
        
        # Main content area
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("background-color: white;")
        
        # Add placeholder pages
        self.dashboard_page = Dashboard()  # Use actual dashboard
        self.patients_page = PatientManagement()  # Use actual patient management
        self.examination_page = DentalChart()  # Use actual dental chart
        self.settings_page = SettingsWidget()  # Use actual settings widget
        
        self.content_stack.addWidget(self.dashboard_page)
        self.content_stack.addWidget(self.patients_page)
        self.content_stack.addWidget(self.examination_page)
        self.content_stack.addWidget(self.settings_page)
        
        main_layout.addWidget(self.content_stack)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Menu bar
        self._setup_menu_bar()
    
    def _setup_menu_bar(self):
        """Set up the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        # Export & Backup submenu
        export_action = QAction("Export & Backup...", self)
        export_action.triggered.connect(self._show_export_dialog)
        file_menu.addAction(export_action)
        
        backup_action = QAction("Quick Backup", self)
        backup_action.triggered.connect(self._backup_database)
        file_menu.addAction(backup_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _connect_signals(self):
        """Connect window signals."""
        self.header_nav.page_changed.connect(self._handle_page_change)
        self.header_nav.logout_requested.connect(self._handle_logout)
        
        # Connect dashboard navigation signals
        self.dashboard_page.navigate_to_patients.connect(self._navigate_to_patients)
        self.dashboard_page.navigate_to_examination.connect(self._navigate_to_examination)
        
        # Connect patient management signals
        self.patients_page.examine_patient.connect(self._examine_patient)
    
    def _handle_page_change(self, page_name: str):
        """Handle navigation page changes."""
        page_map = {
            'dashboard': 0,
            'patients': 1,
            'examination': 2,
            'settings': 3
        }
        
        if page_name in page_map:
            self.content_stack.setCurrentIndex(page_map[page_name])
            self.status_bar.showMessage(f"Viewing {page_name.title()}")
            logger.info(f"Navigated to {page_name}")
    
    def _navigate_to_patients(self):
        """Navigate to patients page from dashboard."""
        # Update navigation button state
        self.header_nav._handle_navigation('patients')
        
        # Switch to patients page
        self.content_stack.setCurrentIndex(1)
        self.status_bar.showMessage("Viewing Patients")
        logger.info("Navigated to patients from dashboard")
    
    def _navigate_to_examination(self):
        """Navigate to examination page from dashboard."""
        # Update navigation button state
        self.header_nav._handle_navigation('examination')
        
        # Switch to examination page
        self.content_stack.setCurrentIndex(2)
        self.status_bar.showMessage("Viewing Examination")
        logger.info("Navigated to examination from dashboard")
    
    def _examine_patient(self, patient: dict):
        """Navigate to examination page with specific patient selected."""
        # Update navigation button state
        self.header_nav._handle_navigation('examination')
        
        # Switch to examination page
        self.content_stack.setCurrentIndex(2)
        
        # Set the patient in the dental chart
        self.examination_page.set_patient(patient)
        
        self.status_bar.showMessage(f"Examining patient: {patient['full_name']}")
        logger.info(f"Navigated to examination for patient: {patient['patient_id']}")
    
    def _handle_logout(self):
        """Handle logout request."""
        reply = QMessageBox.question(
            self,
            "Confirm Logout",
            "Are you sure you want to logout?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            auth_service.logout()
            self.close()
    
    def _backup_database(self):
        """Create database backup."""
        try:
            from ..database.database import db_manager
            from pathlib import Path
            import datetime
            
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = Path.home() / "Desktop" / f"dental_backup_{timestamp}.db"
            
            if db_manager.backup_database(backup_path):
                QMessageBox.information(
                    self,
                    "Backup Successful",
                    f"Database backed up to:\n{backup_path}"
                )
            else:
                QMessageBox.warning(
                    self,
                    "Backup Failed",
                    "Failed to create database backup."
                )
        except Exception as e:
            logger.error(f"Backup error: {str(e)}")
            QMessageBox.critical(
                self,
                "Backup Error",
                f"An error occurred during backup:\n{str(e)}"
            )
    
    def _show_export_dialog(self):
        """Show export and backup dialog."""
        try:
            export_dialog = ExportDialog(self)
            export_dialog.exec()
        except Exception as e:
            logger.error(f"Export dialog error: {str(e)}")
            QMessageBox.critical(
                self,
                "Export Error", 
                f"Failed to open export dialog:\n{str(e)}"
            )
    
    def _show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About",
            f"{APP_NAME}\n"
            f"Version {APP_VERSION}\n\n"
            "A comprehensive dental practice management system\n"
            "built with PySide6 and SQLite.\n\n"
            "© 2025 Dental Solutions"
        )
    
    def closeEvent(self, event):
        """Handle window close event."""
        reply = QMessageBox.question(
            self,
            "Confirm Exit",
            "Are you sure you want to exit?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            auth_service.logout()
            event.accept()
        else:
            event.ignore()
