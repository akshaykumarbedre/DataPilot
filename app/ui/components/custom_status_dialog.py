"""
Custom Status Dialog for creating custom tooth statuses.
"""
import logging
from typing import Dict, Optional
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, 
    QLineEdit, QPushButton, QColorDialog, QMessageBox, QComboBox,
    QTextEdit, QFrame, QDialogButtonBox, QGroupBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont, QPalette

from ...services.custom_status_service import custom_status_service

logger = logging.getLogger(__name__)


class ColorPreviewWidget(QFrame):
    """Widget to preview the selected color."""
    
    def __init__(self, color: str = "#808080", parent=None):
        super().__init__(parent)
        self.color = color
        self.setFixedSize(40, 40)
        self.setFrameStyle(QFrame.Box)
        self.update_color()
    
    def set_color(self, color: str):
        """Set the preview color."""
        self.color = color
        self.update_color()
    
    def update_color(self):
        """Update the widget background color."""
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {self.color};
                border: 2px solid #19c5e5;
                border-radius: 4px;
            }}
        """)


class CustomStatusDialog(QDialog):
    """Dialog for creating custom tooth statuses"""
    
    status_created = Signal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_color = "#808080"
        self.preview_widget = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the custom status dialog UI."""
        self.setWindowTitle("Create Custom Dental Status")
        self.setModal(True)
        self.resize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("Create Custom Dental Status")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        header.setStyleSheet("color: #19c5e5; margin: 10px;")
        layout.addWidget(header)
        
        # Form layout
        form_layout = QFormLayout()
        
        # Status name (internal identifier)
        self.status_name_edit = QLineEdit()
        self.status_name_edit.setPlaceholderText("e.g., custom_implant_crown")
        self.status_name_edit.textChanged.connect(self.validate_form)
        form_layout.addRow("Status Name (Internal ID):", self.status_name_edit)
        
        # Display name (what users see)
        self.display_name_edit = QLineEdit()
        self.display_name_edit.setPlaceholderText("e.g., Implant Crown")
        self.display_name_edit.textChanged.connect(self.validate_form)
        form_layout.addRow("Display Name:", self.display_name_edit)
        
        # Category selection
        self.category_combo = QComboBox()
        self.populate_categories()
        form_layout.addRow("Category:", self.category_combo)
        
        # Color selection
        color_layout = QHBoxLayout()
        
        self.color_button = QPushButton("Choose Color")
        self.color_button.setStyleSheet("""
            QPushButton {
                background-color: #19c5e5;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0ea5c7;
            }
        """)
        self.color_button.clicked.connect(self.choose_color)
        color_layout.addWidget(self.color_button)
        
        # Color preview
        self.preview_widget = ColorPreviewWidget(self.selected_color)
        color_layout.addWidget(self.preview_widget)
        
        # Color hex input
        self.color_edit = QLineEdit(self.selected_color)
        self.color_edit.setMaximumWidth(100)
        self.color_edit.textChanged.connect(self.on_color_text_changed)
        color_layout.addWidget(self.color_edit)
        
        color_layout.addStretch()
        form_layout.addRow("Color:", color_layout)
        
        # Description
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        self.description_edit.setPlaceholderText("Optional description of this status...")
        form_layout.addRow("Description:", self.description_edit)
        
        layout.addLayout(form_layout)
        
        # Preview area
        self.create_preview_area(layout)
        
        # Validation message
        self.validation_label = QLabel("")
        self.validation_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
        layout.addWidget(self.validation_label)
        
        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.save_custom_status)
        button_box.rejected.connect(self.reject)
        
        # Style the save button
        self.save_button = button_box.button(QDialogButtonBox.Save)
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #19c5e5;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #0ea5c7;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        self.save_button.setEnabled(False)
        
        layout.addWidget(button_box)
        
        # Initial validation
        self.validate_form()
    
    def populate_categories(self):
        """Populate category dropdown."""
        categories = [
            "healthy", "decay", "restoration", "prosthetic", "endodontic",
            "periodontal", "missing", "orthodontic", "trauma", "anomaly",
            "planned", "other", "custom"
        ]
        
        for category in categories:
            self.category_combo.addItem(category.title(), category)
        
        # Set default to custom
        self.category_combo.setCurrentText("Custom")
    
    def create_preview_area(self, parent_layout):
        """Create preview area showing tooth with new status."""
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        # Preview label
        self.preview_label = QLabel("Preview of tooth with new status:")
        preview_layout.addWidget(self.preview_label)
        
        # Mock tooth button for preview
        self.preview_tooth = QPushButton("(1,1)")
        self.preview_tooth.setFixedSize(60, 45)
        self.preview_tooth.setFont(QFont("Arial", 8, QFont.Bold))
        self.update_preview_tooth()
        
        # Center the preview tooth
        tooth_layout = QHBoxLayout()
        tooth_layout.addStretch()
        tooth_layout.addWidget(self.preview_tooth)
        tooth_layout.addStretch()
        preview_layout.addLayout(tooth_layout)
        
        parent_layout.addWidget(preview_group)
    
    def update_preview_tooth(self):
        """Update the preview tooth button with selected color."""
        style = f"""
            QPushButton {{
                background-color: {self.selected_color};
                border: 2px solid #19c5e5;
                border-radius: 8px;
                color: white;
                font-weight: bold;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.7);
            }}
        """
        self.preview_tooth.setStyleSheet(style)
        
        # Update preview text
        display_name = self.display_name_edit.text() or "Custom Status"
        self.preview_label.setText(f"Preview of tooth with '{display_name}' status:")
    
    def choose_color(self):
        """Open color picker dialog."""
        color = QColorDialog.getColor(QColor(self.selected_color), self, "Choose Status Color")
        
        if color.isValid():
            self.selected_color = color.name()
            self.color_edit.setText(self.selected_color)
            self.preview_widget.set_color(self.selected_color)
            self.update_preview_tooth()
    
    def on_color_text_changed(self, text: str):
        """Handle manual color text input."""
        # Validate hex color format
        if len(text) == 7 and text.startswith('#'):
            try:
                color = QColor(text)
                if color.isValid():
                    self.selected_color = text
                    self.preview_widget.set_color(self.selected_color)
                    self.update_preview_tooth()
            except:
                pass
    
    def validate_form(self):
        """Validate form inputs and enable/disable save button."""
        status_name = self.status_name_edit.text().strip()
        display_name = self.display_name_edit.text().strip()
        
        # Check required fields
        if not status_name or not display_name:
            self.validation_label.setText("Status name and display name are required.")
            self.save_button.setEnabled(False)
            return
        
        # Validate status name format (no spaces, lowercase, underscores allowed)
        if not status_name.replace('_', '').isalnum() or ' ' in status_name:
            self.validation_label.setText("Status name must contain only letters, numbers, and underscores.")
            self.save_button.setEnabled(False)
            return
        
        # Check if status name already exists
        try:
            existing = custom_status_service.get_custom_status_by_name(status_name)
            if existing:
                self.validation_label.setText("A status with this name already exists.")
                self.save_button.setEnabled(False)
                return
        except Exception as e:
            logger.error(f"Error checking existing status: {str(e)}")
        
        # Validate color
        try:
            color = QColor(self.selected_color)
            if not color.isValid():
                self.validation_label.setText("Invalid color format.")
                self.save_button.setEnabled(False)
                return
        except:
            self.validation_label.setText("Invalid color format.")
            self.save_button.setEnabled(False)
            return
        
        # All validations passed
        self.validation_label.setText("")
        self.save_button.setEnabled(True)
        
        # Update preview
        self.update_preview_tooth()
    
    def save_custom_status(self):
        """Save the custom status."""
        try:
            status_data = {
                'status_name': self.status_name_edit.text().strip(),
                'display_name': self.display_name_edit.text().strip(),
                'description': self.description_edit.toPlainText().strip(),
                'color': self.selected_color,
                'category': self.category_combo.currentData(),
                'is_active': True,
                'sort_order': 999,  # Custom statuses at end
                'icon_name': '',
                'created_by': 'user'
            }
            
            result = custom_status_service.create_custom_status(status_data)
            
            if result:
                self.status_created.emit(result)
                QMessageBox.information(
                    self, 
                    "Success", 
                    f"Custom status '{status_data['display_name']}' created successfully!"
                )
                self.accept()
            else:
                QMessageBox.warning(
                    self, 
                    "Error", 
                    "Failed to create custom status. The status name might already exist."
                )
                
        except Exception as e:
            logger.error(f"Error saving custom status: {str(e)}")
            QMessageBox.critical(
                self, 
                "Error", 
                f"Error saving custom status: {str(e)}"
            )
