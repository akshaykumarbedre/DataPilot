"""
Visit Records Panel - Visit history display with total amount calculation.
"""
import logging
from datetime import date, datetime
from typing import Dict, List, Optional, Any
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, 
    QScrollArea, QFrame, QPushButton, QTextEdit, QComboBox,
    QListWidget, QListWidgetItem, QSizePolicy, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor

from ...services.visit_records_service import visit_records_service
from ..dialogs.edit_visit_dialog import EditVisitDialog

logger = logging.getLogger(__name__)


class VisitRecordWidget(QFrame):
    """Individual visit record display widget."""
    
    visit_selected = Signal(dict)
    visit_edit_requested = Signal(dict)
    
    def __init__(self, visit_data: Dict, parent=None):
        super().__init__(parent)
        self.visit_data = visit_data
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the visit record widget UI."""
        self.setFrameStyle(QFrame.NoFrame)
        self.setStyleSheet("background-color: transparent;")
        
        layout = QVBoxLayout(self)
        layout.setSpacing(3)
        
        # Header with date and amount
        header_layout = QHBoxLayout()
        
        # Date and time
        visit_date = self.visit_data.get('visit_date', '')
        visit_time = self.visit_data.get('visit_time', '')
        if isinstance(visit_time, str) and visit_time:
            time_str = visit_time
        elif hasattr(visit_time, 'strftime'):
            time_str = visit_time.strftime("%I:%M %p")
        else:
            time_str = ""
        
        date_time_text = f"{visit_date}"
        if time_str:
            date_time_text += f" at {time_str}"
        
        date_label = QLabel(date_time_text)
        date_label.setFont(QFont("Arial", 10, QFont.Bold))
        date_label.setStyleSheet("color: #2C3E50;")
        header_layout.addWidget(date_label)
        
        header_layout.addStretch()
        
        # Amount
        cost = self.visit_data.get('cost', 0)
        if cost and cost > 0:
            amount_label = QLabel(f"₹{cost:.2f}")
            amount_label.setFont(QFont("Arial", 10, QFont.Bold))
            amount_label.setStyleSheet("color: #27ae60;")
            header_layout.addWidget(amount_label)
        
        layout.addLayout(header_layout)
        
        # Visit type and status
        type_status_layout = QHBoxLayout()
        
        visit_type = self.visit_data.get('visit_type', '').replace('_', ' ').title()
        if visit_type:
            type_label = QLabel(f"Type: {visit_type}")
            type_label.setStyleSheet("color: #7F8C8D; font-size: 11px;")
            type_status_layout.addWidget(type_label)
        
        status = self.visit_data.get('status', '').title()
        if status:
            status_label = QLabel(f"Status: {status}")
            status_label.setStyleSheet("color: #7F8C8D; font-size: 11px;")
            type_status_layout.addWidget(status_label)
        
        type_status_layout.addStretch()
        layout.addLayout(type_status_layout)
        
        # Chief complaint
        chief_complaint = self.visit_data.get('chief_complaint') or self.visit_data.get('notes', '')
        if chief_complaint:
            cc_label = QLabel("Chief Complaint:")
            cc_label.setFont(QFont("Arial", 9, QFont.Bold))
            layout.addWidget(cc_label)
            
            cc_text = QLabel(chief_complaint)
            cc_text.setWordWrap(True)
            cc_text.setStyleSheet("color: #333; margin-left: 10px; font-size: 11px;")
            layout.addWidget(cc_text)
        
        # Diagnosis
        diagnosis = self.visit_data.get('diagnosis', '')
        if diagnosis:
            diag_label = QLabel("Diagnosis:")
            diag_label.setFont(QFont("Arial", 9, QFont.Bold))
            layout.addWidget(diag_label)
            
            diag_text = QLabel(diagnosis)
            diag_text.setWordWrap(True)
            diag_text.setStyleSheet("color: #333; margin-left: 10px; font-size: 11px;")
            layout.addWidget(diag_text)
        
        # Treatment performed
        treatment = self.visit_data.get('treatment_performed', '')
        if treatment:
            treatment_label = QLabel("Treatment:")
            treatment_label.setFont(QFont("Arial", 9, QFont.Bold))
            layout.addWidget(treatment_label)
            
            treatment_text = QLabel(treatment)
            treatment_text.setWordWrap(True)
            treatment_text.setStyleSheet("color: #333; margin-left: 10px; font-size: 11px;")
            layout.addWidget(treatment_text)
        
        # Doctor's advice
        advice = self.visit_data.get('advice', '')
        if advice:
            advice_label = QLabel("Advice:")
            advice_label.setFont(QFont("Arial", 9, QFont.Bold))
            layout.addWidget(advice_label)
            
            advice_text = QLabel(advice)
            advice_text.setWordWrap(True)
            advice_text.setStyleSheet("color: #333; margin-left: 10px; font-size: 11px;")
            layout.addWidget(advice_text)
        
        # Affected teeth
        affected_teeth = self.visit_data.get('affected_teeth', [])
        if affected_teeth and len(affected_teeth) > 0:
            teeth_label = QLabel("Affected Teeth:")
            teeth_label.setFont(QFont("Arial", 9, QFont.Bold))
            layout.addWidget(teeth_label)
            
            teeth_text = QLabel(", ".join(map(str, affected_teeth)))
            teeth_text.setStyleSheet("color: #333; margin-left: 10px; font-size: 11px;")
            layout.addWidget(teeth_text)
        
        # Doctor name
        doctor = self.visit_data.get('doctor_name', '')
        if doctor:
            doctor_label = QLabel(f"Doctor: {doctor}")
            doctor_label.setStyleSheet("color: #666; font-size: 10px; font-style: italic;")
            layout.addWidget(doctor_label)
        
        # Actions
        actions_layout = QHBoxLayout()
        actions_layout.addStretch()
        
        edit_btn = QPushButton("Edit")
        edit_btn.setMaximumWidth(60)
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        edit_btn.clicked.connect(lambda: self.visit_edit_requested.emit(self.visit_data))
        actions_layout.addWidget(edit_btn)
        
        layout.addLayout(actions_layout)
        
        # Make clickable
        self.mousePressEvent = lambda event: self.visit_selected.emit(self.visit_data)


class VisitRecordsPanel(QGroupBox):
    """Visit history display"""
    
    visit_selected = Signal(dict)
    visit_edit_requested = Signal(dict)
    total_amount_changed = Signal(float)
    
    def __init__(self, patient_id: Optional[int] = None, examination_id: Optional[int] = None, parent=None):
        super().__init__("Visit Records", parent)
        self.patient_id = patient_id
        self.examination_id = examination_id
        self.visit_records = []
        self.total_amount = 0.0
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the visit records panel UI."""
        layout = QVBoxLayout(self)
        
        # Header with controls
        header_layout = QHBoxLayout()
        
        header_layout.addStretch()
        
        # Total amount display
        self.total_label = QLabel("Total: ₹0.00")
        self.total_label.setFont(QFont("Arial", 20, QFont.Bold))
        self.total_label.setStyleSheet("color: #27ae60; padding: 5px;")
        header_layout.addWidget(self.total_label)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setMaximumWidth(80)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 2px 6;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_records)
        header_layout.addWidget(refresh_btn)
        
        layout.addLayout(header_layout)
        
        # Scrollable visit records list
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.records_widget = QWidget()
        self.records_layout = QVBoxLayout(self.records_widget)
        self.records_layout.setAlignment(Qt.AlignTop)
        
        self.scroll_area.setWidget(self.records_widget)
        layout.addWidget(self.scroll_area)
        
        # Summary info
        self.summary_label = QLabel("No visits recorded")
        self.summary_label.setStyleSheet("color: #7F8C8D; font-style: italic; padding: 8px;")
        layout.addWidget(self.summary_label)
        
        # Load initial data
        self.update_panel_state()
        self.setMinimumHeight(600)  # Increased from 400 to 600 for better visibility
    
    def set_patient(self, patient_id: int):
        """Set the current patient and load records."""
        self.patient_id = patient_id
        self.update_panel_state()
        self.load_visit_records()
    
    def set_examination(self, examination_id: int):
        """Set the current examination context."""
        self.examination_id = examination_id
        self.update_panel_state()
        self.load_visit_records()
    
    def update_panel_state(self):
        """Update panel title and state."""
        if not self.patient_id:
            self.setTitle("Visit Records (Select a patient first)")
        elif self.examination_id:
            self.setTitle(f"Visit Records - Exam #{self.examination_id}")
        else:
            self.setTitle("Visit Records - All Examinations")
    
    def load_visit_records(self):
        """Load visit records for the current patient."""
        if not self.patient_id:
            self.clear_records()
            return
        
        try:
            # Get all visits for patient
            self.visit_records = visit_records_service.get_visit_records(
                patient_id=self.patient_id, 
                examination_id=self.examination_id
            )
            
            # Apply current filter
            self.apply_filter()
            
        except Exception as e:
            logger.error(f"Error loading visit records: {str(e)}")
            self.clear_records()
    
    def apply_filter(self):
        """Apply the selected filter to visit records."""
        self.display_records(self.visit_records)
    
    def parse_visit_date(self, visit_date) -> date:
        """Parse visit date to date object."""
        if isinstance(visit_date, str):
            try:
                return datetime.strptime(visit_date, '%Y-%m-%d').date()
            except:
                return date.today()
        elif isinstance(visit_date, date):
            return visit_date
        else:
            return date.today()
    
    def display_records(self, records: List[Dict]):
        """Display visit records in the scroll area."""
        # Clear existing records
        self.clear_records_display()
        
        if not records:
            self.summary_label.setText("No visits found for selected filter")
            self.total_label.setText("Total: Rs 0.00")
            self.total_amount = 0.0
            return
        
        # Sort records by date (newest first)
        sorted_records = sorted(
            records, 
            key=lambda x: self.parse_visit_date(x.get('visit_date')), 
            reverse=True
        )
        
        # Add record widgets
        total_amount = 0.0
        for record in sorted_records:
            record_widget = VisitRecordWidget(record)
            record_widget.visit_selected.connect(self.visit_selected)
            record_widget.visit_edit_requested.connect(self.edit_visit_record)
            self.records_layout.addWidget(record_widget)
            
            # Add to total
            cost = record.get('cost', 0)
            if cost and cost > 0:
                total_amount += float(cost)
        
        # Update total and summary
        self.total_amount = total_amount
        self.total_label.setText(f"Total: Rs {total_amount:.2f}")
        self.summary_label.setText(f"{len(sorted_records)} visit{'s' if len(sorted_records) != 1 else ''} found")
        
        # Emit total amount change
        self.total_amount_changed.emit(total_amount)
    
    def clear_records_display(self):
        """Clear the records display area."""
        while self.records_layout.count():
            child = self.records_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def clear_records(self):
        """Clear all records and reset display."""
        self.visit_records = []
        self.clear_records_display()
        self.total_label.setText("Total: Rs 0.00")
        self.summary_label.setText("No visits recorded")
        self.total_amount = 0.0
    
    def refresh_records(self):
        """Refresh visit records from database."""
        self.load_visit_records()
    
    def add_visit_record(self, visit_data: Dict):
        """Add a new visit record to the display."""
        # Reload all records to ensure consistency
        self.load_visit_records()
    
    def get_total_amount(self) -> float:
        """Get the current total amount."""
        return self.total_amount
    
    def get_visit_count(self) -> int:
        """Get the number of displayed visits."""
        return len([record for record in self.visit_records if self.is_record_visible(record)])
    
    def is_record_visible(self, record: Dict) -> bool:
        """Check if a record is visible based on current filter."""
        return True

    def edit_visit_record(self, visit_data: Dict):
        """Handle the edit visit record request."""
        dialog = EditVisitDialog(visit_data, self.patient_id, self)
        if dialog.exec():
            updated_data = dialog.get_visit_data()
            visit_id = visit_data.get('id')
            if visit_id:
                success = visit_records_service.update_visit_record(visit_id, updated_data)
                if success:
                    self.refresh_records()
                    QMessageBox.information(self, "Success", "Visit record updated successfully!")
                else:
                    QMessageBox.warning(self, "Error", "Failed to update visit record.")
