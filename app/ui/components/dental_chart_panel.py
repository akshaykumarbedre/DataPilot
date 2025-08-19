"""
Dual Dental Chart Panel - Individual dental chart panel for Patient Problems or Doctor Findings.
"""
import logging
from typing import Dict, List, Optional, Any, Callable
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox, 
    QLabel, QTextEdit, QScrollArea, QFrame, QPushButton, QSplitter
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from .enhanced_tooth_widget import EnhancedToothWidget
from ...services.tooth_history_service import tooth_history_service

logger = logging.getLogger(__name__)


class DentalChartPanel(QGroupBox):
    """Individual dental chart panel (Patient/Doctor)"""
    
    tooth_selected = Signal(int, str)  # tooth_number, panel_type
    tooth_status_changed = Signal(int, str, str)  # tooth_number, status, record_type
    
    def __init__(self, panel_type: str, patient_id: Optional[int] = None, parent=None):
        super().__init__(parent)
        self.panel_type = panel_type  # 'patient' or 'doctor'
        self.patient_id = patient_id
        self.examination_id = None
        self.selected_tooth = None
        self.tooth_widgets = {}
        
        # Set panel title
        title = "Patient Problems" if panel_type == 'patient' else "Doctor Findings"
        self.setTitle(title)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the dental chart panel UI."""
        layout = QVBoxLayout(self)
        
        # Main splitter
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # Dental chart area
        chart_area = self.create_dental_chart_area()
        splitter.addWidget(chart_area)
        
        # Right panel for tooth info and history
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        # Set splitter sizes (chart larger than info panel)
        splitter.setSizes([600, 300])
    
    def create_dental_chart_area(self) -> QWidget:
        """Create the 32-tooth layout area."""
        chart_widget = QWidget()
        layout = QVBoxLayout(chart_widget)
        
        # Upper teeth section
        upper_section = QGroupBox("Upper Teeth")
        upper_layout = QGridLayout(upper_section)
        
        # Upper right: 18-11 (reversed for visual layout)
        for i, tooth_num in enumerate(range(18, 10, -1)):
            tooth_widget = EnhancedToothWidget(tooth_num)
            tooth_widget.set_mode(self.panel_type)
            tooth_widget.tooth_clicked.connect(self.on_tooth_clicked)
            tooth_widget.status_changed.connect(self.on_tooth_status_changed)
            self.tooth_widgets[tooth_num] = tooth_widget
            upper_layout.addWidget(tooth_widget, 0, i)
        
        # Upper left: 21-28
        for i, tooth_num in enumerate(range(21, 29)):
            tooth_widget = EnhancedToothWidget(tooth_num)
            tooth_widget.set_mode(self.panel_type)
            tooth_widget.tooth_clicked.connect(self.on_tooth_clicked)
            tooth_widget.status_changed.connect(self.on_tooth_status_changed)
            self.tooth_widgets[tooth_num] = tooth_widget
            upper_layout.addWidget(tooth_widget, 0, 8 + i)
        
        layout.addWidget(upper_section)
        
        # Add spacing between upper and lower
        layout.addSpacing(20)
        
        # Lower teeth section
        lower_section = QGroupBox("Lower Teeth")
        lower_layout = QGridLayout(lower_section)
        
        # Lower right: 48-41 (reversed for visual layout)
        for i, tooth_num in enumerate(range(48, 40, -1)):
            tooth_widget = EnhancedToothWidget(tooth_num)
            tooth_widget.set_mode(self.panel_type)
            tooth_widget.tooth_clicked.connect(self.on_tooth_clicked)
            tooth_widget.status_changed.connect(self.on_tooth_status_changed)
            self.tooth_widgets[tooth_num] = tooth_widget
            lower_layout.addWidget(tooth_widget, 0, i)
        
        # Lower left: 31-38
        for i, tooth_num in enumerate(range(31, 39)):
            tooth_widget = EnhancedToothWidget(tooth_num)
            tooth_widget.set_mode(self.panel_type)
            tooth_widget.tooth_clicked.connect(self.on_tooth_clicked)
            tooth_widget.status_changed.connect(self.on_tooth_status_changed)
            self.tooth_widgets[tooth_num] = tooth_widget
            lower_layout.addWidget(tooth_widget, 0, 8 + i)
        
        layout.addWidget(lower_section)
        
        return chart_widget
    
    def create_right_panel(self) -> QWidget:
        """Create right panel for selected tooth info and history."""
        right_widget = QWidget()
        layout = QVBoxLayout(right_widget)
        
        # Selected tooth info
        self.tooth_info_group = QGroupBox("Selected Tooth Information")
        info_layout = QVBoxLayout(self.tooth_info_group)
        
        self.tooth_info_label = QLabel("No tooth selected")
        self.tooth_info_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.tooth_info_label.setStyleSheet("color: #19c5e5; padding: 5px;")
        info_layout.addWidget(self.tooth_info_label)
        
        self.current_status_label = QLabel("")
        self.current_status_label.setWordWrap(True)
        info_layout.addWidget(self.current_status_label)
        
        layout.addWidget(self.tooth_info_group)
        
        # History text area for selected tooth
        self.history_group = QGroupBox("Tooth History")
        history_layout = QVBoxLayout(self.history_group)
        
        self.history_text = QTextEdit()
        self.history_text.setReadOnly(True)
        self.history_text.setMaximumHeight(200)
        self.history_text.setPlaceholderText("Select a tooth to view history...")
        history_layout.addWidget(self.history_text)
        
        # Add new record button
        self.add_record_btn = QPushButton(f"Add {self.panel_type.title()} Record")
        self.add_record_btn.setStyleSheet("""
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
                background-color: #bdc3c7;
            }
        """)
        self.add_record_btn.setEnabled(False)
        self.add_record_btn.clicked.connect(self.add_tooth_record)
        history_layout.addWidget(self.add_record_btn)
        
        layout.addWidget(self.history_group)
        
        return right_widget
    
    def set_patient(self, patient_id: int):
        """Set the current patient and load data."""
        self.patient_id = patient_id
        self.load_patient_data()
    
    def set_examination(self, examination_id: int):
        """Set the current examination context."""
        self.examination_id = examination_id
        self.load_patient_data()
    
    def load_patient_data(self):
        """Load patient's tooth data for this panel type."""
        if not self.patient_id:
            return
        
        try:
            # Get tooth summary for patient
            tooth_summary = tooth_history_service.get_patient_tooth_summary(
                self.patient_id, self.examination_id
            )
            
            # Update tooth widgets based on panel type
            for tooth_number, tooth_widget in self.tooth_widgets.items():
                if tooth_number in tooth_summary:
                    summary = tooth_summary[tooth_number]
                    
                    if self.panel_type == 'patient':
                        # Show patient problems
                        status = 'normal'
                        if summary['latest_patient_problem']:
                            status = summary['latest_patient_problem']['status']
                        tooth_widget.set_patient_status(status)
                    else:
                        # Show doctor findings
                        status = 'normal'
                        if summary['latest_doctor_finding']:
                            status = summary['latest_doctor_finding']['status']
                        tooth_widget.set_doctor_status(status)
                else:
                    # Reset to normal if no data
                    if self.panel_type == 'patient':
                        tooth_widget.set_patient_status('normal')
                    else:
                        tooth_widget.set_doctor_status('normal')
        
        except Exception as e:
            logger.error(f"Error loading patient data: {str(e)}")
    
    def on_tooth_clicked(self, tooth_number: int, click_type: str):
        """Handle tooth click events."""
        self.selected_tooth = tooth_number
        
        # Update selected tooth display
        quadrant = tooth_number // 10
        position = tooth_number % 10
        self.tooth_info_label.setText(f"Tooth {tooth_number} ({quadrant},{position})")
        
        # Load tooth history
        self.load_tooth_history(tooth_number)
        
        # Enable add record button
        self.add_record_btn.setEnabled(True)
        
        # Emit signal
        self.tooth_selected.emit(tooth_number, self.panel_type)
        
        if click_type == 'right':
            # Right click - could open detailed dialog
            self.show_tooth_details(tooth_number)
    
    def load_tooth_history(self, tooth_number: int):
        """Load and display tooth history."""
        if not self.patient_id:
            return
        
        try:
            # Get tooth history for this panel type
            record_type = 'patient_problem' if self.panel_type == 'patient' else 'doctor_finding'
            
            history = tooth_history_service.get_tooth_history(
                self.patient_id, 
                tooth_number, 
                record_type=record_type,
                examination_id=self.examination_id
            )
            
            # Get current status
            current_status = tooth_history_service.get_tooth_current_status(
                self.patient_id, tooth_number
            )
            
            # Update current status display
            if self.panel_type == 'patient':
                if current_status['latest_patient_problem']:
                    latest = current_status['latest_patient_problem']
                    status_text = f"Current Status: {latest['status']}"
                    if latest['description']:
                        status_text += f"\nDescription: {latest['description']}"
                    status_text += f"\nDate: {latest['date_recorded']}"
                else:
                    status_text = "Current Status: Normal\nNo patient problems recorded"
            else:
                if current_status['latest_doctor_finding']:
                    latest = current_status['latest_doctor_finding']
                    status_text = f"Current Status: {latest['status']}"
                    if latest['description']:
                        status_text += f"\nDescription: {latest['description']}"
                    status_text += f"\nDate: {latest['date_recorded']}"
                else:
                    status_text = "Current Status: Normal\nNo doctor findings recorded"
            
            self.current_status_label.setText(status_text)
            
            # Format history text
            if history:
                history_text = f"{self.panel_type.title()} History for Tooth {tooth_number}:\n\n"
                
                for record in history:
                    history_text += f"Date: {record['date_recorded']}\n"
                    history_text += f"Status: {record['status']}\n"
                    if record['description']:
                        history_text += f"Description: {record['description']}\n"
                    if record['examination_date']:
                        history_text += f"Examination: {record['examination_date']}\n"
                    history_text += "-" * 40 + "\n\n"
                
                self.history_text.setPlainText(history_text)
            else:
                self.history_text.setPlainText(f"No {self.panel_type} history recorded for this tooth.")
                
        except Exception as e:
            logger.error(f"Error loading tooth history: {str(e)}")
            self.history_text.setPlainText("Error loading tooth history.")
    
    def on_tooth_status_changed(self, tooth_number: int, status: str, record_type: str):
        """Handle tooth status change."""
        if not self.patient_id:
            return
        
        try:
            # Update tooth status in database
            record_type_db = 'patient_problem' if record_type == 'patient' else 'doctor_finding'
            
            success = tooth_history_service.update_tooth_status(
                self.patient_id,
                tooth_number,
                status,
                record_type_db,
                f"Status changed to {status}",
                self.examination_id
            )
            
            if success:
                # Refresh tooth history if this tooth is selected
                if tooth_number == self.selected_tooth:
                    self.load_tooth_history(tooth_number)
                
                # Emit signal
                self.tooth_status_changed.emit(tooth_number, status, record_type_db)
            
        except Exception as e:
            logger.error(f"Error updating tooth status: {str(e)}")
    
    def show_tooth_details(self, tooth_number: int):
        """Show detailed tooth information dialog."""
        # Import here to avoid circular imports
        from ...widgets.dental_chart_widget import ToothDetailsDialog
        
        dialog = ToothDetailsDialog(tooth_number, self.patient_id, self)
        dialog.exec()
        
        # Refresh data after dialog closes
        self.load_patient_data()
        if tooth_number == self.selected_tooth:
            self.load_tooth_history(tooth_number)
    
    def add_tooth_record(self):
        """Add new tooth record for selected tooth."""
        if not self.selected_tooth or not self.patient_id:
            return
        
        # Import here to avoid circular imports
        from ...widgets.dental_chart_widget import ToothDetailsDialog
        
        dialog = ToothDetailsDialog(self.selected_tooth, self.patient_id, self)
        dialog.exec()
        
        # Refresh data after dialog closes
        self.load_patient_data()
        self.load_tooth_history(self.selected_tooth)
    
    def refresh_data(self):
        """Refresh all tooth data."""
        self.load_patient_data()
        if self.selected_tooth:
            self.load_tooth_history(self.selected_tooth)
    
    def clear_selection(self):
        """Clear tooth selection."""
        self.selected_tooth = None
        self.tooth_info_label.setText("No tooth selected")
        self.current_status_label.setText("")
        self.history_text.clear()
        self.add_record_btn.setEnabled(False)
    
    def hide_all_dropdowns(self):
        """Hide all tooth status dropdowns."""
        for tooth_widget in self.tooth_widgets.values():
            tooth_widget.force_hide_dropdown()
