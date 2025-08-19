"""
Dental Examination Panel - Comprehensive examination management interface.
"""
import logging
from datetime import date, datetime
from typing import Dict, List, Optional, Any
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, 
    QLineEdit, QTextEdit, QComboBox, QPushButton, QDateEdit,
    QSpinBox, QCheckBox, QTabWidget, QFormLayout, QScrollArea,
    QGridLayout, QFrame, QMessageBox, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import QFont, QPixmap, QPainter, QBrush, QColor

from ...services.dental_examination_service import dental_examination_service

logger = logging.getLogger(__name__)


class ExaminationFormWidget(QFrame):
    """Examination details form widget."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_examination = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the examination form UI."""
        self.setFrameStyle(QFrame.Box)
        self.setStyleSheet("""
            QFrame {
                border: 1px solid #19c5e5;
                border-radius: 8px;
                padding: 10px;
                background-color: #f8f9fa;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Form layout
        form_layout = QFormLayout()
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        
        # Examination date
        self.exam_date_edit = QDateEdit()
        self.exam_date_edit.setDate(QDate.currentDate())
        self.exam_date_edit.setCalendarPopup(True)
        form_layout.addRow("Examination Date:", self.exam_date_edit)
        
        # Examination type
        self.exam_type_combo = QComboBox()
        self.exam_type_combo.addItems([
            "routine_checkup", "emergency", "consultation", 
            "follow_up", "pre_treatment", "post_treatment"
        ])
        form_layout.addRow("Examination Type:", self.exam_type_combo)
        
        # Chief complaint
        self.chief_complaint_edit = QTextEdit()
        self.chief_complaint_edit.setMaximumHeight(80)
        self.chief_complaint_edit.setPlaceholderText("Patient's main concern or reason for visit...")
        form_layout.addRow("Chief Complaint:", self.chief_complaint_edit)
        
        # Present illness
        self.present_illness_edit = QTextEdit()
        self.present_illness_edit.setMaximumHeight(80)
        self.present_illness_edit.setPlaceholderText("History of present illness...")
        form_layout.addRow("Present Illness:", self.present_illness_edit)
        
        # Medical history
        self.medical_history_edit = QTextEdit()
        self.medical_history_edit.setMaximumHeight(80)
        self.medical_history_edit.setPlaceholderText("Relevant medical history...")
        form_layout.addRow("Medical History:", self.medical_history_edit)
        
        # Dental history
        self.dental_history_edit = QTextEdit()
        self.dental_history_edit.setMaximumHeight(80)
        self.dental_history_edit.setPlaceholderText("Previous dental treatments and history...")
        form_layout.addRow("Dental History:", self.dental_history_edit)
        
        layout.addLayout(form_layout)
        
        # Vital signs section
        vitals_group = QGroupBox("Vital Signs")
        vitals_layout = QGridLayout(vitals_group)
        
        # Blood pressure
        vitals_layout.addWidget(QLabel("Blood Pressure:"), 0, 0)
        self.bp_systolic_spin = QSpinBox()
        self.bp_systolic_spin.setRange(50, 250)
        self.bp_systolic_spin.setValue(120)
        vitals_layout.addWidget(self.bp_systolic_spin, 0, 1)
        vitals_layout.addWidget(QLabel("/"), 0, 2)
        self.bp_diastolic_spin = QSpinBox()
        self.bp_diastolic_spin.setRange(30, 150)
        self.bp_diastolic_spin.setValue(80)
        vitals_layout.addWidget(self.bp_diastolic_spin, 0, 3)
        vitals_layout.addWidget(QLabel("mmHg"), 0, 4)
        
        # Pulse rate
        vitals_layout.addWidget(QLabel("Pulse Rate:"), 1, 0)
        self.pulse_spin = QSpinBox()
        self.pulse_spin.setRange(40, 200)
        self.pulse_spin.setValue(72)
        vitals_layout.addWidget(self.pulse_spin, 1, 1)
        vitals_layout.addWidget(QLabel("bpm"), 1, 2)
        
        # Temperature
        vitals_layout.addWidget(QLabel("Temperature:"), 2, 0)
        self.temp_line_edit = QLineEdit()
        self.temp_line_edit.setText("98.6")
        self.temp_line_edit.setMaximumWidth(60)
        vitals_layout.addWidget(self.temp_line_edit, 2, 1)
        vitals_layout.addWidget(QLabel("°F"), 2, 2)
        
        layout.addWidget(vitals_group)
    
    def load_examination(self, examination_data: Dict):
        """Load examination data into the form."""
        self.current_examination = examination_data
        
        # Load basic info
        exam_date = examination_data.get('examination_date')
        if exam_date:
            if isinstance(exam_date, str):
                exam_date = datetime.strptime(exam_date, '%Y-%m-%d').date()
            self.exam_date_edit.setDate(QDate(exam_date))
        
        exam_type = examination_data.get('examination_type', '')
        index = self.exam_type_combo.findText(exam_type)
        if index >= 0:
            self.exam_type_combo.setCurrentIndex(index)
        
        self.chief_complaint_edit.setPlainText(examination_data.get('chief_complaint', ''))
        self.present_illness_edit.setPlainText(examination_data.get('present_illness', ''))
        self.medical_history_edit.setPlainText(examination_data.get('medical_history', ''))
        self.dental_history_edit.setPlainText(examination_data.get('dental_history', ''))
        
        # Load vital signs
        vital_signs = examination_data.get('vital_signs', {})
        if isinstance(vital_signs, dict):
            self.bp_systolic_spin.setValue(vital_signs.get('blood_pressure_systolic', 120))
            self.bp_diastolic_spin.setValue(vital_signs.get('blood_pressure_diastolic', 80))
            self.pulse_spin.setValue(vital_signs.get('pulse_rate', 72))
            self.temp_line_edit.setText(str(vital_signs.get('temperature', '98.6')))
    
    def get_examination_data(self) -> Dict:
        """Get examination data from the form."""
        return {
            'examination_date': self.exam_date_edit.date().toPython(),
            'examination_type': self.exam_type_combo.currentText(),
            'chief_complaint': self.chief_complaint_edit.toPlainText().strip(),
            'present_illness': self.present_illness_edit.toPlainText().strip(),
            'medical_history': self.medical_history_edit.toPlainText().strip(),
            'dental_history': self.dental_history_edit.toPlainText().strip(),
            'vital_signs': {
                'blood_pressure_systolic': self.bp_systolic_spin.value(),
                'blood_pressure_diastolic': self.bp_diastolic_spin.value(),
                'pulse_rate': self.pulse_spin.value(),
                'temperature': self.temp_line_edit.text().strip()
            }
        }
    
    def clear_form(self):
        """Clear all form fields."""
        self.current_examination = None
        self.exam_date_edit.setDate(QDate.currentDate())
        self.exam_type_combo.setCurrentIndex(0)
        self.chief_complaint_edit.clear()
        self.present_illness_edit.clear()
        self.medical_history_edit.clear()
        self.dental_history_edit.clear()
        self.bp_systolic_spin.setValue(120)
        self.bp_diastolic_spin.setValue(80)
        self.pulse_spin.setValue(72)
        self.temp_line_edit.setText("98.6")


class ExaminationFindings(QFrame):
    """Examination findings and diagnosis section."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the examination findings UI."""
        self.setFrameStyle(QFrame.Box)
        self.setStyleSheet("""
            QFrame {
                border: 1px solid #19c5e5;
                border-radius: 8px;
                padding: 10px;
                background-color: #f8f9fa;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Extra-oral examination
        extraoral_group = QGroupBox("Extra-oral Examination")
        extraoral_layout = QVBoxLayout(extraoral_group)
        
        self.extraoral_findings_edit = QTextEdit()
        self.extraoral_findings_edit.setMaximumHeight(100)
        self.extraoral_findings_edit.setPlaceholderText("Face, neck, lymph nodes, TMJ examination findings...")
        extraoral_layout.addWidget(self.extraoral_findings_edit)
        
        layout.addWidget(extraoral_group)
        
        # Intra-oral examination
        intraoral_group = QGroupBox("Intra-oral Examination")
        intraoral_layout = QVBoxLayout(intraoral_group)
        
        self.intraoral_findings_edit = QTextEdit()
        self.intraoral_findings_edit.setMaximumHeight(100)
        self.intraoral_findings_edit.setPlaceholderText("Oral hygiene, gingiva, teeth, oral lesions, etc...")
        intraoral_layout.addWidget(self.intraoral_findings_edit)
        
        layout.addWidget(intraoral_group)
        
        # Periodontal examination
        perio_group = QGroupBox("Periodontal Examination")
        perio_layout = QVBoxLayout(perio_group)
        
        self.periodontal_findings_edit = QTextEdit()
        self.periodontal_findings_edit.setMaximumHeight(100)
        self.periodontal_findings_edit.setPlaceholderText("Gingival condition, pocket depths, bleeding, mobility...")
        perio_layout.addWidget(self.periodontal_findings_edit)
        
        layout.addWidget(perio_group)
        
        # Diagnosis
        diagnosis_group = QGroupBox("Diagnosis")
        diagnosis_layout = QVBoxLayout(diagnosis_group)
        
        self.diagnosis_edit = QTextEdit()
        self.diagnosis_edit.setMaximumHeight(100)
        self.diagnosis_edit.setPlaceholderText("Primary and secondary diagnoses...")
        diagnosis_layout.addWidget(self.diagnosis_edit)
        
        layout.addWidget(diagnosis_group)
        
        # Treatment plan
        treatment_group = QGroupBox("Treatment Plan")
        treatment_layout = QVBoxLayout(treatment_group)
        
        self.treatment_plan_edit = QTextEdit()
        self.treatment_plan_edit.setMaximumHeight(100)
        self.treatment_plan_edit.setPlaceholderText("Proposed treatment plan and recommendations...")
        treatment_layout.addWidget(self.treatment_plan_edit)
        
        layout.addWidget(treatment_group)
    
    def load_findings(self, examination_data: Dict):
        """Load examination findings data."""
        findings = examination_data.get('examination_findings', {})
        if isinstance(findings, dict):
            self.extraoral_findings_edit.setPlainText(findings.get('extraoral_findings', ''))
            self.intraoral_findings_edit.setPlainText(findings.get('intraoral_findings', ''))
            self.periodontal_findings_edit.setPlainText(findings.get('periodontal_findings', ''))
        
        self.diagnosis_edit.setPlainText(examination_data.get('diagnosis', ''))
        self.treatment_plan_edit.setPlainText(examination_data.get('treatment_plan', ''))
    
    def get_findings_data(self) -> Dict:
        """Get findings data from the form."""
        return {
            'examination_findings': {
                'extraoral_findings': self.extraoral_findings_edit.toPlainText().strip(),
                'intraoral_findings': self.intraoral_findings_edit.toPlainText().strip(),
                'periodontal_findings': self.periodontal_findings_edit.toPlainText().strip()
            },
            'diagnosis': self.diagnosis_edit.toPlainText().strip(),
            'treatment_plan': self.treatment_plan_edit.toPlainText().strip()
        }
    
    def clear_findings(self):
        """Clear all findings fields."""
        self.extraoral_findings_edit.clear()
        self.intraoral_findings_edit.clear()
        self.periodontal_findings_edit.clear()
        self.diagnosis_edit.clear()
        self.treatment_plan_edit.clear()


class DentalExaminationPanel(QGroupBox):
    """Comprehensive dental examination management panel."""
    
    examination_saved = Signal(dict)
    examination_selected = Signal(dict)
    
    def __init__(self, patient_id: Optional[int] = None, parent=None):
        super().__init__("Dental Examination", parent)
        self.patient_id = patient_id
        self.current_examination_id = None
        self.examinations_list = []
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the dental examination panel UI."""
        layout = QVBoxLayout(self)
        
        # Header with controls
        header_layout = QHBoxLayout()
        
        # Examination selector
        selector_label = QLabel("Select Examination:")
        header_layout.addWidget(selector_label)
        
        self.examination_combo = QComboBox()
        self.examination_combo.setMinimumWidth(200)
        self.examination_combo.currentTextChanged.connect(self.on_examination_selected)
        header_layout.addWidget(self.examination_combo)
        
        header_layout.addStretch()
        
        # Action buttons
        self.new_btn = QPushButton("New Examination")
        self.new_btn.clicked.connect(self.create_new_examination)
        header_layout.addWidget(self.new_btn)
        
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_examination)
        header_layout.addWidget(self.save_btn)
        
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.clicked.connect(self.delete_examination)
        self.delete_btn.setStyleSheet("background-color: #dc3545; color: white;")
        header_layout.addWidget(self.delete_btn)
        
        layout.addLayout(header_layout)
        
        # Main content in tabs
        self.tab_widget = QTabWidget()
        
        # Basic Information Tab
        basic_scroll = QScrollArea()
        basic_scroll.setWidgetResizable(True)
        self.form_widget = ExaminationFormWidget()
        basic_scroll.setWidget(self.form_widget)
        self.tab_widget.addTab(basic_scroll, "Basic Information")
        
        # Findings & Diagnosis Tab
        findings_scroll = QScrollArea()
        findings_scroll.setWidgetResizable(True)
        self.findings_widget = ExaminationFindings()
        findings_scroll.setWidget(self.findings_widget)
        self.tab_widget.addTab(findings_scroll, "Findings & Diagnosis")
        
        layout.addWidget(self.tab_widget)
        
        # Status bar
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #666; font-style: italic; padding: 5px;")
        layout.addWidget(self.status_label)
        
        # Apply styles
        self.apply_styles()
        
        # Initial state
        self.update_panel_state()
    
    def apply_styles(self):
        """Apply consistent styling to the panel."""
        self.setStyleSheet("""
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
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            QComboBox {
                padding: 5px;
                border: 1px solid #19c5e5;
                border-radius: 3px;
            }
        """)
    
    def set_patient(self, patient_id: int):
        """Set the current patient and load examinations."""
        self.patient_id = patient_id
        self.update_panel_state()
        self.load_examinations()
    
    def update_panel_state(self):
        """Update panel title and controls state."""
        if not self.patient_id:
            self.setTitle("Dental Examination (Select a patient first)")
            self.setEnabled(False)
        else:
            self.setTitle(f"Dental Examination - Patient #{self.patient_id}")
            self.setEnabled(True)
        
        # Update button states
        has_examination = self.current_examination_id is not None
        self.save_btn.setEnabled(has_examination or self.form_widget.current_examination is not None)
        self.delete_btn.setEnabled(has_examination)
    
    def load_examinations(self):
        """Load examinations for the current patient."""
        if not self.patient_id:
            self.examinations_list = []
            self.examination_combo.clear()
            return
        
        try:
            # Get examinations from service
            self.examinations_list = dental_examination_service.get_patient_examinations(self.patient_id)
            
            # Update combo box
            self.examination_combo.clear()
            self.examination_combo.addItem("-- Select Examination --", None)
            
            for exam in self.examinations_list:
                exam_date = exam.get('examination_date', 'Unknown')
                exam_type = exam.get('examination_type', '').replace('_', ' ').title()
                display_text = f"{exam_date} - {exam_type}"
                self.examination_combo.addItem(display_text, exam.get('id'))
            
            # Update status
            count = len(self.examinations_list)
            self.status_label.setText(f"{count} examination{'s' if count != 1 else ''} found")
            
        except Exception as e:
            logger.error(f"Error loading examinations: {str(e)}")
            self.status_label.setText("Error loading examinations")
    
    def on_examination_selected(self):
        """Handle examination selection from combo box."""
        current_data = self.examination_combo.currentData()
        if current_data:
            self.current_examination_id = current_data
            self.load_selected_examination()
        else:
            self.current_examination_id = None
            self.clear_forms()
        
        self.update_panel_state()
    
    def load_selected_examination(self):
        """Load the selected examination data."""
        if not self.current_examination_id:
            return
        
        try:
            # Find examination in list
            examination = None
            for exam in self.examinations_list:
                if exam.get('id') == self.current_examination_id:
                    examination = exam
                    break
            
            if examination:
                # Load into forms
                self.form_widget.load_examination(examination)
                self.findings_widget.load_findings(examination)
                
                # Emit signal
                self.examination_selected.emit(examination)
                
                self.status_label.setText(f"Loaded examination from {examination.get('examination_date', 'Unknown')}")
            
        except Exception as e:
            logger.error(f"Error loading examination: {str(e)}")
            self.status_label.setText("Error loading examination")
    
    def create_new_examination(self):
        """Create a new examination."""
        if not self.patient_id:
            QMessageBox.warning(self, "Warning", "Please select a patient first.")
            return
        
        # Clear forms
        self.clear_forms()
        self.current_examination_id = None
        
        # Reset combo selection
        self.examination_combo.setCurrentIndex(0)
        
        # Update status
        self.status_label.setText("New examination - ready to save")
        self.update_panel_state()
    
    def save_examination(self):
        """Save the current examination."""
        if not self.patient_id:
            QMessageBox.warning(self, "Warning", "Please select a patient first.")
            return
        
        try:
            # Get data from forms
            basic_data = self.form_widget.get_examination_data()
            findings_data = self.findings_widget.get_findings_data()
            
            # Combine data
            examination_data = {
                'patient_id': self.patient_id,
                **basic_data,
                **findings_data
            }
            
            # Validate required fields
            if not examination_data.get('chief_complaint', '').strip():
                QMessageBox.warning(self, "Validation Error", "Chief complaint is required.")
                return
            
            if self.current_examination_id:
                # Update existing examination
                examination_data['id'] = self.current_examination_id
                result = dental_examination_service.update_examination(
                    self.current_examination_id, examination_data
                )
                action = "updated"
            else:
                # Create new examination
                result = dental_examination_service.create_examination(examination_data)
                if result.get('success') and result.get('examination'):
                    self.current_examination_id = result['examination'].get('id')
                action = "created"
            
            if result.get('success'):
                # Reload examinations list
                self.load_examinations()
                
                # Select the saved examination
                if self.current_examination_id:
                    for i in range(self.examination_combo.count()):
                        if self.examination_combo.itemData(i) == self.current_examination_id:
                            self.examination_combo.setCurrentIndex(i)
                            break
                
                # Emit signal
                if result.get('examination'):
                    self.examination_saved.emit(result['examination'])
                
                self.status_label.setText(f"Examination {action} successfully")
                QMessageBox.information(self, "Success", f"Examination {action} successfully!")
            else:
                error_msg = result.get('error', 'Unknown error occurred')
                self.status_label.setText(f"Error: {error_msg}")
                QMessageBox.critical(self, "Error", f"Failed to save examination: {error_msg}")
                
        except Exception as e:
            logger.error(f"Error saving examination: {str(e)}")
            error_msg = f"Error saving examination: {str(e)}"
            self.status_label.setText(error_msg)
            QMessageBox.critical(self, "Error", error_msg)
    
    def delete_examination(self):
        """Delete the current examination."""
        if not self.current_examination_id:
            QMessageBox.warning(self, "Warning", "Please select an examination to delete.")
            return
        
        # Confirm deletion
        reply = QMessageBox.question(
            self, 
            "Confirm Deletion", 
            "Are you sure you want to delete this examination?\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                result = dental_examination_service.delete_examination(self.current_examination_id)
                
                if result.get('success'):
                    # Clear forms and reload list
                    self.clear_forms()
                    self.current_examination_id = None
                    self.load_examinations()
                    
                    self.status_label.setText("Examination deleted successfully")
                    QMessageBox.information(self, "Success", "Examination deleted successfully!")
                else:
                    error_msg = result.get('error', 'Unknown error occurred')
                    self.status_label.setText(f"Error: {error_msg}")
                    QMessageBox.critical(self, "Error", f"Failed to delete examination: {error_msg}")
                    
            except Exception as e:
                logger.error(f"Error deleting examination: {str(e)}")
                error_msg = f"Error deleting examination: {str(e)}"
                self.status_label.setText(error_msg)
                QMessageBox.critical(self, "Error", error_msg)
    
    def clear_forms(self):
        """Clear all form fields."""
        self.form_widget.clear_form()
        self.findings_widget.clear_findings()
    
    def get_current_examination_id(self) -> Optional[int]:
        """Get the current examination ID."""
        return self.current_examination_id
    
    def get_current_examination_data(self) -> Optional[Dict]:
        """Get the current examination data from forms."""
        if not self.patient_id:
            return None
        
        try:
            basic_data = self.form_widget.get_examination_data()
            findings_data = self.findings_widget.get_findings_data()
            
            return {
                'patient_id': self.patient_id,
                'id': self.current_examination_id,
                **basic_data,
                **findings_data
            }
        except Exception as e:
            logger.error(f"Error getting examination data: {str(e)}")
            return None
