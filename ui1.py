import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QGridLayout, QLabel, QTextEdit, 
                               QLineEdit, QPushButton, QFrame, QScrollArea,
                               QCheckBox, QDateEdit, QGroupBox, QComboBox)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont, QPalette, QColor
from datetime import datetime

class ToothWidget(QWidget):
    def __init__(self, tooth_number, quadrant, parent_widget):
        super().__init__()
        self.tooth_number = tooth_number
        self.quadrant = quadrant  # 'upper_right', 'upper_left', 'lower_right', 'lower_left'
        self.parent_widget = parent_widget
        self.full_tooth_number = self.get_full_tooth_number()
        
        # Simple vertical layout
        layout = QVBoxLayout(self)
        layout.setSpacing(1)
        layout.setContentsMargins(1, 1, 1, 1)
        
        # Combined tooth button with number
        self.tooth_button = QPushButton(str(tooth_number))
        self.tooth_button.setFixedSize(40, 40)
        self.tooth_button.clicked.connect(self.on_tooth_click)
        layout.addWidget(self.tooth_button)
        
        # Simple status dropdown - compact
        self.status_combo = QComboBox()
        self.status_combo.setFixedSize(40, 20)
        self.status_combo.addItems(['N', 'P', 'F', 'R', 'M', 'C'])  # Simplified labels
        self.status_combo.setToolTip("N=Normal, P=Problem, F=Fixed, R=Root Canal, M=Missing, C=Crown")
        self.status_combo.currentTextChanged.connect(self.on_status_change)
        layout.addWidget(self.status_combo)
        
        self.update_tooth_color()
    
    def get_full_tooth_number(self):
        """Convert simple numbering to full dental numbering"""
        if self.quadrant == 'upper_right':
            return 10 + self.tooth_number  # 11-18
        elif self.quadrant == 'upper_left':
            return 20 + self.tooth_number  # 21-28
        elif self.quadrant == 'lower_left':
            return 30 + self.tooth_number  # 31-38
        elif self.quadrant == 'lower_right':
            return 40 + self.tooth_number  # 41-48
        return self.tooth_number
    
    def on_tooth_click(self):
        self.parent_widget.select_tooth(self.full_tooth_number)
    
    def on_status_change(self):
        self.update_tooth_color()
        status_map = {'N': 'Normal', 'P': 'Problem', 'F': 'Fixed', 'R': 'Root Canal', 'M': 'Missing', 'C': 'Crown'}
        full_status = status_map.get(self.status_combo.currentText(), 'Normal')
        self.parent_widget.update_tooth_status(self.full_tooth_number, full_status)
    
    def update_tooth_color(self):
        status = self.status_combo.currentText()
        color_map = {
            'N': '#e8f5e8',      # Light green - Normal
            'P': '#ffebee',      # Light red - Problem  
            'F': '#e3f2fd',      # Light blue - Fixed
            'R': '#fff3e0',      # Light orange - Root Canal
            'M': '#f5f5f5',      # Light gray - Missing
            'C': '#fffde7'       # Light yellow - Crown
        }
        
        border_color_map = {
            'N': '#4caf50',      # Green
            'P': '#f44336',      # Red
            'F': '#2196f3',      # Blue  
            'R': '#ff9800',      # Orange
            'M': '#9e9e9e',      # Gray
            'C': '#ffeb3b'       # Yellow
        }
        
        bg_color = color_map.get(status, '#e8f5e8')
        border_color = border_color_map.get(status, '#4caf50')
        
        self.tooth_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                border: 3px solid {border_color};
                border-radius: 8px;
                font-weight: bold;
                font-size: 12px;
                color: #333;
            }}
            QPushButton:hover {{
                background-color: {border_color};
                color: white;
            }}
            QPushButton:pressed {{
                background-color: #333;
            }}
        """)

class VisitRecord:
    def __init__(self, date, amount, problems, diagnosis, treatment, advice, teeth):
        self.date = date
        self.amount = amount
        self.problems = problems
        self.diagnosis = diagnosis
        self.treatment = treatment
        self.advice = advice
        self.teeth = teeth

class DentalClinicApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🦷 Dental Clinic System")
        self.setGeometry(100, 100, 1400, 800)
        self.setMinimumSize(1200, 600)
        
        # Sample data
        self.selected_tooth = 21  # Default selection
        self.tooth_widgets = {}
        self.tooth_statuses = {}
        
        # Initialize with some sample data
        self.tooth_statuses = {
            21: 'Fixed',
            26: 'Problem', 
            34: 'Root Canal',
            18: 'Missing'
        }
        
        self.visit_records = [
            VisitRecord("15-08-2025", 2500, "Pain in upper molar", 
                       "Caries in tooth #26", "Composite filling", 
                       "Avoid hard foods 24h", [26]),
            VisitRecord("19-08-2025", 2000, "Swelling gums", 
                       "Gum infection tooth #21", "Cleaning & Antibiotics", 
                       "Salt water rinse", [21])
        ]
        
        # Patient and doctor findings
        self.patient_findings = {
            21: ["[19-08-25] Swelling gums", "[15-08-25] Sensitivity"],
            26: ["[15-08-25] Pain in upper molar"]
        }
        
        self.doctor_findings = {
            21: ["[19-08-25] Gum infection treated", "[15-08-25] Cleaning done"],
            26: ["[15-08-25] Caries filled"]
        }
        
        self.init_ui()
    
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main scroll area
        main_scroll = QScrollArea()
        main_scroll.setWidgetResizable(True)
        main_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        main_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        scroll_content = QWidget()
        main_layout = QVBoxLayout(scroll_content)
        
        main_scroll.setWidget(scroll_content)
        central_widget_layout = QVBoxLayout(central_widget)
        central_widget_layout.addWidget(main_scroll)
        
        # Title
        title_label = QLabel("🦷 Dental Clinic System")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setStyleSheet("padding: 10px; background-color: #4CAF50; color: white; border-radius: 5px; margin-bottom: 10px;")
        main_layout.addWidget(title_label)
        
        # Dental charts section
        charts_layout = QHBoxLayout()
        
        # Patient Problems Chart
        patient_panel = self.create_dental_chart_panel("Patient Problems", "patient")
        charts_layout.addWidget(patient_panel)
        
        # Doctor Findings Chart
        doctor_panel = self.create_dental_chart_panel("Doctor Findings", "doctor")
        charts_layout.addWidget(doctor_panel)
        
        main_layout.addLayout(charts_layout)
        
        # Visit entry and records
        visit_entry_panel = self.create_visit_entry_panel()
        main_layout.addWidget(visit_entry_panel)
        
        records_panel = self.create_visit_records_panel()
        main_layout.addWidget(records_panel)
        
        # Update displays
        self.update_tooth_displays()
    
    def create_dental_chart_panel(self, title, panel_type):
        group_box = QGroupBox(title)
        group_box.setMinimumWidth(600)
        group_box.setMinimumHeight(350)
        
        layout = QVBoxLayout(group_box)
        
        # Dental chart
        chart_layout = QVBoxLayout()
        
        # Upper jaw label
        upper_label = QLabel("Upper Jaw (Right 8-1 | Left 1-8)")
        upper_label.setFont(QFont("Arial", 10, QFont.Bold))
        upper_label.setAlignment(Qt.AlignCenter)
        chart_layout.addWidget(upper_label)
        
        # Upper jaw teeth
        upper_layout = QHBoxLayout()
        upper_layout.setSpacing(2)
        
        # Upper right (18-11)
        for i in range(8, 0, -1):
            tooth_widget = ToothWidget(i, 'upper_right', self)
            self.tooth_widgets[10 + i] = tooth_widget
            upper_layout.addWidget(tooth_widget)
        
        # Separator
        separator1 = QLabel(" | ")
        separator1.setFont(QFont("Arial", 16, QFont.Bold))
        separator1.setAlignment(Qt.AlignCenter)
        upper_layout.addWidget(separator1)
        
        # Upper left (21-28)
        for i in range(1, 9):
            tooth_widget = ToothWidget(i, 'upper_left', self)
            self.tooth_widgets[20 + i] = tooth_widget
            upper_layout.addWidget(tooth_widget)
            
        chart_layout.addLayout(upper_layout)
        
        # Lower jaw label  
        lower_label = QLabel("Lower Jaw (Right 8-1 | Left 1-8)")
        lower_label.setFont(QFont("Arial", 10, QFont.Bold))
        lower_label.setAlignment(Qt.AlignCenter)
        chart_layout.addWidget(lower_label)
        
        # Lower jaw teeth
        lower_layout = QHBoxLayout()
        lower_layout.setSpacing(2)
        
        # Lower right (48-41)
        for i in range(8, 0, -1):
            tooth_widget = ToothWidget(i, 'lower_right', self)
            self.tooth_widgets[40 + i] = tooth_widget
            lower_layout.addWidget(tooth_widget)
        
        # Separator
        separator2 = QLabel(" | ")
        separator2.setFont(QFont("Arial", 16, QFont.Bold))
        separator2.setAlignment(Qt.AlignCenter)
        lower_layout.addWidget(separator2)
        
        # Lower left (31-38)
        for i in range(1, 9):
            tooth_widget = ToothWidget(i, 'lower_left', self)
            self.tooth_widgets[30 + i] = tooth_widget
            lower_layout.addWidget(tooth_widget)
            
        chart_layout.addLayout(lower_layout)
        layout.addLayout(chart_layout)
        
        # Selected tooth info
        selected_info = QLabel(f"Selected: Tooth #{self.selected_tooth}")
        selected_info.setFont(QFont("Arial", 11, QFont.Bold))
        selected_info.setStyleSheet("padding: 5px; background-color: #f0f0f0; border-radius: 3px;")
        layout.addWidget(selected_info)
        
        if panel_type == "patient":
            self.patient_selected_info = selected_info
        else:
            self.doctor_selected_info = selected_info
        
        # History area
        history_area = QTextEdit()
        history_area.setMinimumHeight(80)
        history_area.setMaximumHeight(120)
        history_area.setReadOnly(True)
        history_area.setStyleSheet("border: 1px solid #ccc; background-color: #fafafa;")
        
        if panel_type == "patient":
            self.patient_history_area = history_area
        else:
            self.doctor_history_area = history_area
            
        layout.addWidget(history_area)
        
        return group_box
    
    def create_visit_entry_panel(self):
        group_box = QGroupBox("New Visit Entry")
        layout = QVBoxLayout(group_box)
        
        # Date and Amount row
        top_row = QHBoxLayout()
        
        top_row.addWidget(QLabel("Date:"))
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setDisplayFormat("dd-MM-yyyy")
        top_row.addWidget(self.date_edit)
        
        top_row.addStretch()
        
        top_row.addWidget(QLabel("Amount: ₹"))
        self.amount_edit = QLineEdit("0")
        self.amount_edit.setFixedWidth(100)
        top_row.addWidget(self.amount_edit)
        
        layout.addLayout(top_row)
        
        # Input fields
        fields_layout = QGridLayout()
        
        fields_layout.addWidget(QLabel("Patient Problems:"), 0, 0)
        self.problems_edit = QLineEdit()
        fields_layout.addWidget(self.problems_edit, 0, 1)
        
        fields_layout.addWidget(QLabel("Diagnosis:"), 1, 0)
        self.diagnosis_edit = QLineEdit()
        fields_layout.addWidget(self.diagnosis_edit, 1, 1)
        
        fields_layout.addWidget(QLabel("Treatment:"), 2, 0)
        self.treatment_edit = QLineEdit()
        fields_layout.addWidget(self.treatment_edit, 2, 1)
        
        fields_layout.addWidget(QLabel("Advice:"), 3, 0)
        self.advice_edit = QLineEdit()
        fields_layout.addWidget(self.advice_edit, 3, 1)
        
        layout.addLayout(fields_layout)
        
        # Teeth selection checkboxes - simplified layout
        tooth_select_label = QLabel("Select Affected Teeth:")
        tooth_select_label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(tooth_select_label)
        
        # Create checkboxes in a more compact layout
        teeth_widget = QWidget()
        teeth_layout = QVBoxLayout(teeth_widget)
        
        # Upper teeth
        upper_widget = QWidget()
        upper_layout = QHBoxLayout(upper_widget)
        upper_layout.addWidget(QLabel("Upper:"))
        
        self.tooth_checkboxes = {}
        
        # Upper right
        for i in range(8, 0, -1):
            tooth_num = 10 + i
            checkbox = QCheckBox(str(i))
            checkbox.setFixedWidth(30)
            self.tooth_checkboxes[tooth_num] = checkbox
            upper_layout.addWidget(checkbox)
        
        upper_layout.addWidget(QLabel("|"))
        
        # Upper left
        for i in range(1, 9):
            tooth_num = 20 + i
            checkbox = QCheckBox(str(i))
            checkbox.setFixedWidth(30)
            self.tooth_checkboxes[tooth_num] = checkbox
            upper_layout.addWidget(checkbox)
        
        teeth_layout.addWidget(upper_widget)
        
        # Lower teeth
        lower_widget = QWidget()
        lower_layout = QHBoxLayout(lower_widget)
        lower_layout.addWidget(QLabel("Lower:"))
        
        # Lower right
        for i in range(8, 0, -1):
            tooth_num = 40 + i
            checkbox = QCheckBox(str(i))
            checkbox.setFixedWidth(30)
            self.tooth_checkboxes[tooth_num] = checkbox
            lower_layout.addWidget(checkbox)
        
        lower_layout.addWidget(QLabel("|"))
        
        # Lower left
        for i in range(1, 9):
            tooth_num = 30 + i
            checkbox = QCheckBox(str(i))
            checkbox.setFixedWidth(30)
            self.tooth_checkboxes[tooth_num] = checkbox
            lower_layout.addWidget(checkbox)
        
        teeth_layout.addWidget(lower_widget)
        layout.addWidget(teeth_widget)
        
        # Add record button
        add_button = QPushButton("➕ Add Visit Record")
        add_button.setStyleSheet("""
            QPushButton { 
                background-color: #4CAF50; 
                color: white; 
                font-weight: bold; 
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        add_button.clicked.connect(self.add_visit_record)
        layout.addWidget(add_button)
        
        return group_box
    
    def create_visit_records_panel(self):
        group_box = QGroupBox("Visit Records History")
        layout = QVBoxLayout(group_box)
        
        # Records scroll area
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        self.records_layout = QVBoxLayout(scroll_widget)
        
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(150)
        scroll_area.setMaximumHeight(250)
        
        layout.addWidget(scroll_area)
        
        # Total amount
        self.total_label = QLabel("💰 Total Amount Paid: ₹0")
        self.total_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.total_label.setStyleSheet("padding: 10px; background-color: #e8f5e8; border: 2px solid #4CAF50; border-radius: 5px;")
        layout.addWidget(self.total_label)
        
        self.update_visit_records_display()
        return group_box
    
    def select_tooth(self, tooth_number):
        self.selected_tooth = tooth_number
        self.update_tooth_displays()
    
    def update_tooth_status(self, tooth_number, status):
        self.tooth_statuses[tooth_number] = status
        
        # Add to history
        date_str = QDate.currentDate().toString("dd-MM-yyyy")
        status_entry = f"[{date_str}] Status changed to: {status}"
        
        if tooth_number not in self.doctor_findings:
            self.doctor_findings[tooth_number] = []
        self.doctor_findings[tooth_number].append(status_entry)
        
        self.update_tooth_displays()
    
    def update_tooth_displays(self):
        # Get current tooth data
        patient_findings = self.patient_findings.get(self.selected_tooth, [])
        doctor_findings = self.doctor_findings.get(self.selected_tooth, [])
        current_status = self.tooth_statuses.get(self.selected_tooth, 'Normal')
        
        # Update patient history
        patient_text = f"Current Status: {current_status}\n\nPatient Reports:\n"
        patient_text += "\n".join(patient_findings) if patient_findings else "No patient reports"
        self.patient_history_area.setPlainText(patient_text)
        
        # Update doctor history  
        doctor_text = "Doctor Notes:\n"
        doctor_text += "\n".join(doctor_findings) if doctor_findings else "No doctor notes"
        self.doctor_history_area.setPlainText(doctor_text)
        
        # Update selected tooth labels
        self.patient_selected_info.setText(f"Selected: Tooth #{self.selected_tooth}")
        self.doctor_selected_info.setText(f"Selected: Tooth #{self.selected_tooth}")
        
        # Set tooth widget statuses
        for tooth_num, status in self.tooth_statuses.items():
            if tooth_num in self.tooth_widgets:
                widget = self.tooth_widgets[tooth_num]
                status_map = {'Normal': 'N', 'Problem': 'P', 'Fixed': 'F', 'Root Canal': 'R', 'Missing': 'M', 'Crown': 'C'}
                short_status = status_map.get(status, 'N')
                index = widget.status_combo.findText(short_status)
                if index >= 0:
                    widget.status_combo.setCurrentIndex(index)
    
    def add_visit_record(self):
        # Get selected teeth
        selected_teeth = []
        for tooth_num, checkbox in self.tooth_checkboxes.items():
            if checkbox.isChecked():
                selected_teeth.append(tooth_num)
        
        if not selected_teeth:
            return  # Need at least one tooth selected
        
        # Create record
        date_str = self.date_edit.date().toString("dd-MM-yyyy")
        amount = int(self.amount_edit.text() or "0")
        
        new_record = VisitRecord(
            date_str, amount,
            self.problems_edit.text(),
            self.diagnosis_edit.text(), 
            self.treatment_edit.text(),
            self.advice_edit.text(),
            selected_teeth
        )
        
        # Update tooth histories
        for tooth_num in selected_teeth:
            if tooth_num not in self.patient_findings:
                self.patient_findings[tooth_num] = []
            if tooth_num not in self.doctor_findings:
                self.doctor_findings[tooth_num] = []
                
            if self.problems_edit.text():
                self.patient_findings[tooth_num].append(f"[{date_str}] {self.problems_edit.text()}")
            if self.diagnosis_edit.text():
                self.doctor_findings[tooth_num].append(f"[{date_str}] {self.diagnosis_edit.text()}")
        
        self.visit_records.append(new_record)
        
        # Clear form
        self.problems_edit.clear()
        self.diagnosis_edit.clear()
        self.treatment_edit.clear()
        self.advice_edit.clear()
        self.amount_edit.setText("0")
        
        for checkbox in self.tooth_checkboxes.values():
            checkbox.setChecked(False)
        
        # Update displays
        self.update_visit_records_display()
        self.update_tooth_displays()
    
    def update_visit_records_display(self):
        # Clear existing
        for i in reversed(range(self.records_layout.count())): 
            self.records_layout.itemAt(i).widget().setParent(None)
        
        # Add records
        total_amount = 0
        for record in reversed(self.visit_records):  # Show newest first
            record_widget = self.create_record_widget(record)
            self.records_layout.addWidget(record_widget)
            total_amount += record.amount
        
        self.total_label.setText(f"💰 Total Amount Paid: ₹{total_amount}")
    
    def create_record_widget(self, record):
        frame = QFrame()
        frame.setFrameStyle(QFrame.Box)
        frame.setStyleSheet("QFrame { border: 1px solid #ddd; padding: 8px; margin: 3px; background-color: white; border-radius: 5px; }")
        
        layout = QVBoxLayout(frame)
        
        # Header
        header = QLabel(f"📅 {record.date} | 💰 ₹{record.amount}")
        header.setFont(QFont("Arial", 11, QFont.Bold))
        header.setStyleSheet("color: #2196F3;")
        layout.addWidget(header)
        
        # Content
        if record.problems:
            layout.addWidget(QLabel(f"🗣️ Problem: {record.problems}"))
        if record.diagnosis:
            layout.addWidget(QLabel(f"🔍 Diagnosis: {record.diagnosis}"))
        if record.treatment:
            layout.addWidget(QLabel(f"⚕️ Treatment: {record.treatment}"))
        if record.advice:
            layout.addWidget(QLabel(f"💡 Advice: {record.advice}"))
        
        return frame

def main():
    app = QApplication(sys.argv)
   
    
    window = DentalClinicApp()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()