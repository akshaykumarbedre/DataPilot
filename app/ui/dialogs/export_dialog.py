"""
Export dialog for data export and backup operations.
"""
import os
from datetime import datetime
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QGroupBox, QCheckBox, QFileDialog,
                               QTextEdit, QProgressBar, QMessageBox, QComboBox,
                               QFormLayout, QLineEdit, QSpacerItem, QSizePolicy)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont
from ...services.export_service import export_service


class ExportWorker(QThread):
    """Worker thread for export operations."""
    
    progress_updated = Signal(int)
    status_updated = Signal(str)
    export_completed = Signal(bool, str)
    
    def __init__(self, export_type: str, file_path: str, options: dict):
        super().__init__()
        self.export_type = export_type
        self.file_path = file_path
        self.options = options
    
    def run(self):
        """Run the export operation."""
        try:
            self.status_updated.emit("Starting export...")
            self.progress_updated.emit(10)
            
            success = False
            message = ""
            
            if self.export_type == "complete_csv":
                self.status_updated.emit("Exporting complete data to CSV...")
                self.progress_updated.emit(50)
                success = export_service.export_complete_data_to_csv(self.file_path)
                message = "Complete data exported successfully" if success else "Failed to export complete data"
                
            elif self.export_type == "complete_backup":
                self.status_updated.emit("Creating complete database backup...")
                self.progress_updated.emit(50)
                success = export_service.create_complete_backup(self.file_path)
                message = f"Complete backup created successfully" if success else "Failed to create complete backup"
            
            self.progress_updated.emit(100)
            self.export_completed.emit(success, message)
            
        except Exception as e:
            self.export_completed.emit(False, f"Export error: {str(e)}")


class ExportDialog(QDialog):
    """Dialog for data export and backup operations."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Data Export & Backup")
        self.setFixedSize(600, 600)
        self.setModal(True)
        
        self.worker = None
        self._setup_ui()
        self._connect_signals()
        self._load_statistics()
    
    def _setup_ui(self):
        """Set up the user interface."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel("Data Export & Backup")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2C3E50; margin-bottom: 10px;")
        main_layout.addWidget(title_label)
        
        # Statistics section
        self._setup_statistics_section(main_layout)
        
        # Export section
        self._setup_export_section(main_layout)
        
        # Progress section
        self._setup_progress_section(main_layout)
        
        # Buttons
        self._setup_buttons(main_layout)
    
    def _setup_statistics_section(self, main_layout):
        """Set up the statistics section."""
        stats_group = QGroupBox("Database Statistics")
        stats_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #BDC3C7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
            }
        """)
        
        stats_layout = QFormLayout(stats_group)
        
        self.total_patients_label = QLabel("0")
        self.total_records_label = QLabel("0")
        self.patients_with_exams_label = QLabel("0")
        self.patients_with_charts_label = QLabel("0")
        
        stats_layout.addRow("Total Patients:", self.total_patients_label)
        stats_layout.addRow("Total Dental Records:", self.total_records_label)
        stats_layout.addRow("Patients with Examinations:", self.patients_with_exams_label)
        stats_layout.addRow("Patients with Charts:", self.patients_with_charts_label)
        
        main_layout.addWidget(stats_group)
    
    def _setup_export_section(self, main_layout):
        """Set up the export section."""
        export_group = QGroupBox("Export Data")
        export_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3498DB;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
            }
        """)
        
        export_layout = QVBoxLayout(export_group)
        
        # Export type selection
        export_type_layout = QHBoxLayout()
        export_type_layout.addWidget(QLabel("Export Type:"))
        
        self.export_type_combo = QComboBox()
        self.export_type_combo.addItems([
            "Complete Data (CSV)",
            "Complete Backup (Database)"
        ])
        export_type_layout.addWidget(self.export_type_combo)
        export_layout.addLayout(export_type_layout)
        
        # Export buttons
        export_buttons_layout = QHBoxLayout()
        
        self.export_button = QPushButton("Export Data")
        self.export_button.setStyleSheet("""
            QPushButton {
                background-color: #3498DB;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
            QPushButton:pressed {
                background-color: #21618C;
            }
        """)
        export_buttons_layout.addWidget(self.export_button)
        
        export_layout.addLayout(export_buttons_layout)
        main_layout.addWidget(export_group)
    
    def _setup_progress_section(self, main_layout):
        """Set up the progress section."""
        progress_group = QGroupBox("Operation Progress")
        progress_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #8E44AD;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
            }
        """)
        
        progress_layout = QVBoxLayout(progress_group)
        
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #2C3E50; font-weight: bold;")
        progress_layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)
        
        self.result_text = QTextEdit()
        self.result_text.setMaximumHeight(100)
        self.result_text.setVisible(False)
        self.result_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #BDC3C7;
                border-radius: 4px;
                padding: 5px;
                background-color: #F8F9FA;
            }
        """)
        progress_layout.addWidget(self.result_text)
        
        main_layout.addWidget(progress_group)
    
    def _setup_buttons(self, main_layout):
        """Set up dialog buttons."""
        main_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        button_layout = QHBoxLayout()
        
        self.refresh_button = QPushButton("Refresh Statistics")
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #95A5A6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7F8C8D;
            }
        """)
        button_layout.addWidget(self.refresh_button)
        
        button_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        self.close_button = QPushButton("Close")
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: #34495E;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2C3E50;
            }
        """)
        button_layout.addWidget(self.close_button)
        
        main_layout.addLayout(button_layout)
    
    def _connect_signals(self):
        """Connect widget signals."""
        self.export_button.clicked.connect(self._export_data)
        self.refresh_button.clicked.connect(self._load_statistics)
        self.close_button.clicked.connect(self.close)
    
    def _load_statistics(self):
        """Load and display database statistics."""
        try:
            stats = export_service.get_export_statistics()
            
            self.total_patients_label.setText(str(stats['total_patients']))
            self.total_records_label.setText(str(stats['total_dental_records']))
            self.patients_with_exams_label.setText(str(stats['patients_with_examinations']))
            self.patients_with_charts_label.setText(str(stats['patients_with_charts']))
            
            self.status_label.setText("Statistics updated")
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load statistics: {str(e)}")
    
    def _export_data(self):
        """Export data based on selected type."""
        try:
            export_type_text = self.export_type_combo.currentText()
            
            # Determine file filter and extension based on simplified options
            if "Complete Data (CSV)" in export_type_text:
                file_filter = "CSV Files (*.csv)"
                default_ext = ".csv"
                export_type = "complete_csv"
            else:  # Complete Backup (Database)
                file_dialog = QFileDialog()
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                default_name = f"dental_complete_backup_{timestamp}.db"
                
                backup_path, _ = file_dialog.getSaveFileName(
                    self,
                    "Save Complete Database Backup",
                    os.path.join(os.path.expanduser("~/Documents"), default_name),
                    "Database Files (*.db);;All Files (*)"
                )
                if backup_path:
                    self._start_export("complete_backup", backup_path, {})
                return
            
            # Get save file path for CSV
            file_dialog = QFileDialog()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_name = f"dental_complete_data_{timestamp}{default_ext}"
            
            file_path, _ = file_dialog.getSaveFileName(
                self,
                f"Save {export_type_text}",
                os.path.join(os.path.expanduser("~/Documents"), default_name),
                file_filter
            )
            
            if file_path:
                self._start_export(export_type, file_path, {})
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Export failed: {str(e)}")
    
    def _start_export(self, export_type: str, file_path: str, options: dict):
        """Start export operation in background thread."""
        if self.worker and self.worker.isRunning():
            QMessageBox.warning(self, "Warning", "An operation is already in progress")
            return
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.result_text.setVisible(False)
        
        self.export_button.setEnabled(False)
        
        self.worker = ExportWorker(export_type, file_path, options)
        self.worker.progress_updated.connect(self.progress_bar.setValue)
        self.worker.status_updated.connect(self.status_label.setText)
        self.worker.export_completed.connect(self._on_export_completed)
        self.worker.start()
    
    def _on_export_completed(self, success: bool, message: str):
        """Handle export completion."""
        self.export_button.setEnabled(True)
        
        self.progress_bar.setVisible(False)
        self.result_text.setVisible(True)
        
        if success:
            self.status_label.setText("Export completed successfully")
            self.result_text.setPlainText(message)
            self.result_text.setStyleSheet("""
                QTextEdit {
                    border: 1px solid #27AE60;
                    border-radius: 4px;
                    padding: 5px;
                    background-color: #D5F4E6;
                    color: #27AE60;
                }
            """)
            self._load_statistics()  # Refresh statistics
        else:
            self.status_label.setText("Export failed")
            self.result_text.setPlainText(f"Error: {message}")
            self.result_text.setStyleSheet("""
                QTextEdit {
                    border: 1px solid #E74C3C;
                    border-radius: 4px;
                    padding: 5px;
                    background-color: #FADBD8;
                    color: #E74C3C;
                }
            """)
    
    def closeEvent(self, event):
        """Handle dialog close event."""
        if self.worker and self.worker.isRunning():
            reply = QMessageBox.question(
                self, 
                "Operation in Progress", 
                "An operation is still in progress. Are you sure you want to close?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                event.ignore()
                return
            
            self.worker.terminate()
            self.worker.wait()
        
        event.accept()
