"""
Dual Dental Chart Panel - Individual dental chart panel for Patient Problems or Doctor Findings.
"""
import logging
from typing import Dict, List, Optional, Any, Callable
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox, 
    QLabel, QTextEdit, QScrollArea, QFrame, QPushButton, QSplitter,
    QSizePolicy
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
        
        # Set panel title with improved formatting
        if panel_type == 'patient':
            title = "Patient Problems (Dental Chart)"
        else:
            title = "Doctor Findings (Dental Chart)"
        
        self.setTitle(title)
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 12pt;
                border: 1px solid #BDC3C7;
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
                color: #2C3E50;
                font-weight: bold;
            }
        """)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the dental chart panel UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(10, 15, 10, 10)
        
        # Set size constraints for better side-by-side display
        self.setMinimumWidth(400)
        self.setMaximumWidth(700)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Dental chart area (top)
        chart_area = self.create_dental_chart_area()
        layout.addWidget(chart_area)
        
        # Selected tooth info and history (bottom)
        bottom_panel = self.create_bottom_panel()
        layout.addWidget(bottom_panel)
    
    def create_dental_chart_area(self) -> QWidget:
        """Create the 32-tooth layout area."""
        chart_widget = QWidget()
        layout = QVBoxLayout(chart_widget)
        layout.setSpacing(10)
        
        # Upper teeth section
        upper_section = QGroupBox("Upper Jaw (Right 8-1 | Left 1-8)")
        upper_section.setFont(QFont("Arial", 10, QFont.Bold))
        upper_section.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #BDC3C7;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 8px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 8px 0 8px;
                color: #2C3E50;
            }
        """)
        upper_layout = QHBoxLayout(upper_section)
        upper_layout.setSpacing(2)
        upper_layout.setContentsMargins(8, 15, 8, 8)
        
        # Upper right: 18-11 (reversed for visual layout)
        for i, tooth_num in enumerate(range(18, 10, -1)):
            tooth_widget = EnhancedToothWidget(tooth_num)
            tooth_widget.set_mode(self.panel_type)
            tooth_widget.tooth_clicked.connect(self.on_tooth_clicked)
            tooth_widget.status_changed.connect(self.on_tooth_status_changed)
            self.tooth_widgets[tooth_num] = tooth_widget
            upper_layout.addWidget(tooth_widget)
        
        # Separator between right and left
        separator1 = QLabel(" | ")
        separator1.setFont(QFont("Arial", 16, QFont.Bold))
        separator1.setAlignment(Qt.AlignCenter)
        separator1.setStyleSheet("color: #2C3E50; margin: 0 5px;")
        upper_layout.addWidget(separator1)
        
        # Upper left: 21-28
        for i, tooth_num in enumerate(range(21, 29)):
            tooth_widget = EnhancedToothWidget(tooth_num)
            tooth_widget.set_mode(self.panel_type)
            tooth_widget.tooth_clicked.connect(self.on_tooth_clicked)
            tooth_widget.status_changed.connect(self.on_tooth_status_changed)
            self.tooth_widgets[tooth_num] = tooth_widget
            upper_layout.addWidget(tooth_widget)
        
        layout.addWidget(upper_section)
        
        # Add spacing between upper and lower
        layout.addSpacing(10)
        
        # Lower teeth section
        lower_section = QGroupBox("Lower Jaw (Right 8-1 | Left 1-8)")
        lower_section.setFont(QFont("Arial", 10, QFont.Bold))
        lower_section.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #BDC3C7;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 8px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 8px 0 8px;
                color: #2C3E50;
            }
        """)
        lower_layout = QHBoxLayout(lower_section)
        lower_layout.setSpacing(2)
        lower_layout.setContentsMargins(8, 15, 8, 8)
        
        # Lower right: 48-41 (reversed for visual layout)
        for i, tooth_num in enumerate(range(48, 40, -1)):
            tooth_widget = EnhancedToothWidget(tooth_num)
            tooth_widget.set_mode(self.panel_type)
            tooth_widget.tooth_clicked.connect(self.on_tooth_clicked)
            tooth_widget.status_changed.connect(self.on_tooth_status_changed)
            self.tooth_widgets[tooth_num] = tooth_widget
            lower_layout.addWidget(tooth_widget)
        
        # Separator between right and left
        separator2 = QLabel(" | ")
        separator2.setFont(QFont("Arial", 16, QFont.Bold))
        separator2.setAlignment(Qt.AlignCenter)
        separator2.setStyleSheet("color: #2C3E50; margin: 0 5px;")
        lower_layout.addWidget(separator2)
        
        # Lower left: 31-38
        for i, tooth_num in enumerate(range(31, 39)):
            tooth_widget = EnhancedToothWidget(tooth_num)
            tooth_widget.set_mode(self.panel_type)
            tooth_widget.tooth_clicked.connect(self.on_tooth_clicked)
            tooth_widget.status_changed.connect(self.on_tooth_status_changed)
            self.tooth_widgets[tooth_num] = tooth_widget
            lower_layout.addWidget(tooth_widget)
        
        layout.addWidget(lower_section)
        
        return chart_widget
    
    def create_bottom_panel(self) -> QWidget:
        """Create bottom panel for selected tooth info and history."""
        bottom_widget = QWidget()
        bottom_widget.setMinimumHeight(160)  # Slightly reduced
        bottom_widget.setMaximumHeight(220)
        layout = QHBoxLayout(bottom_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Selected tooth info (left side of bottom panel)
        self.tooth_info_group = QGroupBox("Selected Tooth")
        self.tooth_info_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 10pt;
                border: 1px solid #BDC3C7;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 8px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 8px 0 8px;
                color: #2C3E50;
            }
        """)
        self.tooth_info_group.setMinimumWidth(200)
        self.tooth_info_group.setMaximumWidth(260)
        self.tooth_info_group.setMinimumHeight(120)
        info_layout = QVBoxLayout(self.tooth_info_group)
        info_layout.setSpacing(6)
        
        self.tooth_info_label = QLabel("No tooth selected")
        self.tooth_info_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.tooth_info_label.setStyleSheet("""
            QLabel {
                color: #2C3E50; 
                padding: 8px;
                background-color: #ECF0F1;
                border-radius: 4px;
                border: 1px solid #BDC3C7;
                min-height: 18px;
            }
        """)
        self.tooth_info_label.setAlignment(Qt.AlignCenter)
        info_layout.addWidget(self.tooth_info_label)
        
        self.current_status_label = QLabel("")
        self.current_status_label.setWordWrap(True)
        self.current_status_label.setStyleSheet("""
            QLabel {
                padding: 6px;
                background-color: white;
                border: 1px solid #BDC3C7;
                border-radius: 4px;
                font-size: 9pt;
                min-height: 25px;
                color: #2C3E50;
            }
        """)
        info_layout.addWidget(self.current_status_label)
        
        # Add record button
        self.add_record_btn = QPushButton(f"Add Record")
        self.add_record_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 12px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 9pt;
                min-height: 12px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #BDC3C7;
                color: #7F8C8D;
            }
        """)
        self.add_record_btn.setEnabled(False)
        self.add_record_btn.clicked.connect(self.add_tooth_record)
        info_layout.addWidget(self.add_record_btn)
        
        layout.addWidget(self.tooth_info_group)
        
        # History text area (right side of bottom panel)
        self.history_group = QGroupBox(f"Tooth History - {self.panel_type.title()}")
        self.history_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 10pt;
                border: 1px solid #BDC3C7;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 8px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 8px 0 8px;
                color: #2C3E50;
            }
        """)
        self.history_group.setMinimumHeight(120)
        history_layout = QVBoxLayout(self.history_group)
        history_layout.setSpacing(6)
        
        self.history_text = QTextEdit()
        self.history_text.setReadOnly(True)
        self.history_text.setMinimumHeight(100)
        self.history_text.setMaximumHeight(160)
        self.history_text.setPlaceholderText("Select a tooth to view history...")
        self.history_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #BDC3C7; 
                background-color: white;
                padding: 6px;
                border-radius: 4px;
                font-family: Arial;
                font-size: 9pt;
                color: #2C3E50;
            }
        """)
        history_layout.addWidget(self.history_text)
        
        layout.addWidget(self.history_group)
        
        return bottom_widget

    def create_right_panel(self) -> QWidget:
        """Create right panel for selected tooth info and history."""
        right_widget = QWidget()
        right_widget.setMinimumWidth(200)
        right_widget.setMaximumWidth(300)
        layout = QVBoxLayout(right_widget)
        layout.setSpacing(8)
        
        # Selected tooth info (compact)
        self.tooth_info_group = QGroupBox("Selected Tooth")
        self.tooth_info_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 10pt;
                border: 1px solid #BDC3C7;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 8px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 8px 0 8px;
                color: #2C3E50;
            }
        """)
        info_layout = QVBoxLayout(self.tooth_info_group)
        info_layout.setSpacing(5)
        
        self.tooth_info_label = QLabel("No tooth selected")
        self.tooth_info_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.tooth_info_label.setStyleSheet("""
            QLabel {
                color: #2C3E50; 
                padding: 6px;
                background-color: #ECF0F1;
                border-radius: 3px;
                border: 1px solid #BDC3C7;
            }
        """)
        self.tooth_info_label.setAlignment(Qt.AlignCenter)
        info_layout.addWidget(self.tooth_info_label)
        
        self.current_status_label = QLabel("")
        self.current_status_label.setWordWrap(True)
        self.current_status_label.setStyleSheet("""
            QLabel {
                padding: 4px;
                background-color: white;
                border: 1px solid #BDC3C7;
                border-radius: 3px;
                font-size: 9pt;
                color: #2C3E50;
            }
        """)
        info_layout.addWidget(self.current_status_label)
        
        layout.addWidget(self.tooth_info_group)
        
        # History text area (compact)
        self.history_group = QGroupBox(f"History")
        self.history_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 10pt;
                border: 1px solid #BDC3C7;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 8px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 8px 0 8px;
                color: #2C3E50;
            }
        """)
        history_layout = QVBoxLayout(self.history_group)
        history_layout.setSpacing(5)
        
        self.history_text = QTextEdit()
        self.history_text.setReadOnly(True)
        self.history_text.setMinimumHeight(80)
        self.history_text.setMaximumHeight(120)
        self.history_text.setPlaceholderText("Select a tooth...")
        self.history_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #BDC3C7; 
                background-color: white;
                padding: 4px;
                border-radius: 3px;
                font-family: Arial;
                font-size: 9pt;
                color: #2C3E50;
            }
        """)
        history_layout.addWidget(self.history_text)
        
        # Add record button (compact)
        self.add_record_btn = QPushButton(f"Add Record")
        self.add_record_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 9pt;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #BDC3C7;
                color: #7F8C8D;
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
    
    def load_tooth_data(self, history_data: List[Dict[str, Any]]):
        """Load tooth data from history records and update tooth widgets."""
        if not history_data:
            return
        
        try:
            # Group history by tooth number and get latest status for each tooth
            tooth_status_map = {}
            
            for record in history_data:
                tooth_number = record.get('tooth_number')
                status = record.get('status', 'normal')
                date_recorded = record.get('date_recorded')
                
                if tooth_number:
                    # Keep the most recent status for each tooth
                    if tooth_number not in tooth_status_map:
                        tooth_status_map[tooth_number] = {
                            'status': status,
                            'date_recorded': date_recorded,
                            'description': record.get('description', '')
                        }
                    else:
                        # Compare dates and keep the most recent
                        existing_date = tooth_status_map[tooth_number]['date_recorded']
                        if date_recorded and (not existing_date or date_recorded > existing_date):
                            tooth_status_map[tooth_number] = {
                                'status': status,
                                'date_recorded': date_recorded,
                                'description': record.get('description', '')
                            }
            
            # Update tooth widgets with the latest status
            for tooth_number, status_info in tooth_status_map.items():
                if tooth_number in self.tooth_widgets:
                    tooth_widget = self.tooth_widgets[tooth_number]
                    status = status_info['status']
                    
                    # Update the tooth widget's visual status
                    if hasattr(tooth_widget, 'update_status'):
                        tooth_widget.update_status(status)
                    elif hasattr(tooth_widget, 'set_status'):
                        tooth_widget.set_status(status)
            
            logger.info(f"Loaded tooth data for {len(tooth_status_map)} teeth in {self.panel_type} panel")
            
        except Exception as e:
            logger.error(f"Error loading tooth data in {self.panel_type} panel: {str(e)}")
    
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
    
    def display_tooth_history(self, tooth_number: int, history: List[Dict[str, Any]]):
        """Display tooth history data in the panel."""
        try:
            # Update current status and history display
            self.selected_tooth = tooth_number
            self.tooth_info_label.setText(f"Tooth #{tooth_number}")
            self.add_record_btn.setEnabled(True)
            
            # Format and display history
            if history:
                history_text = f"{self.panel_type.title()} History for Tooth {tooth_number}:\n\n"
                
                for record in history:
                    history_text += f"Date: {record.get('date_recorded', 'Unknown')}\n"
                    history_text += f"Status: {record.get('status', 'Unknown')}\n"
                    if record.get('description'):
                        history_text += f"Description: {record['description']}\n"
                    if record.get('examination_date'):
                        history_text += f"Examination: {record['examination_date']}\n"
                    history_text += "-" * 40 + "\n\n"
                
                self.history_text.setPlainText(history_text)
            else:
                self.history_text.setPlainText(f"No {self.panel_type} history recorded for this tooth.")
            
            # Update tooth widget visual status if available
            if tooth_number in self.tooth_widgets and history:
                latest_record = history[0]  # Assuming history is sorted by date descending
                latest_status = latest_record.get('status', 'normal')
                self.tooth_widgets[tooth_number].update_status(latest_status)
                
        except Exception as e:
            logger.error(f"Error displaying tooth history: {str(e)}")
            if hasattr(self, 'history_text'):
                self.history_text.setPlainText("Error displaying tooth history.")
    
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
        try:
            from ...widgets.dental_chart_widget import ToothDetailsDialog
            dialog = ToothDetailsDialog(tooth_number, self.patient_id, self)
            dialog.exec()
        except ImportError:
            logger.warning("ToothDetailsDialog not available")
            # Fallback - just log the tooth selection
            logger.info(f"Tooth {tooth_number} details requested")
        
        # Refresh data after dialog closes
        self.load_patient_data()
        if tooth_number == self.selected_tooth:
            self.load_tooth_history(tooth_number)
    
    def add_tooth_record(self):
        """Add new tooth record for selected tooth."""
        if not self.selected_tooth or not self.patient_id:
            return
        
        # Import here to avoid circular imports
        try:
            from ...widgets.dental_chart_widget import ToothDetailsDialog
            dialog = ToothDetailsDialog(self.selected_tooth, self.patient_id, self)
            dialog.exec()
            
            # Refresh data after dialog closes
            self.load_patient_data()
            self.load_tooth_history(self.selected_tooth)
        except ImportError:
            logger.warning("ToothDetailsDialog not available")
            # Fallback - just refresh the data
            self.load_patient_data()
            if self.selected_tooth:
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
