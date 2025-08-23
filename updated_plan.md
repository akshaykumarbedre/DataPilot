# Dental Chart System Update Plan

## Overview
Based on the analysis of `ui1.py` demo code, we need to implement a comprehensive dental chart system with dual patient/doctor tracking, visit records, and detailed tooth history management.

## Key Requirements Analysis

### 1. **Dual Dental Charts** (from ui1.py)
- **Patient Problems Chart**: Records patient-reported issues and complaints
- **Doctor Findings Chart**: Records doctor's diagnosis, treatments, and observations
- Both charts show the same dental layout but track different types of data
- Each chart has its own history area showing tooth-specific records

### 2. **Tooth History Tracking**
- Each tooth maintains separate history logs for:
  - Patient problems/complaints over time
  - Doctor findings and treatments over time
- Status changes are timestamped (e.g., "Problem" → "Root Canal" → "Fixed")
- Visual tooth status updates with color coding

### 3. **Dental Examinations Management**
- **Separate Examination Records**: Each patient can have multiple dental examinations over time
- **Independent Examinations**: New problems/visits create new examination records  
- **Examination History**: Track all examinations chronologically for each patient
- **Problem-Specific Data**: Each examination captures specific chief complaint and findings
- **Time-Based Tracking**: Patients can return after months/years with new problems

### 4. **Visit Records System**
- Complete visit tracking with:
  - Date, Amount paid
  - Chief Complaint (CC)
  - Diagnosis
  - Treatment performed
  - Doctor's advice
  - Affected teeth selection
- Historical visit records with total amount calculation

## Database Schema Updates

### New Tables Required:

#### 1. `dental_examinations` table
```sql
CREATE TABLE dental_examinations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    examination_date DATE NOT NULL,
    chief_complaint TEXT NOT NULL,
    history_of_presenting_illness TEXT,
    medical_history TEXT,
    dental_history TEXT,
    examination_findings TEXT,
    diagnosis TEXT,
    treatment_plan TEXT,
    notes TEXT,
    examiner_id INTEGER,  -- Reference to doctor/user
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(id),
    FOREIGN KEY (examiner_id) REFERENCES users(id)
);
```

#### 2. `tooth_history` table
```sql
CREATE TABLE tooth_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    examination_id INTEGER,  -- Link to specific examination
    tooth_number INTEGER NOT NULL,  -- Full tooth number (11-18, 21-28, 31-38, 41-48)
    record_type VARCHAR(20) NOT NULL,  -- 'patient_problem' or 'doctor_finding'
    status VARCHAR(50),  -- Current status (Normal, Problem, Fixed, Root Canal, Missing, Crown)
    description TEXT,  -- Detailed description
    date_recorded DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(id),
    FOREIGN KEY (examination_id) REFERENCES dental_examinations(id)
);
```

#### 3. `visit_records` table
```sql
CREATE TABLE visit_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    examination_id INTEGER,  -- Link to specific examination
    visit_date DATE NOT NULL,
    amount_paid DECIMAL(10,2) DEFAULT 0,
    chief_complaint TEXT,
    diagnosis TEXT,
    treatment_performed TEXT,
    advice TEXT,
    affected_teeth TEXT,  -- JSON array of tooth numbers
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(id),
    FOREIGN KEY (examination_id) REFERENCES dental_examinations(id)
);
```

#### 4. `custom_statuses` table
```sql
CREATE TABLE custom_statuses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    status_code VARCHAR(50) UNIQUE NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    color_code VARCHAR(7) NOT NULL,  -- Hex color code
    created_by INTEGER,  -- User who created it
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id)
);
```

#### 5. Update `patients` table
```sql
-- Remove examination fields from patients table as they move to dental_examinations
ALTER TABLE patients DROP COLUMN examination_date;
ALTER TABLE patients DROP COLUMN chief_complaint;
```

#### 6. Update `dental_chart_records` table
```sql
ALTER TABLE dental_chart_records ADD COLUMN examination_id INTEGER;
ALTER TABLE dental_chart_records ADD COLUMN current_status VARCHAR(50) DEFAULT 'normal';
ALTER TABLE dental_chart_records ADD COLUMN last_patient_complaint TEXT;
ALTER TABLE dental_chart_records ADD COLUMN last_doctor_finding TEXT;
ALTER TABLE dental_chart_records ADD FOREIGN KEY (examination_id) REFERENCES dental_examinations(id);
```

## Implementation Plan

### Phase 1: Database Layer Updates

#### 1.1 Update Models (`app/database/models.py`)
- Add `ToothHistory` model
- Add `VisitRecord` model
- Update `DentalChartRecord` model with new fields
- Add proper relationships


#### 1.3 Update Services
- Create `tooth_history_service.py`
- Create `visit_records_service.py`
- Update `dental_service.py` with new functionality

### Phase 2: UI Components Update

#### 2.1 Enhanced Tooth Widget (`app/ui/components/enhanced_tooth_widget.py`)
```python
class EnhancedToothWidget(QWidget):
    """Enhanced tooth widget with comprehensive status tracking"""
    - Tooth button with (quadrant.position) display format
    - Comprehensive status dropdown with 15+ predefined options
    - Custom status creation capability
    - Dynamic color coding based on status
    - Click handling for selection
    - Status change tracking with timestamps
    - Primary color theme (#19c5e5) integration
    
    def get_display_number(self, full_tooth_number):
        """Convert full tooth number to (quadrant.position) format"""
        # 11-18 → (1,1)-(1,8), 21-28 → (2,1)-(2,8), etc.
        
    def setup_status_dropdown(self):
        """Setup comprehensive status dropdown with colors"""
        # Include all 15 predefined statuses + custom option
        # Color-coded dropdown items
        # Custom status dialog integration
```

#### 2.2 Dual Dental Chart Panel (`app/ui/components/dental_chart_panel.py`)
```python
class DentalChartPanel(QGroupBox):
    """Individual dental chart panel (Patient/Doctor)"""
    - Chart title (Patient Problems / Doctor Findings)
    - 32-tooth layout (18-11 | 21-28 / 48-41 | 31-38)
    - Selected tooth info display
    - History text area for selected tooth
    - Panel type identification
```

#### 2.3 Visit Entry Panel (`app/ui/components/visit_entry_panel.py`)
```python
class VisitEntryPanel(QGroupBox):
    """New visit entry form"""
    - Date picker (default: today)
    - Amount field
    - Chief complaint input
    - Diagnosis input
    - Treatment input
    - Advice input
    - Tooth selection checkboxes (compact layout)
    - Add visit button
```

#### 2.4 Visit Records Panel (`app/ui/components/visit_records_panel.py`)
```python
class VisitRecordsPanel(QGroupBox):
    """Visit history display"""
    - Scrollable visit records list
    - Total amount calculation
    - Visit record widgets with date, amount, details
```

#### 2.5 Dental Examination Panel (`app/ui/components/dental_examination_panel.py`)
```python
class DentalExaminationPanel(QGroupBox):
    """Dental examination management panel"""
    - Current examination selector (latest/create new)
    - Examination date picker
    - Chief complaint input (multi-line)
    - Medical history input
    - Examination findings input
    - Diagnosis input
    - Treatment plan input
    - Save examination button
    - Examination history list
    
class NewExaminationDialog(QDialog):
    """Dialog for creating new dental examination"""
    - Examination date picker (default: today)
    - Chief complaint input (required)
    - Pre-filled patient information
    - Quick examination template selection
```

#### 2.6 Custom Status Management (`app/ui/components/custom_status_dialog.py`)
```python
class CustomStatusDialog(QDialog):
    """Dialog for creating custom tooth statuses"""
    - Status name input field
    - Color picker widget
    - Preview area showing tooth with new status
    - Save/Cancel buttons
    - Validation for unique status names
    - Integration with primary color theme
```

#### 2.7 Treatment Episodes Panel (`app/ui/components/treatment_episodes_panel.py`)
```python
class CustomStatusDialog(QDialog):
    """Dialog for creating custom tooth statuses"""
    - Status name input field
    - Color picker widget
    - Preview area showing tooth with new status
    - Save/Cancel buttons
    - Validation for unique status names
    - Integration with primary color theme
```

### Phase 3: Main Dental Chart Integration - Complete Rewrite

#### 3.1 Analysis of Current Implementation
**Current File:** `app/ui/dental_chart.py`
- **Legacy Structure**: Single chart system with basic tooth widgets
- **Limited Functionality**: Only basic status tracking (normal, treated, problem, missing)
- **Missing Features**: No dual charts, no examination management, no visit tracking
- **Outdated UI**: Not aligned with new component architecture

**Replacement Strategy**: Complete rewrite to integrate all Phase 2 components

#### 3.2 New Dental Chart Architecture

##### 3.2.1 Main Layout Structure
```
Enhanced Dental Chart Window (1200x900)
├── Header Section (Height: 80px)
│   ├── Title: "Advanced Dental Chart System"
│   ├── Patient Selector: QComboBox with search capability
│   ├── Current Examination Display: "Exam #123 - 2025-08-19"
│   └── Quick Actions: [New Exam] [Save All] [Export]
│
├── Main Content (HSplitter - 70%:30%)
│   ├── Left Panel (Chart & Examination)
│   │   ├── Examination Management Panel (Height: 200px)
│   │   │   ├── Current Examination Details
│   │   │   ├── Examination Selector/Creator
│   │   │   └── Quick Findings Input
│   │   │
│   │   ├── Dual Chart Container (Height: 400px)
│   │   │   ├── Patient Problems Chart (Left)
│   │   │   └── Doctor Findings Chart (Right)
│   │   │
│   │   └── Visit Entry Panel (Height: 250px)
│   │       ├── Visit Details Form
│   │       ├── Affected Teeth Selector
│   │       └── Cost & Treatment Info
│   │
│   └── Right Panel (Records & Episodes)
│       ├── Visit Records Panel (Top 50%)
│       │   ├── Filterable Visit History
│       │   ├── Total Amount Display
│       │   └── Visit Details Viewer
│       │
│       └── Treatment Episodes Panel (Bottom 50%)
│           ├── Episode Timeline
│           ├── Progress Tracking
│           └── Cost Management
│
└── Status Bar
    ├── Current Examination Status
    ├── Total Visit Amount
    └── Last Saved Timestamp
```

#### 3.3 Step-by-Step Implementation Plan

##### Step 3.3.1: File Structure Preparation
```python
# Create backup of current implementation
# File: app/ui/dental_chart_legacy.py (backup)
# Main: app/ui/dental_chart.py (complete rewrite)

# Import all Phase 2 components
from .components import (
    EnhancedToothWidget,
    DentalChartPanel, 
    CustomStatusDialog,
    VisitEntryPanel,
    VisitRecordsPanel,
    DentalExaminationPanel,
    TreatmentEpisodesPanel
)

# Import all Phase 1 services
from ..services import (
    dental_examination_service,
    tooth_history_service,
    visit_records_service,
    custom_status_service
)
```

##### Step 3.3.2: Main Window Class Structure
```python
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
        self.visit_records_panel = None
        self.treatment_episodes_panel = None
        
        # UI setup
        self.setup_ui()
        self.connect_signals()
        self.load_initial_data()
```

##### Step 3.3.3: UI Setup Implementation
```python
def setup_ui(self):
    """Setup the complete UI with all components."""
    
    # Main layout
    main_layout = QVBoxLayout(self)
    main_layout.setContentsMargins(10, 10, 10, 10)
    main_layout.setSpacing(10)
    
    # === HEADER SECTION ===
    header_widget = self.create_header_section()
    main_layout.addWidget(header_widget)
    
    # === MAIN CONTENT SPLITTER ===
    main_splitter = QSplitter(Qt.Horizontal)
    main_splitter.setSizes([850, 350])  # 70% : 30%
    
    # Left panel (Charts & Examination)
    left_panel = self.create_left_panel()
    main_splitter.addWidget(left_panel)
    
    # Right panel (Records & Episodes)
    right_panel = self.create_right_panel()
    main_splitter.addWidget(right_panel)
    
    main_layout.addWidget(main_splitter)
    
    # === STATUS BAR ===
    status_bar = self.create_status_bar()
    main_layout.addWidget(status_bar)
    
    # Apply global styling
    self.apply_global_styles()

def create_header_section(self) -> QWidget:
    """Create header with patient selection and quick actions."""
    header_widget = QFrame()
    header_widget.setFixedHeight(80)
    header_widget.setStyleSheet("""
        QFrame {
            background-color: #19c5e5;
            border-radius: 8px;
            padding: 10px;
        }
    """)
    
    header_layout = QHBoxLayout(header_widget)
    
    # Title
    title_label = QLabel("Advanced Dental Chart System")
    title_label.setStyleSheet("""
        color: white;
        font-size: 18px;
        font-weight: bold;
    """)
    header_layout.addWidget(title_label)
    
    header_layout.addStretch()
    
    # Patient selector
    patient_label = QLabel("Patient:")
    patient_label.setStyleSheet("color: white; font-weight: bold;")
    header_layout.addWidget(patient_label)
    
    self.patient_combo = QComboBox()
    self.patient_combo.setMinimumWidth(250)
    self.patient_combo.setStyleSheet("""
        QComboBox {
            background-color: white;
            border: 2px solid #0ea5c7;
            border-radius: 4px;
            padding: 8px;
            font-size: 12px;
        }
    """)
    header_layout.addWidget(self.patient_combo)
    
    # Current examination display
    self.current_exam_label = QLabel("No examination selected")
    self.current_exam_label.setStyleSheet("""
        color: white;
        font-weight: bold;
        background-color: rgba(255, 255, 255, 0.2);
        padding: 8px;
        border-radius: 4px;
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
                color: #19c5e5;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f0f9fc;
            }
        """)
        header_layout.addWidget(btn)
    
    return header_widget

def create_left_panel(self) -> QWidget:
    """Create left panel with examination and charts."""
    left_widget = QWidget()
    left_layout = QVBoxLayout(left_widget)
    left_layout.setContentsMargins(0, 0, 0, 0)
    left_layout.setSpacing(10)
    
    # Examination Management Panel
    self.examination_panel = DentalExaminationPanel()
    self.examination_panel.setMaximumHeight(200)
    left_layout.addWidget(self.examination_panel)
    
    # Dual Chart Container
    charts_container = self.create_dual_charts()
    charts_container.setMaximumHeight(400)
    left_layout.addWidget(charts_container)
    
    # Visit Entry Panel
    self.visit_entry_panel = VisitEntryPanel()
    self.visit_entry_panel.setMaximumHeight(250)
    left_layout.addWidget(self.visit_entry_panel)
    
    return left_widget

def create_dual_charts(self) -> QWidget:
    """Create dual dental charts (Patient/Doctor)."""
    charts_widget = QFrame()
    charts_widget.setStyleSheet("""
        QFrame {
            border: 2px solid #19c5e5;
            border-radius: 8px;
            background-color: #f8f9fa;
        }
    """)
    
    charts_layout = QHBoxLayout(charts_widget)
    charts_layout.setContentsMargins(10, 10, 10, 10)
    charts_layout.setSpacing(15)
    
    # Patient Problems Chart
    self.patient_chart_panel = DentalChartPanel(
        chart_type="patient",
        title="Patient Problems Chart"
    )
    charts_layout.addWidget(self.patient_chart_panel)
    
    # Separator line
    separator = QFrame()
    separator.setFrameShape(QFrame.VLine)
    separator.setFrameShadow(QFrame.Sunken)
    separator.setStyleSheet("color: #19c5e5;")
    charts_layout.addWidget(separator)
    
    # Doctor Findings Chart
    self.doctor_chart_panel = DentalChartPanel(
        chart_type="doctor", 
        title="Doctor Findings Chart"
    )
    charts_layout.addWidget(self.doctor_chart_panel)
    
    return charts_widget

def create_right_panel(self) -> QWidget:
    """Create right panel with records and episodes."""
    right_widget = QWidget()
    right_layout = QVBoxLayout(right_widget)
    right_layout.setContentsMargins(0, 0, 0, 0)
    right_layout.setSpacing(10)
    
    # Visit Records Panel (Top 50%)
    self.visit_records_panel = VisitRecordsPanel()
    right_layout.addWidget(self.visit_records_panel)
    
    # Treatment Episodes Panel (Bottom 50%)
    self.treatment_episodes_panel = TreatmentEpisodesPanel()
    right_layout.addWidget(self.treatment_episodes_panel)
    
    return right_widget

def create_status_bar(self) -> QWidget:
    """Create status bar with current info."""
    status_widget = QFrame()
    status_widget.setFixedHeight(30)
    status_widget.setStyleSheet("""
        QFrame {
            background-color: #e6f9fd;
            border-top: 1px solid #19c5e5;
        }
    """)
    
    status_layout = QHBoxLayout(status_widget)
    status_layout.setContentsMargins(10, 5, 10, 5)
    
    # Status labels
    self.exam_status_label = QLabel("Ready")
    self.total_amount_label = QLabel("Total: ₹0.00") 
    self.last_saved_label = QLabel("Never saved")
    
    for label in [self.exam_status_label, self.total_amount_label, self.last_saved_label]:
        label.setStyleSheet("color: #0ea5c7; font-size: 11px;")
    
    status_layout.addWidget(self.exam_status_label)
    status_layout.addStretch()
    status_layout.addWidget(self.total_amount_label)
    status_layout.addStretch()
    status_layout.addWidget(self.last_saved_label)
    
    return status_widget
```

##### Step 3.3.4: Signal Connection and Data Flow
```python
def connect_signals(self):
    """Connect all component signals for data flow."""
    
    # === PATIENT SELECTION ===
    self.patient_combo.currentTextChanged.connect(self.on_patient_selected)
    
    # === EXAMINATION MANAGEMENT ===
    self.examination_panel.examination_saved.connect(self.on_examination_saved)
    self.examination_panel.examination_selected.connect(self.on_examination_selected)
    
    # === DENTAL CHARTS ===
    self.patient_chart_panel.tooth_selected.connect(
        lambda tooth_num: self.on_tooth_selected(tooth_num, "patient")
    )
    self.doctor_chart_panel.tooth_selected.connect(
        lambda tooth_num: self.on_tooth_selected(tooth_num, "doctor")
    )
    self.patient_chart_panel.status_changed.connect(self.on_tooth_status_changed)
    self.doctor_chart_panel.status_changed.connect(self.on_tooth_status_changed)
    
    # === VISIT MANAGEMENT ===
    self.visit_entry_panel.visit_added.connect(self.on_visit_added)
    self.visit_records_panel.visit_selected.connect(self.on_visit_selected)
    self.visit_records_panel.total_amount_changed.connect(self.update_total_amount)
    
    # === TREATMENT EPISODES ===
    self.treatment_episodes_panel.episode_saved.connect(self.on_episode_saved)
    self.treatment_episodes_panel.episode_selected.connect(self.on_episode_selected)
    
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
        self.examination_panel.set_patient(self.current_patient_id)
        self.visit_records_panel.set_patient(self.current_patient_id)
        self.treatment_episodes_panel.set_patient(self.current_patient_id)
        
        # Clear chart selections
        self.clear_tooth_selections()
        
        # Load latest examination
        self.load_latest_examination()
        
        # Emit signal
        self.patient_changed.emit(self.current_patient_id)
        
        # Update status
        self.exam_status_label.setText(f"Patient #{self.current_patient_id} loaded")

def on_examination_selected(self, examination_data):
    """Handle examination selection."""
    self.current_examination_id = examination_data.get('id')
    
    if self.current_examination_id:
        # Update UI components with examination context
        self.visit_records_panel.set_examination(self.current_examination_id)
        self.treatment_episodes_panel.set_examination(self.current_examination_id)
        
        # Load dental chart data for this examination
        self.load_examination_dental_data()
        
        # Update current examination display
        exam_date = examination_data.get('examination_date', '')
        chief_complaint = examination_data.get('chief_complaint', '')[:30]
        self.current_exam_label.setText(f"Exam #{self.current_examination_id} - {exam_date} - {chief_complaint}...")
        
        # Emit signal
        self.examination_changed.emit(self.current_examination_id)

def on_tooth_selected(self, tooth_number, chart_type):
    """Handle tooth selection from either chart."""
    self.selected_tooth_number = tooth_number
    self.selected_chart_type = chart_type
    
    # Clear selection from the other chart
    if chart_type == "patient":
        self.doctor_chart_panel.clear_selection()
    else:
        self.patient_chart_panel.clear_selection()
    
    # Load tooth history for selected tooth and chart type
    self.load_tooth_history(tooth_number, chart_type)
    
    # Update visit entry panel with selected tooth
    self.visit_entry_panel.set_selected_tooth(tooth_number)
    
    # Emit signal
    self.tooth_selected.emit(tooth_number, chart_type)

def on_tooth_status_changed(self, tooth_number, new_status, chart_type):
    """Handle tooth status change."""
    if not self.current_patient_id or not self.current_examination_id:
        return
    
    # Save tooth history record
    history_data = {
        'patient_id': self.current_patient_id,
        'examination_id': self.current_examination_id,
        'tooth_number': tooth_number,
        'record_type': f'{chart_type}_problem' if chart_type == 'patient' else f'{chart_type}_finding',
        'status': new_status,
        'description': f"Status changed to {new_status}",
        'date_recorded': date.today()
    }
    
    # Save using tooth history service
    tooth_history_service.add_tooth_history(history_data)
    
    # Update tooth history display
    self.load_tooth_history(tooth_number, chart_type)
    
    # Update status
    self.exam_status_label.setText(f"Tooth #{tooth_number} status updated")

def on_visit_added(self, visit_data):
    """Handle new visit addition."""
    if not self.current_patient_id or not self.current_examination_id:
        return
    
    # Add examination context to visit data
    visit_data['patient_id'] = self.current_patient_id
    visit_data['examination_id'] = self.current_examination_id
    
    # Save visit record
    result = visit_records_service.add_visit_record(visit_data)
    
    if result.get('success'):
        # Refresh visit records display
        self.visit_records_panel.add_visit_record(visit_data)
        
        # Update affected teeth in charts if specified
        affected_teeth = visit_data.get('affected_teeth', [])
        for tooth_num in affected_teeth:
            # Add tooth history entries for affected teeth
            self.add_tooth_history_from_visit(tooth_num, visit_data)
        
        # Clear visit entry form
        self.visit_entry_panel.clear_form()
        
        # Update status
        amount = visit_data.get('cost', 0)
        self.exam_status_label.setText(f"Visit added - ₹{amount:.2f}")
        
        # Emit signal
        self.visit_added.emit(visit_data)

def load_examination_dental_data(self):
    """Load dental chart data for current examination."""
    if not self.current_patient_id or not self.current_examination_id:
        return
    
    # Load tooth history for current examination
    patient_history = tooth_history_service.get_examination_tooth_history(
        self.current_patient_id, 
        self.current_examination_id,
        'patient_problem'
    )
    
    doctor_history = tooth_history_service.get_examination_tooth_history(
        self.current_patient_id,
        self.current_examination_id, 
        'doctor_finding'
    )
    
    # Update charts with loaded data
    self.patient_chart_panel.load_tooth_data(patient_history)
    self.doctor_chart_panel.load_tooth_data(doctor_history)

def save_all_changes(self):
    """Save all pending changes across components."""
    try:
        # Save examination if modified
        if self.examination_panel.has_unsaved_changes():
            self.examination_panel.save_examination()
        
        # Save any pending tooth changes
        self.patient_chart_panel.save_pending_changes()
        self.doctor_chart_panel.save_pending_changes()
        
        # Update timestamp
        from datetime import datetime
        self.last_saved_label.setText(f"Saved: {datetime.now().strftime('%H:%M:%S')}")
        
        # Update status
        self.exam_status_label.setText("All changes saved successfully")
        
        # Emit signal
        self.data_saved.emit()
        
    except Exception as e:
        QMessageBox.critical(self, "Save Error", f"Failed to save changes: {str(e)}")
```

##### Step 3.3.5: Data Loading and Management
```python
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
        # Import patient service
        from ..services.patient_service import patient_service
        
        patients = patient_service.get_all_patients()
        
        self.patient_combo.clear()
        self.patient_combo.addItem("Select a patient...", None)
        
        for patient in patients:
            display_text = f"{patient['full_name']} - ID: {patient['patient_id']}"
            self.patient_combo.addItem(display_text, patient)
            
    except Exception as e:
        logger.error(f"Error loading patients: {str(e)}")

def load_latest_examination(self):
    """Load the most recent examination for current patient."""
    if not self.current_patient_id:
        return
    
    # Get latest examination
    examinations = dental_examination_service.get_patient_examinations(self.current_patient_id)
    
    if examinations:
        # Load most recent examination
        latest_exam = examinations[0]  # Assuming sorted by date desc
        self.examination_panel.load_examination(latest_exam)
        self.on_examination_selected(latest_exam)
    else:
        # No examinations - prepare for new one
        self.current_examination_id = None
        self.current_exam_label.setText("No examinations - Create new")

def apply_global_styles(self):
    """Apply consistent styling across the widget."""
    self.setStyleSheet("""
        QWidget {
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 12px;
        }
        
        QGroupBox {
            font-weight: bold;
            border: 2px solid #19c5e5;
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 15px;
            background-color: white;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 10px;
            color: #19c5e5;
            font-size: 14px;
        }
        
        QPushButton {
            background-color: #19c5e5;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            font-weight: bold;
        }
        
        QPushButton:hover {
            background-color: #0ea5c7;
        }
        
        QPushButton:disabled {
            background-color: #cccccc;
            color: #666666;
        }
    """)
```

#### 3.4 Implementation Steps Summary

**Step 1**: Backup current implementation to `dental_chart_legacy.py`
**Step 2**: Create new `AdvancedDentalChart` class with complete UI structure
**Step 3**: Integrate all Phase 2 components into layout
**Step 4**: Implement signal connections for data flow
**Step 5**: Add data loading and management methods
**Step 6**: Test component integration and data persistence
**Step 7**: Add error handling and validation
**Step 8**: Update main application to use new dental chart

#### 3.5 Integration Benefits

1. **Professional Workflow**: Matches real dental practice procedures
2. **Comprehensive Tracking**: Patient problems + Doctor findings in dual charts
3. **Examination Context**: All data linked to specific examinations
4. **Visit Management**: Complete visit tracking with cost calculation
5. **Treatment Planning**: Episode management with progress tracking
6. **Data Persistence**: All changes automatically saved with proper relationships
7. **Modern UI**: Professional interface with consistent #19c5e5 theming

#### 3.6 Testing Requirements

1. **Component Integration**: Verify all Phase 2 components work together
2. **Data Flow**: Test signal connections and data persistence
3. **Patient Workflow**: Complete patient examination workflow testing
4. **Error Handling**: Test edge cases and error scenarios
5. **Performance**: Ensure responsive UI with large datasets

### Phase 4: Data Integration

#### 4.1 Data Loading
- Load patient's existing tooth history
- Populate both charts with current statuses
- Load visit records history
- Calculate totals

#### 4.2 Data Saving
- Save tooth status changes to history
- Save visit records with affected teeth
- Update chart records with latest status
- Maintain separate patient/doctor logs

#### 4.3 Synchronization
- Ensure both charts reflect current tooth status
- Update history when status changes
- Link visit records to tooth histories

## Key Features Implementation

### 1. **Tooth Selection & History Display**
```python
def select_tooth(self, tooth_number):
    """Update both charts to show selected tooth history"""
    # Load patient problems for this tooth
    # Load doctor findings for this tooth
    # Display current status
    # Update both history areas
```

### 2. **Status Change Tracking**
```python
def update_tooth_status(self, tooth_number, status, record_type):
    """Track status changes with timestamp"""
    # Add entry to tooth_history table
    # Update visual appearance
    # Refresh history display
```

### 3. **Visit Record Creation**
```python
def add_visit_record(self):
    """Create new visit record and update tooth histories"""
    # Link visit to current active examination
    # Create visit record with examination_id
    # Add patient problems to tooth histories
    # Add doctor findings to tooth histories
    # Update affected teeth statuses
    # Update examination total amount
    # Refresh all displays
```

### 4. **Dental Examination Management**
```python
def create_new_examination(self, patient_id, chief_complaint, examination_date):
    """Create new dental examination for patient"""
    # Create new dental_examinations record
    # Set as current active examination
    # Clear charts for new examination context
    # Initialize examination form
    
def load_examination(self, examination_id):
    """Load specific examination data"""
    # Load examination details
    # Load related visit records
    # Load tooth history for this examination
    # Update all UI components with examination context
    
def save_examination_findings(self, examination_id, findings_data):
    """Save examination findings and diagnosis"""
    # Update examination record with findings
    # Link any new tooth status changes to this examination
    # Update dental chart records with examination_id
```
```python
def add_visit_record(self):
    """Create new visit record and update tooth histories"""
    # Create visit record
    # Add patient problems to tooth histories
    # Add doctor findings to tooth histories
    # Update affected teeth statuses
    # Refresh all displays
```

## Design Specifications

### Primary UI Color Scheme
- **Primary Color**: `#19c5e5` (Bright cyan/turquoise)
- **Primary Hover**: `#14a8c4` (Darker cyan for hover states)
- **Primary Light**: `#e6f9fd` (Light cyan for backgrounds)
- **Primary Dark**: `#0f7a8f` (Dark cyan for text/borders)

### Tooth Numbering Display Format
- Display format: `quadrant.position` (e.g., 11 → (1,1), 41 → (4,1))
- **Quadrant 1 (Upper Right)**: 18→(1,8), 17→(1,7), ..., 11→(1,1)
- **Quadrant 2 (Upper Left)**: 21→(2,1), 22→(2,2), ..., 28→(2,8)
- **Quadrant 3 (Lower Left)**: 31→(3,1), 32→(3,2), ..., 38→(3,8)
- **Quadrant 4 (Lower Right)**: 41→(4,1), 42→(4,2), ..., 48→(4,8)

### Comprehensive Status Types & Color Coding

#### 1. Teeth & Hard Tissue Findings:
1. **Normal (P.I. / D.C.)** - `#2ecc71` (Green)
   - Periodontal Index / Dental Condition normal
2. **Caries (Incipient)** - `#f1c40f` (Yellow)
   - Early stage decay
3. **Caries (Moderate)** - `#f39c12` (Orange)
   - Moderate decay progression
4. **Caries (Deep)** - `#e74c3c` (Red)
   - Deep cavity requiring immediate attention
5. **Caries (Recurrent)** - `#c0392b` (Dark Red)
   - Decay around existing fillings
6. **Attrition** - `#8e44ad` (Purple)
   - Tooth wear due to grinding
7. **Abrasion** - `#9b59b6` (Light Purple)
   - Tooth wear due to brushing/habits
8. **Erosion** - `#6c3483` (Dark Purple)
   - Chemical wear from acids
9. **Fractured Tooth (Ellis I)** - `#e67e22` (Orange)
   - Enamel fracture only
10. **Fractured Tooth (Ellis II)** - `#d35400` (Dark Orange)
    - Enamel and dentin fracture
11. **Fractured Tooth (Ellis III)** - `#a0522d` (Brown)
    - Pulp exposure fracture
12. **Chipped Enamel** - `#f4d03f` (Light Yellow)
    - Minor enamel chip
13. **Hypoplastic Enamel** - `#85929e` (Gray)
    - Developmental defect
14. **Discoloration/Stains** - `#95a5a6` (Light Gray)
    - Extrinsic or intrinsic staining
15. **Fluorosis** - `#d5dbdb` (Very Light Gray)
    - Fluoride-induced mottling
16. **Calculus** - `#566573` (Dark Gray)
    - Tartar deposits

#### 2. Pulpal & Periapical Findings:
17. **Pulpitis (Reversible)** - `#ff6b6b` (Light Red)
    - Treatable pulp inflammation
18. **Pulpitis (Irreversible)** - `#ee5a52` (Red)
    - Requires root canal treatment
19. **Periapical Abscess** - `#8e44ad` (Purple)
    - Infection at root tip
20. **Periapical Granuloma** - `#af7ac5` (Lavender)
    - Chronic inflammatory lesion
21. **Pulp Necrosis** - `#2c3e50` (Dark Blue-Gray)
    - Dead tooth pulp
22. **Non-vital Tooth** - `#34495e` (Dark Gray)
    - Confirmed dead tooth
23. **Sinus Tract** - `#7d3c98` (Dark Purple)
    - Pus drainage pathway

#### 3. Periodontal Findings:
24. **Gingivitis (Mild)** - `#f8c471` (Light Orange)
    - Mild gum inflammation
25. **Gingivitis (Moderate)** - `#f5b041` (Orange)
    - Moderate gum inflammation
26. **Gingivitis (Severe)** - `#e67e22` (Dark Orange)
    - Severe gum inflammation
27. **Gingival Recession** - `#dc7633` (Brown-Orange)
    - Gum tissue loss
28. **Periodontal Pocket (Shallow)** - `#e74c3c` (Red)
    - 4-6mm pocket depth
29. **Periodontal Pocket (Deep)** - `#c0392b` (Dark Red)
    - >6mm pocket depth
30. **Periodontitis (Chronic)** - `#922b21` (Very Dark Red)
    - Chronic gum disease
31. **Periodontitis (Aggressive)** - `#641e16` (Maroon)
    - Rapid bone loss
32. **Mobility (Grade I)** - `#f7dc6f` (Light Yellow)
    - Slight tooth movement
33. **Mobility (Grade II)** - `#f4d03f` (Yellow)
    - Moderate tooth movement
34. **Mobility (Grade III)** - `#f1c40f` (Dark Yellow)
    - Severe tooth movement
35. **Furcation Involvement** - `#d68910` (Golden)
    - Root separation involvement

#### 4. Soft Tissue/Oral Mucosa:
36. **Ulcer (Aphthous)** - `#ec7063` (Pink-Red)
    - Canker sore
37. **Ulcer (Traumatic)** - `#e8743b` (Orange-Red)
    - Injury-related ulcer
38. **Leukoplakia** - `#f8f9fa` (White)
    - White patch lesion
39. **Erythroplakia** - `#e74c3c` (Red)
    - Red patch lesion
40. **Lichen Planus** - `#bb8fce` (Light Purple)
    - Autoimmune condition
41. **Candidiasis** - `#f7dc6f` (Cream)
    - Oral fungal infection
42. **Hyperplasia** - `#aed6f1` (Light Blue)
    - Gingival overgrowth
43. **Pigmentation** - `#5d6d7e` (Blue-Gray)
    - Melanin deposits

#### 5. Other Clinical Observations:
44. **Malocclusion** - `#85c1e9` (Sky Blue)
    - Bite problems
45. **Impacted Tooth** - `#3498db` (Blue)
    - Unerupted tooth
46. **Missing Tooth** - `#34495e` (Dark Gray)
    - Absent tooth
47. **Retained Deciduous** - `#a9dfbf` (Light Green)
    - Baby tooth not shed
48. **Diastema** - `#82e0aa` (Green)
    - Gap between teeth
49. **TMJ Findings** - `#f06292` (Pink)
    - Jaw joint issues
50. **Halitosis** - `#ffab91` (Peach)
    - Bad breath
51. **Custom** - `#19c5e5` (Primary Color)
    - User-defined status

#### Custom Status Management:
- **Add Custom Label**: Dropdown includes "+ Add Custom" option
- **Custom Status Storage**: Store in separate `custom_statuses` table
- **Color Assignment**: Automatically assign from predefined palette or allow user selection
- **Status Persistence**: Custom statuses saved per clinic/user

### Enhanced Status Dropdown Design:
```python
# Core Teeth & Hard Tissue Findings
teeth_hard_tissue = [
    ("normal", "Normal (P.I. / D.C.)", "#2ecc71"),
    ("caries_incipient", "Caries (Incipient)", "#f1c40f"),
    ("caries_moderate", "Caries (Moderate)", "#f39c12"),
    ("caries_deep", "Caries (Deep)", "#e74c3c"),
    ("caries_recurrent", "Caries (Recurrent)", "#c0392b"),
    ("attrition", "Attrition", "#8e44ad"),
    ("abrasion", "Abrasion", "#9b59b6"),
    ("erosion", "Erosion", "#6c3483"),
    ("fracture_ellis1", "Fractured Tooth (Ellis I)", "#e67e22"),
    ("fracture_ellis2", "Fractured Tooth (Ellis II)", "#d35400"),
    ("fracture_ellis3", "Fractured Tooth (Ellis III)", "#a0522d"),
    ("chipped_enamel", "Chipped Enamel", "#f4d03f"),
    ("hypoplastic_enamel", "Hypoplastic Enamel", "#85929e"),
    ("discoloration", "Discoloration/Stains", "#95a5a6"),
    ("fluorosis", "Fluorosis", "#d5dbdb"),
    ("calculus", "Calculus", "#566573"),
]

# Pulpal & Periapical Findings
pulpal_findings = [
    ("pulpitis_reversible", "Pulpitis (Reversible)", "#ff6b6b"),
    ("pulpitis_irreversible", "Pulpitis (Irreversible)", "#ee5a52"),
    ("periapical_abscess", "Periapical Abscess", "#8e44ad"),
    ("periapical_granuloma", "Periapical Granuloma", "#af7ac5"),
    ("pulp_necrosis", "Pulp Necrosis", "#2c3e50"),
    ("non_vital", "Non-vital Tooth", "#34495e"),
    ("sinus_tract", "Sinus Tract", "#7d3c98"),
]

# Periodontal Findings
periodontal_findings = [
    ("gingivitis_mild", "Gingivitis (Mild)", "#f8c471"),
    ("gingivitis_moderate", "Gingivitis (Moderate)", "#f5b041"),
    ("gingivitis_severe", "Gingivitis (Severe)", "#e67e22"),
    ("gingival_recession", "Gingival Recession", "#dc7633"),
    ("pocket_shallow", "Periodontal Pocket (Shallow)", "#e74c3c"),
    ("pocket_deep", "Periodontal Pocket (Deep)", "#c0392b"),
    ("periodontitis_chronic", "Periodontitis (Chronic)", "#922b21"),
    ("periodontitis_aggressive", "Periodontitis (Aggressive)", "#641e16"),
    ("mobility_grade1", "Mobility (Grade I)", "#f7dc6f"),
    ("mobility_grade2", "Mobility (Grade II)", "#f4d03f"),
    ("mobility_grade3", "Mobility (Grade III)", "#f1c40f"),
    ("furcation", "Furcation Involvement", "#d68910"),
]

# Soft Tissue/Oral Mucosa
soft_tissue_findings = [
    ("ulcer_aphthous", "Ulcer (Aphthous)", "#ec7063"),
    ("ulcer_traumatic", "Ulcer (Traumatic)", "#e8743b"),
    ("leukoplakia", "Leukoplakia", "#f8f9fa"),
    ("erythroplakia", "Erythroplakia", "#e74c3c"),
    ("lichen_planus", "Lichen Planus", "#bb8fce"),
    ("candidiasis", "Candidiasis", "#f7dc6f"),
    ("hyperplasia", "Hyperplasia", "#aed6f1"),
    ("pigmentation", "Pigmentation", "#5d6d7e"),
]

# Other Clinical Observations
other_findings = [
    ("malocclusion", "Malocclusion", "#85c1e9"),
    ("impacted", "Impacted Tooth", "#3498db"),
    ("missing", "Missing Tooth", "#34495e"),
    ("retained_deciduous", "Retained Deciduous", "#a9dfbf"),
    ("diastema", "Diastema", "#82e0aa"),
    ("tmj_findings", "TMJ Findings", "#f06292"),
    ("halitosis", "Halitosis", "#ffab91"),
    ("custom", "+ Add Custom", "#19c5e5")
]

# Combined status options (51 total)
status_options = (teeth_hard_tissue + pulpal_findings + 
                 periodontal_findings + soft_tissue_findings + 
                 other_findings)
```

### Data Flow
1. User selects patient → Load patient data & examination history
2. **Examination Selection**: User selects current examination OR creates new examination
3. **Examination Context**: All data filtered by current examination (tooth history, visits, etc.)
4. Charts display tooth statuses for selected examination
5. User selects tooth → Display tooth history for current examination
6. User changes status → Update history + visual linked to current examination
7. **New Examination**: Patient returns with new problem → Create new examination record
8. User adds visit → Create record linked to current examination
9. **Examination Completion**: Save findings, diagnosis, treatment plan
10. All changes auto-save to database with proper examination linking

## Benefits of New System

1. **Comprehensive Examination Tracking**: Each patient visit creates separate examination records
2. **Timeline Management**: Track patient problems and treatments across multiple time periods
3. **Independent Problem Tracking**: New problems don't interfere with previous examination data
4. **Complete History**: Dental professionals can review all past examinations and treatments
5. **Contextual Data**: All tooth status changes and visits linked to specific examinations
6. **Professional Workflow**: Matches real dental practice workflow with proper examination documentation
7. **Financial Separation**: Each examination period maintains its own visit and cost records

## Files to Modify/Create

### New Files:
- `app/database/models/dental_examination.py`
- `app/database/models/tooth_history.py`
- `app/database/models/visit_record.py`
- `app/database/models/custom_status.py`
- `app/services/dental_examination_service.py`
- `app/services/tooth_history_service.py`
- `app/services/visit_records_service.py`
- `app/services/custom_status_service.py`
- `app/ui/components/enhanced_tooth_widget.py`
- `app/ui/components/dental_chart_panel.py`
- `app/ui/components/dental_examination_panel.py`
- `app/ui/components/new_examination_dialog.py`
- `app/ui/components/visit_entry_panel.py`
- `app/ui/components/visit_records_panel.py`
- `app/ui/components/custom_status_dialog.py`
- `app/utils/tooth_numbering.py`

### Modified Files:
- `app/database/models.py` (add new models)
- `app/ui/dental_chart.py` (complete rewrite)
- `app/services/dental_service.py` (enhanced functionality)
- `app/database/database.py` (migration support)

## Timeline Estimate
- **Phase 1**: Database Layer (2-3 hours)
- **Phase 2**: UI Components (4-5 hours)
- **Phase 3**: Integration (2-3 hours)
- **Phase 4**: Testing & Polish (1-2 hours)
- **Total**: 9-13 hours

This plan provides a complete roadmap for implementing the enhanced dental chart system as demonstrated in the `ui1.py` file while maintaining compatibility with the existing codebase.
