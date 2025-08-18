"""
Login dialog for user authentication.
"""
import logging
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                               QLineEdit, QPushButton, QLabel, QCheckBox,
                               QMessageBox, QFrame)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QFont, QIcon
from pathlib import Path
from ..services.auth_service import auth_service

logger = logging.getLogger(__name__)


class LoginDialog(QDialog):
    """Login dialog for user authentication."""
    
    login_successful = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Dental Practice Management - Login")
        self.setFixedSize(450, 420)  # Increase height to ensure all elements are visible
        self.setWindowFlags(Qt.Dialog | Qt.MSWindowsFixedSizeDialogHint)
        
        # Set window icon
        icon_path = Path(__file__).parent.parent / "icon" / "logo.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        
        self._setup_ui()
        self._connect_signals()
        
        # Set focus to username field
        self.username_edit.setFocus()
    
    def _setup_ui(self):
        """Set up the user interface."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(30, 20, 30, 20)
        
        # Logo
        # logo_label = QLabel()
        # icon_path = Path(__file__).parent.parent / "icon" / "logo.png"
        # if icon_path.exists():
        #     pixmap = QPixmap(str(icon_path))
        #     # Scale the logo to a reasonable size (64x64 pixels)
        #     scaled_pixmap = pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        #     logo_label.setPixmap(scaled_pixmap)
        #     logo_label.setAlignment(Qt.AlignCenter)
        #     main_layout.addWidget(logo_label)
        
        # Title
        title_label = QLabel("Login")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Subtitle
        subtitle_label = QLabel("Dental Practice Management System")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("color: #666666; font-size: 12px;")
        main_layout.addWidget(subtitle_label)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separator)
        
        # Form layout with explicit label-field pairs
        form_layout = QVBoxLayout()
        form_layout.setSpacing(5)
        form_layout.setContentsMargins(10, 15, 10, 15)

        # Username section
        username_label = QLabel("Username:")
        username_label.setStyleSheet("font-weight: bold; color: #2C3E50; font-size: 14px; margin-bottom: 5px;")
        form_layout.addWidget(username_label)
        
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Enter your username")
        self.username_edit.setMinimumHeight(50)
        self.username_edit.setStyleSheet("""
            QLineEdit {
                border: 2px solid #3498DB;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                background-color: #F8F9FA;
                color: #2C3E50;
            }
            QLineEdit:focus {
                border-color: #E74C3C;
                background-color: white;
            }
        """)
        form_layout.addWidget(self.username_edit)
        
        # Password section
        password_label = QLabel("Password:")
        password_label.setStyleSheet("font-weight: bold; color: #2C3E50; font-size: 14px; margin-top: 10px; margin-bottom: 5px;")
        form_layout.addWidget(password_label)

        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Enter your password")
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setMinimumHeight(50)
        self.password_edit.setStyleSheet("""
            QLineEdit {
                border: 2px solid #27AE60;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                background-color: #F8F9FA;
                color: #2C3E50;
            }
            QLineEdit:focus {
                border-color: #E74C3C;
                background-color: white;
            }
        """)
        form_layout.addWidget(self.password_edit)
        
        main_layout.addLayout(form_layout)
        
        # Error message label
        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: red; font-size: 11px;")
        self.error_label.setWordWrap(True)
        self.error_label.hide()
        main_layout.addWidget(self.error_label)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        button_layout.setContentsMargins(0, 15, 0, 0)
        
        # Cancel button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setMinimumHeight(45)
        self.cancel_button.setMinimumWidth(120)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #95A5A6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7F8C8D;
            }
            QPushButton:pressed {
                background-color: #34495E;
            }
        """)
        button_layout.addWidget(self.cancel_button)
        
        # Login button
        self.login_button = QPushButton("Login")
        self.login_button.setMinimumHeight(45)
        self.login_button.setMinimumWidth(120)
        self.login_button.setDefault(True)
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #3498DB;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
            QPushButton:pressed {
                background-color: #21618C;
            }
        """)
        button_layout.addWidget(self.login_button)
        
        main_layout.addLayout(button_layout)
        
        # Default credentials hint
        hint_label = QLabel("Default: admin / admin123")
        hint_label.setAlignment(Qt.AlignCenter)
        hint_label.setStyleSheet("color: #888888; font-size: 10px; font-style: italic;")
        main_layout.addWidget(hint_label)
    
    def _connect_signals(self):
        """Connect UI signals to slots."""
        self.login_button.clicked.connect(self._handle_login)
        self.cancel_button.clicked.connect(self.reject)
        self.username_edit.returnPressed.connect(self._handle_login)
        self.password_edit.returnPressed.connect(self._handle_login)
    
    def _handle_login(self):
        """Handle login button click."""
        username = self.username_edit.text().strip()
        password = self.password_edit.text()
        
        # Clear previous error
        self.error_label.hide()
        
        # Validate input
        if not username:
            self._show_error("Please enter your username.")
            self.username_edit.setFocus()
            return
        
        if not password:
            self._show_error("Please enter your password.")
            self.password_edit.setFocus()
            return
        
        # Check for lockout
        if auth_service.is_locked_out():
            remaining_time = auth_service.get_lockout_time_remaining()
            if remaining_time:
                minutes = remaining_time // 60
                seconds = remaining_time % 60
                self._show_error(f"Account locked. Try again in {minutes}m {seconds}s.")
                return
        
        # Disable login button during authentication
        self.login_button.setEnabled(False)
        self.login_button.setText("Authenticating...")
        
        try:
            # Attempt authentication
            if auth_service.authenticate(username, password):
                logger.info(f"Login successful for user: {username}")
                self.login_successful.emit()
                self.accept()
            else:
                # Authentication failed
                if auth_service.is_locked_out():
                    self._show_error("Too many failed attempts. Account locked for 5 minutes.")
                else:
                    attempts_left = 3 - auth_service.failed_attempts
                    if attempts_left > 0:
                        self._show_error(f"Invalid credentials. {attempts_left} attempts remaining.")
                    else:
                        self._show_error("Invalid credentials.")
                
                self.password_edit.clear()
                self.password_edit.setFocus()
                
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            self._show_error("An error occurred during login. Please try again.")
        
        finally:
            # Re-enable login button
            self.login_button.setEnabled(True)
            self.login_button.setText("Login")
    
    def _show_error(self, message: str):
        """Show error message to user."""
        self.error_label.setText(message)
        self.error_label.show()
    
    def keyPressEvent(self, event):
        """Handle key press events."""
        if event.key() == Qt.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)
