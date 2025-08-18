"""UI module containing all user interface components."""

from .main_window import MainWindow
from .dashboard import Dashboard
from .patient_management import PatientManagement
from .dental_chart import DentalChart
from .settings import SettingsWidget
from .login_dialog import LoginDialog

__all__ = [
    'MainWindow',
    'Dashboard', 
    'PatientManagement',
    'DentalChart',
    'SettingsWidget',
    'LoginDialog'
]