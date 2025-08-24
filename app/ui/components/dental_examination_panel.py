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
        self.setObjectName("examinationForm")
        
        layout = QVBoxLayout(self)
        
        # Form layout
        form_layout = QFormLayout()
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        
        # Examination date
        self.exam_date_edit = QDateEdit()
        self.exam_date_edit.setDate(QDate.currentDate())
        self.exam_date_edit.setCalendarPopup(True)
        form_layout.addRow("Examination Date:", self.exam_date_edit)
        
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
    
    def load_examination(self, examination_data: Dict):
        """Load examination data into the form."""
        self.current_examination = examination_data
        
        # Load basic info
        exam_date = examination_data.get('examination_date')
        if exam_date:
            if isinstance(exam_date, str):
                exam_date = datetime.strptime(exam_date, '%Y-%m-%d').date()
            self.exam_date_edit.setDate(QDate(exam_date))
        
        self.chief_complaint_edit.setPlainText(examination_data.get('chief_complaint', ''))
        self.present_illness_edit.setPlainText(examination_data.get('history_of_presenting_illness', ''))
        self.medical_history_edit.setPlainText(examination_data.get('medical_history', ''))
        self.dental_history_edit.setPlainText(examination_data.get('dental_history', ''))
    
    def get_examination_data(self) -> Dict:
        """Get examination data from the form."""
        return {
            'examination_date': self.exam_date_edit.date().toPython(),
            'chief_complaint': self.chief_complaint_edit.toPlainText().strip(),
            'history_of_presenting_illness': self.present_illness_edit.toPlainText().strip(),
            'medical_history': self.medical_history_edit.toPlainText().strip(),
            'dental_history': self.dental_history_edit.toPlainText().strip()
        }
    
    def clear_form(self):
        """Clear all form fields."""
        self.current_examination = None
        self.exam_date_edit.setDate(QDate.currentDate())
        self.chief_complaint_edit.clear()
        self.present_illness_edit.clear()
        self.medical_history_edit.clear()
        self.dental_history_edit.clear()


class ExaminationFindings(QFrame):
    """Examination findings and diagnosis section."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the examination findings UI."""
        self.setFrameStyle(QFrame.Box)
        self.setObjectName("examinationFindings")
        
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)

        self.extraoral_findings_edit = QTextEdit()
        self.extraoral_findings_edit.setMaximumHeight(40)
        self.extraoral_findings_edit.setPlaceholderText("Face, neck, lymph nodes, TMJ examination findings...")
        form_layout.addRow("Extra-oral Examination:", self.extraoral_findings_edit)

        self.intraoral_findings_edit = QTextEdit()
        self.intraoral_findings_edit.setMaximumHeight(40)
        self.intraoral_findings_edit.setPlaceholderText("Oral hygiene, gingiva, teeth, oral lesions, etc...")
        form_layout.addRow("Intra-oral Examination:", self.intraoral_findings_edit)

        self.periodontal_findings_edit = QTextEdit()
        self.periodontal_findings_edit.setMaximumHeight(40)
        self.periodontal_findings_edit.setPlaceholderText("Gingival condition, pocket depths, bleeding, mobility...")
        form_layout.addRow("Periodontal Examination:", self.periodontal_findings_edit)

        self.diagnosis_edit = QTextEdit()
        self.diagnosis_edit.setMaximumHeight(40)
        self.diagnosis_edit.setPlaceholderText("Primary and secondary diagnoses...")
        form_layout.addRow("Diagnosis:", self.diagnosis_edit)

        self.treatment_plan_edit = QTextEdit()
        self.treatment_plan_edit.setMaximumHeight(40)
        self.treatment_plan_edit.setPlaceholderText("Proposed treatment plan and recommendations...")
        form_layout.addRow("Treatment Plan:", self.treatment_plan_edit)
        
        layout.addLayout(form_layout)
    
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
        self.setObjectName("dentalExaminationPanel")
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
        self.new_btn.setObjectName("new_examination_button")
        self.new_btn.setStyleSheet("background-color: #27ae60; color: white; border: none; border-radius: 4px; padding: 6px 12px; font-weight: bold;")
        self.new_btn.clicked.connect(self.create_new_examination)
        header_layout.addWidget(self.new_btn)
        
        self.save_btn = QPushButton("Save")
        self.save_btn.setObjectName("save_examination_button")
        self.save_btn.setStyleSheet("background-color: #27ae60; color: white; border: none; border-radius: 4px; padding: 6px 12px; font-weight: bold;")
        self.save_btn.clicked.connect(self.save_examination)
        header_layout.addWidget(self.save_btn)
        
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setObjectName("deleteExaminationButton")
        self.delete_btn.setStyleSheet("background-color: #e74c3c; color: white; border: none; border-radius: 4px; padding: 6px 12px; font-weight: bold;")
        self.delete_btn.clicked.connect(self.delete_examination)
        header_layout.addWidget(self.delete_btn)
        
        layout.addLayout(header_layout)
        
        # Main content in tabs
        self.tab_widget = QTabWidget()
        self.tab_widget.setObjectName("examinationTabWidget")
        
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
        
        # Set minimum height for better visibility
        self.setMinimumHeight(400)  # Increased height
        
        # Status bar
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #7F8C8D; font-style: italic; padding: 4px;")
        layout.addWidget(self.status_label)
        
        
        
        # Connect form change signals to update button states
        self.connect_form_signals()
        
        # Initial state
        self.update_panel_state()
    
    
    
    def connect_form_signals(self):
        """Connect form field signals to update button states."""
        if hasattr(self.form_widget, 'chief_complaint_edit'):
            self.form_widget.chief_complaint_edit.textChanged.connect(self.update_panel_state)
    
    def set_patient(self, patient_id: int):
        """Set the current patient and load examinations."""
        self.patient_id = patient_id
        # Clear forms when patient changes
        self.clear_forms()
        self.current_examination_id = None
        # Reset examination selector
        self.examination_combo.setCurrentIndex(0)
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
        has_patient = self.patient_id is not None
        has_chief_complaint = bool(self.form_widget.chief_complaint_edit.toPlainText().strip()) if hasattr(self.form_widget, 'chief_complaint_edit') else False
        
        # Enable save button if we have a patient and chief complaint (for new) or existing examination
        self.save_btn.setEnabled(has_patient and (has_examination or has_chief_complaint))
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
                chief_complaint = exam.get('chief_complaint', '')[:40]  # First 40 chars of complaint
                display_text = f"{exam_date} - {chief_complaint}..."
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
        
        # Clear forms and reset to defaults
        self.clear_forms()
        self.current_examination_id = None
        
        # Reset combo selection to default
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
