"""
Treatment Episodes Panel - Treatment planning and episode management.
"""
import logging
from datetime import date, datetime
from typing import Dict, List, Optional, Any
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, 
    QLineEdit, QTextEdit, QComboBox, QPushButton, QDateEdit,
    QSpinBox, QDoubleSpinBox, QCheckBox, QListWidget, QListWidgetItem,
    QFrame, QFormLayout, QGridLayout, QMessageBox, QSizePolicy,
    QScrollArea, QTabWidget, QProgressBar
)
from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import QFont, QColor

logger = logging.getLogger(__name__)


class TreatmentEpisodeWidget(QFrame):
    """Individual treatment episode display widget."""
    
    episode_selected = Signal(dict)
    episode_edit_requested = Signal(dict)
    
    def __init__(self, episode_data: Dict, parent=None):
        super().__init__(parent)
        self.episode_data = episode_data
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the treatment episode widget UI."""
        self.setFrameStyle(QFrame.Box)
        self.setStyleSheet("""
            QFrame {
                border: 1px solid #19c5e5;
                border-radius: 6px;
                margin: 2px;
                padding: 8px;
                background-color: #f8f9fa;
            }
            QFrame:hover {
                background-color: #e6f9fd;
                border: 2px solid #0ea5c7;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(4)
        
        # Header with treatment name and status
        header_layout = QHBoxLayout()
        
        # Treatment name
        treatment_name = self.episode_data.get('treatment_name', 'Unknown Treatment')
        name_label = QLabel(treatment_name)
        name_label.setFont(QFont("Arial", 11, QFont.Bold))
        name_label.setStyleSheet("color: #19c5e5;")
        header_layout.addWidget(name_label)
        
        header_layout.addStretch()
        
        # Status badge
        status = self.episode_data.get('status', 'planned').title()
        status_label = QLabel(status)
        status_label.setStyleSheet(self.get_status_style(status.lower()))
        header_layout.addWidget(status_label)
        
        layout.addLayout(header_layout)
        
        # Episode details
        details_layout = QGridLayout()
        details_layout.setSpacing(2)
        
        # Start and end dates
        start_date = self.episode_data.get('start_date', '')
        end_date = self.episode_data.get('end_date', '')
        
        if start_date:
            details_layout.addWidget(QLabel("Start:"), 0, 0)
            details_layout.addWidget(QLabel(str(start_date)), 0, 1)
        
        if end_date:
            details_layout.addWidget(QLabel("End:"), 0, 2)
            details_layout.addWidget(QLabel(str(end_date)), 0, 3)
        
        # Doctor and cost
        doctor = self.episode_data.get('doctor_name', '')
        if doctor:
            details_layout.addWidget(QLabel("Doctor:"), 1, 0)
            doctor_label = QLabel(doctor)
            doctor_label.setStyleSheet("color: #666;")
            details_layout.addWidget(doctor_label, 1, 1)
        
        estimated_cost = self.episode_data.get('estimated_cost', 0)
        if estimated_cost and estimated_cost > 0:
            details_layout.addWidget(QLabel("Cost:"), 1, 2)
            cost_label = QLabel(f"${estimated_cost:.2f}")
            cost_label.setStyleSheet("color: #27ae60; font-weight: bold;")
            details_layout.addWidget(cost_label, 1, 3)
        
        layout.addLayout(details_layout)
        
        # Progress bar for ongoing treatments
        status_lower = status.lower()
        if status_lower in ['in_progress', 'ongoing']:
            progress = self.episode_data.get('progress', 0)
            progress_bar = QProgressBar()
            progress_bar.setValue(int(progress))
            progress_bar.setStyleSheet("""
                QProgressBar {
                    border: 1px solid #19c5e5;
                    border-radius: 3px;
                    text-align: center;
                    height: 20px;
                }
                QProgressBar::chunk {
                    background-color: #19c5e5;
                    border-radius: 2px;
                }
            """)
            layout.addWidget(progress_bar)
        
        # Description/notes
        description = self.episode_data.get('description', '') or self.episode_data.get('notes', '')
        if description:
            desc_label = QLabel(description)
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("color: #666; font-size: 10px; margin-top: 4px;")
            layout.addWidget(desc_label)
        
        # Affected teeth
        affected_teeth = self.episode_data.get('affected_teeth', [])
        if affected_teeth and len(affected_teeth) > 0:
            teeth_text = f"Teeth: {', '.join(map(str, affected_teeth))}"
            teeth_label = QLabel(teeth_text)
            teeth_label.setStyleSheet("color: #666; font-size: 10px;")
            layout.addWidget(teeth_label)
        
        # Actions
        actions_layout = QHBoxLayout()
        actions_layout.addStretch()
        
        edit_btn = QPushButton("Edit")
        edit_btn.setMaximumWidth(60)
        edit_btn.setStyleSheet("""
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
        edit_btn.clicked.connect(lambda: self.episode_edit_requested.emit(self.episode_data))
        actions_layout.addWidget(edit_btn)
        
        layout.addLayout(actions_layout)
        
        # Make clickable
        self.mousePressEvent = lambda event: self.episode_selected.emit(self.episode_data)
    
    def get_status_style(self, status: str) -> str:
        """Get CSS style for status badge."""
        status_styles = {
            'planned': "background-color: #6c757d; color: white; padding: 3px 8px; border-radius: 10px; font-size: 10px;",
            'in_progress': "background-color: #007bff; color: white; padding: 3px 8px; border-radius: 10px; font-size: 10px;",
            'ongoing': "background-color: #007bff; color: white; padding: 3px 8px; border-radius: 10px; font-size: 10px;",
            'completed': "background-color: #28a745; color: white; padding: 3px 8px; border-radius: 10px; font-size: 10px;",
            'cancelled': "background-color: #dc3545; color: white; padding: 3px 8px; border-radius: 10px; font-size: 10px;",
            'postponed': "background-color: #ffc107; color: black; padding: 3px 8px; border-radius: 10px; font-size: 10px;"
        }
        return status_styles.get(status, status_styles['planned'])


class TreatmentEpisodeForm(QFrame):
    """Form for creating/editing treatment episodes."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_episode = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the treatment episode form UI."""
        self.setFrameStyle(QFrame.Box)
        self.setStyleSheet("""
            QFrame {
                border: 1px solid #19c5e5;
                border-radius: 8px;
                padding: 10px;
                background-color: #f8f9fa;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Basic information
        basic_layout = QFormLayout()
        basic_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        
        # Treatment name
        self.treatment_name_edit = QLineEdit()
        self.treatment_name_edit.setPlaceholderText("e.g., Root Canal Therapy, Crown Placement")
        basic_layout.addRow("Treatment Name:", self.treatment_name_edit)
        
        # Treatment category
        self.treatment_category_combo = QComboBox()
        self.treatment_category_combo.addItems([
            "preventive", "restorative", "endodontic", "periodontal", 
            "oral_surgery", "prosthodontic", "orthodontic", "cosmetic", "emergency"
        ])
        basic_layout.addRow("Category:", self.treatment_category_combo)
        
        # Status
        self.status_combo = QComboBox()
        self.status_combo.addItems(["planned", "in_progress", "completed", "cancelled", "postponed"])
        basic_layout.addRow("Status:", self.status_combo)
        
        # Priority
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["low", "medium", "high", "urgent"])
        basic_layout.addRow("Priority:", self.priority_combo)
        
        layout.addLayout(basic_layout)
        
        # Dates section
        dates_group = QGroupBox("Timeline")
        dates_layout = QGridLayout(dates_group)
        
        # Start date
        dates_layout.addWidget(QLabel("Start Date:"), 0, 0)
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setDate(QDate.currentDate())
        self.start_date_edit.setCalendarPopup(True)
        dates_layout.addWidget(self.start_date_edit, 0, 1)
        
        # End date
        dates_layout.addWidget(QLabel("End Date:"), 0, 2)
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setDate(QDate.currentDate().addDays(30))
        self.end_date_edit.setCalendarPopup(True)
        dates_layout.addWidget(self.end_date_edit, 0, 3)
        
        # Progress
        dates_layout.addWidget(QLabel("Progress:"), 1, 0)
        self.progress_spin = QSpinBox()
        self.progress_spin.setRange(0, 100)
        self.progress_spin.setSuffix("%")
        dates_layout.addWidget(self.progress_spin, 1, 1)
        
        layout.addWidget(dates_group)
        
        # Financial information
        financial_group = QGroupBox("Financial Information")
        financial_layout = QGridLayout(financial_group)
        
        # Estimated cost
        financial_layout.addWidget(QLabel("Estimated Cost:"), 0, 0)
        self.estimated_cost_spin = QDoubleSpinBox()
        self.estimated_cost_spin.setRange(0, 999999.99)
        self.estimated_cost_spin.setPrefix("$")
        self.estimated_cost_spin.setDecimals(2)
        financial_layout.addWidget(self.estimated_cost_spin, 0, 1)
        
        # Insurance coverage
        financial_layout.addWidget(QLabel("Insurance Coverage:"), 0, 2)
        self.insurance_coverage_spin = QSpinBox()
        self.insurance_coverage_spin.setRange(0, 100)
        self.insurance_coverage_spin.setSuffix("%")
        financial_layout.addWidget(self.insurance_coverage_spin, 0, 3)
        
        layout.addWidget(financial_group)
        
        # Clinical details
        clinical_group = QGroupBox("Clinical Details")
        clinical_layout = QVBoxLayout(clinical_group)
        
        # Description
        clinical_layout.addWidget(QLabel("Description:"))
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        self.description_edit.setPlaceholderText("Detailed treatment description...")
        clinical_layout.addWidget(self.description_edit)
        
        # Pre-treatment requirements
        clinical_layout.addWidget(QLabel("Pre-treatment Requirements:"))
        self.pre_treatment_edit = QTextEdit()
        self.pre_treatment_edit.setMaximumHeight(60)
        self.pre_treatment_edit.setPlaceholderText("Any requirements before treatment...")
        clinical_layout.addWidget(self.pre_treatment_edit)
        
        # Post-treatment care
        clinical_layout.addWidget(QLabel("Post-treatment Care:"))
        self.post_treatment_edit = QTextEdit()
        self.post_treatment_edit.setMaximumHeight(60)
        self.post_treatment_edit.setPlaceholderText("Care instructions after treatment...")
        clinical_layout.addWidget(self.post_treatment_edit)
        
        layout.addWidget(clinical_group)
        
        # Affected teeth selection
        teeth_group = QGroupBox("Affected Teeth")
        teeth_layout = QVBoxLayout(teeth_group)
        
        # Teeth input
        teeth_input_layout = QHBoxLayout()
        teeth_input_layout.addWidget(QLabel("Teeth:"))
        self.affected_teeth_edit = QLineEdit()
        self.affected_teeth_edit.setPlaceholderText("e.g., 11, 12, 21 (comma-separated)")
        teeth_input_layout.addWidget(self.affected_teeth_edit)
        teeth_layout.addLayout(teeth_input_layout)
        
        layout.addWidget(teeth_group)
    
    def load_episode(self, episode_data: Dict):
        """Load episode data into the form."""
        self.current_episode = episode_data
        
        # Basic information
        self.treatment_name_edit.setText(episode_data.get('treatment_name', ''))
        
        category = episode_data.get('treatment_category', '')
        category_index = self.treatment_category_combo.findText(category)
        if category_index >= 0:
            self.treatment_category_combo.setCurrentIndex(category_index)
        
        status = episode_data.get('status', '')
        status_index = self.status_combo.findText(status)
        if status_index >= 0:
            self.status_combo.setCurrentIndex(status_index)
        
        priority = episode_data.get('priority', '')
        priority_index = self.priority_combo.findText(priority)
        if priority_index >= 0:
            self.priority_combo.setCurrentIndex(priority_index)
        
        # Dates
        start_date = episode_data.get('start_date')
        if start_date:
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            self.start_date_edit.setDate(QDate(start_date))
        
        end_date = episode_data.get('end_date')
        if end_date:
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            self.end_date_edit.setDate(QDate(end_date))
        
        self.progress_spin.setValue(episode_data.get('progress', 0))
        
        # Financial
        self.estimated_cost_spin.setValue(episode_data.get('estimated_cost', 0))
        self.insurance_coverage_spin.setValue(episode_data.get('insurance_coverage', 0))
        
        # Clinical details
        self.description_edit.setPlainText(episode_data.get('description', ''))
        self.pre_treatment_edit.setPlainText(episode_data.get('pre_treatment_requirements', ''))
        self.post_treatment_edit.setPlainText(episode_data.get('post_treatment_care', ''))
        
        # Affected teeth
        affected_teeth = episode_data.get('affected_teeth', [])
        if affected_teeth:
            teeth_str = ', '.join(map(str, affected_teeth))
            self.affected_teeth_edit.setText(teeth_str)
    
    def get_episode_data(self) -> Dict:
        """Get episode data from the form."""
        # Parse affected teeth
        teeth_text = self.affected_teeth_edit.text().strip()
        affected_teeth = []
        if teeth_text:
            try:
                affected_teeth = [int(tooth.strip()) for tooth in teeth_text.split(',') if tooth.strip()]
            except ValueError:
                pass  # Invalid tooth numbers will be ignored
        
        return {
            'treatment_name': self.treatment_name_edit.text().strip(),
            'treatment_category': self.treatment_category_combo.currentText(),
            'status': self.status_combo.currentText(),
            'priority': self.priority_combo.currentText(),
            'start_date': self.start_date_edit.date().toPython(),
            'end_date': self.end_date_edit.date().toPython(),
            'progress': self.progress_spin.value(),
            'estimated_cost': self.estimated_cost_spin.value(),
            'insurance_coverage': self.insurance_coverage_spin.value(),
            'description': self.description_edit.toPlainText().strip(),
            'pre_treatment_requirements': self.pre_treatment_edit.toPlainText().strip(),
            'post_treatment_care': self.post_treatment_edit.toPlainText().strip(),
            'affected_teeth': affected_teeth
        }
    
    def clear_form(self):
        """Clear all form fields."""
        self.current_episode = None
        self.treatment_name_edit.clear()
        self.treatment_category_combo.setCurrentIndex(0)
        self.status_combo.setCurrentIndex(0)
        self.priority_combo.setCurrentIndex(1)  # medium
        self.start_date_edit.setDate(QDate.currentDate())
        self.end_date_edit.setDate(QDate.currentDate().addDays(30))
        self.progress_spin.setValue(0)
        self.estimated_cost_spin.setValue(0)
        self.insurance_coverage_spin.setValue(0)
        self.description_edit.clear()
        self.pre_treatment_edit.clear()
        self.post_treatment_edit.clear()
        self.affected_teeth_edit.clear()


class TreatmentEpisodesPanel(QGroupBox):
    """Treatment planning and episode management panel."""
    
    episode_selected = Signal(dict)
    episode_saved = Signal(dict)
    
    def __init__(self, patient_id: Optional[int] = None, examination_id: Optional[int] = None, parent=None):
        super().__init__("Treatment Episodes", parent)
        self.patient_id = patient_id
        self.examination_id = examination_id
        self.episodes_list = []
        self.current_episode_id = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the treatment episodes panel UI."""
        layout = QVBoxLayout(self)
        
        # Header with controls
        header_layout = QHBoxLayout()
        
        # Filter options
        filter_label = QLabel("Filter:")
        header_layout.addWidget(filter_label)
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All Episodes", "Current Exam", "Planned", "In Progress", "Completed"])
        self.filter_combo.currentTextChanged.connect(self.apply_filter)
        header_layout.addWidget(self.filter_combo)
        
        header_layout.addStretch()
        
        # Action buttons
        self.new_btn = QPushButton("New Episode")
        self.new_btn.clicked.connect(self.create_new_episode)
        header_layout.addWidget(self.new_btn)
        
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_episode)
        header_layout.addWidget(self.save_btn)
        
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.clicked.connect(self.delete_episode)
        self.delete_btn.setStyleSheet("background-color: #dc3545; color: white;")
        header_layout.addWidget(self.delete_btn)
        
        layout.addLayout(header_layout)
        
        # Main content in tabs
        self.tab_widget = QTabWidget()
        
        # Episodes List Tab
        list_scroll = QScrollArea()
        list_scroll.setWidgetResizable(True)
        
        self.episodes_widget = QWidget()
        self.episodes_layout = QVBoxLayout(self.episodes_widget)
        self.episodes_layout.setAlignment(Qt.AlignTop)
        
        list_scroll.setWidget(self.episodes_widget)
        self.tab_widget.addTab(list_scroll, "Episodes List")
        
        # Episode Form Tab
        form_scroll = QScrollArea()
        form_scroll.setWidgetResizable(True)
        self.form_widget = TreatmentEpisodeForm()
        form_scroll.setWidget(self.form_widget)
        self.tab_widget.addTab(form_scroll, "Episode Details")
        
        layout.addWidget(self.tab_widget)
        
        # Summary information
        summary_layout = QHBoxLayout()
        
        self.summary_label = QLabel("No episodes recorded")
        self.summary_label.setStyleSheet("color: #666; font-style: italic;")
        summary_layout.addWidget(self.summary_label)
        
        summary_layout.addStretch()
        
        self.total_cost_label = QLabel("Total Cost: $0.00")
        self.total_cost_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.total_cost_label.setStyleSheet("color: #27ae60;")
        summary_layout.addWidget(self.total_cost_label)
        
        layout.addLayout(summary_layout)
        
        # Apply styles
        self.apply_styles()
        
        # Initial state
        self.update_panel_state()
    
    def apply_styles(self):
        """Apply consistent styling to the panel."""
        self.setStyleSheet("""
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
                background-color: #cccccc;
                color: #666666;
            }
            QComboBox {
                padding: 5px;
                border: 1px solid #19c5e5;
                border-radius: 3px;
            }
        """)
    
    def set_patient(self, patient_id: int):
        """Set the current patient and load episodes."""
        self.patient_id = patient_id
        self.update_panel_state()
        self.load_episodes()
    
    def set_examination(self, examination_id: int):
        """Set the current examination context."""
        self.examination_id = examination_id
        self.update_panel_state()
        self.apply_filter()
    
    def update_panel_state(self):
        """Update panel title and controls state."""
        if not self.patient_id:
            self.setTitle("Treatment Episodes (Select a patient first)")
            self.setEnabled(False)
        elif self.examination_id:
            self.setTitle(f"Treatment Episodes - Exam #{self.examination_id}")
            self.setEnabled(True)
        else:
            self.setTitle(f"Treatment Episodes - Patient #{self.patient_id}")
            self.setEnabled(True)
        
        # Update button states
        has_episode = self.current_episode_id is not None
        self.save_btn.setEnabled(has_episode or self.form_widget.current_episode is not None)
        self.delete_btn.setEnabled(has_episode)
    
    def load_episodes(self):
        """Load episodes for the current patient."""
        if not self.patient_id:
            self.clear_episodes()
            return
        
        try:
            # Mock data for now - replace with actual service call
            self.episodes_list = self.get_mock_episodes()
            
            # Apply current filter
            self.apply_filter()
            
        except Exception as e:
            logger.error(f"Error loading episodes: {str(e)}")
            self.clear_episodes()
    
    def get_mock_episodes(self) -> List[Dict]:
        """Get mock episode data for demonstration."""
        return [
            {
                'id': 1,
                'treatment_name': 'Root Canal Therapy - Tooth 16',
                'treatment_category': 'endodontic',
                'status': 'in_progress',
                'priority': 'high',
                'start_date': '2024-01-15',
                'end_date': '2024-02-15',
                'progress': 60,
                'estimated_cost': 1200.00,
                'insurance_coverage': 80,
                'description': 'Root canal treatment for severely infected molar',
                'affected_teeth': [16],
                'examination_id': self.examination_id
            },
            {
                'id': 2,
                'treatment_name': 'Crown Placement - Tooth 16',
                'treatment_category': 'prosthodontic',
                'status': 'planned',
                'priority': 'medium',
                'start_date': '2024-02-20',
                'end_date': '2024-03-05',
                'progress': 0,
                'estimated_cost': 800.00,
                'insurance_coverage': 50,
                'description': 'Porcelain crown following root canal therapy',
                'affected_teeth': [16],
                'examination_id': self.examination_id
            }
        ]
    
    def apply_filter(self):
        """Apply the selected filter to episodes."""
        if not self.episodes_list:
            self.display_episodes([])
            return
        
        filter_type = self.filter_combo.currentText()
        filtered_episodes = self.episodes_list.copy()
        
        if filter_type == "Current Exam" and self.examination_id:
            filtered_episodes = [
                episode for episode in filtered_episodes
                if episode.get('examination_id') == self.examination_id
            ]
        elif filter_type == "Planned":
            filtered_episodes = [
                episode for episode in filtered_episodes
                if episode.get('status') == 'planned'
            ]
        elif filter_type == "In Progress":
            filtered_episodes = [
                episode for episode in filtered_episodes
                if episode.get('status') == 'in_progress'
            ]
        elif filter_type == "Completed":
            filtered_episodes = [
                episode for episode in filtered_episodes
                if episode.get('status') == 'completed'
            ]
        
        self.display_episodes(filtered_episodes)
    
    def display_episodes(self, episodes: List[Dict]):
        """Display episodes in the list."""
        # Clear existing episodes
        self.clear_episodes_display()
        
        if not episodes:
            self.summary_label.setText("No episodes found for selected filter")
            self.total_cost_label.setText("Total Cost: $0.00")
            return
        
        # Sort episodes by start date
        sorted_episodes = sorted(
            episodes,
            key=lambda x: x.get('start_date', ''),
            reverse=False
        )
        
        # Add episode widgets
        total_cost = 0.0
        for episode in sorted_episodes:
            episode_widget = TreatmentEpisodeWidget(episode)
            episode_widget.episode_selected.connect(self.on_episode_selected)
            episode_widget.episode_edit_requested.connect(self.on_episode_edit_requested)
            self.episodes_layout.addWidget(episode_widget)
            
            # Add to total cost
            cost = episode.get('estimated_cost', 0)
            if cost and cost > 0:
                total_cost += float(cost)
        
        # Update summary
        count = len(sorted_episodes)
        self.summary_label.setText(f"{count} episode{'s' if count != 1 else ''} found")
        self.total_cost_label.setText(f"Total Cost: ${total_cost:.2f}")
    
    def clear_episodes_display(self):
        """Clear the episodes display area."""
        while self.episodes_layout.count():
            child = self.episodes_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def clear_episodes(self):
        """Clear all episodes and reset display."""
        self.episodes_list = []
        self.clear_episodes_display()
        self.summary_label.setText("No episodes recorded")
        self.total_cost_label.setText("Total Cost: $0.00")
    
    def on_episode_selected(self, episode_data: Dict):
        """Handle episode selection."""
        self.current_episode_id = episode_data.get('id')
        self.episode_selected.emit(episode_data)
        self.update_panel_state()
    
    def on_episode_edit_requested(self, episode_data: Dict):
        """Handle episode edit request."""
        self.current_episode_id = episode_data.get('id')
        self.form_widget.load_episode(episode_data)
        self.tab_widget.setCurrentIndex(1)  # Switch to form tab
        self.update_panel_state()
    
    def create_new_episode(self):
        """Create a new treatment episode."""
        if not self.patient_id:
            QMessageBox.warning(self, "Warning", "Please select a patient first.")
            return
        
        # Clear form and switch to form tab
        self.form_widget.clear_form()
        self.current_episode_id = None
        self.tab_widget.setCurrentIndex(1)
        self.update_panel_state()
    
    def save_episode(self):
        """Save the current episode."""
        if not self.patient_id:
            QMessageBox.warning(self, "Warning", "Please select a patient first.")
            return
        
        try:
            # Get data from form
            episode_data = self.form_widget.get_episode_data()
            episode_data['patient_id'] = self.patient_id
            if self.examination_id:
                episode_data['examination_id'] = self.examination_id
            
            # Validate required fields
            if not episode_data.get('treatment_name', '').strip():
                QMessageBox.warning(self, "Validation Error", "Treatment name is required.")
                return
            
            # Mock save operation - replace with actual service call
            if self.current_episode_id:
                # Update existing episode
                episode_data['id'] = self.current_episode_id
                # Mock update
                for i, episode in enumerate(self.episodes_list):
                    if episode.get('id') == self.current_episode_id:
                        self.episodes_list[i] = episode_data
                        break
                action = "updated"
            else:
                # Create new episode
                episode_data['id'] = len(self.episodes_list) + 1
                self.episodes_list.append(episode_data)
                self.current_episode_id = episode_data['id']
                action = "created"
            
            # Refresh display
            self.apply_filter()
            
            # Emit signal
            self.episode_saved.emit(episode_data)
            
            # Switch back to list tab
            self.tab_widget.setCurrentIndex(0)
            
            QMessageBox.information(self, "Success", f"Episode {action} successfully!")
            
        except Exception as e:
            logger.error(f"Error saving episode: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to save episode: {str(e)}")
    
    def delete_episode(self):
        """Delete the current episode."""
        if not self.current_episode_id:
            QMessageBox.warning(self, "Warning", "Please select an episode to delete.")
            return
        
        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            "Are you sure you want to delete this treatment episode?\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # Mock delete operation - replace with actual service call
                self.episodes_list = [
                    episode for episode in self.episodes_list
                    if episode.get('id') != self.current_episode_id
                ]
                
                # Clear form and refresh display
                self.form_widget.clear_form()
                self.current_episode_id = None
                self.apply_filter()
                
                # Switch back to list tab
                self.tab_widget.setCurrentIndex(0)
                
                QMessageBox.information(self, "Success", "Episode deleted successfully!")
                
            except Exception as e:
                logger.error(f"Error deleting episode: {str(e)}")
                QMessageBox.critical(self, "Error", f"Failed to delete episode: {str(e)}")
    
    def get_total_estimated_cost(self) -> float:
        """Get total estimated cost of all episodes."""
        total = 0.0
        for episode in self.episodes_list:
            cost = episode.get('estimated_cost', 0)
            if cost and cost > 0:
                total += float(cost)
        return total
    
    def get_episodes_by_status(self, status: str) -> List[Dict]:
        """Get episodes filtered by status."""
        return [
            episode for episode in self.episodes_list
            if episode.get('status') == status
        ]
