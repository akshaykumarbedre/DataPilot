"""
Edit Visit Dialog - A dialog for editing an existing visit record.
"""
import logging
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QDialogButtonBox
)

from ..components.visit_entry_panel import VisitEntryPanel

logger = logging.getLogger(__name__)


class EditVisitDialog(QDialog):
    """Dialog for editing a visit record."""
    
    def __init__(self, visit_data: dict, patient_id: int, parent=None):
        super().__init__(parent)
        self.visit_data = visit_data
        self.patient_id = patient_id
        
        self.setWindowTitle("Edit Visit Record")
        
        self.setup_ui()
        self.load_visit_data()
    
    def setup_ui(self):
        """Setup the dialog UI."""
        layout = QVBoxLayout(self)
        
        self.visit_entry_panel = VisitEntryPanel(patient_id=self.patient_id)
        layout.addWidget(self.visit_entry_panel)
        
        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def load_visit_data(self):
        """Load the visit data into the entry panel."""
        self.visit_entry_panel.load_visit_data(self.visit_data)
    
    def get_visit_data(self) -> dict:
        """Get the updated visit data from the entry panel."""
        return self.visit_entry_panel.get_visit_data()
