"""
Patient management interface with CRUD operations.
"""
import logging
from datetime import date, datetime
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                               QTableWidgetItem, QPushButton, QLineEdit, QLabel,
                               QMessageBox, QHeaderView, QAbstractItemView,
                               QFrame, QDateEdit, QTextEdit, QFormLayout,
                               QDialog, QDialogButtonBox, QSplitter)
from PySide6.QtCore import Qt, Signal, QDate, QTimer
from PySide6.QtGui import QFont, QIcon
from ..services.patient_service import patient_service

logger = logging.getLogger(__name__)


class AddEditPatientDialog(QDialog):
    """Dialog for adding or editing patient information."""
    
    patient_saved = Signal()
    
    def __init__(self, patient_data=None, parent=None):
        super().__init__(parent)
        self.patient_data = patient_data
        self.is_edit_mode = patient_data is not None
        
        self.setWindowTitle("Edit Patient" if self.is_edit_mode else "Add New Patient")
        self.setModal(True)
        self.setFixedSize(500, 400)
        
        # Set dialog background to white with black text
        self.setStyleSheet("""
            QDialog {
                background-color: white;
                color: black;
            }
            QLabel {
                color: black;
            }
        """)
        
        self._setup_ui()
        self._connect_signals()
        
        if self.is_edit_mode:
            self._populate_fields()
    
    def _setup_ui(self):
        """Set up the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 20)
        
        # Title
        title_label = QLabel("Edit Patient Information" if self.is_edit_mode else "Add New Patient")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: black;")
        layout.addWidget(title_label)
        
        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        
        # Style for form labels
        label_style = "color: black; font-weight: bold;"
        
        # Full Name (Required)
        name_label = QLabel("Full Name *:")
        name_label.setStyleSheet(label_style)
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter patient's full name")
        self.name_edit.setStyleSheet(self._get_input_style())
        form_layout.addRow(name_label, self.name_edit)
        
        # Phone Number (Required)
        phone_label = QLabel("Phone Number *:")
        phone_label.setStyleSheet(label_style)
        self.phone_edit = QLineEdit()
        self.phone_edit.setPlaceholderText("Enter phone number")
        self.phone_edit.setStyleSheet(self._get_input_style())
        form_layout.addRow(phone_label, self.phone_edit)
        
        # Date of Birth (Optional)
        dob_label = QLabel("Date of Birth:")
        dob_label.setStyleSheet(label_style)
        self.dob_edit = QDateEdit()
        self.dob_edit.setCalendarPopup(True)
        self.dob_edit.setSpecialValueText("Not specified")  # Show when date is null
        self.dob_edit.setDate(QDate(1900, 1, 1))  # Start with null date for new patients
        self.dob_edit.setStyleSheet(self._get_input_style())
        
        # Add clear button for date of birth
        dob_layout = QHBoxLayout()
        dob_layout.addWidget(self.dob_edit)
        self.clear_dob_button = QPushButton("Clear")
        self.clear_dob_button.setMaximumWidth(60)
        self.clear_dob_button.setStyleSheet("""
            QPushButton {
                background-color: #E74C3C;
                color: white;
                border: none;
                border-radius: 3px;
                font-size: 11px;
                padding: 4px 8px;
            }
            QPushButton:hover {
                background-color: #C0392B;
            }
        """)
        dob_layout.addWidget(self.clear_dob_button)
        form_layout.addRow(dob_label, dob_layout)
        
        # Email (Optional)
        email_label = QLabel("Email:")
        email_label.setStyleSheet(label_style)
        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("Enter email address")
        self.email_edit.setStyleSheet(self._get_input_style())
        form_layout.addRow(email_label, self.email_edit)
        
        # Address (Optional)
        address_label = QLabel("Address:")
        address_label.setStyleSheet(label_style)
        self.address_edit = QTextEdit()
        self.address_edit.setPlaceholderText("Enter address")
        self.address_edit.setMaximumHeight(80)
        self.address_edit.setStyleSheet(self._get_input_style())
        form_layout.addRow(address_label, self.address_edit)
        
        layout.addLayout(form_layout)
        
        # Error label
        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: red; font-size: 12px;")
        self.error_label.setWordWrap(True)
        self.error_label.hide()
        layout.addWidget(self.error_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setMinimumHeight(35)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #95A5A6;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #7F8C8D;
            }
        """)
        button_layout.addWidget(self.cancel_button)
        
        self.save_button = QPushButton("Update Patient" if self.is_edit_mode else "Add Patient")
        self.save_button.setMinimumHeight(35)
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        button_layout.addWidget(self.save_button)
        
        layout.addLayout(button_layout)
        
        # Required fields note
        note_label = QLabel("* Required fields")
        note_label.setStyleSheet("color: #888; font-size: 11px; font-style: italic;")
        layout.addWidget(note_label)
    
    def _get_input_style(self):
        """Get consistent input styling."""
        return """
            QLineEdit, QDateEdit, QTextEdit {
                border: 2px solid #BDC3C7;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
                color: black;
                background-color: white;
            }
            QLineEdit:focus, QDateEdit:focus, QTextEdit:focus {
                border-color: #3498DB;
            }
        """
    
    def _connect_signals(self):
        """Connect dialog signals."""
        self.cancel_button.clicked.connect(self.reject)
        self.save_button.clicked.connect(self._save_patient)
        self.clear_dob_button.clicked.connect(self._clear_date_of_birth)
    
    def _clear_date_of_birth(self):
        """Clear the date of birth field."""
        # Set to a special null date that will be handled as None
        self.dob_edit.setDate(QDate(1900, 1, 1))  # Use a recognizable "null" date
    
    def _populate_fields(self):
        """Populate fields with existing patient data."""
        if not self.patient_data:
            return
        
        self.name_edit.setText(self.patient_data.get('full_name') or '')
        self.phone_edit.setText(self.patient_data.get('phone_number') or '')
        self.email_edit.setText(self.patient_data.get('email') or '')
        self.address_edit.setPlainText(self.patient_data.get('address') or '')
        
        # Date of birth - only set if there's an actual value
        dob = self.patient_data.get('date_of_birth')
        if dob:
            if isinstance(dob, str):
                try:
                    dob = datetime.strptime(dob, '%Y-%m-%d').date()
                except:
                    dob = None
            if isinstance(dob, date):
                self.dob_edit.setDate(QDate(dob.year, dob.month, dob.day))
            else:
                self._clear_date_of_birth()
        else:
            self._clear_date_of_birth()
    
    def _save_patient(self):
        """Save patient data."""
        try:
            # Clear previous errors
            self.error_label.hide()
            
            # Get form data with proper null handling
            email_text = self.email_edit.text() or ""
            email_value = email_text.strip() if email_text else ""
            
            # For date of birth, check if it's the special "null" date or if user actually set a value
            dob_value = None
            current_dob_date = self.dob_edit.date().toPython()
            null_date = date(1900, 1, 1)
            
            if current_dob_date != null_date:
                # User has set a valid date
                dob_value = current_dob_date
            
            patient_data = {
                'full_name': (self.name_edit.text() or "").strip(),
                'phone_number': (self.phone_edit.text() or "").strip(),
                'email': email_value if email_value else "",
                'address': (self.address_edit.toPlainText() or "").strip() or None,
                'date_of_birth': dob_value
            }
            
            # Validate data
            errors = patient_service.validate_patient_data(patient_data)
            if errors:
                error_messages = []
                for field, message in errors.items():
                    error_messages.append(f"• {message}")
                self.error_label.setText("Please fix the following errors:\n" + "\n".join(error_messages))
                self.error_label.show()
                return
            
            # Save patient
            if self.is_edit_mode:
                success = patient_service.update_patient(
                    self.patient_data['patient_id'],
                    patient_data
                )
                action = "updated"
            else:
                result = patient_service.create_patient(patient_data)
                success = result is not None
                action = "created"
            
            if success:
                success_box = QMessageBox(self)
                success_box.setIcon(QMessageBox.Information)
                success_box.setWindowTitle("Success")
                success_box.setText(f"Patient {action} successfully!")
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
                self.patient_saved.emit()
                self.accept()
            else:
                error_box = QMessageBox(self)
                error_box.setIcon(QMessageBox.Critical)
                error_box.setWindowTitle("Error")
                error_box.setText(f"Failed to {action.replace('ed', '')} patient. Please try again.")
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
                
        except Exception as e:
            logger.error(f"Error saving patient: {str(e)}")
            error_box = QMessageBox(self)
            error_box.setIcon(QMessageBox.Critical)
            error_box.setWindowTitle("Error")
            error_box.setText(f"An unexpected error occurred: {str(e)}")
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


class PatientManagement(QWidget):
    """Patient management widget with CRUD operations."""
    
    examine_patient = Signal(dict)  # Signal to open examination for selected patient
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.patients_data = []
        
        self._setup_ui()
        self._connect_signals()
        self._load_patients()
        
        # Set up search timer
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self._perform_search)
    
    def _setup_ui(self):
        """Set up the patient management UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Patient Management")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #2C3E50;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Patient count
        self.count_label = QLabel("0 patients")
        self.count_label.setStyleSheet("color: #7F8C8D; font-size: 14px;")
        header_layout.addWidget(self.count_label)
        
        layout.addLayout(header_layout)
        
        # Search and action bar
        action_layout = QHBoxLayout()
        action_layout.setSpacing(15)
        
        # Search box
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search patients by name, ID, phone, or email...")
        self.search_edit.setMinimumHeight(35)
        self.search_edit.setStyleSheet("""
            QLineEdit {
                border: 2px solid #BDC3C7;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 14px;
                color: black;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #3498DB;
            }
        """)
        action_layout.addWidget(self.search_edit)
        
        # Add patient button
        self.add_button = QPushButton("Add New Patient")
        self.add_button.setMinimumHeight(35)
        self.add_button.setMinimumWidth(150)
        self.add_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        action_layout.addWidget(self.add_button)
        
        layout.addLayout(action_layout)
        
        # Patient table
        self.patients_table = QTableWidget()
        self.patients_table.setColumnCount(6)
        self.patients_table.setHorizontalHeaderLabels([
            "Patient ID", "Full Name", "Phone", "Email", "Created/Updated", "Actions"
        ])
        
        # Table styling
        self.patients_table.setAlternatingRowColors(False)  # Disable alternating colors
        self.patients_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.patients_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.patients_table.verticalHeader().setVisible(False)
        
        # Set row height to accommodate the action buttons
        self.patients_table.verticalHeader().setDefaultSectionSize(40)  # Set default row height
        
        # Set column widths
        header = self.patients_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # Patient ID
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Name
        header.setSectionResizeMode(2, QHeaderView.Fixed)  # Phone
        header.setSectionResizeMode(3, QHeaderView.Stretch)  # Email
        header.setSectionResizeMode(4, QHeaderView.Fixed)  # Created/Updated
        header.setSectionResizeMode(5, QHeaderView.Fixed)  # Actions
        
        self.patients_table.setColumnWidth(0, 100)  # Patient ID
        self.patients_table.setColumnWidth(2, 120)  # Phone
        self.patients_table.setColumnWidth(4, 250)  # Created/Updated
        self.patients_table.setColumnWidth(5, 190)  # Actions (increased for Examine button)
        
        self.patients_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #ECF0F1;
                background-color: white;
                border: 1px solid #BDC3C7;
                border-radius: 4px;
                color: black;
                alternate-background-color: white;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #ECF0F1;
                color: black;
                background-color: white;
            }
            QTableWidget::item:selected {
                background-color: #E3F2FD;
                color: black;
            }
            QTableWidget::item:hover {
                background-color: #F5F5F5;
                color: black;
            }
            QHeaderView::section {
                background-color: #F8F9FA;
                padding: 10px;
                border: none;
                border-bottom: 2px solid #3498DB;
                font-weight: bold;
                color: #2C3E50;
            }
        """)
        
        layout.addWidget(self.patients_table)
    
    def _connect_signals(self):
        """Connect widget signals."""
        self.add_button.clicked.connect(self._add_patient)
        self.search_edit.textChanged.connect(self._on_search_changed)
        self.patients_table.cellDoubleClicked.connect(self._edit_patient)
    
    def _on_search_changed(self):
        """Handle search text changes with debouncing."""
        self.search_timer.stop()
        self.search_timer.start(300)  # 300ms delay
    
    def _perform_search(self):
        """Perform the actual search."""
        search_term = self.search_edit.text().strip()
        self._load_patients(search_term)
    
    def _load_patients(self, search_term: str = ""):
        """Load patients into the table."""
        try:
            # Get patients from service
            self.patients_data = patient_service.search_patients(search_term)

            
            # Update table
            self.patients_table.setRowCount(len(self.patients_data))

            
            for row, patient in enumerate(self.patients_data):
                # Patient ID
                self.patients_table.setItem(row, 0, QTableWidgetItem(patient['patient_id']))
                
                # Full Name
                self.patients_table.setItem(row, 1, QTableWidgetItem(patient['full_name']))
                
                # Phone
                self.patients_table.setItem(row, 2, QTableWidgetItem(patient['phone_number']))
                
                # Email
                email = patient.get('email') or ""
                self.patients_table.setItem(row, 3, QTableWidgetItem(email))
                
                # Created/Updated Date
                created_at = patient.get('created_at')
                updated_at = patient.get('updated_at')
                
                # Determine which date to show and format it
                date_str = ""
                if updated_at and created_at:
                    # If updated_at is different from created_at, show updated date
                    if isinstance(updated_at, str):
                        try:
                            updated_dt = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                            date_str = f"Updated: {updated_dt.strftime('%Y-%m-%d')}"
                        except:
                            date_str = f"Updated: {str(updated_at)[:10]}"
                    elif hasattr(updated_at, 'strftime'):
                        date_str = f"Updated: {updated_at.strftime('%Y-%m-%d')}"
                elif created_at:
                    # Show creation date
                    if isinstance(created_at, str):
                        try:
                            created_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                            date_str = f"Created: {created_dt.strftime('%Y-%m-%d')}"
                        except:
                            date_str = f"Created: {str(created_at)[:10]}"
                    elif hasattr(created_at, 'strftime'):
                        date_str = f"Created: {created_at.strftime('%Y-%m-%d')}"
                
                self.patients_table.setItem(row, 4, QTableWidgetItem(date_str))
                
                # Actions buttons
                actions_widget = self._create_action_buttons(patient)
                self.patients_table.setCellWidget(row, 5, actions_widget)
            
            # Update count label
            count = len(self.patients_data)
            self.count_label.setText(f"{count} patient{'s' if count != 1 else ''}")
            
            logger.info(f"Loaded {count} patients")
            
        except Exception as e:
            logger.error(f"Error loading patients: {str(e)}")
            error_box = QMessageBox(self)
            error_box.setIcon(QMessageBox.Critical)
            error_box.setWindowTitle("Error")
            error_box.setText(f"Failed to load patients: {str(e)}")
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
    
    def _create_action_buttons(self, patient: dict) -> QWidget:
        """Create action buttons for each patient row."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(5)
        
        # Examine button
        examine_btn = QPushButton("Examine")
        examine_btn.setMinimumWidth(60)
        examine_btn.setMinimumHeight(15)  # Reduced from 80 to 30
        examine_btn.setStyleSheet("""
            QPushButton {
                background-color: #9B59B6;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 2px 4px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #8E44AD;
            }
        """)
        examine_btn.clicked.connect(lambda: self._examine_patient(patient))
        layout.addWidget(examine_btn)
        
        # Edit button
        edit_btn = QPushButton("Edit")
        edit_btn.setMaximumWidth(50)
        edit_btn.setMinimumHeight(15)  # Reduced from 80 to 30

        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498DB;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 4px 8px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
        """)
        edit_btn.clicked.connect(lambda: self._edit_patient_by_data(patient))
        layout.addWidget(edit_btn)
        
        # Delete button
        delete_btn = QPushButton("Delete")
        delete_btn.setMaximumWidth(60)
        delete_btn.setMinimumHeight(15)  # Reduced from 80 to 30
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #E74C3C;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 4px 8px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #C0392B;
            }
        """)
        delete_btn.clicked.connect(lambda: self._delete_patient(patient))
        layout.addWidget(delete_btn)
        
        return widget
    
    def _add_patient(self):
        """Open add patient dialog."""
        dialog = AddEditPatientDialog(parent=self)
        dialog.patient_saved.connect(self._load_patients)
        dialog.exec()
    
    def _examine_patient(self, patient: dict):
        """Open examination for selected patient."""
        self.examine_patient.emit(patient)
    
    def _edit_patient(self, row, column):
        """Edit patient from table double-click."""
        if row < len(self.patients_data):
            patient = self.patients_data[row]
            self._edit_patient_by_data(patient)
    
    def _edit_patient_by_data(self, patient: dict):
        """Open edit patient dialog."""
        dialog = AddEditPatientDialog(patient, parent=self)
        dialog.patient_saved.connect(self._load_patients)
        dialog.exec()
    
    def _delete_patient(self, patient: dict):
        """Delete a patient with confirmation."""
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle("Confirm Delete")
        msg_box.setText(f"Are you sure you want to delete patient:\n\n"
                       f"ID: {patient['patient_id']}\n"
                       f"Name: {patient['full_name']}\n\n"
                       f"This action cannot be undone.")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        
        # Set stylesheet to ensure black text on white background
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
            QMessageBox QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """)
        
        reply = msg_box.exec()
        
        if reply == QMessageBox.Yes:
            success = patient_service.delete_patient(patient['patient_id'])
            if success:
                success_box = QMessageBox(self)
                success_box.setIcon(QMessageBox.Information)
                success_box.setWindowTitle("Success")
                success_box.setText("Patient deleted successfully!")
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
                self._load_patients()
            else:
                error_box = QMessageBox(self)
                error_box.setIcon(QMessageBox.Critical)
                error_box.setWindowTitle("Error")
                error_box.setText("Failed to delete patient. Please try again.")
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
