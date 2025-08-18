"""
Dashboard interface with statistics and quick actions.
"""
import logging
import os
import shutil
from datetime import datetime
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QFrame, QGridLayout, QScrollArea,
                               QGroupBox, QMessageBox, QFileDialog)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QPalette
from ..services.patient_service import patient_service
from .dialogs import ExportDialog

logger = logging.getLogger(__name__)


class StatCard(QFrame):
    """Statistics card widget."""
    
    def __init__(self, title: str, value: str, color: str = "#3498DB", parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Box)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                border-left: 4px solid {color};
            }}
        """)
        self.setFixedHeight(120)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(5)
        
        # Value label
        self.value_label = QLabel(value)
        value_font = QFont()
        value_font.setPointSize(24)
        value_font.setBold(True)
        self.value_label.setFont(value_font)
        self.value_label.setStyleSheet(f"color: {color};")
        self.value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.value_label)
        
        # Title label
        title_label = QLabel(title)
        title_font = QFont()
        title_font.setPointSize(12)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #7F8C8D;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
    
    def update_value(self, value: str):
        """Update the card value."""
        self.value_label.setText(value)


class QuickActionButton(QPushButton):
    """Quick action button with custom styling."""
    
    def __init__(self, text: str, description: str, icon: str = "📋", parent=None):
        super().__init__(parent)
        self.setText(f"{icon}  {text}")
        self.setToolTip(description)
        self.setMinimumHeight(60)
        self.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                text-align: left;
                padding: 15px 20px;
                font-size: 14px;
                font-weight: bold;
                color: #2C3E50;
            }
            QPushButton:hover {
                border-color: #3498DB;
                background-color: #F8F9FF;
            }
            QPushButton:pressed {
                background-color: #E3F2FD;
            }
        """)


class RecentPatientsWidget(QGroupBox):
    """Widget showing recent patients."""
    
    patient_selected = Signal(dict)
    
    def __init__(self, parent=None):
        super().__init__("Recent Patients", parent)
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 10px;
                color: #2C3E50;
            }
        """)
        
        self._setup_ui()
        self._load_recent_patients()
    
    def _setup_ui(self):
        """Set up the recent patients UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 20, 15, 15)
        layout.setSpacing(5)
        
        # Scroll area for patients
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        self.patients_widget = QWidget()
        self.patients_layout = QVBoxLayout(self.patients_widget)
        self.patients_layout.setContentsMargins(0, 0, 0, 0)
        self.patients_layout.setSpacing(5)
        
        scroll.setWidget(self.patients_widget)
        layout.addWidget(scroll)
        
        # No patients message
        self.no_patients_label = QLabel("No patients found")
        self.no_patients_label.setAlignment(Qt.AlignCenter)
        self.no_patients_label.setStyleSheet("color: #BDC3C7; font-style: italic;")
        self.no_patients_label.hide()
        layout.addWidget(self.no_patients_label)
    
    def _load_recent_patients(self):
        """Load recent patients."""
        try:
            patients = patient_service.get_recent_patients(5)
            
            # Clear existing patients
            for i in reversed(range(self.patients_layout.count())):
                item = self.patients_layout.itemAt(i)
                if item and item.widget():
                    item.widget().setParent(None)
                else:
                    self.patients_layout.removeItem(item)
            
            if not patients:
                self.no_patients_label.show()
                return
            
            self.no_patients_label.hide()
            
            for patient in patients:
                patient_widget = self._create_patient_item(patient)
                self.patients_layout.addWidget(patient_widget)
            
            # Add stretch to push items to top
            self.patients_layout.addStretch()
            
        except Exception as e:
            logger.error(f"Error loading recent patients: {str(e)}")
    
    def _create_patient_item(self, patient: dict) -> QWidget:
        """Create a patient item widget."""
        widget = QFrame()
        widget.setStyleSheet("""
            QFrame {
                background-color: #F8F9FA;
                border: 1px solid #E9ECEF;
                border-radius: 4px;
                padding: 5px;
            }
            QFrame:hover {
                background-color: #E9ECEF;
                border-color: #3498DB;
            }
        """)
        widget.setFixedHeight(120)
        widget.setCursor(Qt.PointingHandCursor)
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(10)
        
        # Patient name
        name_label = QLabel(patient['full_name'])
        name_font = QFont()
        name_font.setBold(True)
        name_label.setFont(name_font)
        name_label.setStyleSheet("color: #2C3E50;")
        layout.addWidget(name_label)
        
        # Patient details
        details = f"ID: {patient['patient_id']} • Phone: {patient['phone_number']}"
        details_label = QLabel(details)
        details_label.setStyleSheet("color: #7F8C8D; font-size: 11px;")
        layout.addWidget(details_label)
        
        # Make clickable
        widget.mousePressEvent = lambda event: self.patient_selected.emit(patient)
        
        return widget
    
    def refresh(self):
        """Refresh the recent patients list."""
        self._load_recent_patients()


class Dashboard(QWidget):
    """Dashboard widget with statistics and quick actions."""
    
    navigate_to_patients = Signal()
    navigate_to_examination = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.stat_cards = {}
        
        self._setup_ui()
        self._connect_signals()
        self._setup_auto_refresh()
        self._refresh_stats()
    
    def _setup_ui(self):
        """Set up the dashboard UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(25)
        
        # Header
        header_label = QLabel("Dashboard")
        header_font = QFont()
        header_font.setPointSize(24)
        header_font.setBold(True)
        header_label.setFont(header_font)
        header_label.setStyleSheet("color: #2C3E50; margin-bottom: 10px;")
        main_layout.addWidget(header_label)
        
        # Statistics cards
        stats_layout = QGridLayout()
        stats_layout.setSpacing(20)
        
        # Total Patients
        self.stat_cards['patients'] = StatCard("Total Patients", "0", "#3498DB")
        stats_layout.addWidget(self.stat_cards['patients'], 0, 0)
        
        # New This Month (placeholder)
        self.stat_cards['new_month'] = StatCard("New This Month", "0", "#2ECC71")
        stats_layout.addWidget(self.stat_cards['new_month'], 0, 1)
        
        # Examinations (placeholder)
        self.stat_cards['examinations'] = StatCard("Total Examinations", "0", "#F39C12")
        stats_layout.addWidget(self.stat_cards['examinations'], 0, 2)
        
        # Active Records (placeholder)
        self.stat_cards['active'] = StatCard("Active Records", "0", "#9B59B6")
        stats_layout.addWidget(self.stat_cards['active'], 0, 3)
        
        main_layout.addLayout(stats_layout)
        
        # Content area
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)
        
        # Quick Actions
        actions_group = QGroupBox("Quick Actions")
        actions_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 10px;
                color: #2C3E50;
            }
        """)
        
        actions_layout = QVBoxLayout(actions_group)
        actions_layout.setContentsMargins(15, 20, 15, 15)
        actions_layout.setSpacing(10)
        
        self.manage_patients_btn = QuickActionButton(
            "Manage Patients",
            "View, add, edit, and delete patient records",
            "👥"
        )
        actions_layout.addWidget(self.manage_patients_btn)
        
        self.start_exam_btn = QuickActionButton(
            "Start Examination",
            "Begin a new dental examination",
            "🦷"
        )
        actions_layout.addWidget(self.start_exam_btn)
        
        # self.view_reports_btn = QuickActionButton(
        #     "View Reports",
        #     "Generate and view patient reports",
        #     "📊"
        # )
        # actions_layout.addWidget(self.view_reports_btn)
        
        self.backup_data_btn = QuickActionButton(
            "Export & Backup",
            "Export data and create database backups",
            "💾"
        )
        actions_layout.addWidget(self.backup_data_btn)
        
        actions_layout.addStretch()
        
        content_layout.addWidget(actions_group, 1)
        
        # Recent Patients
        self.recent_patients = RecentPatientsWidget()
        content_layout.addWidget(self.recent_patients, 2)
        
        main_layout.addLayout(content_layout)
    
    def _connect_signals(self):
        """Connect dashboard signals."""
        self.manage_patients_btn.clicked.connect(self.navigate_to_patients.emit)
        self.start_exam_btn.clicked.connect(self.navigate_to_examination.emit)
        # self.view_reports_btn.clicked.connect(self._handle_view_reports)
        self.backup_data_btn.clicked.connect(self._handle_backup_data)
        self.recent_patients.patient_selected.connect(self._handle_patient_selected)
    
    def _setup_auto_refresh(self):
        """Set up automatic refresh timer."""
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self._refresh_stats)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds
    
    def _refresh_stats(self):
        """Refresh dashboard statistics."""
        try:
            # Get comprehensive statistics
            stats = patient_service.get_patients_statistics()
            
            # Update stat cards
            self.stat_cards['patients'].update_value(str(stats['total']))
            self.stat_cards['new_month'].update_value(str(stats['this_month']))
            
            # Update examinations with real data
            self.stat_cards['examinations'].update_value(str(stats['total_examinations']))
            self.stat_cards['active'].update_value(str(stats['total']))
            
            # Refresh recent patients
            self.recent_patients.refresh()
            
            logger.info(f"Dashboard refreshed - Total: {stats['total']}, This month: {stats['this_month']}, Examinations: {stats['total_examinations']}")
            
        except Exception as e:
            logger.error(f"Error refreshing dashboard stats: {str(e)}")
            # Set default values on error
            self.stat_cards['patients'].update_value("0")
            self.stat_cards['new_month'].update_value("0")
            self.stat_cards['examinations'].update_value("0")
            self.stat_cards['active'].update_value("0")
    
    def _handle_patient_selected(self, patient: dict):
        """Handle patient selection from recent patients."""
        # For now, just navigate to patients page
        # TODO: In future, could open patient details directly
        self.navigate_to_patients.emit()
    
    def _handle_view_reports(self):
        """Handle view reports button click."""
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("Reports")
        msg_box.setText("Reports functionality will be available in a future update.\n\nFor now, you can export patient data from the Patient Management section.")
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: white;
                color: black;
            }
            QMessageBox QLabel {
                color: black;
                background-color: white;
            }
            QMessageBox QPushButton {
                background-color: #f0f0f0;
                color: black;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 8px 16px;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        msg_box.exec()
    
    def _handle_backup_data(self):
        """Handle export & backup button click."""
        try:
            export_dialog = ExportDialog(self)
            export_dialog.exec()
        except Exception as e:
            logger.error(f"Export dialog error: {str(e)}")
            error_box = QMessageBox(self)
            error_box.setIcon(QMessageBox.Critical)
            error_box.setWindowTitle("Export Error")
            error_box.setText(f"Failed to open export dialog:\n{str(e)}")
            error_box.setStyleSheet("""
                QMessageBox {
                    background-color: white;
                    color: black;
                }
                QMessageBox QLabel {
                    color: black;
                    background-color: white;
                }
                QMessageBox QPushButton {
                    background-color: #f0f0f0;
                    color: black;
                    border: 1px solid #ccc;
                    border-radius: 4px;
                    padding: 8px 16px;
                    min-width: 80px;
                }
                QMessageBox QPushButton:hover {
                    background-color: #e0e0e0;
                }
            """)
            error_box.exec()
    
    def refresh(self):
        """Manually refresh dashboard data."""
        self._refresh_stats()
