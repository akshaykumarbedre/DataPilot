"""
Enhanced Dental Chart Widget with dual patient/doctor tracking and comprehensive status system.
"""
import logging
from typing import Dict, List, Optional, Any
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, 
    QLabel, QComboBox, QTextEdit, QTabWidget, QFrame, QScrollArea,
    QButtonGroup, QGroupBox, QSplitter, QMessageBox, QDialog,
    QDialogButtonBox, QFormLayout, QLineEdit, QDateEdit, QSpinBox
)
from PySide6.QtCore import Qt, Signal, QDate, QSize
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont, QPalette

from ..services.tooth_history_service import tooth_history_service
from ..services.custom_status_service import custom_status_service
from ..services.dental_examination_service import dental_examination_service

logger = logging.getLogger(__name__)


class ToothButton(QPushButton):
    """Custom tooth button with enhanced visual representation."""
    
    tooth_clicked = Signal(int, str)  # tooth_number, click_type (left/right)
    
    def __init__(self, tooth_number: int, parent=None):
        super().__init__(parent)
        self.tooth_number = tooth_number
        self.patient_status = 'normal'
        self.doctor_status = 'normal'
        self.current_mode = 'doctor'  # 'patient' or 'doctor'
        
        # Tooth display formatting
        quadrant = tooth_number // 10
        position = tooth_number % 10
        self.setText(f"({quadrant},{position})")
        
        self.setFixedSize(60, 45)
        self.setFont(QFont("Arial", 8, QFont.Bold))
        self.update_appearance()
        
        # Enable context menu for right-click
        self.setContextMenuPolicy(Qt.CustomContextMenu)
    
    def set_patient_status(self, status: str):
        """Set patient-reported status."""
        self.patient_status = status
        self.update_appearance()
    
    def set_doctor_status(self, status: str):
        """Set doctor-diagnosed status."""
        self.doctor_status = status
        self.update_appearance()
    
    def set_mode(self, mode: str):
        """Set display mode (patient or doctor)."""
        self.current_mode = mode
        self.update_appearance()
    
    def get_status_color(self, status: str) -> str:
        """Get color for dental status."""
        # Get color from custom status service
        custom_status = custom_status_service.get_custom_status_by_name(status)
        if custom_status:
            return custom_status['color']
        
        # Fallback color mapping
        color_map = {
            'normal': '#00FF00',
            'healthy': '#32CD32',
            'initial_caries': '#FFD700',
            'moderate_caries': '#FF8C00',
            'deep_caries': '#FF4500',
            'extensive_caries': '#DC143C',
            'amalgam_filling': '#708090',
            'composite_filling': '#F5F5DC',
            'porcelain_crown': '#E6E6FA',
            'root_canal_treatment': '#FF69B4',
            'extracted': '#000000',
            'missing': '#2F2F2F',
            'implant': '#4169E1',
            'treatment_planned': '#00CED1'
        }
        return color_map.get(status, '#808080')
    
    def update_appearance(self):
        """Update button appearance based on current status and mode."""
        if self.current_mode == 'doctor':
            primary_color = self.get_status_color(self.doctor_status)
            secondary_color = self.get_status_color(self.patient_status)
        else:
            primary_color = self.get_status_color(self.patient_status)
            secondary_color = self.get_status_color(self.doctor_status)
        
        # Create gradient style for dual status indication
        if self.patient_status != 'normal' and self.doctor_status != 'normal' and self.patient_status != self.doctor_status:
            # Split background to show both statuses
            self.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 {primary_color}, stop:0.5 {primary_color},
                        stop:0.5 {secondary_color}, stop:1 {secondary_color});
                    border: 2px solid #19c5e5;
                    border-radius: 8px;
                    color: white;
                    font-weight: bold;
                    text-shadow: 1px 1px 2px rgba(0,0,0,0.7);
                }}
                QPushButton:hover {{
                    border: 3px solid #0ea5c7;
                    transform: scale(1.05);
                }}
                QPushButton:pressed {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 {self.adjust_color(primary_color, -30)}, 
                        stop:0.5 {self.adjust_color(primary_color, -30)},
                        stop:0.5 {self.adjust_color(secondary_color, -30)}, 
                        stop:1 {self.adjust_color(secondary_color, -30)});
                }}
            """)
        else:
            # Single status
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {primary_color};
                    border: 2px solid #19c5e5;
                    border-radius: 8px;
                    color: white;
                    font-weight: bold;
                    text-shadow: 1px 1px 2px rgba(0,0,0,0.7);
                }}
                QPushButton:hover {{
                    border: 3px solid #0ea5c7;
                    background-color: {self.adjust_color(primary_color, 20)};
                }}
                QPushButton:pressed {{
                    background-color: {self.adjust_color(primary_color, -30)};
                }}
            """)
    
    def adjust_color(self, hex_color: str, adjustment: int) -> str:
        """Adjust color brightness."""
        try:
            color = QColor(hex_color)
            h, s, v, a = color.getHsv()
            v = max(0, min(255, v + adjustment))
            color.setHsv(h, s, v, a)
            return color.name()
        except:
            return hex_color
    
    def mousePressEvent(self, event):
        """Handle mouse press events."""
        if event.button() == Qt.LeftButton:
            self.tooth_clicked.emit(self.tooth_number, 'left')
        elif event.button() == Qt.RightButton:
            self.tooth_clicked.emit(self.tooth_number, 'right')
        super().mousePressEvent(event)


class StatusPalette(QWidget):
    """Widget for displaying and selecting dental statuses."""
    
    status_selected = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_statuses()
    
    def setup_ui(self):
        """Setup the status palette UI."""
        layout = QVBoxLayout(self)
        
        # Status category tabs
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Search box
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search dental statuses...")
        self.search_edit.textChanged.connect(self.filter_statuses)
        layout.addWidget(self.search_edit)
    
    def load_statuses(self):
        """Load dental statuses grouped by category."""
        try:
            # Get all custom statuses (includes predefined ones)
            all_statuses = custom_status_service.get_all_custom_statuses(is_active=True)
            
            # Group by category
            categories = {}
            for status in all_statuses:
                category = status['category']
                if category not in categories:
                    categories[category] = []
                categories[category].append(status)
            
            # Create tabs for each category
            for category, statuses in categories.items():
                self.create_category_tab(category.title(), statuses)
        
        except Exception as e:
            logger.error(f"Error loading statuses: {str(e)}")
            # Create a default tab with basic statuses
            self.create_default_tab()
    
    def create_category_tab(self, category_name: str, statuses: List[Dict]):
        """Create a tab for a status category."""
        tab = QWidget()
        layout = QGridLayout(tab)
        
        row, col = 0, 0
        max_cols = 3
        
        for status in sorted(statuses, key=lambda x: x['display_name']):
            btn = QPushButton(status['display_name'])
            btn.setFixedSize(120, 35)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {status['color']};
                    border: 1px solid #19c5e5;
                    border-radius: 5px;
                    color: white;
                    font-weight: bold;
                    text-shadow: 1px 1px 1px rgba(0,0,0,0.5);
                }}
                QPushButton:hover {{
                    border: 2px solid #0ea5c7;
                }}
            """)
            btn.clicked.connect(lambda checked, s=status['status_name']: self.status_selected.emit(s))
            
            layout.addWidget(btn, row, col)
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        # Add stretch to push buttons to top
        layout.setRowStretch(row + 1, 1)
        
        self.tab_widget.addTab(tab, category_name)
    
    def create_default_tab(self):
        """Create default tab with basic statuses."""
        basic_statuses = [
            {'status_name': 'normal', 'display_name': 'Normal', 'color': '#00FF00'},
            {'status_name': 'initial_caries', 'display_name': 'Initial Caries', 'color': '#FFD700'},
            {'status_name': 'deep_caries', 'display_name': 'Deep Caries', 'color': '#FF4500'},
            {'status_name': 'amalgam_filling', 'display_name': 'Amalgam Filling', 'color': '#708090'},
            {'status_name': 'composite_filling', 'display_name': 'Composite Filling', 'color': '#F5F5DC'},
            {'status_name': 'root_canal_treatment', 'display_name': 'Root Canal', 'color': '#FF69B4'},
            {'status_name': 'extracted', 'display_name': 'Extracted', 'color': '#000000'},
            {'status_name': 'implant', 'display_name': 'Implant', 'color': '#4169E1'}
        ]
        self.create_category_tab('Basic', basic_statuses)
    
    def filter_statuses(self, text: str):
        """Filter statuses based on search text."""
        # Implementation for filtering statuses in real-time
        pass


class ToothDetailsDialog(QDialog):
    """Dialog for viewing and editing tooth details."""
    
    def __init__(self, tooth_number: int, patient_id: int, parent=None):
        super().__init__(parent)
        self.tooth_number = tooth_number
        self.patient_id = patient_id
        self.setup_ui()
        self.load_tooth_data()
    
    def setup_ui(self):
        """Setup the dialog UI."""
        self.setWindowTitle(f"Tooth {self.tooth_number} Details")
        self.setModal(True)
        self.resize(600, 500)
        
        layout = QVBoxLayout(self)
        
        # Tooth info header
        quadrant = self.tooth_number // 10
        position = self.tooth_number % 10
        header = QLabel(f"Tooth {self.tooth_number} ({quadrant},{position})")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        header.setStyleSheet("color: #2C3E50; margin: 10px;")
        layout.addWidget(header)
        
        # Tab widget for different views
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Current Status tab
        self.create_current_status_tab()
        
        # History tab
        self.create_history_tab()
        
        # Add New Record tab
        self.create_add_record_tab()
        
        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def create_current_status_tab(self):
        """Create current status display tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Current status display
        self.current_status_label = QLabel()
        self.current_status_label.setFont(QFont("Arial", 12))
        layout.addWidget(self.current_status_label)
        
        self.tab_widget.addTab(tab, "Current Status")
    
    def create_history_tab(self):
        """Create history display tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # History list
        self.history_area = QScrollArea()
        self.history_widget = QWidget()
        self.history_layout = QVBoxLayout(self.history_widget)
        self.history_area.setWidget(self.history_widget)
        self.history_area.setWidgetResizable(True)
        layout.addWidget(self.history_area)
        
        self.tab_widget.addTab(tab, "History")
    
    def create_add_record_tab(self):
        """Create add new record tab."""
        tab = QWidget()
        layout = QFormLayout(tab)
        
        # Record type
        self.record_type_combo = QComboBox()
        self.record_type_combo.addItems(['Patient Problem', 'Doctor Finding'])
        layout.addRow("Record Type:", self.record_type_combo)
        
        # Status selection
        self.status_combo = QComboBox()
        self.populate_status_combo()
        layout.addRow("Status:", self.status_combo)
        
        # Description
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(100)
        layout.addRow("Description:", self.description_edit)
        
        # Date
        self.date_edit = QDateEdit(QDate.currentDate())
        layout.addRow("Date:", self.date_edit)
        
        # Add record button
        self.add_button = QPushButton("Add Record")
        self.add_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.add_button.clicked.connect(self.add_record)
        layout.addRow(self.add_button)
        
        self.tab_widget.addTab(tab, "Add Record")
    
    def populate_status_combo(self):
        """Populate status combo box."""
        try:
            statuses = custom_status_service.get_all_custom_statuses(is_active=True)
            for status in sorted(statuses, key=lambda x: x['display_name']):
                self.status_combo.addItem(status['display_name'], status['status_name'])
        except Exception as e:
            logger.error(f"Error populating status combo: {str(e)}")
    
    def load_tooth_data(self):
        """Load tooth data from database."""
        try:
            # Get current status
            current_status = tooth_history_service.get_tooth_current_status(
                self.patient_id, self.tooth_number
            )
            
            # Update current status display
            status_text = f"""
            <h3>Current Status: {current_status['current_status'].title()}</h3>
            <p><b>Patient Problems:</b> {current_status['patient_problems_count']}</p>
            <p><b>Doctor Findings:</b> {current_status['doctor_findings_count']}</p>
            """
            
            if current_status['latest_patient_problem']:
                latest_patient = current_status['latest_patient_problem']
                status_text += f"""
                <h4>Latest Patient Problem:</h4>
                <p>Status: {latest_patient['status']}</p>
                <p>Date: {latest_patient['date_recorded']}</p>
                <p>Description: {latest_patient['description']}</p>
                """
            
            if current_status['latest_doctor_finding']:
                latest_doctor = current_status['latest_doctor_finding']
                status_text += f"""
                <h4>Latest Doctor Finding:</h4>
                <p>Status: {latest_doctor['status']}</p>
                <p>Date: {latest_doctor['date_recorded']}</p>
                <p>Description: {latest_doctor['description']}</p>
                """
            
            self.current_status_label.setText(status_text)
            
            # Load history
            self.load_history()
            
        except Exception as e:
            logger.error(f"Error loading tooth data: {str(e)}")
            self.current_status_label.setText("Error loading tooth data")
    
    def load_history(self):
        """Load tooth history."""
        try:
            history = tooth_history_service.get_tooth_history(
                self.patient_id, self.tooth_number
            )
            
            # Clear existing history
            for i in reversed(range(self.history_layout.count())):
                self.history_layout.itemAt(i).widget().setParent(None)
            
            # Add history records
            for record in history:
                record_widget = self.create_history_record_widget(record)
                self.history_layout.addWidget(record_widget)
            
            # Add stretch
            self.history_layout.addStretch()
            
        except Exception as e:
            logger.error(f"Error loading history: {str(e)}")
    
    def create_history_record_widget(self, record: Dict) -> QWidget:
        """Create widget for a history record."""
        widget = QFrame()
        widget.setFrameStyle(QFrame.Box)
        widget.setStyleSheet("QFrame { border: 1px solid #BDC3C7; margin: 2px; padding: 5px; }")
        
        layout = QVBoxLayout(widget)
        
        # Header
        header = QLabel(f"{record['record_type'].replace('_', ' ').title()} - {record['status']}")
        header.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(header)
        
        # Date
        date_label = QLabel(f"Date: {record['date_recorded']}")
        layout.addWidget(date_label)
        
        # Description
        if record['description']:
            desc_label = QLabel(f"Description: {record['description']}")
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)
        
        return widget
    
    def add_record(self):
        """Add new tooth record."""
        try:
            record_type = 'patient_problem' if self.record_type_combo.currentText() == 'Patient Problem' else 'doctor_finding'
            status = self.status_combo.currentData()
            description = self.description_edit.toPlainText()
            date_recorded = self.date_edit.date().toPython()
            
            success = tooth_history_service.update_tooth_status(
                self.patient_id,
                self.tooth_number,
                status,
                record_type,
                description
            )
            
            if success:
                QMessageBox.information(self, "Success", "Record added successfully!")
                self.load_tooth_data()  # Refresh data
                # Clear form
                self.description_edit.clear()
                self.status_combo.setCurrentIndex(0)
            else:
                QMessageBox.warning(self, "Error", "Failed to add record.")
                
        except Exception as e:
            logger.error(f"Error adding record: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error adding record: {str(e)}")


class DentalChartWidget(QWidget):
    """Main dental chart widget with dual patient/doctor tracking."""
    
    tooth_selected = Signal(int)
    chart_updated = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.patient_id = None
        self.current_examination_id = None
        self.current_mode = 'doctor'  # 'patient' or 'doctor'
        self.tooth_buttons = {}
        
        self.setup_ui()
        self.load_initial_data()
    
    def setup_ui(self):
        """Setup the dental chart UI."""
        layout = QVBoxLayout(self)
        
        # Mode selection and controls
        controls_layout = QHBoxLayout()
        
        # Mode selection
        mode_group = QGroupBox("Chart Mode")
        mode_layout = QHBoxLayout(mode_group)
        
        self.mode_button_group = QButtonGroup()
        self.doctor_mode_btn = QPushButton("Doctor Findings")
        self.patient_mode_btn = QPushButton("Patient Problems")
        
        self.doctor_mode_btn.setCheckable(True)
        self.patient_mode_btn.setCheckable(True)
        self.doctor_mode_btn.setChecked(True)
        
        self.mode_button_group.addButton(self.doctor_mode_btn, 0)
        self.mode_button_group.addButton(self.patient_mode_btn, 1)
        self.mode_button_group.buttonClicked.connect(self.on_mode_changed)
        
        mode_layout.addWidget(self.doctor_mode_btn)
        mode_layout.addWidget(self.patient_mode_btn)
        controls_layout.addWidget(mode_group)
        
        # Patient info
        self.patient_info_label = QLabel("No patient selected")
        self.patient_info_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.patient_info_label.setStyleSheet("color: #19c5e5; margin: 10px;")
        controls_layout.addWidget(self.patient_info_label)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Main splitter
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # Dental chart area
        chart_area = self.create_dental_chart()
        splitter.addWidget(chart_area)
        
        # Status palette
        self.status_palette = StatusPalette()
        self.status_palette.status_selected.connect(self.apply_status_to_selected)
        splitter.addWidget(self.status_palette)
        
        # Set splitter sizes (chart larger than palette)
        splitter.setSizes([700, 300])
        
        # Style mode buttons
        self.style_mode_buttons()
    
    def style_mode_buttons(self):
        """Apply styling to mode buttons."""
        button_style = """
            QPushButton {
                background-color: #f0f0f0;
                border: 2px solid #19c5e5;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:checked {
                background-color: #19c5e5;
                color: white;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:checked:hover {
                background-color: #0ea5c7;
            }
        """
        self.doctor_mode_btn.setStyleSheet(button_style)
        self.patient_mode_btn.setStyleSheet(button_style)
    
    def create_dental_chart(self) -> QWidget:
        """Create the dental chart layout."""
        chart_widget = QWidget()
        layout = QVBoxLayout(chart_widget)
        
        # Title
        title = QLabel("Dental Chart")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #19c5e5; margin: 10px;")
        layout.addWidget(title)
        
        # Upper teeth
        upper_group = QGroupBox("Upper Teeth")
        upper_layout = QGridLayout(upper_group)
        
        # Upper right: 18-11 (reversed for visual layout)
        for i, tooth_num in enumerate(range(18, 10, -1)):
            btn = ToothButton(tooth_num)
            btn.tooth_clicked.connect(self.on_tooth_clicked)
            self.tooth_buttons[tooth_num] = btn
            upper_layout.addWidget(btn, 0, i)
        
        # Upper left: 21-28
        for i, tooth_num in enumerate(range(21, 29)):
            btn = ToothButton(tooth_num)
            btn.tooth_clicked.connect(self.on_tooth_clicked)
            self.tooth_buttons[tooth_num] = btn
            upper_layout.addWidget(btn, 0, 8 + i)
        
        layout.addWidget(upper_group)
        
        # Add some spacing
        layout.addSpacing(20)
        
        # Lower teeth
        lower_group = QGroupBox("Lower Teeth")
        lower_layout = QGridLayout(lower_group)
        
        # Lower right: 48-41 (reversed for visual layout)
        for i, tooth_num in enumerate(range(48, 40, -1)):
            btn = ToothButton(tooth_num)
            btn.tooth_clicked.connect(self.on_tooth_clicked)
            self.tooth_buttons[tooth_num] = btn
            lower_layout.addWidget(btn, 0, i)
        
        # Lower left: 31-38
        for i, tooth_num in enumerate(range(31, 39)):
            btn = ToothButton(tooth_num)
            btn.tooth_clicked.connect(self.on_tooth_clicked)
            self.tooth_buttons[tooth_num] = btn
            lower_layout.addWidget(btn, 0, 8 + i)
        
        layout.addWidget(lower_group)
        
        return chart_widget
    
    def load_initial_data(self):
        """Load initial data and setup."""
        try:
            # Initialize predefined statuses if needed
            custom_status_service.initialize_predefined_statuses()
        except Exception as e:
            logger.error(f"Error loading initial data: {str(e)}")
    
    def set_patient(self, patient_id: int, patient_name: str = ""):
        """Set the current patient."""
        self.patient_id = patient_id
        self.patient_info_label.setText(f"Patient: {patient_name}" if patient_name else f"Patient ID: {patient_id}")
        self.load_patient_chart()
    
    def set_examination(self, examination_id: int):
        """Set the current examination."""
        self.current_examination_id = examination_id
        self.load_patient_chart()
    
    def load_patient_chart(self):
        """Load patient's dental chart data."""
        if not self.patient_id:
            return
        
        try:
            # Get patient tooth summary
            tooth_summary = tooth_history_service.get_patient_tooth_summary(
                self.patient_id, self.current_examination_id
            )
            
            # Update tooth buttons
            for tooth_number, tooth_btn in self.tooth_buttons.items():
                if tooth_number in tooth_summary:
                    summary = tooth_summary[tooth_number]
                    
                    # Set patient and doctor statuses
                    patient_status = 'normal'
                    doctor_status = 'normal'
                    
                    if summary['latest_patient_problem']:
                        patient_status = summary['latest_patient_problem']['status']
                    
                    if summary['latest_doctor_finding']:
                        doctor_status = summary['latest_doctor_finding']['status']
                    
                    tooth_btn.set_patient_status(patient_status)
                    tooth_btn.set_doctor_status(doctor_status)
                    tooth_btn.set_mode(self.current_mode)
                else:
                    # Reset to normal if no data
                    tooth_btn.set_patient_status('normal')
                    tooth_btn.set_doctor_status('normal')
                    tooth_btn.set_mode(self.current_mode)
        
        except Exception as e:
            logger.error(f"Error loading patient chart: {str(e)}")
    
    def on_mode_changed(self, button):
        """Handle mode change."""
        if button == self.doctor_mode_btn:
            self.current_mode = 'doctor'
        else:
            self.current_mode = 'patient'
        
        # Update all tooth buttons to show new mode
        for tooth_btn in self.tooth_buttons.values():
            tooth_btn.set_mode(self.current_mode)
    
    def on_tooth_clicked(self, tooth_number: int, click_type: str):
        """Handle tooth button clicks."""
        if not self.patient_id:
            QMessageBox.warning(self, "No Patient", "Please select a patient first.")
            return
        
        if click_type == 'left':
            # Single click - select tooth
            self.tooth_selected.emit(tooth_number)
        elif click_type == 'right':
            # Right click - show tooth details
            self.show_tooth_details(tooth_number)
    
    def show_tooth_details(self, tooth_number: int):
        """Show detailed tooth information."""
        dialog = ToothDetailsDialog(tooth_number, self.patient_id, self)
        dialog.exec()
        # Refresh chart after dialog closes
        self.load_patient_chart()
    
    def apply_status_to_selected(self, status: str):
        """Apply selected status to the currently selected tooth."""
        # This would be implemented based on how tooth selection is handled
        # For now, show a message
        QMessageBox.information(
            self, 
            "Status Selected", 
            f"Status '{status}' selected. Click on a tooth to apply."
        )
    
    def refresh_chart(self):
        """Refresh the dental chart display."""
        self.load_patient_chart()
        self.chart_updated.emit()
