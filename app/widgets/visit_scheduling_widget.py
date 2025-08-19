"""
Visit Scheduling Widget for managing patient appointments and visits.
"""
import logging
from datetime import date, datetime, time, timedelta
from typing import Dict, List, Optional, Any
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, 
    QLabel, QComboBox, QTextEdit, QTabWidget, QFrame, QScrollArea,
    QGroupBox, QSplitter, QMessageBox, QDialog, QDialogButtonBox, 
    QFormLayout, QLineEdit, QDateEdit, QSpinBox, QListWidget,
    QListWidgetItem, QTableWidget, QTableWidgetItem, QHeaderView,
    QCheckBox, QProgressBar, QTimeEdit, QDoubleSpinBox, QCalendarWidget
)
from PySide6.QtCore import Qt, Signal, QDate, QTime, QTimer
from PySide6.QtGui import QFont, QPixmap, QIcon, QColor

from ..services.visit_records_service import visit_records_service
from ..services.dental_examination_service import dental_examination_service

logger = logging.getLogger(__name__)


class VisitDialog(QDialog):
    """Dialog for creating/editing visit appointments."""
    
    visit_saved = Signal(dict)
    
    def __init__(self, patient_id: int, visit_data: Optional[Dict] = None, parent=None):
        super().__init__(parent)
        self.patient_id = patient_id
        self.visit_data = visit_data
        self.is_edit_mode = visit_data is not None
        
        self.setup_ui()
        if self.is_edit_mode:
            self.populate_form()
    
    def setup_ui(self):
        """Setup the visit dialog UI."""
        self.setWindowTitle("Edit Visit" if self.is_edit_mode else "Schedule New Visit")
        self.setModal(True)
        self.resize(500, 600)
        
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("Edit Visit" if self.is_edit_mode else "Schedule New Visit")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        header.setStyleSheet("color: #19c5e5; margin: 10px;")
        layout.addWidget(header)
        
        # Form layout
        form_layout = QFormLayout()
        
        # Visit date
        self.date_edit = QDateEdit(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setMinimumDate(QDate.currentDate())  # Can't schedule in the past
        form_layout.addRow("Visit Date:", self.date_edit)
        
        # Visit time
        self.time_edit = QTimeEdit(QTime(9, 0))  # Default to 9:00 AM
        self.time_edit.setDisplayFormat("hh:mm AP")
        form_layout.addRow("Visit Time:", self.time_edit)
        
        # Visit type
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "consultation", "treatment", "follow_up", "emergency", 
            "cleaning", "checkup", "extraction", "filling", "root_canal"
        ])
        form_layout.addRow("Visit Type:", self.type_combo)
        
        # Status
        self.status_combo = QComboBox()
        self.status_combo.addItems([
            "scheduled", "confirmed", "in_progress", "completed", 
            "cancelled", "no_show", "rescheduled"
        ])
        form_layout.addRow("Status:", self.status_combo)
        
        # Doctor name
        self.doctor_edit = QLineEdit()
        self.doctor_edit.setPlaceholderText("Enter doctor name...")
        form_layout.addRow("Doctor:", self.doctor_edit)
        
        # Duration
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(15, 480)  # 15 minutes to 8 hours
        self.duration_spin.setValue(60)  # Default 1 hour
        self.duration_spin.setSuffix(" minutes")
        form_layout.addRow("Duration:", self.duration_spin)
        
        # Notes
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(100)
        self.notes_edit.setPlaceholderText("Additional notes or instructions...")
        form_layout.addRow("Notes:", self.notes_edit)
        
        # Treatment performed (for completed visits)
        self.treatment_edit = QTextEdit()
        self.treatment_edit.setMaximumHeight(80)
        self.treatment_edit.setPlaceholderText("Treatment performed (if completed)...")
        form_layout.addRow("Treatment Performed:", self.treatment_edit)
        
        # Cost
        self.cost_spin = QDoubleSpinBox()
        self.cost_spin.setRange(0.0, 99999.99)
        self.cost_spin.setPrefix("$")
        self.cost_spin.setDecimals(2)
        form_layout.addRow("Cost:", self.cost_spin)
        
        # Payment status
        self.payment_combo = QComboBox()
        self.payment_combo.addItems(["pending", "paid", "partial", "insurance_pending"])
        form_layout.addRow("Payment Status:", self.payment_combo)
        
        # Next visit date
        self.next_visit_edit = QDateEdit()
        self.next_visit_edit.setCalendarPopup(True)
        self.next_visit_edit.setSpecialValueText("No follow-up scheduled")
        self.next_visit_edit.setDate(QDate())  # Empty date
        form_layout.addRow("Next Visit Date:", self.next_visit_edit)
        
        layout.addLayout(form_layout)
        
        # Examination selection (optional)
        exam_group = QGroupBox("Link to Examination (Optional)")
        exam_layout = QVBoxLayout(exam_group)
        
        self.examination_combo = QComboBox()
        self.examination_combo.addItem("No examination selected", None)
        self.load_patient_examinations()
        exam_layout.addWidget(self.examination_combo)
        
        layout.addWidget(exam_group)
        
        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.save_visit)
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
        
        # Connect status change to enable/disable fields
        self.status_combo.currentTextChanged.connect(self.on_status_changed)
    
    def load_patient_examinations(self):
        """Load patient examinations for linking."""
        try:
            examinations = dental_examination_service.get_patient_examinations(self.patient_id)
            for exam in examinations:
                exam_text = f"{exam.get('examination_date', '')} - {exam.get('examination_type', '').replace('_', ' ').title()}"
                self.examination_combo.addItem(exam_text, exam.get('id'))
        except Exception as e:
            logger.error(f"Error loading examinations: {str(e)}")
    
    def on_status_changed(self, status: str):
        """Handle status change to enable/disable relevant fields."""
        # Enable treatment and cost fields for completed visits
        is_completed = status == "completed"
        self.treatment_edit.setEnabled(True)  # Always allow treatment notes
        self.cost_spin.setEnabled(is_completed or status in ["in_progress", "scheduled"])
        
        # Suggest next visit date for completed visits
        if is_completed and self.next_visit_edit.date() == QDate():
            # Suggest a date 6 months from now for regular checkups
            suggested_date = QDate.currentDate().addMonths(6)
            self.next_visit_edit.setDate(suggested_date)
    
    def populate_form(self):
        """Populate form with existing visit data."""
        if not self.visit_data:
            return
        
        try:
            data = self.visit_data
            
            # Visit date
            if data.get('visit_date'):
                if isinstance(data['visit_date'], str):
                    visit_date = datetime.strptime(data['visit_date'], '%Y-%m-%d').date()
                    self.date_edit.setDate(QDate(visit_date))
                else:
                    self.date_edit.setDate(QDate(data['visit_date']))
            
            # Visit time
            if data.get('visit_time'):
                if isinstance(data['visit_time'], str):
                    visit_time = datetime.strptime(data['visit_time'], '%H:%M:%S').time()
                    self.time_edit.setTime(QTime(visit_time))
                else:
                    self.time_edit.setTime(QTime(data['visit_time']))
            
            # Other fields
            if data.get('visit_type'):
                self.type_combo.setCurrentText(data['visit_type'])
            
            if data.get('status'):
                self.status_combo.setCurrentText(data['status'])
            
            self.doctor_edit.setText(data.get('doctor_name', ''))
            
            if data.get('duration_minutes'):
                self.duration_spin.setValue(data['duration_minutes'])
            
            self.notes_edit.setPlainText(data.get('notes', ''))
            self.treatment_edit.setPlainText(data.get('treatment_performed', ''))
            
            if data.get('cost'):
                self.cost_spin.setValue(float(data['cost']))
            
            if data.get('payment_status'):
                self.payment_combo.setCurrentText(data['payment_status'])
            
            # Next visit date
            if data.get('next_visit_date'):
                if isinstance(data['next_visit_date'], str):
                    next_date = datetime.strptime(data['next_visit_date'], '%Y-%m-%d').date()
                    self.next_visit_edit.setDate(QDate(next_date))
                else:
                    self.next_visit_edit.setDate(QDate(data['next_visit_date']))
            
            # Examination link
            if data.get('examination_id'):
                for i in range(self.examination_combo.count()):
                    if self.examination_combo.itemData(i) == data['examination_id']:
                        self.examination_combo.setCurrentIndex(i)
                        break
                        
        except Exception as e:
            logger.error(f"Error populating form: {str(e)}")
            QMessageBox.warning(self, "Error", "Error loading visit data.")
    
    def save_visit(self):
        """Save the visit."""
        try:
            # Gather form data
            visit_data = {
                'visit_date': self.date_edit.date().toPython(),
                'visit_time': self.time_edit.time().toPython(),
                'visit_type': self.type_combo.currentText(),
                'status': self.status_combo.currentText(),
                'doctor_name': self.doctor_edit.text().strip(),
                'duration_minutes': self.duration_spin.value(),
                'notes': self.notes_edit.toPlainText().strip(),
                'treatment_performed': self.treatment_edit.toPlainText().strip(),
                'cost': self.cost_spin.value() if self.cost_spin.value() > 0 else None,
                'payment_status': self.payment_combo.currentText()
            }
            
            # Next visit date (optional)
            next_date = self.next_visit_edit.date()
            if next_date.isValid() and next_date != QDate():
                visit_data['next_visit_date'] = next_date.toPython()
            
            # Examination link (optional)
            examination_id = self.examination_combo.currentData()
            if examination_id:
                visit_data['examination_id'] = examination_id
            
            # Validate required fields
            if not visit_data['doctor_name']:
                QMessageBox.warning(self, "Validation Error", "Doctor name is required.")
                return
            
            # Check for scheduling conflicts (only for new/rescheduled visits)
            if visit_data['status'] in ['scheduled', 'confirmed'] and not self.is_edit_mode:
                if self.check_scheduling_conflict(visit_data['visit_date'], visit_data['visit_time'], visit_data['duration_minutes']):
                    reply = QMessageBox.question(
                        self, 
                        "Scheduling Conflict", 
                        "There may be a scheduling conflict. Do you want to continue?",
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.No
                    )
                    if reply == QMessageBox.No:
                        return
            
            # Save visit
            if self.is_edit_mode:
                # Update existing visit
                success = visit_records_service.update_visit(
                    self.visit_data['id'], visit_data
                )
                if success:
                    visit_data['id'] = self.visit_data['id']
                    self.visit_saved.emit(visit_data)
                    QMessageBox.information(self, "Success", "Visit updated successfully!")
                    self.accept()
                else:
                    QMessageBox.warning(self, "Error", "Failed to update visit.")
            else:
                # Create new visit
                result = visit_records_service.create_visit(self.patient_id, visit_data)
                if result:
                    self.visit_saved.emit(result)
                    QMessageBox.information(self, "Success", "Visit scheduled successfully!")
                    self.accept()
                else:
                    QMessageBox.warning(self, "Error", "Failed to schedule visit.")
                    
        except Exception as e:
            logger.error(f"Error saving visit: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error saving visit: {str(e)}")
    
    def check_scheduling_conflict(self, visit_date: date, visit_time: time, duration: int) -> bool:
        """Check for potential scheduling conflicts."""
        try:
            # Get visits for the same date
            existing_visits = visit_records_service.get_visits_by_date_range(
                visit_date, visit_date, status="scheduled"
            )
            
            # Check for time overlaps
            visit_start = datetime.combine(visit_date, visit_time)
            visit_end = visit_start + timedelta(minutes=duration)
            
            for existing in existing_visits:
                if existing.get('visit_time'):
                    existing_start = datetime.combine(visit_date, existing['visit_time'])
                    existing_duration = existing.get('duration_minutes', 60)
                    existing_end = existing_start + timedelta(minutes=existing_duration)
                    
                    # Check for overlap
                    if (visit_start < existing_end and visit_end > existing_start):
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking scheduling conflict: {str(e)}")
            return False


class VisitCalendarWidget(QWidget):
    """Calendar widget for viewing scheduled visits."""
    
    visit_selected = Signal(dict)
    date_selected = Signal(object)  # QDate
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_patient_id = None
        self.visits_by_date = {}
        
        self.setup_ui()
        self.load_visits()
    
    def setup_ui(self):
        """Setup the calendar UI."""
        layout = QVBoxLayout(self)
        
        # Calendar controls
        controls_layout = QHBoxLayout()
        
        # View mode selection
        view_group = QGroupBox("View")
        view_layout = QHBoxLayout(view_group)
        
        self.view_combo = QComboBox()
        self.view_combo.addItems(["All Patients", "Current Patient"])
        self.view_combo.currentTextChanged.connect(self.on_view_changed)
        view_layout.addWidget(self.view_combo)
        
        controls_layout.addWidget(view_group)
        
        # Refresh button
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.load_visits)
        controls_layout.addWidget(self.refresh_button)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Calendar widget
        self.calendar = QCalendarWidget()
        self.calendar.clicked.connect(self.on_date_clicked)
        layout.addWidget(self.calendar)
        
        # Visits for selected date
        self.selected_date_group = QGroupBox("Visits for Selected Date")
        self.selected_date_layout = QVBoxLayout(self.selected_date_group)
        
        self.selected_date_label = QLabel("Select a date to view visits")
        self.selected_date_layout.addWidget(self.selected_date_label)
        
        self.visits_list = QListWidget()
        self.visits_list.itemDoubleClicked.connect(self.on_visit_double_clicked)
        self.selected_date_layout.addWidget(self.visits_list)
        
        layout.addWidget(self.selected_date_group)
    
    def set_patient(self, patient_id: int):
        """Set the current patient for filtering."""
        self.current_patient_id = patient_id
        if self.view_combo.currentText() == "Current Patient":
            self.load_visits()
    
    def on_view_changed(self, view_mode: str):
        """Handle view mode change."""
        self.load_visits()
    
    def load_visits(self):
        """Load visits and update calendar."""
        try:
            # Determine date range (current month ± 3 months)
            today = date.today()
            start_date = today.replace(day=1) - timedelta(days=90)
            end_date = today + timedelta(days=90)
            
            # Get visits
            if self.view_combo.currentText() == "Current Patient" and self.current_patient_id:
                visits = visit_records_service.get_patient_visits(self.current_patient_id)
                # Filter by date range
                visits = [v for v in visits if start_date <= v.get('visit_date', today) <= end_date]
            else:
                visits = visit_records_service.get_visits_by_date_range(start_date, end_date)
            
            # Group visits by date
            self.visits_by_date = {}
            for visit in visits:
                visit_date = visit.get('visit_date')
                if visit_date:
                    if isinstance(visit_date, str):
                        visit_date = datetime.strptime(visit_date, '%Y-%m-%d').date()
                    
                    if visit_date not in self.visits_by_date:
                        self.visits_by_date[visit_date] = []
                    self.visits_by_date[visit_date].append(visit)
            
            # Update calendar highlighting
            self.update_calendar_highlighting()
            
            # Update selected date if it has visits
            selected_date = self.calendar.selectedDate().toPython()
            self.update_selected_date_visits(selected_date)
            
        except Exception as e:
            logger.error(f"Error loading visits: {str(e)}")
    
    def update_calendar_highlighting(self):
        """Update calendar to highlight dates with visits."""
        # Reset calendar format
        self.calendar.setDateTextFormat(QDate(), self.calendar.dateTextFormat(QDate()))
        
        # Highlight dates with visits
        for visit_date in self.visits_by_date.keys():
            qdate = QDate(visit_date)
            
            # Create format with background color
            format = self.calendar.dateTextFormat(qdate)
            format.setBackground(QColor("#19c5e5"))
            format.setForeground(QColor("white"))
            self.calendar.setDateTextFormat(qdate, format)
    
    def on_date_clicked(self, qdate: QDate):
        """Handle calendar date click."""
        selected_date = qdate.toPython()
        self.update_selected_date_visits(selected_date)
        self.date_selected.emit(qdate)
    
    def update_selected_date_visits(self, selected_date: date):
        """Update the visits list for selected date."""
        self.visits_list.clear()
        
        date_str = selected_date.strftime("%A, %B %d, %Y")
        
        if selected_date in self.visits_by_date:
            visits = self.visits_by_date[selected_date]
            self.selected_date_label.setText(f"Visits for {date_str} ({len(visits)} visit{'s' if len(visits) != 1 else ''})")
            
            for visit in sorted(visits, key=lambda v: v.get('visit_time', time())):
                # Format visit display
                visit_time = visit.get('visit_time', '')
                if isinstance(visit_time, time):
                    time_str = visit_time.strftime("%I:%M %p")
                else:
                    time_str = str(visit_time)
                
                patient_name = visit.get('patient_name', f"Patient {visit.get('patient_id', '')}")
                visit_type = visit.get('visit_type', '').replace('_', ' ').title()
                status = visit.get('status', '').title()
                
                display_text = f"{time_str} - {patient_name} ({visit_type}) - {status}"
                
                item = QListWidgetItem(display_text)
                item.setData(Qt.UserRole, visit)
                
                # Color code by status
                if status == "Completed":
                    item.setBackground(QColor("#d4edda"))
                elif status == "Cancelled":
                    item.setBackground(QColor("#f8d7da"))
                elif status == "No Show":
                    item.setBackground(QColor("#fff3cd"))
                
                self.visits_list.addItem(item)
        else:
            self.selected_date_label.setText(f"No visits scheduled for {date_str}")
    
    def on_visit_double_clicked(self, item: QListWidgetItem):
        """Handle visit item double click."""
        visit_data = item.data(Qt.UserRole)
        if visit_data:
            self.visit_selected.emit(visit_data)


class VisitSchedulingWidget(QWidget):
    """Main widget for visit scheduling and management."""
    
    visit_changed = Signal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.patient_id = None
        self.current_visit = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the visit scheduling UI."""
        layout = QVBoxLayout(self)
        
        # Patient info header
        self.patient_info_label = QLabel("No patient selected")
        self.patient_info_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.patient_info_label.setStyleSheet("color: #19c5e5; margin: 10px;")
        layout.addWidget(self.patient_info_label)
        
        # Tab widget for different views
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Calendar view tab
        self.calendar_widget = VisitCalendarWidget()
        self.calendar_widget.visit_selected.connect(self.on_visit_selected)
        self.calendar_widget.date_selected.connect(self.on_date_selected)
        self.tab_widget.addTab(self.calendar_widget, "Calendar View")
        
        # List view tab
        self.create_list_view_tab()
        
        # Quick actions
        self.create_quick_actions(layout)
    
    def create_list_view_tab(self):
        """Create the list view tab."""
        list_widget = QWidget()
        layout = QVBoxLayout(list_widget)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        # Filter options
        filter_group = QGroupBox("Filter")
        filter_layout = QHBoxLayout(filter_group)
        
        self.status_filter = QComboBox()
        self.status_filter.addItems([
            "All", "Scheduled", "Confirmed", "In Progress", 
            "Completed", "Cancelled", "No Show"
        ])
        self.status_filter.currentTextChanged.connect(self.filter_visits)
        filter_layout.addWidget(QLabel("Status:"))
        filter_layout.addWidget(self.status_filter)
        
        self.date_filter = QComboBox()
        self.date_filter.addItems([
            "All", "Today", "This Week", "Next Week", "This Month"
        ])
        self.date_filter.currentTextChanged.connect(self.filter_visits)
        filter_layout.addWidget(QLabel("Date:"))
        filter_layout.addWidget(self.date_filter)
        
        controls_layout.addWidget(filter_group)
        controls_layout.addStretch()
        
        # Refresh button
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.refresh_visits)
        controls_layout.addWidget(refresh_button)
        
        layout.addLayout(controls_layout)
        
        # Visits table
        self.visits_table = QTableWidget()
        self.visits_table.setColumnCount(7)
        self.visits_table.setHorizontalHeaderLabels([
            "Date", "Time", "Type", "Status", "Doctor", "Duration", "Actions"
        ])
        
        # Configure table
        header = self.visits_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Date
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Time
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Type
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Status
        header.setSectionResizeMode(4, QHeaderView.Stretch)  # Doctor
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Duration
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Actions
        
        self.visits_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.visits_table.setAlternatingRowColors(True)
        
        layout.addWidget(self.visits_table)
        
        self.tab_widget.addTab(list_widget, "List View")
    
    def create_quick_actions(self, parent_layout):
        """Create quick action buttons."""
        actions_layout = QHBoxLayout()
        
        # Schedule new visit
        self.schedule_button = QPushButton("Schedule New Visit")
        self.schedule_button.setStyleSheet("""
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
        self.schedule_button.clicked.connect(self.schedule_new_visit)
        actions_layout.addWidget(self.schedule_button)
        
        # Today's visits
        today_button = QPushButton("Today's Visits")
        today_button.clicked.connect(self.show_todays_visits)
        actions_layout.addWidget(today_button)
        
        # Upcoming visits
        upcoming_button = QPushButton("Upcoming Visits")
        upcoming_button.clicked.connect(self.show_upcoming_visits)
        actions_layout.addWidget(upcoming_button)
        
        actions_layout.addStretch()
        parent_layout.addLayout(actions_layout)
    
    def set_patient(self, patient_id: int, patient_name: str = ""):
        """Set the current patient."""
        self.patient_id = patient_id
        self.patient_info_label.setText(f"Patient: {patient_name}" if patient_name else f"Patient ID: {patient_id}")
        
        # Update calendar widget
        self.calendar_widget.set_patient(patient_id)
        
        # Refresh data
        self.refresh_visits()
    
    def schedule_new_visit(self):
        """Schedule a new visit."""
        if not self.patient_id:
            QMessageBox.warning(self, "No Patient", "Please select a patient first.")
            return
        
        dialog = VisitDialog(self.patient_id, parent=self)
        dialog.visit_saved.connect(self.on_visit_saved)
        dialog.exec()
    
    def on_visit_selected(self, visit_data: Dict):
        """Handle visit selection from calendar."""
        self.current_visit = visit_data
        self.visit_changed.emit(visit_data)
        
        # Edit the selected visit
        if visit_data.get('patient_id') == self.patient_id:
            self.edit_visit(visit_data)
    
    def edit_visit(self, visit_data: Dict):
        """Edit an existing visit."""
        dialog = VisitDialog(self.patient_id, visit_data, parent=self)
        dialog.visit_saved.connect(self.on_visit_saved)
        dialog.exec()
    
    def on_visit_saved(self, visit_data: Dict):
        """Handle visit saved event."""
        self.refresh_visits()
        self.visit_changed.emit(visit_data)
    
    def on_date_selected(self, qdate):
        """Handle date selection from calendar."""
        # Could be used to pre-fill date when scheduling new visit
        pass
    
    def refresh_visits(self):
        """Refresh visits data."""
        self.calendar_widget.load_visits()
        self.filter_visits()
    
    def filter_visits(self):
        """Apply filters to visits list."""
        if not self.patient_id:
            self.visits_table.setRowCount(0)
            return
        
        try:
            # Get visits for patient
            visits = visit_records_service.get_patient_visits(self.patient_id)
            
            # Apply status filter
            status_filter = self.status_filter.currentText()
            if status_filter != "All":
                visits = [v for v in visits if v.get('status', '').title() == status_filter]
            
            # Apply date filter
            date_filter = self.date_filter.currentText()
            if date_filter != "All":
                today = date.today()
                
                if date_filter == "Today":
                    visits = [v for v in visits if v.get('visit_date') == today]
                elif date_filter == "This Week":
                    week_start = today - timedelta(days=today.weekday())
                    week_end = week_start + timedelta(days=6)
                    visits = [v for v in visits if week_start <= v.get('visit_date', today) <= week_end]
                elif date_filter == "Next Week":
                    week_start = today + timedelta(days=7-today.weekday())
                    week_end = week_start + timedelta(days=6)
                    visits = [v for v in visits if week_start <= v.get('visit_date', today) <= week_end]
                elif date_filter == "This Month":
                    month_start = today.replace(day=1)
                    if today.month == 12:
                        month_end = today.replace(year=today.year+1, month=1, day=1) - timedelta(days=1)
                    else:
                        month_end = today.replace(month=today.month+1, day=1) - timedelta(days=1)
                    visits = [v for v in visits if month_start <= v.get('visit_date', today) <= month_end]
            
            # Update table
            self.update_visits_table(visits)
            
        except Exception as e:
            logger.error(f"Error filtering visits: {str(e)}")
    
    def update_visits_table(self, visits: List[Dict]):
        """Update the visits table with filtered data."""
        self.visits_table.setRowCount(len(visits))
        
        for row, visit in enumerate(visits):
            # Date
            date_item = QTableWidgetItem(str(visit.get('visit_date', '')))
            self.visits_table.setItem(row, 0, date_item)
            
            # Time
            visit_time = visit.get('visit_time', '')
            if isinstance(visit_time, time):
                time_str = visit_time.strftime("%I:%M %p")
            else:
                time_str = str(visit_time)
            time_item = QTableWidgetItem(time_str)
            self.visits_table.setItem(row, 1, time_item)
            
            # Type
            type_item = QTableWidgetItem(visit.get('visit_type', '').replace('_', ' ').title())
            self.visits_table.setItem(row, 2, type_item)
            
            # Status
            status_item = QTableWidgetItem(visit.get('status', '').title())
            self.visits_table.setItem(row, 3, status_item)
            
            # Doctor
            doctor_item = QTableWidgetItem(visit.get('doctor_name', ''))
            self.visits_table.setItem(row, 4, doctor_item)
            
            # Duration
            duration = visit.get('duration_minutes', 0)
            duration_item = QTableWidgetItem(f"{duration} min" if duration else "")
            self.visits_table.setItem(row, 5, duration_item)
            
            # Actions
            self.create_visit_action_buttons(row, visit)
    
    def create_visit_action_buttons(self, row: int, visit: Dict):
        """Create action buttons for a visit row."""
        actions_widget = QWidget()
        actions_layout = QHBoxLayout(actions_widget)
        actions_layout.setContentsMargins(4, 4, 4, 4)
        
        # Edit button
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
        edit_button.clicked.connect(lambda: self.edit_visit(visit))
        actions_layout.addWidget(edit_button)
        
        # Cancel/Complete button based on status
        status = visit.get('status', '')
        if status in ['scheduled', 'confirmed']:
            action_button = QPushButton("Cancel")
            action_button.setStyleSheet("""
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
            action_button.clicked.connect(lambda: self.cancel_visit(visit))
        elif status == 'in_progress':
            action_button = QPushButton("Complete")
            action_button.setStyleSheet("""
                QPushButton {
                    background-color: #28a745;
                    color: white;
                    border: none;
                    padding: 4px 8px;
                    border-radius: 3px;
                    font-size: 10px;
                }
                QPushButton:hover {
                    background-color: #218838;
                }
            """)
            action_button.clicked.connect(lambda: self.complete_visit(visit))
        else:
            action_button = QPushButton("Delete")
            action_button.setStyleSheet("""
                QPushButton {
                    background-color: #6c757d;
                    color: white;
                    border: none;
                    padding: 4px 8px;
                    border-radius: 3px;
                    font-size: 10px;
                }
                QPushButton:hover {
                    background-color: #5a6268;
                }
            """)
            action_button.clicked.connect(lambda: self.delete_visit(visit))
        
        action_button.setMaximumWidth(60)
        actions_layout.addWidget(action_button)
        
        self.visits_table.setCellWidget(row, 6, actions_widget)
    
    def cancel_visit(self, visit: Dict):
        """Cancel a visit."""
        reply = QMessageBox.question(
            self, 
            "Cancel Visit", 
            "Are you sure you want to cancel this visit?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success = visit_records_service.update_visit_status(visit['id'], 'cancelled')
            if success:
                self.refresh_visits()
                QMessageBox.information(self, "Success", "Visit cancelled successfully.")
            else:
                QMessageBox.warning(self, "Error", "Failed to cancel visit.")
    
    def complete_visit(self, visit: Dict):
        """Mark a visit as completed."""
        success = visit_records_service.update_visit_status(visit['id'], 'completed')
        if success:
            self.refresh_visits()
            QMessageBox.information(self, "Success", "Visit marked as completed.")
        else:
            QMessageBox.warning(self, "Error", "Failed to complete visit.")
    
    def delete_visit(self, visit: Dict):
        """Delete a visit."""
        reply = QMessageBox.question(
            self, 
            "Delete Visit", 
            "Are you sure you want to delete this visit? This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success = visit_records_service.delete_visit(visit['id'])
            if success:
                self.refresh_visits()
                QMessageBox.information(self, "Success", "Visit deleted successfully.")
            else:
                QMessageBox.warning(self, "Error", "Failed to delete visit.")
    
    def show_todays_visits(self):
        """Show today's visits."""
        self.date_filter.setCurrentText("Today")
        self.tab_widget.setCurrentIndex(1)  # Switch to list view
    
    def show_upcoming_visits(self):
        """Show upcoming visits."""
        self.date_filter.setCurrentText("This Week")
        self.tab_widget.setCurrentIndex(1)  # Switch to list view
