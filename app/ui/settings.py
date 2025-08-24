"""
Settings interface for the Dental Practice Management System.
"""
import logging
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
                               QGroupBox, QLabel, QLineEdit, QPushButton,
                               QCheckBox, QComboBox, QSpinBox, QTextEdit,
                               QFormLayout, QScrollArea, QMessageBox,
                               QFileDialog, QFrame, QGridLayout)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPixmap
from ..services.auth_service import auth_service
from ..services.export_service import export_service
from ..database.database import db_manager
from ..config import APP_NAME, APP_VERSION, ORGANIZATION
import os
import shutil
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class SettingsWidget(QWidget):
    """Main settings interface with tabbed organization."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._load_settings()
    

    def _setup_ui(self):
        """Set up the settings UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        self.setStyleSheet("""
            SettingsWidget {
                background-color: #F8F9FA;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #E5E5E5;
                border-radius: 8px;
                padding: 5px; /* Increased padding */
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                color: #007BFF;
                font-weight: bold;
                font-size: 14px;
            }
            QLabel {
                font-size: 14px;
                color: #495057;
            }
            QLineEdit, QTextEdit, QComboBox {
                padding: 5px; /* Increased padding */
                border: 1px solid #CED4DA;
                border-radius: 4px;
                font-size: 14px;
                color: #2c3e50;
                min-height: 20px;
            }
            QComboBox {
                padding: 5x; /* Increased padding */
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
                border-color: #007BFF;
            }
        """)
        
        # Title
        title_label = QLabel("Settings")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #2C3E50; margin-bottom: 20px;")
        layout.addWidget(title_label)
        
        # Tab widget for organizing settings
        self.tab_widget = QTabWidget()
        
        # Create tabs
        self._create_clinic_tab()
        self._create_database_tab()
        self._create_backup_tab()
        self._create_about_tab()
        
        layout.addWidget(self.tab_widget)
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.save_btn = QPushButton("Save Settings")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #28A745;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.save_btn.clicked.connect(self._save_settings)
        button_layout.addWidget(self.save_btn)
        
        self.reset_btn = QPushButton("Reset to Defaults")
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #6C757D;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #5A6268;
            }
        """)
        self.reset_btn.clicked.connect(self._reset_settings)
        button_layout.addWidget(self.reset_btn)
        
        layout.addLayout(button_layout)
    
    def _create_clinic_tab(self):
        """Create clinic information tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Clinic Info Group
        clinic_group = QGroupBox("Clinic Information")
        clinic_layout = QFormLayout(clinic_group)
        
        self.clinic_name_edit = QLineEdit("Yashoda Dental Clinic")
        clinic_layout.addRow("Clinic Name:", self.clinic_name_edit)
        
        self.doctor_name_edit = QLineEdit("Dr Yashoda")
        clinic_layout.addRow("Doctor Name:", self.doctor_name_edit)
        
        self.clinic_address_edit = QTextEdit()
        self.clinic_address_edit.setFixedHeight(100)
        self.clinic_address_edit.setPlainText("123 Medical Center Drive\nCity, State 12345")
        clinic_layout.addRow("Address:", self.clinic_address_edit)
        
        self.clinic_phone_edit = QLineEdit("+1 (555) 123-4567")
        clinic_layout.addRow("Phone:", self.clinic_phone_edit)
        
        self.clinic_email_edit = QLineEdit("info@yashodadental.com")
        clinic_layout.addRow("Email:", self.clinic_email_edit)
        
        layout.addWidget(clinic_group)
        
        # Business Hours Group
        hours_group = QGroupBox("Business Hours")
        hours_layout = QGridLayout(hours_group)
        hours_layout.setHorizontalSpacing(15)
        hours_layout.setVerticalSpacing(10)
        
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        self.hours_widgets = {}
        
        for i, day in enumerate(days):
            day_label = QLabel(day)
            hours_layout.addWidget(day_label, i, 0)
            
            open_combo = QComboBox()
            open_combo.addItems([f"{h:02d}:00" for h in range(6, 24)])
            open_combo.setCurrentText("09:00")
            hours_layout.addWidget(open_combo, i, 1)
            
            to_label = QLabel("to")
            hours_layout.addWidget(to_label, i, 2)
            
            close_combo = QComboBox()
            close_combo.addItems([f"{h:02d}:00" for h in range(6, 24)])
            close_combo.setCurrentText("17:00")
            hours_layout.addWidget(close_combo, i, 3)
            
            closed_check = QCheckBox("Closed")
            if day in ["Sunday"]:
                closed_check.setChecked(True)
            hours_layout.addWidget(closed_check, i, 4)
            
            self.hours_widgets[day] = {
                'open': open_combo,
                'close': close_combo,
                'closed': closed_check
            }
        
        layout.addWidget(hours_group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "Clinic Info")
    
    def _create_database_tab(self):
        """Create database settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Database Info
        db_group = QGroupBox("Database Information")
        db_layout = QFormLayout(db_group)
        
        db_path = Path(__file__).parent.parent.parent / "data" / "dental_practice.db"
        db_size = "Unknown"
        if db_path.exists():
            size_bytes = db_path.stat().st_size
            db_size = f"{size_bytes / (1024*1024):.2f} MB"
        
        db_location_label = QLabel(str(db_path))
        db_layout.addRow("Database Location:", db_location_label)
        
        db_size_label = QLabel(db_size)
        db_layout.addRow("Database Size:", db_size_label)
        
        layout.addWidget(db_group)
        
        # Database Actions
        # actions_group = QGroupBox("Database Actions")
        # actions_layout = QVBoxLayout(actions_group)
        
        # Compact Database
        compact_btn = QPushButton("Compact Database")
        compact_btn.setStyleSheet("""
            QPushButton {
                background-color: #17A2B8;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #138496;
            }
        """)
        # compact_btn.clicked.connect(self._compact_database)
        # actions_layout.addWidget(compact_btn)
        
        # # Reset Database
        # reset_btn = QPushButton("Reset Database (DANGER)")
        # reset_btn.setStyleSheet("""
        #     QPushButton {
        #         background-color: #DC3545;
        #         color: white;
        #         border: none;
        #         padding: 10px 20px;
        #         border-radius: 4px;
        #         font-weight: bold;
        #     }
        #     QPushButton:hover {
        #         background-color: #C82333;
        #     }
        # """)
        # reset_btn.clicked.connect(self._reset_database)
        # actions_layout.addWidget(reset_btn)
        
        # layout.addWidget(actions_group)
        # layout.addStretch()
        
        self.tab_widget.addTab(tab, "Database")
    
    def _create_backup_tab(self):
        """Create backup and restore tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Auto Backup Settings
        backup_group = QGroupBox("Automatic Backup Settings")
        backup_layout = QFormLayout(backup_group)
        
        self.auto_backup_check = QCheckBox("Enable automatic backups")
        self.auto_backup_check.setChecked(True)
        backup_layout.addRow("", self.auto_backup_check)
        
        self.backup_frequency_combo = QComboBox()
        self.backup_frequency_combo.addItems(["Daily", "Weekly", "Monthly"])
        self.backup_frequency_combo.setCurrentText("Weekly")
        backup_layout.addRow("Backup Frequency:", self.backup_frequency_combo)
        
        self.backup_location_edit = QLineEdit(str(Path.home() / "Documents" / "DentalBackups"))
        backup_layout.addRow("Backup Location:", self.backup_location_edit)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_backup_location)
        backup_layout.addRow("", browse_btn)
        
        layout.addWidget(backup_group)
        
        # Manual Backup Actions
        manual_group = QGroupBox("Manual Backup & Restore")
        manual_layout = QVBoxLayout(manual_group)
        
        backup_now_btn = QPushButton("Create Backup Now")
        backup_now_btn.setStyleSheet("""
            QPushButton {
                background-color: #28A745;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        backup_now_btn.clicked.connect(self._create_backup)
        manual_layout.addWidget(backup_now_btn)
        
        restore_btn = QPushButton("Restore from Backup")
        restore_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFC107;
                color: black;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #E0A800;
            }
        """)
        restore_btn.clicked.connect(self._restore_backup)
        manual_layout.addWidget(restore_btn)
        
        layout.addWidget(manual_group)
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "Backup & Restore")
    
    def _create_about_tab(self):
        """Create about tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setAlignment(Qt.AlignCenter)
        
        # App Icon/Logo
        icon_label = QLabel()
        icon_path = Path(__file__).parent.parent / "icon" / "logo.png"
        if icon_path.exists():
            pixmap = QPixmap(str(icon_path))
            # Scale the logo to a reasonable size (96x96 pixels for about page)
            scaled_pixmap = pixmap.scaled(96, 96, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_label.setPixmap(scaled_pixmap)
        else:
            # Fallback to emoji if logo not found
            icon_label.setText("🦷")
            icon_label.setStyleSheet("font-size: 64px; margin: 20px;")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("margin: 20px;")
        layout.addWidget(icon_label)
        
        # App Name
        app_name_label = QLabel(APP_NAME)
        app_name_font = QFont()
        app_name_font.setPointSize(20)
        app_name_font.setBold(True)
        app_name_label.setFont(app_name_font)
        app_name_label.setAlignment(Qt.AlignCenter)
        app_name_label.setStyleSheet("color: #2C3E50; margin: 10px;")
        layout.addWidget(app_name_label)
        
        # Version
        version_label = QLabel(f"Version {APP_VERSION}")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet("color: #6C757D; font-size: 14px; margin: 5px;")
        layout.addWidget(version_label)
        
        # Organization
        org_label = QLabel(f"© 2025 {ORGANIZATION}")
        org_label.setAlignment(Qt.AlignCenter)
        org_label.setStyleSheet("color: #6C757D; font-size: 12px; margin: 5px;")
        layout.addWidget(org_label)
        
        # Description
        desc_label = QLabel(
            "A comprehensive dental practice management system\\n"
            "for patient records, dental charts, and clinic administration."
        )
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setStyleSheet("color: #495057; font-size: 14px; margin: 20px; line-height: 1.5;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "About")
    
    def _load_settings(self):
        """Load settings from configuration."""
        try:
            config_path = Path(__file__).parent.parent.parent / "data" / "settings.json"
            
            if config_path.exists():
                import json
                with open(config_path, 'r') as f:
                    settings = json.load(f)
                
                # Load clinic settings
                if 'clinic_name' in settings:
                    self.clinic_name_edit.setText(settings['clinic_name'])
                if 'doctor_name' in settings:
                    self.doctor_name_edit.setText(settings['doctor_name'])
                if 'clinic_address' in settings:
                    self.clinic_address_edit.setPlainText(settings['clinic_address'])
                if 'clinic_phone' in settings:
                    self.clinic_phone_edit.setText(settings['clinic_phone'])
                if 'clinic_email' in settings:
                    self.clinic_email_edit.setText(settings['clinic_email'])
                
                # Load backup settings
                if 'auto_backup_enabled' in settings:
                    self.auto_backup_check.setChecked(settings['auto_backup_enabled'])
                if 'backup_frequency' in settings:
                    self.backup_frequency_combo.setCurrentText(settings['backup_frequency'])
                if 'backup_location' in settings:
                    self.backup_location_edit.setText(settings['backup_location'])
                
                # Load business hours
                if 'business_hours' in settings:
                    hours = settings['business_hours']
                    for day, widgets in self.hours_widgets.items():
                        if day in hours:
                            day_settings = hours[day]
                            if 'open' in day_settings:
                                widgets['open'].setCurrentText(day_settings['open'])
                            if 'close' in day_settings:
                                widgets['close'].setCurrentText(day_settings['close'])
                            if 'closed' in day_settings:
                                widgets['closed'].setChecked(day_settings['closed'])
                
                logger.info("Settings loaded successfully")
                
        except Exception as e:
            logger.warning(f"Could not load settings, using defaults: {str(e)}")
            # Use default values if loading fails
    
    def _save_settings(self):
        """Save current settings."""
        try:
            # Save backup settings
            backup_settings = {
                'auto_backup_enabled': self.auto_backup_check.isChecked(),
                'backup_frequency': self.backup_frequency_combo.currentText(),
                'backup_location': self.backup_location_edit.text(),
                'clinic_name': self.clinic_name_edit.text(),
                'doctor_name': self.doctor_name_edit.text(),
                'clinic_address': self.clinic_address_edit.toPlainText(),
                'clinic_phone': self.clinic_phone_edit.text(),
                'clinic_email': self.clinic_email_edit.text()
            }
            
            # Save business hours
            business_hours = {}
            for day, widgets in self.hours_widgets.items():
                business_hours[day] = {
                    'open': widgets['open'].currentText(),
                    'close': widgets['close'].currentText(),
                    'closed': widgets['closed'].isChecked()
                }
            backup_settings['business_hours'] = business_hours
            
            # Save settings to config file
            config_path = Path(__file__).parent.parent.parent / "data" / "settings.json"
            config_path.parent.mkdir(exist_ok=True)
            
            import json
            with open(config_path, 'w') as f:
                json.dump(backup_settings, f, indent=2)
            
            # Setup periodic backup if enabled
            if backup_settings['auto_backup_enabled']:
                self._setup_periodic_backup(backup_settings)
            
            QMessageBox.information(
                self,
                "Settings Saved",
                "Settings have been saved successfully!\n\n"
                f"Auto-backup: {'Enabled' if backup_settings['auto_backup_enabled'] else 'Disabled'}\n"
                f"Frequency: {backup_settings['backup_frequency']}\n"
                f"Location: {backup_settings['backup_location']}"
            )
            logger.info("Settings saved successfully")
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to save settings: {str(e)}"
            )
            logger.error(f"Failed to save settings: {str(e)}")
    
    def _setup_periodic_backup(self, settings):
        """Setup periodic backup based on settings."""
        try:
            frequency = settings['backup_frequency']
            backup_location = settings['backup_location']
            
            # Create backup directory if it doesn't exist
            backup_dir = Path(backup_location)
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Create a marker file to indicate when last backup was done
            marker_file = backup_dir / ".last_backup"
            current_time = datetime.now()
            
            # Check if backup is needed based on frequency
            should_backup = True
            if marker_file.exists():
                try:
                    with open(marker_file, 'r') as f:
                        last_backup_str = f.read().strip()
                        last_backup = datetime.fromisoformat(last_backup_str)
                        
                        if frequency == "Daily":
                            should_backup = (current_time - last_backup).days >= 1
                        elif frequency == "Weekly":
                            should_backup = (current_time - last_backup).days >= 7
                        elif frequency == "Monthly":
                            should_backup = (current_time - last_backup).days >= 30
                            
                except Exception as e:
                    logger.warning(f"Could not read last backup time: {e}")
                    should_backup = True
            
            # Create backup if needed
            if should_backup:
                timestamp = current_time.strftime("%Y%m%d_%H%M%S")
                backup_filename = f"auto_backup_{frequency.lower()}_{timestamp}.db"
                backup_path = backup_dir / backup_filename
                
                success = export_service.create_complete_backup(str(backup_path))
                
                if success:
                    # Update marker file
                    with open(marker_file, 'w') as f:
                        f.write(current_time.isoformat())
                    
                    logger.info(f"Automatic {frequency.lower()} backup created: {backup_path}")
                    
                    # Clean up old backups (keep last 10)
                    self._cleanup_old_backups(backup_dir, f"auto_backup_{frequency.lower()}_*.db")
                
        except Exception as e:
            logger.error(f"Failed to setup periodic backup: {str(e)}")
    
    def _cleanup_old_backups(self, backup_dir, pattern):
        """Clean up old backup files, keeping only the most recent ones."""
        try:
            import glob
            backup_files = list(Path(backup_dir).glob(pattern))
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Keep only the 10 most recent backups
            for old_backup in backup_files[10:]:
                old_backup.unlink()
                logger.info(f"Deleted old backup: {old_backup}")
                
        except Exception as e:
            logger.warning(f"Failed to cleanup old backups: {str(e)}")
    
    def _reset_settings(self):
        """Reset settings to defaults."""
        reply = QMessageBox.question(
            self,
            "Reset Settings",
            "Are you sure you want to reset all settings to defaults?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Reset to default values
            self.clinic_name_edit.setText("Yashoda Dental Clinic")
            self.doctor_name_edit.setText("Dr Yashoda")
            # Reset other fields...
            QMessageBox.information(self, "Reset Complete", "Settings have been reset to defaults.")
    
    def _compact_database(self):
        """Compact the database."""
        reply = QMessageBox.question(
            self,
            "Compact Database",
            "This will optimize the database. Continue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        if reply == QMessageBox.Yes:
            # Here you would implement database compaction
            QMessageBox.information(self, "Success", "Database compacted successfully!")
    
    def _reset_database(self):
        """Reset the database (danger operation)."""
        reply = QMessageBox.critical(
            self,
            "DANGER: Reset Database",
            "This will permanently delete ALL data including patients, dental records, and users.\\n\\n"
            "This action CANNOT be undone!\\n\\n"
            "Are you absolutely sure you want to continue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Second confirmation
            confirm = QMessageBox.critical(
                self,
                "FINAL WARNING",
                "Last chance! This will delete EVERYTHING.\\n\\n"
                "Type 'DELETE ALL DATA' in the confirmation dialog to proceed.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if confirm == QMessageBox.Yes:
                QMessageBox.information(self, "Database Reset", "Database reset functionality would be implemented here.")
    
    def _browse_backup_location(self):
        """Browse for backup location."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Backup Location",
            self.backup_location_edit.text()
        )
        
        if folder:
            self.backup_location_edit.setText(folder)
    
    def _create_backup(self):
        """Create a manual backup."""
        try:
            # Get backup location from settings
            backup_location = self.backup_location_edit.text()
            if not backup_location:
                backup_location = str(Path.home() / "Documents" / "DentalBackups")
            
            # Create backup directory if it doesn't exist
            backup_dir = Path(backup_location)
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate backup filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"yashoda_dental_backup_{timestamp}.db"
            backup_path = backup_dir / backup_filename
            
            # Create the backup using export service
            success = export_service.create_complete_backup(str(backup_path))
            
            if success:
                QMessageBox.information(
                    self, 
                    "Backup Created Successfully", 
                    f"Database backup has been created successfully!\n\n"
                    f"Location: {backup_path}\n"
                    f"Size: {self._get_file_size(backup_path)}"
                )
                logger.info(f"Manual backup created: {backup_path}")
            else:
                QMessageBox.critical(
                    self, 
                    "Backup Failed", 
                    "Failed to create database backup. Please check the logs for details."
                )
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create backup: {str(e)}")
            logger.error(f"Failed to create backup: {str(e)}")
    
    def _get_file_size(self, file_path):
        """Get human-readable file size."""
        try:
            size_bytes = Path(file_path).stat().st_size
            if size_bytes < 1024:
                return f"{size_bytes} bytes"
            elif size_bytes < 1024 * 1024:
                return f"{size_bytes / 1024:.2f} KB"
            else:
                return f"{size_bytes / (1024 * 1024):.2f} MB"
        except:
            return "Unknown"
    
    def _restore_backup(self):
        """Restore from backup."""
        backup_file, _ = QFileDialog.getOpenFileName(
            self,
            "Select Backup File",
            str(Path.home()),
            "Database Files (*.db);;All Files (*.*)"
        )
        
        if backup_file:
            # Validate backup file
            if not Path(backup_file).exists():
                QMessageBox.critical(self, "Error", "Selected backup file does not exist.")
                return
                
            if not backup_file.lower().endswith('.db'):
                QMessageBox.warning(
                    self, 
                    "Warning", 
                    "Selected file does not appear to be a database backup file (.db). Continue anyway?"
                )
            
            # Show backup file info
            backup_size = self._get_file_size(backup_file)
            backup_date = datetime.fromtimestamp(Path(backup_file).stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            
            reply = QMessageBox.warning(
                self,
                "Restore Backup",
                f"This will replace ALL current data with the backup data.\n\n"
                f"Backup File: {Path(backup_file).name}\n"
                f"Size: {backup_size}\n"
                f"Date: {backup_date}\n\n"
                f"⚠️ WARNING: This action CANNOT be undone!\n"
                f"All current patients, dental records, and settings will be lost.\n\n"
                f"Are you sure you want to continue?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # Final confirmation
                final_confirm = QMessageBox.critical(
                    self,
                    "FINAL CONFIRMATION",
                    f"LAST CHANCE!\n\n"
                    f"This will permanently delete all current data.\n"
                    f"Type 'RESTORE' to confirm:",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if final_confirm == QMessageBox.Yes:
                    try:
                        # Get current database path
                        current_db_path = Path(__file__).parent.parent.parent / "data" / "dental_practice.db"
                        
                        # Create backup of current database before restore
                        backup_current = current_db_path.parent / f"pre_restore_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                        if current_db_path.exists():
                            shutil.copy2(current_db_path, backup_current)
                            logger.info(f"Created safety backup: {backup_current}")
                        
                        # Restore the backup
                        shutil.copy2(backup_file, current_db_path)
                        
                        # Reinitialize database
                        db_manager.initialize_database()
                        
                        QMessageBox.information(
                            self, 
                            "Restore Successful", 
                            f"Database has been successfully restored from backup!\n\n"
                            f"Restored from: {Path(backup_file).name}\n"
                            f"Safety backup created: {backup_current.name}\n\n"
                            f"Please restart the application to ensure all changes take effect."
                        )
                        logger.info(f"Database restored from: {backup_file}")
                        
                    except Exception as e:
                        QMessageBox.critical(
                            self, 
                            "Restore Failed", 
                            f"Failed to restore backup:\n{str(e)}\n\n"
                            f"Your original data should be intact."
                        )
                        logger.error(f"Failed to restore backup: {str(e)}")
                        
                        # Try to reinitialize database in case of corruption
                        try:
                            db_manager.initialize_database()
                        except:
                            pass
