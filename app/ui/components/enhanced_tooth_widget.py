"""
Enhanced Tooth Widget with comprehensive status tracking and (quadrant.position) display format.
"""
import logging
from typing import Dict, List, Optional, Any, Callable
from PySide6.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QComboBox, 
    QLabel, QDialog, QDialogButtonBox, QFormLayout, QLineEdit,
    QColorDialog, QMessageBox, QFrame
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont

from ...services.custom_status_service import custom_status_service

logger = logging.getLogger(__name__)


class EnhancedToothWidget(QWidget):
    """Enhanced tooth widget with comprehensive status tracking"""
    
    tooth_clicked = Signal(int, str)  # tooth_number, click_type
    status_changed = Signal(int, str, str)  # tooth_number, new_status, record_type
    
    def __init__(self, tooth_number: int, parent=None):
        super().__init__(parent)
        self.tooth_number = tooth_number
        self.patient_status = 'normal'
        self.doctor_status = 'normal'
        self.current_mode = 'doctor'  # 'patient' or 'doctor'
        self.on_status_change_callback = None
        
        self.setup_ui()
        self.load_status_options()
    
    def setup_ui(self):
        """Setup the tooth widget UI with button and dropdown."""
        layout = QVBoxLayout(self)
        layout.setSpacing(1)
        layout.setContentsMargins(1, 1, 1, 1)
        
        # Tooth button with (quadrant.position) display format
        self.tooth_button = QPushButton()
        self.tooth_button.setFixedSize(65, 50)  # Increased size for better visibility
        self.tooth_button.setFont(QFont("Arial", 9, QFont.Bold))  # Slightly larger font
        self.tooth_button.setText(self.get_display_number(self.tooth_number))
        self.tooth_button.clicked.connect(self.on_tooth_button_clicked)
        self.tooth_button.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tooth_button.customContextMenuRequested.connect(self.on_right_click)
        layout.addWidget(self.tooth_button)
        
        # Status dropdown (initially hidden)
        self.status_dropdown = QComboBox()
        self.status_dropdown.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.status_dropdown.setMaximumHeight(25)
        self.status_dropdown.hide()
        self.status_dropdown.currentTextChanged.connect(self.on_status_dropdown_changed)
        layout.addWidget(self.status_dropdown)
        
        # Update appearance
        self.update_tooth_appearance()
    
    def get_display_number(self, full_tooth_number: int) -> str:
        """Convert full tooth number to (quadrant.position) format"""
        # 11-18 → (1,1)-(1,8), 21-28 → (2,1)-(2,8), etc.
        quadrant = full_tooth_number // 10
        position = full_tooth_number % 10
        return f"({quadrant},{position})"
    
    def setup_status_dropdown(self):
        """Setup comprehensive status dropdown with colors"""
        self.status_dropdown.clear()
        
        try:
            # Get all active custom statuses (includes predefined ones)
            statuses = custom_status_service.get_all_custom_statuses(is_active=True)
            
            # Group by category for better organization
            categories = custom_status_service.get_statuses_by_category()
            
            # Add statuses grouped by category
            for category, category_statuses in categories.items():
                # Add category separator
                self.status_dropdown.addItem(f"--- {category.title()} ---", None)
                
                for status in sorted(category_statuses, key=lambda x: x['display_name']):
                    self.status_dropdown.addItem(status['display_name'], status['status_name'])
            
            # Add custom status option (no addSeparator, use regular item)
            self.status_dropdown.addItem("---", None)  # Separator item
            self.status_dropdown.addItem("+ Add Custom Status", "add_custom")
            
        except Exception as e:
            logger.error(f"Error setting up status dropdown: {str(e)}")
            # Fallback to basic statuses
            basic_statuses = [
                ("normal", "Normal"),
                ("caries_incipient", "Caries (Incipient)"),
                ("caries_deep", "Caries (Deep)"),
                ("filling", "Filling"),
                ("crown", "Crown"),
                ("root_canal", "Root Canal"),
                ("extracted", "Extracted"),
                ("missing", "Missing"),
                ("add_custom", "+ Add Custom Status")
            ]
            
            for status_code, display_name in basic_statuses:
                self.status_dropdown.addItem(display_name, status_code)
    
    def load_status_options(self):
        """Load status options into dropdown"""
        self.setup_status_dropdown()
    
    def set_patient_status(self, status: str):
        """Set patient-reported status."""
        self.patient_status = status
        self.update_tooth_appearance()
    
    def set_doctor_status(self, status: str):
        """Set doctor-diagnosed status."""
        self.doctor_status = status
        self.update_tooth_appearance()

    def update_status(self, status: str):
        """Update the status based on the current mode."""
        if self.current_mode == 'doctor':
            self.set_doctor_status(status)
        else:
            self.set_patient_status(status)
    
    def set_mode(self, mode: str):
        """Set display mode (patient or doctor)."""
        self.current_mode = mode
        self.update_tooth_appearance()
    
    def get_status_color(self, status: str) -> str:
        """Get color for dental status."""
        try:
            # Get color from custom status service
            custom_status = custom_status_service.get_custom_status_by_name(status)
            if custom_status:
                return custom_status['color']
        except:
            pass
        
        # Fallback color mapping
        color_map = {
            'normal': '#2ecc71',
            'caries_incipient': '#f1c40f',
            'caries_moderate': '#f39c12',
            'caries_deep': '#e74c3c',
            'filling': '#95a5a6',
            'crown': '#3498db',
            'root_canal': '#e91e63',
            'extracted': '#2c3e50',
            'missing': '#34495e',
            'implant': '#9b59b6'
        }
        return color_map.get(status, '#808080')
    
    def update_tooth_appearance(self):
        """Update tooth button appearance based on current status and mode."""
        if self.current_mode == 'doctor':
            primary_color = self.get_status_color(self.doctor_status)
            secondary_color = self.get_status_color(self.patient_status)
        else:
            primary_color = self.get_status_color(self.patient_status)
            secondary_color = self.get_status_color(self.doctor_status)
        
        # Create style based on whether there are different statuses
        if (self.patient_status != 'normal' and self.doctor_status != 'normal' and 
            self.patient_status != self.doctor_status):
            # Split gradient for dual status
            style = f"""
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 {primary_color}, stop:0.5 {primary_color},
                        stop:0.5 {secondary_color}, stop:1 {secondary_color});
                    border: 2px solid #BDC3C7;
                    border-radius: 6px;
                    color: white;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    border: 2px solid #95A5A6;
                }}
                QPushButton:pressed {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 {self.adjust_color(primary_color, -30)}, 
                        stop:0.5 {self.adjust_color(primary_color, -30)},
                        stop:0.5 {self.adjust_color(secondary_color, -30)}, 
                        stop:1 {self.adjust_color(secondary_color, -30)});
                }}
            """
        else:
            # Single color
            style = f"""
                QPushButton {{
                    background-color: {primary_color};
                    border: 2px solid #BDC3C7;
                    border-radius: 6px;
                    color: white;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    border: 2px solid #95A5A6;
                    background-color: {self.adjust_color(primary_color, 20)};
                }}
                QPushButton:pressed {{
                    background-color: {self.adjust_color(primary_color, -30)};
                }}
            """
        
        self.tooth_button.setStyleSheet(style)
    
    def adjust_color(self, hex_color: str, adjustment: int) -> str:
        """Adjust color brightness."""
        try:
            color = QColor(hex_color)
            h, s, v, a = color.getHsv()
            v = max(0, min(255, v + adjustment))
            color.setHsv(h, s, v, a)
            return color.name()
        except:
            return hex_color
    
    def on_tooth_button_clicked(self):
        """Handle tooth button click."""
        self.tooth_clicked.emit(self.tooth_number, 'left')
        # Toggle status dropdown visibility
        if self.status_dropdown.isVisible():
            self.status_dropdown.hide()
        else:
            self.status_dropdown.show()
            # Set current status in dropdown
            current_status = self.doctor_status if self.current_mode == 'doctor' else self.patient_status
            self.set_dropdown_status(current_status)
    
    def on_right_click(self):
        """Handle right click for detailed view."""
        self.tooth_clicked.emit(self.tooth_number, 'right')
    
    def set_dropdown_status(self, status: str):
        """Set the dropdown to show the specified status."""
        for i in range(self.status_dropdown.count()):
            if self.status_dropdown.itemData(i) == status:
                self.status_dropdown.setCurrentIndex(i)
                break
    
    def on_status_dropdown_changed(self, text: str):
        """Handle status dropdown change."""
        status_code = self.status_dropdown.currentData()
        
        if status_code == "add_custom":
            # Open custom status dialog
            self.create_custom_status()
        elif status_code and status_code.startswith("---"):
            # Ignore category separators
            return
        elif status_code:
            # Update tooth status
            if self.current_mode == 'doctor':
                self.set_doctor_status(status_code)
            else:
                self.set_patient_status(status_code)
            
            # Emit status change signal
            self.status_changed.emit(self.tooth_number, status_code, self.current_mode)
            
            # Hide dropdown after selection
            self.status_dropdown.hide()
    
    def create_custom_status(self):
        """Open dialog to create custom status."""
        from .custom_status_dialog import CustomStatusDialog
        
        dialog = CustomStatusDialog(self)
        if dialog.exec() == QDialog.Accepted:
            # Reload status options
            self.load_status_options()
    
    def set_status_change_callback(self, callback: Callable):
        """Set callback function for status changes."""
        self.on_status_change_callback = callback
    
    def get_current_status(self) -> str:
        """Get current status based on mode."""
        return self.doctor_status if self.current_mode == 'doctor' else self.patient_status
    
    def force_hide_dropdown(self):
        """Force hide the status dropdown."""
        self.status_dropdown.hide()
