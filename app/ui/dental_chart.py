"""
Dental chart interface for examination and treatment tracking.
"""
import logging
from datetime import date, datetime
from typing import Optional, Dict, Any
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                               QLabel, QPushButton, QTextEdit, QComboBox,
                               QDateEdit, QFrame, QGroupBox, QScrollArea,
                               QMessageBox, QSplitter, QFormLayout, QLineEdit)
from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import QFont, QPalette
from ..services.dental_service import dental_service
from ..services.patient_service import patient_service

logger = logging.getLogger(__name__)


class ToothWidget(QPushButton):
    """Individual tooth widget for the dental chart."""
    
    tooth_selected = Signal(str, int)  # quadrant, tooth_number
    
    def __init__(self, quadrant: str, tooth_number: int, parent=None):
        super().__init__(parent)
        self.quadrant = quadrant
        self.tooth_number = tooth_number
        self.status = 'normal'
        
        self.setText(str(tooth_number))
        self.setFixedSize(50, 50)  # Reduce from 60x60 to 50x50
        self.setCheckable(True)
        self.clicked.connect(self._on_clicked)
        
        self._update_style()
    
    def _on_clicked(self):
        """Handle tooth click."""
        self.tooth_selected.emit(self.quadrant, self.tooth_number)
    
    def set_status(self, status: str):
        """Set tooth status and update appearance."""
        self.status = status
        self._update_style()
    
    def _update_style(self):
        """Update tooth appearance based on status."""
        base_style = """
            QPushButton {
                border: 2px solid #BDC3C7;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                padding: 10px;
                margin: 2px;
            }
            QPushButton:hover {
                border-color: #3498DB;
                border-width: 2px;
            }
            QPushButton:checked {
                border-color: #1B4F72;
                border-width: 3px;
                background-color: #2E86C1;
                color: white;
            }
        """
        
        if self.status == 'normal':
            color_style = """
                QPushButton {
                    background-color: #E8F4FD;
                    color: #1B4F72;
                }
            """
        elif self.status == 'treated':
            color_style = """
                QPushButton {
                    background-color: #A8E6A3;
                    color: #0D5016;
                }
            """
        elif self.status == 'problem':
            color_style = """
                QPushButton {
                    background-color: #FADBD8;
                    color: #7B1818;
                }
            """
        elif self.status == 'missing':
            color_style = """
                QPushButton {
                    background-color: #D5D8DC;
                    color: #2C3E50;
                }
            """
        else:  # other statuses
            color_style = """
                QPushButton {
                    background-color: #FFE066;
                    color: #6B4E00;
                }
            """
        
        self.setStyleSheet(base_style + color_style)


class QuadrantWidget(QGroupBox):
    """Dental quadrant widget containing 7 teeth."""
    
    tooth_selected = Signal(str, int)
    
    def __init__(self, quadrant: str, title: str, parent=None):
        super().__init__(title, parent)
        self.quadrant = quadrant
        self.teeth = {}
        
        # Set maximum height to make quadrants more compact
        self.setMaximumHeight(100)
        
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
                subcontrol-position: top center;
                padding: 0 10px;
                color: #2C3E50;
            }
        """)
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the quadrant UI with 7 teeth in a single row."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 15, 10, 10)  # Reduce margins
        layout.setSpacing(8)  # Reduce spacing from 10 to 8
        
        # Arrange 7 teeth in a single horizontal row
        for i in range(7):
            tooth_number = i + 1
            
            tooth = ToothWidget(self.quadrant, tooth_number)
            tooth.tooth_selected.connect(self._on_tooth_selected)
            self.teeth[tooth_number] = tooth
            
            layout.addWidget(tooth)
    
    def _on_tooth_selected(self, quadrant: str, tooth_number: int):
        """Handle tooth selection with single-selection behavior."""
        # Clear all other teeth in this quadrant first
        for tooth in self.teeth.values():
            tooth.setChecked(False)
        
        # Select only the clicked tooth
        if tooth_number in self.teeth:
            self.teeth[tooth_number].setChecked(True)
        
        # Emit the selection signal
        self.tooth_selected.emit(quadrant, tooth_number)
    
    def update_tooth_status(self, tooth_number: int, status: str):
        """Update specific tooth status."""
        if tooth_number in self.teeth:
            self.teeth[tooth_number].set_status(status)
    
    def clear_selection(self):
        """Clear all tooth selections."""
        for tooth in self.teeth.values():
            tooth.setChecked(False)
    
    def select_tooth(self, tooth_number: int):
        """Select specific tooth with single-selection behavior."""
        # First clear all selections
        self.clear_selection()
        # Then select the specified tooth
        if tooth_number in self.teeth:
            self.teeth[tooth_number].setChecked(True)


class ToothDetailPanel(QGroupBox):
    """Panel for editing tooth details."""
    
    tooth_saved = Signal()
    
    def __init__(self, parent=None):
        super().__init__("Tooth Details", parent)
        self.current_patient_id = None
        self.current_quadrant = None
        self.current_tooth_number = None
        
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
        self._connect_signals()
        self.set_enabled(False)
    
    def _setup_ui(self):
        """Set up the tooth detail UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 20, 15, 15)
        layout.setSpacing(15)
        
        # Tooth info
        self.tooth_info_label = QLabel("No tooth selected")
        self.tooth_info_label.setStyleSheet("color: #7F8C8D; font-style: italic;")
        layout.addWidget(self.tooth_info_label)
        
        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # Status
        self.status_combo = QComboBox()
        self.status_combo.addItems(['normal', 'treated', 'problem', 'missing'])
        self.status_combo.setStyleSheet("""
            QComboBox {
                border: 2px solid #BDC3C7;
                border-radius: 4px;
                padding: 8px;
                color: black;
                background-color: white;
            }
            QComboBox:focus {
                border-color: #3498DB;
            }
        """)
        form_layout.addRow("Status:", self.status_combo)
        
        # Diagnosis
        self.diagnosis_edit = QTextEdit()
        self.diagnosis_edit.setMaximumHeight(80)
        self.diagnosis_edit.setPlaceholderText("Enter diagnosis...")
        self.diagnosis_edit.setStyleSheet("""
            QTextEdit {
                border: 2px solid #BDC3C7;
                border-radius: 4px;
                padding: 8px;
                color: black;
                background-color: white;
            }
            QTextEdit:focus {
                border-color: #3498DB;
            }
        """)
        form_layout.addRow("Diagnosis:", self.diagnosis_edit)
        
        # Treatment
        self.treatment_edit = QTextEdit()
        self.treatment_edit.setMaximumHeight(80)
        self.treatment_edit.setPlaceholderText("Enter treatment performed...")
        self.treatment_edit.setStyleSheet("""
            QTextEdit {
                border: 2px solid #BDC3C7;
                border-radius: 4px;
                padding: 8px;
                color: black;
                background-color: white;
            }
            QTextEdit:focus {
                border-color: #3498DB;
            }
        """)
        form_layout.addRow("Treatment:", self.treatment_edit)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Save Tooth Data")
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #27AE60;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:disabled {
                background-color: #BDC3C7;
            }
        """)
        button_layout.addWidget(self.save_button)
        
        self.clear_button = QPushButton("Clear")
        self.clear_button.setStyleSheet("""
            QPushButton {
                background-color: #95A5A6;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7F8C8D;
            }
            QPushButton:disabled {
                background-color: #BDC3C7;
            }
        """)
        button_layout.addWidget(self.clear_button)
        
        layout.addLayout(button_layout)
        layout.addStretch()
    
    def _connect_signals(self):
        """Connect signals."""
        self.save_button.clicked.connect(self._save_tooth_data)
        self.clear_button.clicked.connect(self._clear_fields)
    
    def set_tooth(self, patient_id: str, quadrant: str, tooth_number: int):
        """Set current tooth and load its data."""
        self.current_patient_id = patient_id
        self.current_quadrant = quadrant
        self.current_tooth_number = tooth_number
        
        # Update info label
        quadrant_names = {
            'upper_right': 'Upper Right',
            'upper_left': 'Upper Left',
            'lower_right': 'Lower Right',
            'lower_left': 'Lower Left'
        }
        quadrant_name = quadrant_names.get(quadrant, quadrant)
        self.tooth_info_label.setText(f"{quadrant_name} - Tooth #{tooth_number}")
        self.tooth_info_label.setStyleSheet("color: #2C3E50; font-weight: bold;")
        
        # Load tooth data
        self._load_tooth_data()
        self.set_enabled(True)
    
    def _load_tooth_data(self):
        """Load current tooth data."""
        if not all([self.current_patient_id, self.current_quadrant, self.current_tooth_number]):
            return
        
        tooth_data = dental_service.get_tooth_record(
            self.current_patient_id,
            self.current_quadrant,
            self.current_tooth_number
        )
        
        if tooth_data:
            self.status_combo.setCurrentText(tooth_data.get('status', 'normal'))
            self.diagnosis_edit.setPlainText(tooth_data.get('diagnosis', ''))
            self.treatment_edit.setPlainText(tooth_data.get('treatment_performed', ''))
        else:
            self._clear_fields()
    
    def _save_tooth_data(self):
        """Save current tooth data."""
        if not all([self.current_patient_id, self.current_quadrant, self.current_tooth_number]):
            return
        
        tooth_data = {
            'status': self.status_combo.currentText(),
            'diagnosis': self.diagnosis_edit.toPlainText().strip(),
            'treatment_performed': self.treatment_edit.toPlainText().strip()
        }
        
        success = dental_service.update_tooth_record(
            self.current_patient_id,
            self.current_quadrant,
            self.current_tooth_number,
            tooth_data
        )
        
        if success:
            self.tooth_saved.emit()
            logger.info(f"Saved tooth data: {self.current_quadrant} #{self.current_tooth_number}")
        else:
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setWindowTitle("Error")
            msg_box.setText("Failed to save tooth data. Please try again.")
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
    
    def _clear_fields(self):
        """Clear all fields."""
        self.status_combo.setCurrentText('normal')
        self.diagnosis_edit.clear()
        self.treatment_edit.clear()
    
    def set_enabled(self, enabled: bool):
        """Enable or disable the panel."""
        self.status_combo.setEnabled(enabled)
        self.diagnosis_edit.setEnabled(enabled)
        self.treatment_edit.setEnabled(enabled)
        self.save_button.setEnabled(enabled)
        self.clear_button.setEnabled(enabled)


class DentalChart(QWidget):
    """Complete dental chart interface."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_patient = None
        self.quadrants = {}
        
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """Set up the dental chart UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Dental Examination")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #2C3E50;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Patient selection
        self.patient_combo = QComboBox()
        self.patient_combo.setMinimumWidth(200)
        self.patient_combo.setStyleSheet("""
            QComboBox {
                border: 2px solid #BDC3C7;
                border-radius: 4px;
                padding: 8px;
                color: black;
                background-color: white;
            }
            QComboBox:focus {
                border-color: #3498DB;
            }
        """)
        header_layout.addWidget(QLabel("Patient:"))
        header_layout.addWidget(self.patient_combo)
        
        # New examination button
        self.new_exam_button = QPushButton("New Examination")
        self.new_exam_button.setStyleSheet("""
            QPushButton {
                background-color: #3498DB;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
        """)
        header_layout.addWidget(self.new_exam_button)
        
        # Save examination button
        self.save_exam_button = QPushButton("Save Examination")
        self.save_exam_button.setStyleSheet("""
            QPushButton {
                background-color: #27AE60;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        header_layout.addWidget(self.save_exam_button)
        
        main_layout.addLayout(header_layout)
        
        # Content area
        content_splitter = QSplitter(Qt.Horizontal)
        
        # Left side - Chart and examination details
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Patient info and chief complaint
        info_group = QGroupBox("Examination Details")
        info_group.setMaximumHeight(180)  # Limit height for better proportions
        info_group.setStyleSheet("""
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
        
        info_layout = QFormLayout(info_group)
        info_layout.setSpacing(8)  # Reduce spacing
        
        self.patient_info_label = QLabel("No patient selected")
        self.patient_info_label.setStyleSheet("color: #7F8C8D; font-style: italic;")
        info_layout.addRow("Patient:", self.patient_info_label)
        
        self.exam_date_edit = QDateEdit()
        self.exam_date_edit.setDate(QDate.currentDate())
        self.exam_date_edit.setCalendarPopup(True)
        self.exam_date_edit.setStyleSheet("""
            QDateEdit {
                border: 2px solid #BDC3C7;
                border-radius: 4px;
                padding: 8px;
                color: black;
                background-color: white;
            }
            QDateEdit:focus {
                border-color: #3498DB;
            }
        """)
        info_layout.addRow("Date:", self.exam_date_edit)
        
        self.chief_complaint_edit = QTextEdit()
        self.chief_complaint_edit.setMaximumHeight(60)  # Reduce height from 80 to 60
        self.chief_complaint_edit.setPlaceholderText("Enter chief complaint...")
        self.chief_complaint_edit.setStyleSheet("""
            QTextEdit {
                border: 2px solid #BDC3C7;
                border-radius: 4px;
                padding: 8px;
                color: black;
                background-color: white;
            }
            QTextEdit:focus {
                border-color: #3498DB;
            }
        """)
        info_layout.addRow("Chief Complaint:", self.chief_complaint_edit)
        
        left_layout.addWidget(info_group)
        
        # Dental chart
        chart_group = QGroupBox("Dental Chart")
        chart_group.setMaximumHeight(250)  # Set maximum height to make it more compact
        chart_group.setStyleSheet("""
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
        
        chart_layout = QGridLayout(chart_group)
        chart_layout.setSpacing(10)  # Reduce spacing from 15 to 10
        
        # Upper quadrants
        self.quadrants['upper_left'] = QuadrantWidget('upper_left', 'Upper Left')
        chart_layout.addWidget(self.quadrants['upper_left'], 0, 0)
        
        self.quadrants['upper_right'] = QuadrantWidget('upper_right', 'Upper Right')
        chart_layout.addWidget(self.quadrants['upper_right'], 0, 1)
        
        # Lower quadrants
        self.quadrants['lower_left'] = QuadrantWidget('lower_left', 'Lower Left')
        chart_layout.addWidget(self.quadrants['lower_left'], 1, 0)
        
        self.quadrants['lower_right'] = QuadrantWidget('lower_right', 'Lower Right')
        chart_layout.addWidget(self.quadrants['lower_right'], 1, 1)
        
        left_layout.addWidget(chart_group)
        
        content_splitter.addWidget(left_widget)
        
        # Right side - Tooth details
        self.tooth_detail_panel = ToothDetailPanel()
        content_splitter.addWidget(self.tooth_detail_panel)
        
        # Set splitter proportions - give more space to left side (dental chart)
        content_splitter.setSizes([800, 250])
        
        main_layout.addWidget(content_splitter)
        
        # Load patients
        self._load_patients()
    
    def _connect_signals(self):
        """Connect signals."""
        self.patient_combo.currentTextChanged.connect(self._on_patient_selected)
        self.new_exam_button.clicked.connect(self._create_new_examination)
        self.save_exam_button.clicked.connect(self._save_examination)
        self.tooth_detail_panel.tooth_saved.connect(self._on_tooth_saved)
        
        # Connect tooth selection signals
        for quadrant in self.quadrants.values():
            quadrant.tooth_selected.connect(self._on_tooth_selected)
    
    def _load_patients(self):
        """Load patients into combo box."""
        try:
            patients = patient_service.get_all_patients()
            self.patient_combo.clear()
            self.patient_combo.addItem("Select a patient...", None)
            
            for patient in patients:
                display_text = f"{patient['full_name']} ({patient['patient_id']})"
                self.patient_combo.addItem(display_text, patient)
                
        except Exception as e:
            logger.error(f"Error loading patients: {str(e)}")
    
    def _on_patient_selected(self):
        """Handle patient selection."""
        current_data = self.patient_combo.currentData()
        if current_data:
            self.current_patient = current_data
            self.patient_info_label.setText(f"{self.current_patient['full_name']} ({self.current_patient['patient_id']})")
            self.patient_info_label.setStyleSheet("color: #2C3E50; font-weight: bold;")
            
            # Load examination data if available
            if self.current_patient.get('examination_date'):
                self.exam_date_edit.setDate(self.current_patient['examination_date'])
            if self.current_patient.get('chief_complaint'):
                self.chief_complaint_edit.setPlainText(self.current_patient['chief_complaint'])
            
            # Clear any existing tooth selections
            for quadrant in self.quadrants.values():
                quadrant.clear_selection()
            
            # Reset tooth detail panel
            self.tooth_detail_panel.set_enabled(False)
            
            # Load dental chart data with fresh colors
            self._load_dental_chart()
        else:
            self.current_patient = None
            self.patient_info_label.setText("No patient selected")
            self.patient_info_label.setStyleSheet("color: #7F8C8D; font-style: italic;")
            self._clear_chart()
    
    def _create_new_examination(self):
        """Create a new examination for the selected patient."""
        if not self.current_patient:
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setWindowTitle("No Patient Selected")
            msg_box.setText("Please select a patient first.")
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
            return
        
        examination_data = {
            'examination_date': self.exam_date_edit.date().toPython(),
            'chief_complaint': self.chief_complaint_edit.toPlainText().strip()
        }
        
        # Update patient with examination data
        success = dental_service.update_patient_examination(
            self.current_patient['patient_id'],
            examination_data
        )
        
        if success:
            # Reload patient data
            updated_patient = patient_service.get_patient_by_id(self.current_patient['patient_id'])
            if updated_patient:
                self.current_patient = updated_patient
                self._load_dental_chart()
            
            success_box = QMessageBox(self)
            success_box.setIcon(QMessageBox.Information)
            success_box.setWindowTitle("Examination Updated")
            success_box.setText("Examination data updated successfully!")
            success_box.setStyleSheet("""
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
            success_box.exec()
        else:
            error_box = QMessageBox(self)
            error_box.setIcon(QMessageBox.Critical)
            error_box.setWindowTitle("Error")
            error_box.setText("Failed to update examination data.")
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
    
    def _save_examination(self):
        """Save examination details (date and chief complaint)."""
        if not self.current_patient:
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setWindowTitle("No Patient Selected")
            msg_box.setText("Please select a patient first.")
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
            return
        
        # Get examination data from the form
        examination_data = {
            'examination_date': self.exam_date_edit.date().toPython(),
            'chief_complaint': self.chief_complaint_edit.toPlainText().strip()
        }
        
        # Save the examination data
        success = dental_service.update_patient_examination(
            self.current_patient['patient_id'],
            examination_data
        )
        
        if success:
            # Reload patient data to get updated information
            updated_patient = patient_service.get_patient_by_id(self.current_patient['patient_id'])
            if updated_patient:
                self.current_patient = updated_patient
            
            success_box = QMessageBox(self)
            success_box.setIcon(QMessageBox.Information)
            success_box.setWindowTitle("Examination Saved")
            success_box.setText("Examination details saved successfully!")
            success_box.setStyleSheet("""
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
            success_box.exec()
            
            # Update patient combo to reflect changes
            self._load_patients()
            
            # Re-select the current patient
            for i in range(self.patient_combo.count()):
                patient_data = self.patient_combo.itemData(i)
                if patient_data and patient_data['patient_id'] == self.current_patient['patient_id']:
                    self.patient_combo.setCurrentIndex(i)
                    break
        else:
            error_box = QMessageBox(self)
            error_box.setIcon(QMessageBox.Critical)
            error_box.setWindowTitle("Error")
            error_box.setText("Failed to save examination details. Please try again.")
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
    
    def _load_dental_chart(self):
        """Load dental chart data for current patient."""
        if not self.current_patient:
            return
        
        # First, reset all teeth to normal status to clear previous patient's data
        for quadrant_name, quadrant in self.quadrants.items():
            for tooth_number in range(1, 8):  # 7 teeth per quadrant
                quadrant.update_tooth_status(tooth_number, 'normal')
        
        # Then load the actual data for the current patient
        chart_data = dental_service.get_dental_chart(self.current_patient['patient_id'])
        
        for quadrant_name, records in chart_data.items():
            if quadrant_name in self.quadrants:
                quadrant = self.quadrants[quadrant_name]
                for record in records:
                    tooth_number = record['tooth_number']
                    status = record['status']
                    quadrant.update_tooth_status(tooth_number, status)
    
    def _on_tooth_selected(self, quadrant: str, tooth_number: int):
        """Handle tooth selection."""
        if not self.current_patient:
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setWindowTitle("No Patient")
            msg_box.setText("Please select a patient first.")
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
            return
        
        # Clear selection from other quadrants
        for quad_name, quad_widget in self.quadrants.items():
            if quad_name != quadrant:
                quad_widget.clear_selection()
        
        # Set tooth in detail panel
        self.tooth_detail_panel.set_tooth(
            self.current_patient['patient_id'],
            quadrant,
            tooth_number
        )
    
    def _on_tooth_saved(self):
        """Handle tooth data saved."""
        # Refresh the chart to show updated status
        if self.current_patient:
            self._load_dental_chart()
    
    def _clear_chart(self):
        """Clear the dental chart."""
        for quadrant in self.quadrants.values():
            quadrant.clear_selection()
            for tooth_number in range(1, 8):  # Changed from range(1, 9) to range(1, 8) for 7 teeth
                quadrant.update_tooth_status(tooth_number, 'normal')
        
        self.tooth_detail_panel.set_enabled(False)
        self.chief_complaint_edit.clear()
    
    def set_patient(self, patient: dict):
        """Set specific patient for examination."""
        # Find and select the patient in the combo box
        for i in range(self.patient_combo.count()):
            combo_patient = self.patient_combo.itemData(i)
            if combo_patient and combo_patient['patient_id'] == patient['patient_id']:
                self.patient_combo.setCurrentIndex(i)
                break
        else:
            # If patient not found in combo, add them and select
            display_text = f"{patient['full_name']} ({patient['patient_id']})"
            self.patient_combo.addItem(display_text, patient)
            self.patient_combo.setCurrentIndex(self.patient_combo.count() - 1)
