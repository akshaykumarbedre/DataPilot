"""
Dental Examination Management Widget for creating and managing dental examinations.
"""
import logging
from datetime import date, datetime
from typing import Dict, List, Optional, Any
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, 
    QLabel, QComboBox, QTextEdit, QTabWidget, QFrame, QScrollArea,
    QGroupBox, QSplitter, QMessageBox, QDialog, QDialogButtonBox, 
    QFormLayout, QLineEdit, QDateEdit, QSpinBox, QListWidget,
    QListWidgetItem, QTableWidget, QTableWidgetItem, QHeaderView,
    QCheckBox, QProgressBar
)
from PySide6.QtCore import Qt, Signal, QDate, QTimer
from PySide6.QtGui import QFont, QPixmap, QIcon

from ..services.dental_examination_service import dental_examination_service
from ..services.tooth_history_service import tooth_history_service
from ..services.visit_records_service import visit_records_service
from ..services.custom_status_service import custom_status_service

logger = logging.getLogger(__name__)


class ExaminationDialog(QDialog):
    """Dialog for creating/editing dental examinations."""
    
    examination_saved = Signal(dict)
    
    def __init__(self, patient_id: int, examination_data: Optional[Dict] = None, parent=None):
        super().__init__(parent)
        self.patient_id = patient_id
        self.examination_data = examination_data
        self.is_edit_mode = examination_data is not None
        
        self.setup_ui()
        if self.is_edit_mode:
            self.populate_form()
    
    def setup_ui(self):
        """Setup the examination dialog UI."""
        self.setWindowTitle("Edit Examination" if self.is_edit_mode else "New Examination")
        self.setModal(True)
        self.resize(600, 700)
        
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("Edit Examination" if self.is_edit_mode else "Create New Examination")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        header.setStyleSheet("color: #19c5e5; margin: 10px;")
        layout.addWidget(header)
        
        # Scroll area for form
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        form_layout = QFormLayout(scroll_widget)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
        
        # Basic Information
        basic_group = QGroupBox("Basic Information")
        basic_layout = QFormLayout(basic_group)
        
        # Examination date
        self.date_edit = QDateEdit(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        basic_layout.addRow("Examination Date:", self.date_edit)
        
        # Examination type
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "routine_checkup", "consultation", "emergency", "follow_up", 
            "comprehensive", "periodontal", "orthodontic", "oral_surgery"
        ])
        basic_layout.addRow("Examination Type:", self.type_combo)
        
        # Doctor name
        self.doctor_edit = QLineEdit()
        basic_layout.addRow("Doctor Name:", self.doctor_edit)
        
        form_layout.addRow(basic_group)
        
        # Chief Complaint
        complaint_group = QGroupBox("Chief Complaint")
        complaint_layout = QVBoxLayout(complaint_group)
        
        self.chief_complaint_edit = QTextEdit()
        self.chief_complaint_edit.setMaximumHeight(80)
        self.chief_complaint_edit.setPlaceholderText("Patient's main concern or reason for visit...")
        complaint_layout.addWidget(self.chief_complaint_edit)
        
        form_layout.addRow(complaint_group)
        
        # Clinical Findings
        findings_group = QGroupBox("Clinical Findings")
        findings_layout = QVBoxLayout(findings_group)
        
        self.clinical_findings_edit = QTextEdit()
        self.clinical_findings_edit.setMaximumHeight(120)
        self.clinical_findings_edit.setPlaceholderText("Detailed clinical observations and findings...")
        findings_layout.addWidget(self.clinical_findings_edit)
        
        form_layout.addRow(findings_group)
        
        # Diagnosis
        diagnosis_group = QGroupBox("Diagnosis")
        diagnosis_layout = QVBoxLayout(diagnosis_group)
        
        self.diagnosis_edit = QTextEdit()
        self.diagnosis_edit.setMaximumHeight(100)
        self.diagnosis_edit.setPlaceholderText("Primary and secondary diagnoses...")
        diagnosis_layout.addWidget(self.diagnosis_edit)
        
        form_layout.addRow(diagnosis_group)
        
        # Treatment Plan
        treatment_group = QGroupBox("Treatment Plan")
        treatment_layout = QVBoxLayout(treatment_group)
        
        self.treatment_plan_edit = QTextEdit()
        self.treatment_plan_edit.setMaximumHeight(120)
        self.treatment_plan_edit.setPlaceholderText("Recommended treatments and procedures...")
        treatment_layout.addWidget(self.treatment_plan_edit)
        
        form_layout.addRow(treatment_group)
        
        # Additional Information
        additional_group = QGroupBox("Additional Information")
        additional_layout = QFormLayout(additional_group)
        
        # Notes
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(80)
        self.notes_edit.setPlaceholderText("Additional notes or observations...")
        additional_layout.addRow("Notes:", self.notes_edit)
        
        # Follow-up date
        self.followup_date_edit = QDateEdit()
        self.followup_date_edit.setCalendarPopup(True)
        self.followup_date_edit.setSpecialValueText("No follow-up scheduled")
        self.followup_date_edit.setDate(QDate())  # Empty date
        additional_layout.addRow("Follow-up Date:", self.followup_date_edit)
        
        # Status
        self.status_combo = QComboBox()
        self.status_combo.addItems(["draft", "completed", "reviewed", "archived"])
        self.status_combo.setCurrentText("draft")
        additional_layout.addRow("Status:", self.status_combo)
        
        form_layout.addRow(additional_group)
        
        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.save_examination)
        button_box.rejected.connect(self.reject)
        
        # Style the save button
        save_button = button_box.button(QDialogButtonBox.Save)
        save_button.setStyleSheet("""
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
        """)
        
        layout.addWidget(button_box)
    
    def populate_form(self):
        """Populate form with existing examination data."""
        if not self.examination_data:
            return
        
        try:
            data = self.examination_data
            
            # Convert date string to QDate if needed
            if isinstance(data.get('examination_date'), str):
                exam_date = datetime.strptime(data['examination_date'], '%Y-%m-%d').date()
                self.date_edit.setDate(QDate(exam_date))
            elif data.get('examination_date'):
                self.date_edit.setDate(QDate(data['examination_date']))
            
            # Set other fields
            if data.get('examination_type'):
                self.type_combo.setCurrentText(data['examination_type'])
            
            self.doctor_edit.setText(data.get('doctor_name', ''))
            self.chief_complaint_edit.setPlainText(data.get('chief_complaint', ''))
            self.clinical_findings_edit.setPlainText(data.get('clinical_findings', ''))
            self.diagnosis_edit.setPlainText(data.get('diagnosis', ''))
            self.treatment_plan_edit.setPlainText(data.get('treatment_plan', ''))
            self.notes_edit.setPlainText(data.get('notes', ''))
            
            # Follow-up date
            if data.get('followup_date'):
                if isinstance(data['followup_date'], str):
                    followup_date = datetime.strptime(data['followup_date'], '%Y-%m-%d').date()
                    self.followup_date_edit.setDate(QDate(followup_date))
                else:
                    self.followup_date_edit.setDate(QDate(data['followup_date']))
            
            if data.get('status'):
                self.status_combo.setCurrentText(data['status'])
                
        except Exception as e:
            logger.error(f"Error populating form: {str(e)}")
            QMessageBox.warning(self, "Error", "Error loading examination data.")
    
    def save_examination(self):
        """Save the examination."""
        try:
            # Gather form data
            examination_data = {
                'examination_date': self.date_edit.date().toPython(),
                'examination_type': self.type_combo.currentText(),
                'doctor_name': self.doctor_edit.text().strip(),
                'chief_complaint': self.chief_complaint_edit.toPlainText().strip(),
                'clinical_findings': self.clinical_findings_edit.toPlainText().strip(),
                'diagnosis': self.diagnosis_edit.toPlainText().strip(),
                'treatment_plan': self.treatment_plan_edit.toPlainText().strip(),
                'notes': self.notes_edit.toPlainText().strip(),
                'status': self.status_combo.currentText()
            }
            
            # Follow-up date (optional)
            followup_date = self.followup_date_edit.date()
            if followup_date.isValid() and followup_date != QDate():
                examination_data['followup_date'] = followup_date.toPython()
            
            # Validate required fields
            if not examination_data['doctor_name']:
                QMessageBox.warning(self, "Validation Error", "Doctor name is required.")
                return
            
            if not examination_data['chief_complaint'] and not examination_data['clinical_findings']:
                QMessageBox.warning(self, "Validation Error", "Either chief complaint or clinical findings must be provided.")
                return
            
            # Save examination
            if self.is_edit_mode:
                # Update existing examination
                success = dental_examination_service.update_examination(
                    self.examination_data['id'], examination_data
                )
                if success:
                    examination_data['id'] = self.examination_data['id']
                    self.examination_saved.emit(examination_data)
                    QMessageBox.information(self, "Success", "Examination updated successfully!")
                    self.accept()
                else:
                    QMessageBox.warning(self, "Error", "Failed to update examination.")
            else:
                # Create new examination
                result = dental_examination_service.create_examination(
                    self.patient_id, examination_data
                )
                if result:
                    self.examination_saved.emit(result)
                    QMessageBox.information(self, "Success", "Examination created successfully!")
                    self.accept()
                else:
                    QMessageBox.warning(self, "Error", "Failed to create examination.")
                    
        except Exception as e:
            logger.error(f"Error saving examination: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error saving examination: {str(e)}")


class ExaminationListWidget(QWidget):
    """Widget for displaying and managing examination list."""
    
    examination_selected = Signal(dict)
    examination_deleted = Signal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.patient_id = None
        self.examinations = []
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the examination list UI."""
        layout = QVBoxLayout(self)
        
        # Header with controls
        header_layout = QHBoxLayout()
        
        title = QLabel("Examinations")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        title.setStyleSheet("color: #19c5e5;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # New examination button
        self.new_exam_button = QPushButton("New Examination")
        self.new_exam_button.setStyleSheet("""
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
        self.new_exam_button.clicked.connect(self.create_new_examination)
        header_layout.addWidget(self.new_exam_button)
        
        # Refresh button
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_examinations)
        header_layout.addWidget(self.refresh_button)
        
        layout.addLayout(header_layout)
        
        # Examinations table
        self.examinations_table = QTableWidget()
        self.examinations_table.setColumnCount(6)
        self.examinations_table.setHorizontalHeaderLabels([
            "Date", "Type", "Doctor", "Status", "Chief Complaint", "Actions"
        ])
        
        # Configure table
        header = self.examinations_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Date
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Type
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Doctor
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Status
        header.setSectionResizeMode(4, QHeaderView.Stretch)  # Chief Complaint
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Actions
        
        self.examinations_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.examinations_table.setAlternatingRowColors(True)
        
        layout.addWidget(self.examinations_table)
        
        # Summary statistics
        self.create_summary_section(layout)
    
    def create_summary_section(self, parent_layout):
        """Create summary statistics section."""
        summary_group = QGroupBox("Summary")
        summary_layout = QHBoxLayout(summary_group)
        
        self.total_exams_label = QLabel("Total: 0")
        self.recent_exams_label = QLabel("Recent (30 days): 0")
        self.draft_exams_label = QLabel("Drafts: 0")
        
        summary_layout.addWidget(self.total_exams_label)
        summary_layout.addWidget(self.recent_exams_label)
        summary_layout.addWidget(self.draft_exams_label)
        summary_layout.addStretch()
        
        parent_layout.addWidget(summary_group)
    
    def set_patient(self, patient_id: int):
        """Set the current patient and load examinations."""
        self.patient_id = patient_id
        self.refresh_examinations()
    
    def refresh_examinations(self):
        """Refresh the examinations list."""
        if not self.patient_id:
            self.examinations_table.setRowCount(0)
            return
        
        try:
            # Get examinations from service
            self.examinations = dental_examination_service.get_patient_examinations(self.patient_id)
            
            # Update table
            self.update_examinations_table()
            
            # Update summary
            self.update_summary()
            
        except Exception as e:
            logger.error(f"Error refreshing examinations: {str(e)}")
            QMessageBox.warning(self, "Error", "Failed to load examinations.")
    
    def update_examinations_table(self):
        """Update the examinations table with current data."""
        self.examinations_table.setRowCount(len(self.examinations))
        
        for row, exam in enumerate(self.examinations):
            # Date
            date_item = QTableWidgetItem(str(exam.get('examination_date', '')))
            self.examinations_table.setItem(row, 0, date_item)
            
            # Type
            type_item = QTableWidgetItem(exam.get('examination_type', '').replace('_', ' ').title())
            self.examinations_table.setItem(row, 1, type_item)
            
            # Doctor
            doctor_item = QTableWidgetItem(exam.get('doctor_name', ''))
            self.examinations_table.setItem(row, 2, doctor_item)
            
            # Status
            status_item = QTableWidgetItem(exam.get('status', '').title())
            self.examinations_table.setItem(row, 3, status_item)
            
            # Chief Complaint (truncated)
            complaint = exam.get('chief_complaint', '')
            if len(complaint) > 50:
                complaint = complaint[:50] + "..."
            complaint_item = QTableWidgetItem(complaint)
            self.examinations_table.setItem(row, 4, complaint_item)
            
            # Actions
            self.create_action_buttons(row, exam)
    
    def create_action_buttons(self, row: int, exam: Dict):
        """Create action buttons for an examination row."""
        actions_widget = QWidget()
        actions_layout = QHBoxLayout(actions_widget)
        actions_layout.setContentsMargins(4, 4, 4, 4)
        
        # View/Edit button
        edit_button = QPushButton("Edit")
        edit_button.setMaximumWidth(50)
        edit_button.setStyleSheet("""
            QPushButton {
                background-color: #19c5e5;
                color: white;
                border: none;
                padding: 4px 8px;
                border-radius: 3px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #0ea5c7;
            }
        """)
        edit_button.clicked.connect(lambda: self.edit_examination(exam))
        actions_layout.addWidget(edit_button)
        
        # Delete button
        delete_button = QPushButton("Delete")
        delete_button.setMaximumWidth(50)
        delete_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 4px 8px;
                border-radius: 3px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        delete_button.clicked.connect(lambda: self.delete_examination(exam))
        actions_layout.addWidget(delete_button)
        
        self.examinations_table.setCellWidget(row, 5, actions_widget)
    
    def update_summary(self):
        """Update summary statistics."""
        total_exams = len(self.examinations)
        
        # Count recent examinations (last 30 days)
        from datetime import timedelta
        thirty_days_ago = date.today() - timedelta(days=30)
        recent_exams = 0
        draft_exams = 0
        
        for exam in self.examinations:
            # Check if recent
            exam_date_str = exam.get('examination_date', '')
            if exam_date_str:
                try:
                    if isinstance(exam_date_str, str):
                        exam_date = datetime.strptime(exam_date_str, '%Y-%m-%d').date()
                    else:
                        exam_date = exam_date_str
                    
                    if exam_date >= thirty_days_ago:
                        recent_exams += 1
                except:
                    pass
            
            # Check if draft
            if exam.get('status') == 'draft':
                draft_exams += 1
        
        self.total_exams_label.setText(f"Total: {total_exams}")
        self.recent_exams_label.setText(f"Recent (30 days): {recent_exams}")
        self.draft_exams_label.setText(f"Drafts: {draft_exams}")
    
    def create_new_examination(self):
        """Create a new examination."""
        if not self.patient_id:
            QMessageBox.warning(self, "No Patient", "Please select a patient first.")
            return
        
        dialog = ExaminationDialog(self.patient_id, parent=self)
        dialog.examination_saved.connect(self.on_examination_saved)
        dialog.exec()
    
    def edit_examination(self, exam: Dict):
        """Edit an existing examination."""
        dialog = ExaminationDialog(self.patient_id, exam, parent=self)
        dialog.examination_saved.connect(self.on_examination_saved)
        dialog.exec()
    
    def delete_examination(self, exam: Dict):
        """Delete an examination."""
        reply = QMessageBox.question(
            self, 
            "Confirm Delete", 
            f"Are you sure you want to delete this examination from {exam.get('examination_date', '')}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                success = dental_examination_service.delete_examination(exam['id'])
                if success:
                    self.examination_deleted.emit(exam['id'])
                    self.refresh_examinations()
                    QMessageBox.information(self, "Success", "Examination deleted successfully.")
                else:
                    QMessageBox.warning(self, "Error", "Failed to delete examination.")
            except Exception as e:
                logger.error(f"Error deleting examination: {str(e)}")
                QMessageBox.critical(self, "Error", f"Error deleting examination: {str(e)}")
    
    def on_examination_saved(self, exam_data: Dict):
        """Handle examination saved event."""
        self.refresh_examinations()
        self.examination_selected.emit(exam_data)


class ExaminationManagementWidget(QWidget):
    """Main widget for examination management."""
    
    examination_changed = Signal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.patient_id = None
        self.current_examination = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the examination management UI."""
        layout = QVBoxLayout(self)
        
        # Patient info header
        self.patient_info_label = QLabel("No patient selected")
        self.patient_info_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.patient_info_label.setStyleSheet("color: #19c5e5; margin: 10px;")
        layout.addWidget(self.patient_info_label)
        
        # Main content
        self.examination_list = ExaminationListWidget()
        self.examination_list.examination_selected.connect(self.on_examination_selected)
        self.examination_list.examination_deleted.connect(self.on_examination_deleted)
        layout.addWidget(self.examination_list)
    
    def set_patient(self, patient_id: int, patient_name: str = ""):
        """Set the current patient."""
        self.patient_id = patient_id
        self.patient_info_label.setText(f"Patient: {patient_name}" if patient_name else f"Patient ID: {patient_id}")
        self.examination_list.set_patient(patient_id)
    
    def on_examination_selected(self, exam_data: Dict):
        """Handle examination selection."""
        self.current_examination = exam_data
        self.examination_changed.emit(exam_data)
    
    def on_examination_deleted(self, exam_id: int):
        """Handle examination deletion."""
        if self.current_examination and self.current_examination.get('id') == exam_id:
            self.current_examination = None
            self.examination_changed.emit({})
    
    def refresh(self):
        """Refresh the examination list."""
        self.examination_list.refresh_examinations()
