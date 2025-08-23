"""
Visit Entry Panel - New visit entry form linked to current examination.
"""
import logging
from datetime import date, time
from typing import Dict, List, Optional, Any
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox, 
    QLabel, QLineEdit, QTextEdit, QDateEdit, QTimeEdit, QDoubleSpinBox,
    QPushButton, QCheckBox, QScrollArea, QFrame, QComboBox, QSpinBox
)
from PySide6.QtCore import Qt, Signal, QDate, QTime
from PySide6.QtGui import QFont

from ...services.visit_records_service import visit_records_service

logger = logging.getLogger(__name__)


class ToothSelectionWidget(QWidget):
    """Compact tooth selection widget with checkboxes."""
    
    teeth_selected = Signal(list)  # List of selected tooth numbers
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tooth_checkboxes = {}
        self.setup_ui()
    
    def setup_ui(self):
        """Setup compact tooth selection layout."""
        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        
        # Upper teeth
        upper_group = QGroupBox("Upper Teeth")
        upper_layout = QGridLayout(upper_group)
        upper_layout.setSpacing(2)
        
        # Upper right: 18-11
        for i, tooth_num in enumerate(range(18, 10, -1)):
            checkbox = QCheckBox(f"{tooth_num}")
            checkbox.setMaximumWidth(50)
            checkbox.stateChanged.connect(self.on_selection_changed)
            self.tooth_checkboxes[tooth_num] = checkbox
            upper_layout.addWidget(checkbox, 0, i)
        
        # Upper left: 21-28
        for i, tooth_num in enumerate(range(21, 29)):
            checkbox = QCheckBox(f"{tooth_num}")
            checkbox.setMaximumWidth(50)
            checkbox.stateChanged.connect(self.on_selection_changed)
            self.tooth_checkboxes[tooth_num] = checkbox
            upper_layout.addWidget(checkbox, 0, 8 + i)
        
        layout.addWidget(upper_group)
        
        # Lower teeth
        lower_group = QGroupBox("Lower Teeth")
        lower_layout = QGridLayout(lower_group)
        lower_layout.setSpacing(2)
        
        # Lower right: 48-41
        for i, tooth_num in enumerate(range(48, 40, -1)):
            checkbox = QCheckBox(f"{tooth_num}")
            checkbox.setMaximumWidth(50)
            checkbox.stateChanged.connect(self.on_selection_changed)
            self.tooth_checkboxes[tooth_num] = checkbox
            lower_layout.addWidget(checkbox, 0, i)
        
        # Lower left: 31-38
        for i, tooth_num in enumerate(range(31, 39)):
            checkbox = QCheckBox(f"{tooth_num}")
            checkbox.setMaximumWidth(50)
            checkbox.stateChanged.connect(self.on_selection_changed)
            self.tooth_checkboxes[tooth_num] = checkbox
            lower_layout.addWidget(checkbox, 0, 8 + i)
        
        layout.addWidget(lower_group)
        
        # Selection controls
        controls_layout = QHBoxLayout()
        
        select_all_btn = QPushButton("Select All")
        select_all_btn.setMaximumWidth(80)
        select_all_btn.clicked.connect(self.select_all)
        controls_layout.addWidget(select_all_btn)
        
        clear_all_btn = QPushButton("Clear All")
        clear_all_btn.setMaximumWidth(80)
        clear_all_btn.clicked.connect(self.clear_all)
        controls_layout.addWidget(clear_all_btn)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
    
    def on_selection_changed(self):
        """Handle tooth selection change."""
        selected_teeth = []
        for tooth_num, checkbox in self.tooth_checkboxes.items():
            if checkbox.isChecked():
                selected_teeth.append(tooth_num)
        
        self.teeth_selected.emit(selected_teeth)
    
    def select_all(self):
        """Select all teeth."""
        for checkbox in self.tooth_checkboxes.values():
            checkbox.setChecked(True)
    
    def clear_all(self):
        """Clear all tooth selections."""
        for checkbox in self.tooth_checkboxes.values():
            checkbox.setChecked(False)
    
    def get_selected_teeth(self) -> List[int]:
        """Get list of selected tooth numbers."""
        selected = []
        for tooth_num, checkbox in self.tooth_checkboxes.items():
            if checkbox.isChecked():
                selected.append(tooth_num)
        return selected
    
    def set_selected_teeth(self, tooth_numbers: List[int]):
        """Set selected teeth."""
        self.clear_all()
        for tooth_num in tooth_numbers:
            if tooth_num in self.tooth_checkboxes:
                self.tooth_checkboxes[tooth_num].setChecked(True)


class VisitEntryPanel(QGroupBox):
    """New visit entry form"""
    
    visit_added = Signal(dict)
    
    def __init__(self, patient_id: Optional[int] = None, examination_id: Optional[int] = None, parent=None):
        super().__init__("Add New Visit", parent)
        self.patient_id = patient_id
        self.examination_id = examination_id
        self.selected_teeth = []
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the visit entry form UI."""
        layout = QVBoxLayout(self)
        
        # Scroll area for form
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        form_layout = QVBoxLayout(scroll_widget)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
        
        # Set minimum height for better visibility
        self.setMinimumHeight(350)  # Increased height for visit entry
        
        # Basic visit information
        basic_group = QGroupBox("Visit Information")
        basic_layout = QGridLayout(basic_group)
        
        # Date picker (default: today)
        basic_layout.addWidget(QLabel("Date:"), 0, 0)
        self.date_edit = QDateEdit(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        basic_layout.addWidget(self.date_edit, 0, 1)
        
        # Time picker
        basic_layout.addWidget(QLabel("Time:"), 0, 2)
        self.time_edit = QTimeEdit(QTime.currentTime())
        self.time_edit.setDisplayFormat("hh:mm AP")
        basic_layout.addWidget(self.time_edit, 0, 3)
        
        # Amount field
        basic_layout.addWidget(QLabel("Amount:"), 1, 0)
        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setRange(0.0, 99999.99)
        self.amount_spin.setPrefix("$")
        self.amount_spin.setDecimals(2)
        basic_layout.addWidget(self.amount_spin, 1, 1)
        
        # Visit type
        basic_layout.addWidget(QLabel("Visit Type:"), 1, 2)
        self.visit_type_combo = QComboBox()
        self.visit_type_combo.addItems([
            "consultation", "treatment", "cleaning", "checkup", 
            "follow_up", "emergency", "extraction", "filling", "root_canal"
        ])
        basic_layout.addWidget(self.visit_type_combo, 1, 3)
        
        form_layout.addWidget(basic_group)
        
        # Clinical information
        clinical_group = QGroupBox("Clinical Information")
        clinical_layout = QVBoxLayout(clinical_group)
        
        # Chief complaint input
        clinical_layout.addWidget(QLabel("Chief Complaint:"))
        self.chief_complaint_edit = QTextEdit()
        self.chief_complaint_edit.setMaximumHeight(40)  # Increased height
        self.chief_complaint_edit.setPlaceholderText("Patient's main concern or reason for visit...")
        clinical_layout.addWidget(self.chief_complaint_edit)
        
        # Diagnosis input
        clinical_layout.addWidget(QLabel("Diagnosis:"))
        self.diagnosis_edit = QTextEdit()
        self.diagnosis_edit.setMaximumHeight(40)  # Increased height
        self.diagnosis_edit.setPlaceholderText("Clinical diagnosis...")
        clinical_layout.addWidget(self.diagnosis_edit)
        
        # Treatment input
        clinical_layout.addWidget(QLabel("Treatment Performed:"))
        self.treatment_edit = QTextEdit()
        self.treatment_edit.setMaximumHeight(40)  # Increased height
        self.treatment_edit.setPlaceholderText("Treatment performed during this visit...")
        clinical_layout.addWidget(self.treatment_edit)
        
        # Advice input
        clinical_layout.addWidget(QLabel("Doctor's Advice:"))
        self.advice_edit = QTextEdit()
        self.advice_edit.setMaximumHeight(40)  # Increased height
        self.advice_edit.setPlaceholderText("Instructions and advice given to patient...")
        clinical_layout.addWidget(self.advice_edit)
        
        form_layout.addWidget(clinical_group)
        
        # Affected teeth selection
        teeth_group = QGroupBox("Affected Teeth")
        teeth_layout = QVBoxLayout(teeth_group)
        
        self.tooth_selection_widget = ToothSelectionWidget()
        self.tooth_selection_widget.teeth_selected.connect(self.on_teeth_selected)
        teeth_layout.addWidget(self.tooth_selection_widget)
        
        form_layout.addWidget(teeth_group)
        
        # Add visit button
        self.add_visit_btn = QPushButton("Add Visit Record")
        self.add_visit_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #BDC3C7;
                color: #7F8C8D;
                border: 1px dashed #95A5A6;
            }
        """)
        self.add_visit_btn.clicked.connect(self.add_visit_record)
        layout.addWidget(self.add_visit_btn)
        
        # Enable/disable based on patient selection
        self.update_form_state()
    
    def set_patient(self, patient_id: int):
        """Set the current patient."""
        self.patient_id = patient_id
        self.update_form_state()
    
    def set_examination(self, examination_id: int):
        """Set the current examination."""
        self.examination_id = examination_id
        self.update_form_state()
    
    def update_form_state(self):
        """Update form enabled state based on patient/examination selection."""
        has_patient = self.patient_id is not None
        self.add_visit_btn.setEnabled(has_patient)
        
        if not has_patient:
            self.setTitle("Add New Visit (Select a patient first)")
            self.add_visit_btn.setText("Select Patient First")
        else:
            examination_text = f" - Exam #{self.examination_id}" if self.examination_id else ""
            self.setTitle(f"Add New Visit{examination_text}")
            self.add_visit_btn.setText("Add Visit Record")
    
    def on_teeth_selected(self, selected_teeth: List[int]):
        """Handle tooth selection change."""
        self.selected_teeth = selected_teeth
    
    def add_visit_record(self):
        """Create new visit record and update tooth histories."""
        if not self.patient_id:
            return
        
        try:
            # Gather visit data
            visit_data = {
                'visit_date': self.date_edit.date().toPython(),
                'visit_time': self.time_edit.time().toPython(),
                'visit_type': self.visit_type_combo.currentText(),
                'status': 'completed',  # Assume completed since adding after the fact
                'cost': self.amount_spin.value() if self.amount_spin.value() > 0 else None,
                'payment_status': 'paid' if self.amount_spin.value() > 0 else 'pending',
                'examination_id': self.examination_id,
                'notes': self.chief_complaint_edit.toPlainText().strip(),
                'treatment_performed': self.treatment_edit.toPlainText().strip(),
                'doctor_name': 'Dr. Default'  # Could be made configurable
            }
            
            # Additional fields for our visit record format
            additional_data = {
                'chief_complaint': self.chief_complaint_edit.toPlainText().strip(),
                'diagnosis': self.diagnosis_edit.toPlainText().strip(),
                'advice': self.advice_edit.toPlainText().strip(),
                'affected_teeth': self.selected_teeth
            }
            
            # Combine data
            visit_data.update(additional_data)
            
            # Validate required fields
            if not visit_data['chief_complaint'] and not visit_data['treatment_performed']:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.warning(
                    self, 
                    "Validation Error", 
                    "Either chief complaint or treatment performed must be provided."
                )
                return
            
            # Create visit record
            result = visit_records_service.create_visit(self.patient_id, visit_data)
            
            if result:
                # Emit success signal
                self.visit_added.emit(result)
                
                # Clear form
                self.clear_form()
                
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.information(
                    self, 
                    "Success", 
                    f"Visit record added successfully!"
                )
            else:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.warning(
                    self, 
                    "Error", 
                    "Failed to create visit record."
                )
                
        except Exception as e:
            logger.error(f"Error creating visit record: {str(e)}")
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(
                self, 
                "Error", 
                f"Error creating visit record: {str(e)}"
            )
    
    def clear_form(self):
        """Clear the form fields."""
        self.date_edit.setDate(QDate.currentDate())
        self.time_edit.setTime(QTime.currentTime())
        self.amount_spin.setValue(0.0)
        self.visit_type_combo.setCurrentIndex(0)
        self.chief_complaint_edit.clear()
        self.diagnosis_edit.clear()
        self.treatment_edit.clear()
        self.advice_edit.clear()
        self.tooth_selection_widget.clear_all()
    
    def populate_from_examination(self, examination_data: Dict):
        """Populate form fields from examination data."""
        if examination_data.get('chief_complaint'):
            self.chief_complaint_edit.setPlainText(examination_data['chief_complaint'])
        
        if examination_data.get('diagnosis'):
            self.diagnosis_edit.setPlainText(examination_data['diagnosis'])
    
    def set_affected_teeth(self, tooth_numbers: List[int]):
        """Set the affected teeth selection."""
        self.tooth_selection_widget.set_selected_teeth(tooth_numbers)

    def get_visit_data(self) -> Dict:
        """Get the visit data from the form fields."""
        visit_data = {
            'visit_date': self.date_edit.date().toPython(),
            'visit_time': self.time_edit.time().toPython(),
            'visit_type': self.visit_type_combo.currentText(),
            'status': 'completed',
            'cost': self.amount_spin.value() if self.amount_spin.value() > 0 else None,
            'payment_status': 'paid' if self.amount_spin.value() > 0 else 'pending',
            'examination_id': self.examination_id,
            'notes': self.chief_complaint_edit.toPlainText().strip(),
            'treatment_performed': self.treatment_edit.toPlainText().strip(),
            'doctor_name': 'Dr. Default',
            'chief_complaint': self.chief_complaint_edit.toPlainText().strip(),
            'diagnosis': self.diagnosis_edit.toPlainText().strip(),
            'advice': self.advice_edit.toPlainText().strip(),
            'affected_teeth': self.selected_teeth
        }
        return visit_data

    def load_visit_data(self, visit_data: Dict):
        """Load visit data into the form fields."""
        visit_date = visit_data.get('visit_date')
        if isinstance(visit_date, str):
            self.date_edit.setDate(QDate.fromString(visit_date, 'yyyy-MM-dd'))
        elif isinstance(visit_date, date):
            self.date_edit.setDate(QDate(visit_date))

        visit_time = visit_data.get('visit_time')
        if isinstance(visit_time, str):
            self.time_edit.setTime(QTime.fromString(visit_time, 'HH:mm:ss'))
        elif isinstance(visit_time, time):
            self.time_edit.setTime(QTime(visit_time))

        cost = visit_data.get('cost')
        self.amount_spin.setValue(cost if cost is not None else 0.0)
        self.visit_type_combo.setCurrentText(visit_data.get('visit_type', ''))
        self.chief_complaint_edit.setPlainText(visit_data.get('chief_complaint', ''))
        self.diagnosis_edit.setPlainText(visit_data.get('diagnosis', ''))
        self.treatment_edit.setPlainText(visit_data.get('treatment_performed', ''))
        self.advice_edit.setPlainText(visit_data.get('advice', ''))
        self.tooth_selection_widget.set_selected_teeth(visit_data.get('affected_teeth', []))
