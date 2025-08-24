"""
Enhanced Tooth Widget with comprehensive status tracking and (quadrant.position) display format.
"""
import logging
from typing import Dict, List, Optional, Any, Callable
from PySide6.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QHBoxLayout, 
    QLabel, QDialog, QDialogButtonBox, QFormLayout, QLineEdit,
    QColorDialog, QMessageBox, QFrame, QListView
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont, QFontMetrics

from ...services.custom_status_service import custom_status_service
from .multi_select_combobox import MultiSelectComboBox

logger = logging.getLogger(__name__)


class EnhancedToothWidget(QWidget):
    """Enhanced tooth widget with comprehensive status tracking"""
    
    tooth_clicked = Signal(int, str)  # tooth_number, click_type
    statuses_selected = Signal(int, list, str)  # tooth_number, new_statuses, record_type
    
    def __init__(self, tooth_number: int, parent=None):
        super().__init__(parent)
        self.tooth_number = tooth_number
        self.patient_statuses = ['normal']
        self.doctor_statuses = ['normal']
        self.current_mode = 'doctor'  # 'patient' or 'doctor'
        self.on_status_change_callback = None
        
        self.setup_ui()
        self.load_status_options()
        self.adjust_dropdown_width()
        self.update_tooltip()
    
    def setup_ui(self):
        """Setup the tooth widget UI with button and dropdown."""
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Tooth button with (quadrant.position) display format
        self.tooth_button = QPushButton()
        self.tooth_button.setFixedSize(35, 40)
        self.tooth_button.setFont(QFont("Arial", 10, QFont.Bold))
        self.tooth_button.setText(self.get_display_number(self.tooth_number))
        self.tooth_button.clicked.connect(self.on_tooth_button_clicked)
        self.tooth_button.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tooth_button.customContextMenuRequested.connect(self.on_right_click)
        layout.addWidget(self.tooth_button)
        
        # Status dropdown (initially hidden)
        self.status_dropdown = MultiSelectComboBox()
        self.status_dropdown.setMaximumHeight(25)
        self.status_dropdown.hide()
        self.status_dropdown.itemsSelected.connect(self.on_statuses_selected)
        layout.addWidget(self.status_dropdown)
        
        # Update appearance
        self.update_tooth_appearance()
    
    def get_display_number(self, full_tooth_number: int) -> str:
        """Convert full tooth number to (quadrant.position) format"""
        # 11-18 → (1,1)-(1,8), 21-28 → (2,1)-(2,8), etc.
        quadrant = full_tooth_number // 10
        position = full_tooth_number % 10
        return f"{position}"

    def update_tooltip(self):
        """Update tooltip with current status."""
        if self.current_mode == 'patient':
            status_text = f"Patient: {', '.join(self.patient_statuses)}"
        else: # doctor
            status_text = f"Doctor: {', '.join(self.doctor_statuses)}"
        self.tooth_button.setToolTip(status_text)
    
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
                ("Normal", "normal"),
                ("Caries (Incipient)", "caries_incipient"),
                ("Caries (Deep)", "caries_deep"),
                ("Filling", "filling"),
                ("Crown", "crown"),
                ("Root Canal", "root_canal"),
                ("Extracted", "extracted"),
                ("Missing", "missing"),
            ]
            
            self.status_dropdown.addItems(basic_statuses)
    
    def load_status_options(self):
        """Load status options into dropdown"""
        self.setup_status_dropdown()
    
    def set_patient_status(self, statuses: List[str]):
        """Set patient-reported status."""
        self.patient_statuses = statuses if statuses else ['normal']
        self.update_tooth_appearance()
        self.update_tooltip()
    
    def set_doctor_status(self, statuses: List[str]):
        """Set doctor-diagnosed status."""
        self.doctor_statuses = statuses if statuses else ['normal']
        self.update_tooth_appearance()
        self.update_tooltip()

    def update_status(self, statuses: List[str]):
        """Update the status based on the current mode."""
        if self.current_mode == 'doctor':
            self.set_doctor_status(statuses)
        else:
            self.set_patient_status(statuses)
    
    def set_mode(self, mode: str):
        """Set display mode (patient or doctor)."""
        self.current_mode = mode
        self.update_tooth_appearance()
    
    def get_status_color(self, status: str) -> str:
        """Get color for dental status."""
        if status == 'normal':
            return '#FFFFFF'

        try:
            # Get color from custom status service
            custom_status = custom_status_service.get_custom_status_by_name(status)
            if custom_status:
                return custom_status['color']
        except:
            pass
        
        # Fallback color mapping
        color_map = {
            'normal': '#FFFFFF',
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
            primary_statuses = self.doctor_statuses
            secondary_statuses = self.patient_statuses
        else:
            primary_statuses = self.patient_statuses
            secondary_statuses = self.doctor_statuses

        primary_color = self.get_status_color(primary_statuses[0])
        text_color = self.get_text_color_for_background(primary_color)

        if len(primary_statuses) > 1:
            # Gradient for multiple statuses
            style = "QPushButton { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 %s, stop:1 %s); " % (self.get_status_color(primary_statuses[0]), self.get_status_color(primary_statuses[1]))
        elif primary_statuses != ['normal'] and secondary_statuses != ['normal'] and primary_statuses != secondary_statuses:
            # Split gradient for dual status (patient vs doctor)
            secondary_color = self.get_status_color(secondary_statuses[0])
            style = f"""
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 {primary_color}, stop:0.5 {primary_color},
                        stop:0.5 {secondary_color}, stop:1 {secondary_color});
            """
        else:
            # Single color
            style = f"QPushButton {{ background-color: {primary_color}; "

        style += f"""
                border: 2px solid #BDC3C7;
                border-radius: 6px;
                color: {text_color};
                font-weight: bold;
                padding: 0px;
            }}
            QPushButton:hover {{
                border: 2px solid #95A5A6;
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

    def get_text_color_for_background(self, hex_color: str) -> str:
        """Determines if text should be black or white based on background color."""
        try:
            color = QColor(hex_color)
            r, g, b, _ = color.getRgb()
            luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
            return '#000000' if luminance > 0.5 else '#FFFFFF'
        except:
            return '#000000'
    
    def on_tooth_button_clicked(self):
        """Handle tooth button click."""
        self.tooth_clicked.emit(self.tooth_number, 'left')
        # Toggle status dropdown visibility
        if self.status_dropdown.isVisible():
            self.status_dropdown.hide()
        else:
            self.status_dropdown.show()
            # Set current status in dropdown
            current_statuses = self.doctor_statuses if self.current_mode == 'doctor' else self.patient_statuses
            self.set_dropdown_status(current_statuses)
    
    def on_right_click(self):
        """Handle right click for detailed view."""
        self.tooth_clicked.emit(self.tooth_number, 'right')
    
    def set_dropdown_status(self, statuses: List[str]):
        """Set the dropdown to show the specified statuses."""
        self.status_dropdown.blockSignals(True)
        for i in range(self.status_dropdown._list_widget.count()):
            item = self.status_dropdown._list_widget.item(i)
            item.setCheckState(Qt.Checked if item.data(Qt.UserRole) in statuses else Qt.Unchecked)
        self.status_dropdown.blockSignals(False)
        self.status_dropdown._update_line_edit()

    def on_statuses_selected(self, statuses: List[str]):
        """Handle status dropdown change."""
        if "add_custom" in statuses:
            # Open custom status dialog
            self.create_custom_status()
        else:
            # Update tooth status
            if self.current_mode == 'doctor':
                self.set_doctor_status(statuses)
            else:
                self.set_patient_status(statuses)
            
            # Emit status change signal
            self.statuses_selected.emit(self.tooth_number, statuses, self.current_mode)
    
    def create_custom_status(self):
        """Open dialog to create custom status."""
        from .custom_status_dialog import CustomStatusDialog
        
        dialog = CustomStatusDialog(self)
        if dialog.exec() == QDialog.Accepted:
            # Reload status options
            self.load_status_options()
            self.adjust_dropdown_width()
    
    def set_status_change_callback(self, callback: Callable):
        """Set callback function for status changes."""
        self.on_status_change_callback = callback
    
    def get_current_status(self) -> List[str]:
        """Get current status based on mode."""
        return self.doctor_statuses if self.current_mode == 'doctor' else self.patient_statuses

    def adjust_dropdown_width(self):
        """Adjust dropdown width to fit the longest item."""
        font = self.status_dropdown.font()
        metrics = QFontMetrics(font)
        
        max_width = 0
        for i in range(self.status_dropdown._list_widget.count()):
            item_text = self.status_dropdown._list_widget.item(i).text()
            width = metrics.horizontalAdvance(item_text)
            if width > max_width:
                max_width = width
                
        # Add some padding for the dropdown arrow and margins
        self.status_dropdown.view().setMinimumWidth(max_width + 40)
    
    def force_hide_dropdown(self):
        """Force hide the status dropdown."""
        self.status_dropdown.hide()
