"""
Advanced Dental Chart System - Phase 3 Implementation
Integrates all Phase 2 components into a comprehensive dental practice interface.
"""
import logging
from datetime import date, datetime
from typing import Optional, Dict, Any, List
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, 
    QPushButton, QComboBox, QMessageBox, QSizePolicy,
    QGroupBox, QFormLayout, QScrollArea, QTextEdit
)
from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import QFont

# Import Phase 2 components
from .components import (
    EnhancedToothWidget,
    DentalChartPanel, 
    CustomStatusDialog,
    VisitEntryPanel,
    DentalExaminationPanel,
    VisitRecordsPanel,  # Re-enabled for displaying old visits
    # COMMENTED OUT FOR SIMPLIFICATION
    # TreatmentEpisodesPanel
)

# Import Phase 1 services
from ..services.dental_examination_service import dental_examination_service
from ..services.tooth_history_service import tooth_history_service
# COMMENTED OUT FOR SIMPLIFICATION
# from ..services.visit_records_service import visit_records_service
from ..services.custom_status_service import custom_status_service
from ..services.patient_service import patient_service

logger = logging.getLogger(__name__)


class AdvancedDentalChart(QWidget):
    """Advanced dental chart with dual tracking and examination management."""
    
    # Signals for component communication
    patient_changed = Signal(int)           # Patient ID
    examination_changed = Signal(int)       # Examination ID  
    tooth_selected = Signal(int, str)       # Tooth number, chart type
    visit_added = Signal(dict)              # Visit data
    data_saved = Signal()                   # Save confirmation
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Core attributes
        self.current_patient_id = None
        self.current_examination_id = None
        self.selected_tooth_number = None
        self.selected_chart_type = None  # 'patient' or 'doctor'
        
        # Component references
        self.examination_panel = None
        self.patient_chart_panel = None
        self.doctor_chart_panel = None
        self.visit_entry_panel = None
        self.visit_records_panel = None  # Re-enabled for displaying old visits
        # COMMENTED OUT FOR SIMPLIFICATION
        # self.treatment_episodes_panel = None
        
        # UI setup
        self.setup_ui()
        self.connect_signals()
        self.load_initial_data()
    
    def setup_ui(self):
        """Setup the complete UI with all components."""
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(3, 3, 3, 3)  # Reduced margins
        main_layout.setSpacing(5)  # Reduced spacing
        
        # === HEADER SECTION ===
        header_widget = self.create_header_section()
        main_layout.addWidget(header_widget)
        
        # === MAIN CONTENT - VERTICAL LAYOUT ===
        # Left panel (Charts & Examination) - now main content
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel)
        
        # Right panel (Records & Episodes) - COMMENTED OUT FOR SIMPLIFICATION
        # right_panel = self.create_right_panel()
        # main_layout.addWidget(right_panel)
        
        # === STATUS BAR ===
        status_bar = self.create_status_bar()
        main_layout.addWidget(status_bar)
        
        # Apply global styling
        self.apply_global_styles()
    
    def create_header_section(self) -> QWidget:
        """Create header with patient selection and quick actions."""
        header_widget = QFrame()
        header_widget.setFixedHeight(60)  # Slightly reduced
        header_widget.setStyleSheet("""
            QFrame {
                background-color: #2C3E50;
                border-radius: 4px;
                padding: 6px;
            }
        """)
        
        header_layout = QHBoxLayout(header_widget)
        header_layout.setSpacing(10)
        header_layout.setContentsMargins(8, 8, 8, 8)
        
        # Title
        title_label = QLabel("Advanced Dental Chart System")
        title_label.setStyleSheet("""
            color: white;
            font-size: 16px;
            font-weight: bold;
        """)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Patient selector
        patient_label = QLabel("Patient:")
        patient_label.setStyleSheet("color: white; font-weight: bold;")
        header_layout.addWidget(patient_label)
        
        self.patient_combo = QComboBox()
        self.patient_combo.setMinimumWidth(230)
        self.patient_combo.setStyleSheet("""
            QComboBox {
                background-color: white;
                border: 1px solid #BDC3C7;
                border-radius: 4px;
                padding: 6px;
                font-size: 12px;
                color: #2C3E50;
            }
            QComboBox:focus {
                border-color: #3498DB;
            }
        """)
        header_layout.addWidget(self.patient_combo)
        
        # Current examination display
        self.current_exam_label = QLabel("No examination selected")
        self.current_exam_label.setStyleSheet("""
            color: white;
            font-weight: bold;
            background-color: rgba(255, 255, 255, 0.15);
            padding: 6px 8px;
            border-radius: 4px;
            font-size: 11px;
        """)
        header_layout.addWidget(self.current_exam_label)
        
        # Quick action buttons
        self.new_exam_btn = QPushButton("New Exam")
        self.save_all_btn = QPushButton("Save All")
        self.export_btn = QPushButton("Export")
        
        for btn in [self.new_exam_btn, self.save_all_btn, self.export_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: white;
                    color: #2C3E50;
                    border: none;
                    border-radius: 4px;
                    padding: 6px 12px;
                    font-weight: bold;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #ECF0F1;
                }
            """)
            header_layout.addWidget(btn)
        
        return header_widget
    
    def create_left_panel(self) -> QWidget:
        """Create left panel with examination and charts."""
        # Main scroll area for the entire left panel
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Content widget inside scroll area
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(3, 3, 3, 3)  # Reduced margins
        left_layout.setSpacing(5)  # Reduced spacing
        
        # Examination Management Panel
        self.examination_panel = DentalExaminationPanel()
        left_layout.addWidget(self.examination_panel)
        
        # Dual Chart Container
        charts_container = self.create_dual_charts()
        left_layout.addWidget(charts_container)
        
        # Visit Entry Panel
        self.visit_entry_panel = VisitEntryPanel()
        left_layout.addWidget(self.visit_entry_panel)
        
        # Visit Records Panel - Display old visits
        self.visit_records_panel = VisitRecordsPanel()
        self.visit_records_panel.setMinimumHeight(300)  # Set minimum height for visit history
        left_layout.addWidget(self.visit_records_panel)
        
        # Set the content widget in the scroll area
        scroll_area.setWidget(left_widget)
        
        return scroll_area
    
    def create_dual_charts(self) -> QWidget:
        """Create dual dental charts (Patient/Doctor) side by side."""
        charts_widget = QFrame()
        charts_widget.setStyleSheet("""
            QFrame {
                border: 1px solid #BDC3C7;
                border-radius: 4px;
                background-color: white;
            }
        """)
        charts_widget.setMinimumHeight(580)  # Slightly adjusted
        
        # Use HORIZONTAL layout for side-by-side charts
        charts_layout = QHBoxLayout(charts_widget)
        charts_layout.setContentsMargins(3, 3, 3, 3)
        charts_layout.setSpacing(5)
        
        # Patient Problems Chart (Left)
        self.patient_chart_panel = DentalChartPanel(
            panel_type="patient"
        )
        # Ensure proper size policies for responsive design
        self.patient_chart_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        charts_layout.addWidget(self.patient_chart_panel, 1)  # Equal stretch
        
        # Separator line (vertical) for side-by-side layout
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Plain)
        separator.setStyleSheet("color: #BDC3C7; background-color: #BDC3C7; max-width: 1px;")
        charts_layout.addWidget(separator, 0)  # No stretch
        
        # Doctor Findings Chart (Right)
        self.doctor_chart_panel = DentalChartPanel(
            panel_type="doctor"
        )
        # Ensure proper size policies for responsive design
        self.doctor_chart_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        charts_layout.addWidget(self.doctor_chart_panel, 1)  # Equal stretch
        
        return charts_widget

    # def create_right_panel(self) -> QWidget:
    #     """Create right panel with records and episodes - COMMENTED OUT FOR SIMPLIFICATION."""
    #     right_widget = QWidget()
    #     right_layout = QVBoxLayout(right_widget)
    #     right_layout.setContentsMargins(0, 0, 0, 0)
    #     right_layout.setSpacing(10)
    #     
    #     # Visit Records Panel (Top 50%)
    #     self.visit_records_panel = VisitRecordsPanel()
    #     right_layout.addWidget(self.visit_records_panel)
    #     
    #     # Treatment Episodes Panel (Bottom 50%)
    #     self.treatment_episodes_panel = TreatmentEpisodesPanel()
    #     right_layout.addWidget(self.treatment_episodes_panel)
    #     
    #     return right_widget
    
    def create_status_bar(self) -> QWidget:
        """Create status bar with current info."""
        status_widget = QFrame()
        status_widget.setFixedHeight(24)  # Slightly reduced
        status_widget.setStyleSheet("""
            QFrame {
                background-color: #ECF0F1;
                border-top: 1px solid #BDC3C7;
            }
        """)
        
        status_layout = QHBoxLayout(status_widget)
        status_layout.setContentsMargins(8, 4, 8, 4)
        
        # Status labels
        self.exam_status_label = QLabel("Ready")
        self.total_amount_label = QLabel("Total: $0.00") 
        self.last_saved_label = QLabel("Never saved")
        
        for label in [self.exam_status_label, self.total_amount_label, self.last_saved_label]:
            label.setStyleSheet("color: #7F8C8D; font-size: 11px;")
        
        status_layout.addWidget(self.exam_status_label)
        status_layout.addStretch()
        status_layout.addWidget(self.total_amount_label)
        status_layout.addStretch()
        status_layout.addWidget(self.last_saved_label)
        
        return status_widget
    
    def connect_signals(self):
        """Connect all component signals for data flow."""
        
        # === PATIENT SELECTION ===
        self.patient_combo.currentTextChanged.connect(self.on_patient_selected)
        
        # === EXAMINATION MANAGEMENT ===
        if self.examination_panel:
            self.examination_panel.examination_saved.connect(self.on_examination_saved)
            self.examination_panel.examination_selected.connect(self.on_examination_selected)
        
        # === DENTAL CHARTS ===
        if self.patient_chart_panel:
            self.patient_chart_panel.tooth_selected.connect(
                lambda tooth_num, panel_type="patient": self.on_tooth_selected(tooth_num, panel_type)
            )
            self.patient_chart_panel.tooth_status_changed.connect(self.on_tooth_status_changed)
        
        if self.doctor_chart_panel:
            self.doctor_chart_panel.tooth_selected.connect(
                lambda tooth_num, panel_type="doctor": self.on_tooth_selected(tooth_num, panel_type)
            )
            self.doctor_chart_panel.tooth_status_changed.connect(self.on_tooth_status_changed)
        
        # === VISIT MANAGEMENT ===
        if self.visit_entry_panel:
            self.visit_entry_panel.visit_added.connect(self.on_visit_added)
        
        # === VISIT RECORDS PANEL - Re-enabled for displaying old visits ===
        if self.visit_records_panel:
            self.visit_records_panel.visit_selected.connect(self.on_visit_selected)
            self.visit_records_panel.total_amount_changed.connect(self.update_total_amount)
        
        # === TREATMENT EPISODES - COMMENTED OUT FOR SIMPLIFICATION ===
        # if self.treatment_episodes_panel:
        #     self.treatment_episodes_panel.episode_saved.connect(self.on_episode_saved)
        #     self.treatment_episodes_panel.episode_selected.connect(self.on_episode_selected)
        
        # === HEADER ACTIONS ===
        self.new_exam_btn.clicked.connect(self.create_new_examination)
        self.save_all_btn.clicked.connect(self.save_all_changes)
        self.export_btn.clicked.connect(self.export_data)
    
    # === EVENT HANDLERS ===
    def on_patient_selected(self):
        """Handle patient selection change."""
        current_data = self.patient_combo.currentData()
        if current_data and current_data.get('id'):
            self.current_patient_id = current_data['id']
            
            # Update all components with new patient
            if self.examination_panel:
                self.examination_panel.set_patient(self.current_patient_id)
            if self.patient_chart_panel:
                self.patient_chart_panel.set_patient(self.current_patient_id)
            if self.doctor_chart_panel:
                self.doctor_chart_panel.set_patient(self.current_patient_id)
            # Re-enabled for displaying old visits
            if self.visit_records_panel:
                self.visit_records_panel.set_patient(self.current_patient_id)
            # Update visit entry panel with patient
            if self.visit_entry_panel:
                self.visit_entry_panel.set_patient(self.current_patient_id)
            # COMMENTED OUT FOR SIMPLIFICATION
            # if self.treatment_episodes_panel:
            #     self.treatment_episodes_panel.set_patient(self.current_patient_id)
            
            # Clear chart selections
            self.clear_tooth_selections()
            
            # Load latest examination
            self.load_latest_examination()
            
            # Emit signal
            self.patient_changed.emit(self.current_patient_id)
            
            # Update status
            self.exam_status_label.setText(f"Patient #{self.current_patient_id} loaded")
        else:
            self.current_patient_id = None
            self.clear_all_data()
    
    def on_examination_selected(self, examination_data):
        """Handle examination selection."""
        self.current_examination_id = examination_data.get('id')
        
        if self.current_examination_id:
            # Update UI components with examination context
            # Re-enabled for displaying old visits
            if self.visit_records_panel:
                self.visit_records_panel.set_examination(self.current_examination_id)
            # Update visit entry panel with examination
            if self.visit_entry_panel:
                self.visit_entry_panel.set_examination(self.current_examination_id)
            # COMMENTED OUT FOR SIMPLIFICATION
            # if self.treatment_episodes_panel:
            #     self.treatment_episodes_panel.set_examination(self.current_examination_id)
            
            # Load dental chart data for this examination
            self.load_examination_dental_data()
            
            # Update current examination display
            exam_date = examination_data.get('examination_date', '')
            chief_complaint = examination_data.get('chief_complaint', '')[:30]
            self.current_exam_label.setText(f"Exam #{self.current_examination_id} - {exam_date} - {chief_complaint}...")
            
            # Emit signal
            self.examination_changed.emit(self.current_examination_id)
    
    def on_examination_saved(self, examination_data):
        """Handle examination save."""
        self.current_examination_id = examination_data.get('id')
        if self.current_examination_id:
            self.on_examination_selected(examination_data)
        
        # Update status
        self.exam_status_label.setText("Examination saved successfully")
        self.update_last_saved()
    
    def on_tooth_selected(self, tooth_number, chart_type):
        """Handle tooth selection from either chart."""
        self.selected_tooth_number = tooth_number
        self.selected_chart_type = chart_type
        
        # Clear selection from the other chart
        if chart_type == "patient" and self.doctor_chart_panel:
            self.doctor_chart_panel.clear_selection()
        elif chart_type == "doctor" and self.patient_chart_panel:
            self.patient_chart_panel.clear_selection()
        
        # Load tooth history for selected tooth and chart type
        self.load_tooth_history(tooth_number, chart_type)
        
        # Update visit entry panel with selected tooth
        if self.visit_entry_panel:
            # Use set_affected_teeth instead of set_selected_tooth
            self.visit_entry_panel.set_affected_teeth([tooth_number])
        
        # Emit signal
        self.tooth_selected.emit(tooth_number, chart_type)
    
    def on_tooth_status_changed(self, tooth_number, new_status, chart_type):
        """Handle tooth status change."""
        if not self.current_patient_id or not self.current_examination_id:
            return
        
        try:
            # Save tooth history record
            history_data = {
                'examination_id': self.current_examination_id,
                'tooth_number': tooth_number,
                'record_type': 'patient_problem' if chart_type == 'patient' else 'doctor_finding',
                'status': new_status,
                'description': f"Status changed to {new_status}",
                'date_recorded': date.today()
            }
            
            # Save using tooth history service
            tooth_history_service.add_tooth_history(self.current_patient_id, history_data)
            
            # Update tooth history display for both panels if the tooth is selected
            if hasattr(self, 'selected_tooth') and self.selected_tooth == tooth_number:
                self.load_tooth_history(tooth_number, chart_type)
            
            # Also refresh the specific panel that changed
            record_type = 'patient_problem' if chart_type == 'patient' else 'doctor_finding'
            history = tooth_history_service.get_tooth_history(
                patient_id=self.current_patient_id,
                tooth_number=tooth_number,
                record_type=record_type,
                examination_id=self.current_examination_id
            )
            
            # Update the appropriate chart panel with updated history
            if chart_type == 'patient' and self.patient_chart_panel:
                self.patient_chart_panel.display_tooth_history(tooth_number, history)
            elif chart_type == 'doctor' and self.doctor_chart_panel:
                self.doctor_chart_panel.display_tooth_history(tooth_number, history)
            
            # Update status
            self.exam_status_label.setText(f"Tooth #{tooth_number} status updated")
            
        except Exception as e:
            logger.error(f"Error saving tooth status change: {str(e)}")
            QMessageBox.warning(self, "Warning", f"Failed to save tooth status: {str(e)}")
    
    def on_visit_added(self, visit_data):
        """Handle new visit addition."""
        if not self.current_patient_id or not self.current_examination_id:
            return
        
        try:
            # Add examination context to visit data
            visit_data['patient_id'] = self.current_patient_id
            visit_data['examination_id'] = self.current_examination_id
            
            # Save visit record - COMMENTED OUT FOR SIMPLIFICATION
            # result = visit_records_service.add_visit_record(visit_data)
            
            # Mock successful result for now
            result = {'success': True}
            
            if result.get('success'):
                # Refresh visit records display - Re-enabled for displaying old visits
                if self.visit_records_panel:
                    self.visit_records_panel.add_visit_record(visit_data)
                
                # Update affected teeth in charts if specified
                affected_teeth = visit_data.get('affected_teeth', [])
                for tooth_num in affected_teeth:
                    # Add tooth history entries for affected teeth
                    self.add_tooth_history_from_visit(tooth_num, visit_data)
                
                # Clear visit entry form
                if self.visit_entry_panel:
                    self.visit_entry_panel.clear_form()
                
                # Update status
                amount = visit_data.get('cost', 0) or 0
                self.exam_status_label.setText(f"Visit added - ${amount:.2f}")
                
                # Emit signal
                self.visit_added.emit(visit_data)
                
        except Exception as e:
            logger.error(f"Error adding visit: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to add visit: {str(e)}")
    
    def on_visit_selected(self, visit_data):
        """Handle visit selection."""
        # Update examination panel with visit context if needed
        visit_id = visit_data.get('id')
        self.exam_status_label.setText(f"Visit #{visit_id} selected")
    
    def on_episode_saved(self, episode_data):
        """Handle treatment episode save."""
        episode_id = episode_data.get('id')
        self.exam_status_label.setText(f"Treatment episode #{episode_id} saved")
        self.update_last_saved()
    
    def on_episode_selected(self, episode_data):
        """Handle treatment episode selection."""
        episode_id = episode_data.get('id')
        self.exam_status_label.setText(f"Treatment episode #{episode_id} selected")
    
    def update_total_amount(self, total_amount):
        """Update total amount display."""
        self.total_amount_label.setText(f"Total: ${total_amount:.2f}")
    
    # === DATA LOADING AND MANAGEMENT ===
    def load_initial_data(self):
        """Load initial data when component starts."""
        # Load patients into combo box
        self.load_patients_list()
        
        # Load custom dental statuses
        self.load_custom_statuses()
        
        # Set initial state
        self.exam_status_label.setText("Ready - Select a patient to begin")
    
    def load_patients_list(self):
        """Load all patients into selection combo."""
        try:
            patients = patient_service.get_all_patients()
            
            self.patient_combo.clear()
            self.patient_combo.addItem("Select a patient...", None)
            
            for patient in patients:
                display_text = f"{patient['full_name']} - ID: {patient['patient_id']}"
                self.patient_combo.addItem(display_text, patient)
                
        except Exception as e:
            logger.error(f"Error loading patients: {str(e)}")
            self.exam_status_label.setText("Error loading patients")
    
    def load_custom_statuses(self):
        """Load custom dental statuses."""
        try:
            # Initialize custom statuses if needed
            custom_status_service.initialize_default_statuses()
            
        except Exception as e:
            logger.error(f"Error loading custom statuses: {str(e)}")
    
    def load_latest_examination(self):
        """Load the most recent examination for current patient."""
        if not self.current_patient_id:
            return
        
        try:
            # Get latest examination
            examinations = dental_examination_service.get_patient_examinations(self.current_patient_id)
            
            if examinations:
                # Load most recent examination
                latest_exam = examinations[0]  # Assuming sorted by date desc
                if self.examination_panel:
                    # Find the examination in the combo and select it
                    for i in range(self.examination_panel.examination_combo.count()):
                        item_data = self.examination_panel.examination_combo.itemData(i)
                        if item_data == latest_exam.get('id'):
                            self.examination_panel.examination_combo.setCurrentIndex(i)
                            break
                self.on_examination_selected(latest_exam)
            else:
                # No examinations - prepare for new one
                self.current_examination_id = None
                self.current_exam_label.setText("No examinations - Create new")
                
        except Exception as e:
            logger.error(f"Error loading latest examination: {str(e)}")
    
    def load_examination_dental_data(self):
        """Load dental chart data for current examination."""
        if not self.current_patient_id or not self.current_examination_id:
            return
        
        try:
            # Load tooth history for current examination
            patient_history = tooth_history_service.get_tooth_history(
                patient_id=self.current_patient_id, 
                examination_id=self.current_examination_id,
                record_type='patient_problem'
            )
            
            doctor_history = tooth_history_service.get_tooth_history(
                patient_id=self.current_patient_id,
                examination_id=self.current_examination_id, 
                record_type='doctor_finding'
            )
            
            # Update charts with loaded data
            if self.patient_chart_panel:
                self.patient_chart_panel.load_tooth_data(patient_history)
            if self.doctor_chart_panel:
                self.doctor_chart_panel.load_tooth_data(doctor_history)
                
        except Exception as e:
            logger.error(f"Error loading examination dental data: {str(e)}")
    
    def load_tooth_history(self, tooth_number, chart_type):
        """Load tooth history for selected tooth."""
        if not self.current_patient_id or not self.current_examination_id:
            return
        
        try:
            record_type = f'{chart_type}_problem' if chart_type == 'patient' else f'{chart_type}_finding'
            
            # Get tooth history for this tooth and examination
            history = tooth_history_service.get_tooth_history(
                self.current_patient_id,
                tooth_number,
                record_type,
                self.current_examination_id
            )
            
            # Update the appropriate chart panel with history
            if chart_type == "patient" and self.patient_chart_panel:
                self.patient_chart_panel.display_tooth_history(tooth_number, history)
            elif chart_type == "doctor" and self.doctor_chart_panel:
                self.doctor_chart_panel.display_tooth_history(tooth_number, history)
                
        except Exception as e:
            logger.error(f"Error loading tooth history: {str(e)}")
    
    def add_tooth_history_from_visit(self, tooth_number, visit_data):
        """Add tooth history entries from visit data."""
        if not self.current_patient_id or not self.current_examination_id:
            return
        
        try:
            # Add patient problem entry if chief complaint mentions this tooth
            chief_complaint = visit_data.get('chief_complaint', '')
            if chief_complaint:
                patient_history = {
                    'examination_id': self.current_examination_id,
                    'tooth_number': tooth_number,
                    'record_type': 'patient_problem',
                    'status': 'problem',
                    'description': chief_complaint,
                    'date_recorded': date.today()
                }
                tooth_history_service.add_tooth_history(self.current_patient_id, patient_history)
            
            # Add doctor finding entry if treatment was performed
            treatment = visit_data.get('treatment_performed', '')
            if treatment:
                doctor_history = {
                    'examination_id': self.current_examination_id,
                    'tooth_number': tooth_number,
                    'record_type': 'doctor_finding',
                    'status': 'treated',
                    'description': treatment,
                    'date_recorded': date.today()
                }
                tooth_history_service.add_tooth_history(self.current_patient_id, doctor_history)
                
        except Exception as e:
            logger.error(f"Error adding tooth history from visit: {str(e)}")
    
    # === UI ACTIONS ===
    def create_new_examination(self):
        """Create a new examination."""
        if not self.current_patient_id:
            QMessageBox.warning(self, "Warning", "Please select a patient first.")
            return
        
        if self.examination_panel:
            self.examination_panel.create_new_examination()
    
    def save_all_changes(self):
        """Save all pending changes across components."""
        try:
            # Save examination if modified
            if self.examination_panel and hasattr(self.examination_panel, 'save_examination'):
                self.examination_panel.save_examination()
            
            # Save any pending tooth changes
            if self.patient_chart_panel and hasattr(self.patient_chart_panel, 'save_pending_changes'):
                self.patient_chart_panel.save_pending_changes()
            if self.doctor_chart_panel and hasattr(self.doctor_chart_panel, 'save_pending_changes'):
                self.doctor_chart_panel.save_pending_changes()
            
            # Update timestamp
            self.update_last_saved()
            
            # Update status
            self.exam_status_label.setText("All changes saved successfully")
            
            # Emit signal
            self.data_saved.emit()
            
        except Exception as e:
            logger.error(f"Error saving changes: {str(e)}")
            QMessageBox.critical(self, "Save Error", f"Failed to save changes: {str(e)}")
    
    def export_data(self):
        """Export current examination data."""
        if not self.current_patient_id or not self.current_examination_id:
            QMessageBox.warning(self, "Warning", "Please select a patient and examination first.")
            return
        
        try:
            # Mock export functionality - implement actual export logic
            self.exam_status_label.setText("Export functionality coming soon...")
            QMessageBox.information(self, "Export", "Export functionality will be implemented in future updates.")
            
        except Exception as e:
            logger.error(f"Error exporting data: {str(e)}")
            QMessageBox.critical(self, "Export Error", f"Failed to export data: {str(e)}")
    
    def clear_tooth_selections(self):
        """Clear all tooth selections."""
        if self.patient_chart_panel:
            self.patient_chart_panel.clear_selection()
        if self.doctor_chart_panel:
            self.doctor_chart_panel.clear_selection()
        
        self.selected_tooth_number = None
        self.selected_chart_type = None
    
    def clear_all_data(self):
        """Clear all data when no patient selected."""
        # Clear chart selections
        self.clear_tooth_selections()
        
        # Reset examination
        self.current_examination_id = None
        self.current_exam_label.setText("No examination selected")
        
        # Clear panels
        if self.examination_panel:
            self.examination_panel.set_patient(None)
        # Re-enabled for displaying old visits
        if self.visit_records_panel:
            self.visit_records_panel.set_patient(None)
        # Clear visit entry panel
        if self.visit_entry_panel:
            self.visit_entry_panel.set_patient(None)
        # COMMENTED OUT FOR SIMPLIFICATION
        # if self.treatment_episodes_panel:
        #     self.treatment_episodes_panel.set_patient(None)
        
        # Update status
        self.exam_status_label.setText("Ready - Select a patient to begin")
        self.total_amount_label.setText("Total: $0.00")
    
    def update_last_saved(self):
        """Update last saved timestamp."""
        current_time = datetime.now().strftime('%H:%M:%S')
        self.last_saved_label.setText(f"Saved: {current_time}")
    
    def apply_global_styles(self):
        """Apply consistent styling across the widget."""
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 12px;
                color: #2C3E50;
            }
            
            QGroupBox {
                font-weight: bold;
                border: 1px solid #BDC3C7;
                border-radius: 4px;
                margin-top: 6px;
                padding-top: 8px;
                background-color: white;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 6px;
                color: #2C3E50;
                font-size: 12px;
            }
            
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
                font-size: 11px;
            }
            
            QPushButton:hover {
                background-color: #45a049;
            }
            
            QPushButton:disabled {
                background-color: #BDC3C7;
                color: #7F8C8D;
            }
            
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            
            QScrollBar:vertical {
                background: #ECF0F1;
                width: 10px;
                border-radius: 5px;
            }
            
            QScrollBar::handle:vertical {
                background: #BDC3C7;
                border-radius: 5px;
                min-height: 20px;
            }
            
            QScrollBar::handle:vertical:hover {
                background: #95A5A6;
            }
            
            QScrollBar:horizontal {
                background: #ECF0F1;
                height: 10px;
                border-radius: 5px;
            }
            
            QScrollBar::handle:horizontal {
                background: #BDC3C7;
                border-radius: 5px;
                min-width: 20px;
            }
            
            QScrollBar::handle:horizontal:hover {
                background: #95A5A6;
            }
        """)
    
    # === PUBLIC INTERFACE ===
    def set_patient(self, patient: dict):
        """Set specific patient for examination (public interface)."""
        # Find and select the patient in the combo box
        for i in range(self.patient_combo.count()):
            combo_patient = self.patient_combo.itemData(i)
            if combo_patient and combo_patient.get('patient_id') == patient.get('patient_id'):
                self.patient_combo.setCurrentIndex(i)
                return
        
        # If patient not found in combo, add them and select
        if patient:
            display_text = f"{patient.get('full_name', 'Unknown')} - ID: {patient.get('patient_id', 'N/A')}"
            self.patient_combo.addItem(display_text, patient)
            self.patient_combo.setCurrentIndex(self.patient_combo.count() - 1)


# Maintain backward compatibility with existing code
DentalChart = AdvancedDentalChart
