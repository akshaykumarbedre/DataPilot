"""
Dual Dental Chart Panel - Individual dental chart panel for Patient Problems or Doctor Findings.
"""
import logging
from typing import Dict, List, Optional, Any, Callable
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox, 
    QLabel, QTextEdit, QScrollArea, QFrame, QPushButton, QSplitter,
    QSizePolicy, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from .enhanced_tooth_widget import EnhancedToothWidget
from ...services.tooth_history_service import tooth_history_service

logger = logging.getLogger(__name__)


class DentalChartPanel(QGroupBox):
    """Individual dental chart panel (Patient/Doctor)"""
    
    tooth_selected = Signal(int, str)  # tooth_number, panel_type
    tooth_statuses_changed = Signal(int, list, str)  # tooth_number, statuses, record_type
    
    def __init__(self, panel_type: str, patient_id: Optional[int] = None, parent=None):
        super().__init__(parent)
        self.panel_type = panel_type  # 'patient' or 'doctor'
        self.patient_id = patient_id
        self.examination_id = None
        self.selected_tooth = None
        self.selected_tooth_widget = None
        self.tooth_widgets = {}
        
        # Set panel title with improved formatting
        if panel_type == 'patient':
            title = "Patient Problems"
        else:
            title = "Doctor Findings"
        
        self.setTitle(title)
        self.setObjectName("dentalChartPanel")
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the dental chart panel UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        layout.setContentsMargins(5, 20, 5, 8)
        
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
        
        # Connect description input change to update button state
        if hasattr(self, 'description_input'):
            self.description_input.textChanged.connect(self.on_description_changed)
    
    def create_dental_chart_area(self) -> QWidget:
        """Create the 32-tooth layout area."""
        chart_widget = QWidget()
        layout = QVBoxLayout(chart_widget)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Upper teeth section
        upper_section = QGroupBox("Upper Jaw (Right 8-1 | Left 1-8)")
        upper_section.setFont(QFont("Arial", 10, QFont.Bold))
        upper_section.setObjectName("upperJaw")
        upper_section.setMaximumHeight(80)
        upper_layout = QHBoxLayout(upper_section)
        upper_layout.setSpacing(0)
        upper_layout.setContentsMargins(0, 0, 0, 0)
        
        # Upper right: 18-11 (reversed for visual layout)
        for i, tooth_num in enumerate(range(18, 10, -1)):
            tooth_widget = EnhancedToothWidget(tooth_num)
            tooth_widget.set_mode(self.panel_type)
            tooth_widget.tooth_clicked.connect(self.on_tooth_clicked)
            tooth_widget.statuses_selected.connect(self.on_tooth_statuses_changed)
            self.tooth_widgets[tooth_num] = tooth_widget
            upper_layout.addWidget(tooth_widget)
        
        # Separator between right and left
        separator1 = QLabel(" | ")
        separator1.setFont(QFont("Arial", 14, QFont.Bold))
        separator1.setAlignment(Qt.AlignCenter)
        separator1.setStyleSheet("color: #2C3E50; margin: 0 2px;")  # Reduced margin
        upper_layout.addWidget(separator1)
        
        # Upper left: 21-28
        for i, tooth_num in enumerate(range(21, 29)):
            tooth_widget = EnhancedToothWidget(tooth_num)
            tooth_widget.set_mode(self.panel_type)
            tooth_widget.tooth_clicked.connect(self.on_tooth_clicked)
            tooth_widget.statuses_selected.connect(self.on_tooth_statuses_changed)
            self.tooth_widgets[tooth_num] = tooth_widget
            upper_layout.addWidget(tooth_widget)
        
        layout.addWidget(upper_section)
        
        # Add spacing between upper and lower
        layout.addSpacing(0)
        
        # Lower teeth section
        lower_section = QGroupBox("Lower Jaw (Right 8-1 | Left 1-8)")
        lower_section.setFont(QFont("Arial", 10, QFont.Bold))
        lower_section.setObjectName("lowerJaw")
        lower_section.setMaximumHeight(80)
        lower_layout = QHBoxLayout(lower_section)
        lower_layout.setSpacing(0)
        lower_layout.setContentsMargins(0, 0, 0, 0)
        
        # Lower right: 48-41 (reversed for visual layout)
        for i, tooth_num in enumerate(range(48, 40, -1)):
            tooth_widget = EnhancedToothWidget(tooth_num)
            tooth_widget.set_mode(self.panel_type)
            tooth_widget.tooth_clicked.connect(self.on_tooth_clicked)
            tooth_widget.statuses_selected.connect(self.on_tooth_statuses_changed)
            self.tooth_widgets[tooth_num] = tooth_widget
            lower_layout.addWidget(tooth_widget)
        
        # Separator between right and left
        separator2 = QLabel(" | ")
        separator2.setFont(QFont("Arial", 14, QFont.Bold))
        separator2.setAlignment(Qt.AlignCenter)
        separator2.setStyleSheet("color: #2C3E50; margin: 0 2px;")  # Reduced margin
        lower_layout.addWidget(separator2)
        
        # Lower left: 31-38
        for i, tooth_num in enumerate(range(31, 39)):
            tooth_widget = EnhancedToothWidget(tooth_num)
            tooth_widget.set_mode(self.panel_type)
            tooth_widget.tooth_clicked.connect(self.on_tooth_clicked)
            tooth_widget.statuses_selected.connect(self.on_tooth_statuses_changed)
            self.tooth_widgets[tooth_num] = tooth_widget
            lower_layout.addWidget(tooth_widget)
        
        layout.addWidget(lower_section)
        
        return chart_widget
    
    def create_bottom_panel(self) -> QWidget:
        """Create bottom panel for selected tooth info and history."""
        bottom_widget = QWidget()
        bottom_widget.setMinimumHeight(140)  # Further reduced
        bottom_widget.setMaximumHeight(280)
        layout = QHBoxLayout(bottom_widget)
        layout.setSpacing(5)
        layout.setContentsMargins(1, 3, 1, 3)
        
        # Selected tooth info (left side of bottom panel)
        self.tooth_info_group = QGroupBox("Selected Tooth")
        self.tooth_info_group.setObjectName("selectedToothGroup")
        self.tooth_info_group.setMinimumWidth(160)
        self.tooth_info_group.setMaximumWidth(180)
        self.tooth_info_group.setMaximumWidth(240)
        self.tooth_info_group.setMinimumHeight(110)
        info_layout = QVBoxLayout(self.tooth_info_group)
        info_layout.setSpacing(4)
        
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
                padding: 4px;
                background-color: white;
                border: 1px solid #BDC3C7;
                border-radius: 4px;
                font-size: 9pt;
                min-height: 20px;
                color: #2C3E50;
            }
        """)
        info_layout.addWidget(self.current_status_label)
        
        # Description input for tooth record
        self.description_label = QLabel("Description:")
        self.description_label.setStyleSheet("QLabel { color: #2C3E50; font-weight: bold; }")
        info_layout.addWidget(self.description_label)
        
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(40)
        self.description_input.setPlaceholderText("Enter description for this tooth...")
        self.description_input.setStyleSheet("""
            QTextEdit {
                border: 1px solid #BDC3C7;
                border-radius: 4px;
                padding: 4px;
                background-color: white;
                font-size: 9pt;
                color: #2C3E50;
            }
            QTextEdit:focus {
                border-color: #4CAF50;
            }
        """)
        info_layout.addWidget(self.description_input)
        
        # Buttons layout
        buttons_layout = QHBoxLayout()

        # Update record button
        self.update_record_btn = QPushButton("Update")
        self.update_record_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 6px 10px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 9pt;
                min-height: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #BDC3C7;
                color: #7F8C8D;
            }
        """)
        self.update_record_btn.setEnabled(False)
        self.update_record_btn.clicked.connect(self.update_tooth_record)
        buttons_layout.addWidget(self.update_record_btn)

        # Delete last record button
        self.delete_last_btn = QPushButton("Delete Last")
        self.delete_last_btn.setStyleSheet("""
            QPushButton {
                background-color: #E74C3C;
                color: white;
                border: none;
                padding: 6px 10px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 9pt;
                min-height: 10px;
            }
            QPushButton:hover {
                background-color: #C0392B;
            }
        """)
        self.delete_last_btn.clicked.connect(self.delete_last_history_record)
        buttons_layout.addWidget(self.delete_last_btn)

        info_layout.addLayout(buttons_layout)
        
        layout.addWidget(self.tooth_info_group)
        
        # History text area (right side of bottom panel)
        self.history_group = QGroupBox(f"Tooth History - {self.panel_type.title()}")
        self.history_group.setObjectName("historyGroup")
        self.history_group.setMinimumHeight(110)
        history_layout = QVBoxLayout(self.history_group)
        history_layout.setSpacing(4)
        
        self.history_text = QTextEdit()
        self.history_text.setReadOnly(True)
        self.history_text.setMinimumHeight(100)
        self.history_text.setMaximumHeight(240)
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
        
        # Description input for tooth record
        self.description_label = QLabel("Description:")
        self.description_label.setStyleSheet("QLabel { color: #2C3E50; font-weight: bold; }")
        info_layout.addWidget(self.description_label)
        
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(50)
        self.description_input.setPlaceholderText("Enter description...")
        self.description_input.setStyleSheet("""
            QTextEdit {
                border: 1px solid #BDC3C7;
                border-radius: 3px;
                padding: 4px;
                background-color: white;
                font-size: 9pt;
                color: #2C3E50;
            }
            QTextEdit:focus {
                border-color: #4CAF50;
            }
        """)
        info_layout.addWidget(self.description_input)
        
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
        self.update_record_btn = QPushButton("Update")
        self.update_record_btn.setStyleSheet("""
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
        self.update_record_btn.setEnabled(False)
        self.update_record_btn.clicked.connect(self.update_tooth_record)
        history_layout.addWidget(self.update_record_btn)
        
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
                statuses = record.get('status', ['normal'])
                date_recorded = record.get('date_recorded')
                
                if tooth_number:
                    # Keep the most recent status for each tooth
                    if tooth_number not in tooth_status_map:
                        tooth_status_map[tooth_number] = {
                            'status': statuses,
                            'date_recorded': date_recorded,
                            'description': record.get('description', '')
                        }
                    else:
                        # Compare dates and keep the most recent
                        existing_date = tooth_status_map[tooth_number]['date_recorded']
                        if date_recorded and (not existing_date or date_recorded > existing_date):
                            tooth_status_map[tooth_number] = {
                                'status': statuses,
                                'date_recorded': date_recorded,
                                'description': record.get('description', '')
                            }
            
            # Update tooth widgets with the latest status
            for tooth_number, status_info in tooth_status_map.items():
                if tooth_number in self.tooth_widgets:
                    tooth_widget = self.tooth_widgets[tooth_number]
                    statuses = status_info['status']
                    
                    # Update the tooth widget's visual status
                    if hasattr(tooth_widget, 'update_status'):
                        tooth_widget.update_status(statuses)
                    elif hasattr(tooth_widget, 'set_status'):
                        tooth_widget.set_status(statuses)
            
            logger.info(f"Loaded tooth data for {len(tooth_status_map)} teeth in {self.panel_type} panel")
            
        except Exception as e:
            logger.error(f"Error loading tooth data in {self.panel_type} panel: {str(e)}")
    
    def load_patient_data(self):
        """Load patient's tooth data for this panel type using the new JSON-based system."""
        if not self.patient_id:
            return
        
        try:
            # Get tooth summary for patient
            tooth_summary = tooth_history_service.get_patient_tooth_summary(
                self.patient_id
            )
            
            # Update tooth widgets based on panel type
            for tooth_number, tooth_widget in self.tooth_widgets.items():
                if tooth_number in tooth_summary:
                    summary = tooth_summary[tooth_number]
                    
                    if self.panel_type == 'patient':
                        # Show patient problems
                        statuses = ['normal']
                        if summary['latest_patient_problem']:
                            statuses = summary['latest_patient_problem']['status']
                        
                        # Update tooth widget appearance
                        if hasattr(tooth_widget, 'set_patient_status'):
                            tooth_widget.set_patient_status(statuses)
                        elif hasattr(tooth_widget, 'update_status'):
                            tooth_widget.update_status(statuses)
                        elif hasattr(tooth_widget, 'set_status'):
                            tooth_widget.set_status(statuses)
                            
                    else:
                        # Show doctor findings
                        statuses = ['normal']
                        if summary['latest_doctor_finding']:
                            statuses = summary['latest_doctor_finding']['status']
                        
                        # Update tooth widget appearance
                        if hasattr(tooth_widget, 'set_doctor_status'):
                            tooth_widget.set_doctor_status(statuses)
                        elif hasattr(tooth_widget, 'update_status'):
                            tooth_widget.update_status(statuses)
                        elif hasattr(tooth_widget, 'set_status'):
                            tooth_widget.set_status(statuses)
                else:
                    # Reset to normal if no data
                    if self.panel_type == 'patient':
                        if hasattr(tooth_widget, 'set_patient_status'):
                            tooth_widget.set_patient_status(['normal'])
                        elif hasattr(tooth_widget, 'update_status'):
                            tooth_widget.update_status(['normal'])
                        elif hasattr(tooth_widget, 'set_status'):
                            tooth_widget.set_status(['normal'])
                    else:
                        if hasattr(tooth_widget, 'set_doctor_status'):
                            tooth_widget.set_doctor_status(['normal'])
                        elif hasattr(tooth_widget, 'update_status'):
                            tooth_widget.update_status(['normal'])
                        elif hasattr(tooth_widget, 'set_status'):
                            tooth_widget.set_status(['normal'])
            
            logger.info(f"Loaded patient data for {len(self.tooth_widgets)} teeth in {self.panel_type} panel")
        
        except Exception as e:
            logger.error(f"Error loading patient data: {str(e)}")
            # Reset all tooth widgets to normal on error
            for tooth_widget in self.tooth_widgets.values():
                if hasattr(tooth_widget, 'set_status'):
                    tooth_widget.set_status(['normal'])
    
    def on_tooth_clicked(self, tooth_number: int, click_type: str = 'left'):
        """Handle tooth click events."""
        
        # Get the clicked tooth widget
        clicked_widget = self.tooth_widgets.get(tooth_number)
        if not clicked_widget:
            return

        # Deselect the previously selected tooth if it's different from the current one
        if self.selected_tooth_widget and self.selected_tooth_widget != clicked_widget:
            self.selected_tooth_widget.force_hide_dropdown()

        # Update the selected tooth and widget
        self.selected_tooth = tooth_number
        self.selected_tooth_widget = clicked_widget

        # Update selected tooth display
        quadrant = tooth_number // 10
        position = tooth_number % 10
        self.tooth_info_label.setText(f"Tooth {tooth_number} ({quadrant},{position})")

        # Enable add record button
        self.update_record_btn.setEnabled(True)

        # Emit signal with correct parameters
        self.tooth_selected.emit(tooth_number, self.panel_type)

        if click_type == 'right':
            # Right click - could open detailed dialog
            self.show_tooth_details(tooth_number)
    
    def load_tooth_history(self, tooth_number: int):
        """Load and display tooth history using a simplified, clear format."""
        if not self.patient_id:
            return
        
        try:
            record_type = 'patient_problem' if self.panel_type == 'patient' else 'doctor_finding'
            
            full_history = tooth_history_service.get_tooth_full_history(
                self.patient_id, tooth_number, record_type
            )
            current_status = tooth_history_service.get_tooth_current_status(
                self.patient_id, tooth_number
            )
            
            # Update current status display
            latest_record = None
            if self.panel_type == 'patient':
                if current_status.get('latest_patient_problem'):
                    latest_record = current_status['latest_patient_problem']
                    count = current_status.get('patient_problems_count', 0)
                    status_text = f"<b>Current Status:</b> {', '.join(latest_record['status'])}<br>"
                    if latest_record['description']:
                        status_text += f"<b>Description:</b> {latest_record['description']}<br>"
                    status_text += f"<b>Date:</b> {latest_record['date_recorded']}<br>"
                    status_text += f"<b>Total Problems:</b> {count}"
                    self.tooth_widgets[tooth_number].set_patient_status(latest_record['status'])
                else:
                    status_text = "<b>Current Status:</b> Normal<br>No patient problems recorded."
                    self.tooth_widgets[tooth_number].set_patient_status(['normal'])
            else: # Doctor findings
                if current_status.get('latest_doctor_finding'):
                    latest_record = current_status['latest_doctor_finding']
                    count = current_status.get('doctor_findings_count', 0)
                    status_text = f"<b>Current Status:</b> {', '.join(latest_record['status'])}<br>"
                    if latest_record['description']:
                        status_text += f"<b>Description:</b> {latest_record['description']}<br>"
                    status_text += f"<b>Date:</b> {latest_record['date_recorded']}<br>"
                    status_text += f"<b>Total Findings:</b> {count}"
                    self.tooth_widgets[tooth_number].set_doctor_status(latest_record['status'])
                else:
                    status_text = "<b>Current Status:</b> Normal<br>No doctor findings recorded."
                    self.tooth_widgets[tooth_number].set_doctor_status(['normal'])
            
            self.current_status_label.setText(status_text)
            
            # Format history text
            history_text = f"<h3>Tooth {tooth_number} History ({self.panel_type.title()})</h3>"
            
            records = full_history.get('patient_problems' if self.panel_type == 'patient' else 'doctor_findings', [])
            
            if records:
                history_text += "<b>Timeline:</b><ul>"
                # Assuming the first record contains the full history
                first_record = records[0]
                status_history = first_record.get('status_history', [])
                desc_history = first_record.get('description_history', [])
                date_history = first_record.get('date_history', [])

                if status_history:
                    # Iterate in reverse for newest first
                    for i in reversed(range(len(status_history))):
                        date = date_history[i] if i < len(date_history) else "N/A"
                        statuses = status_history[i] if i < len(status_history) else []
                        desc = desc_history[i] if i < len(desc_history) and desc_history[i] else ""
                        
                        history_text += f"<li><b>{date}:</b> {', '.join(statuses)}"
                        if desc:
                            history_text += f" - <i>{desc}</i>"
                        history_text += "</li>"
                history_text += "</ul>"
            else:
                history_text += f"<p>No {self.panel_type.replace('_', ' ')} history recorded for this tooth.</p>"

            self.history_text.setHtml(history_text)
            
        except Exception as e:
            logger.error(f"Error loading tooth history for tooth {tooth_number}: {str(e)}")
            self.history_text.setHtml(f"<p>Error loading history for tooth {tooth_number}.</p>")
            self.current_status_label.setText("Error loading status.")
    
    def on_tooth_statuses_changed(self, tooth_number: int, statuses: list, record_type: str):
        """Handle tooth status change from tooth widget interactions."""
        if not self.patient_id:
            return
        
        try:
            # Convert panel type to database record type
            db_record_type = 'patient_problem' if record_type == 'patient' else 'doctor_finding'
            
            # Get description from input field
            description = self.description_input.toPlainText().strip()
            if not description:
                description = f"Status changed to {', '.join(statuses)}"

            # Add new history entry for the status change
            success = tooth_history_service.add_tooth_history_entry(
                patient_id=self.patient_id,
                tooth_number=tooth_number,
                record_type=db_record_type,
                statuses=statuses,
                description=description,
                examination_id=self.examination_id
            )
            
            if success:
                # Refresh tooth history if this tooth is selected
                if tooth_number == self.selected_tooth:
                    self.load_tooth_history(tooth_number)
                
                # Refresh patient data to update tooth widget appearance
                self.load_patient_data()
                
                # Emit signal for parent components
                self.tooth_statuses_changed.emit(tooth_number, statuses, db_record_type)
                
                logger.info(f"Updated tooth {tooth_number} status to {', '.join(statuses)} in {self.panel_type} panel")
            else:
                logger.error(f"Failed to update tooth {tooth_number} status")
            
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
    
    def update_tooth_record(self):
        """Add new tooth record for selected tooth."""
        if self.selected_tooth is None or not self.patient_id:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Warning", "Please select a tooth first.")
            return
        
        # Get description from input field
        description = self.description_input.toPlainText().strip()
        
        if not description:
            description=""
            # from PySide6.QtWidgets import QMessageBox
            # QMessageBox.warning(self, "Warning", "Please enter a description for this tooth record.")
            # return
        
        try:
            # Get current status from tooth widget (if available)
            current_statuses = ['normal']
            if self.selected_tooth in self.tooth_widgets:
                tooth_widget = self.tooth_widgets[self.selected_tooth]
                if hasattr(tooth_widget, 'get_current_status'):
                    current_statuses = tooth_widget.get_current_status()
            
            # If no specific status is set, try to get from existing records
            if current_statuses == ['normal']:
                existing_status = tooth_history_service.get_tooth_current_status(
                    self.patient_id, self.selected_tooth
                )
                if self.panel_type == 'patient':
                    if existing_status.get('latest_patient_problem'):
                        current_statuses = existing_status['latest_patient_problem']['status']
                else:
                    if existing_status.get('latest_doctor_finding'):
                        current_statuses = existing_status['latest_doctor_finding']['status']
            
            # Determine record type based on panel type
            record_type = 'patient_problem' if self.panel_type == 'patient' else 'doctor_finding'
            
            # Add new tooth history entry using JSON-based system
            success = tooth_history_service.add_tooth_history_entry(
                patient_id=self.patient_id,
                tooth_number=self.selected_tooth,
                record_type=record_type,
                statuses=current_statuses,
                description=description,
                examination_id=self.examination_id
            )
            
            if success:
                # Clear description input
                self.description_input.clear()
                
                # Refresh tooth widget appearance
                self.load_patient_data()
                
                # Refresh tooth history display
                self.load_tooth_history(self.selected_tooth)
                
                # Emit signal for parent components
                self.tooth_statuses_changed.emit(self.selected_tooth, current_statuses, record_type)
                
                # Show success message
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.information(self, "Success", 
                    f"Tooth {self.selected_tooth} record added successfully!\n"
                    f"Type: {record_type.replace('_', ' ').title()}\n"
                    f"Status: {', '.join(current_statuses)}\n"
                    f"Description: {description[:50]}{'...' if len(description) > 50 else ''}")
                
                # Disable button until new description is entered
                self.update_record_btn.setEnabled(False)
                
            else:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Error", "Failed to save tooth record.")
                
        except Exception as e:
            logger.error(f"Error saving tooth record: {str(e)}")
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Error saving record: {str(e)}")
    
    def delete_last_history_record(self):
        if self.selected_tooth is None or not self.patient_id:
            QMessageBox.warning(self, "Warning", "Please select a tooth first.")
            return
            
        record_type = 'patient_problem' if self.panel_type == 'patient' else 'doctor_finding'
        
        reply = QMessageBox.question(self, 'Confirm Deletion', 
            f"Are you sure you want to delete the last history record for tooth {self.selected_tooth}?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            
        if reply == QMessageBox.Yes:
            success = tooth_history_service.delete_last_tooth_history_entry(
                self.patient_id, self.selected_tooth, record_type
            )
            
            if success:
                self.load_tooth_history(self.selected_tooth)
                QMessageBox.information(self, "Success", "Last history record deleted.")
            else:
                QMessageBox.warning(self, "Error", "Failed to delete last history record.")

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
        if hasattr(self, 'description_input'):
            self.description_input.clear()  # Clear description input
        self.update_record_btn.setEnabled(False)
    
    def hide_all_dropdowns(self):
        """Hide all tooth status dropdowns."""
        for tooth_widget in self.tooth_widgets.values():
            tooth_widget.force_hide_dropdown()
    
    def on_description_changed(self):
        """Handle description input change to update button state."""
        pass
    def get_description(self) -> str:
        return self.description_input.toPlainText().strip()