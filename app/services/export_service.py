"""
Export service for data export and backup operations.
"""
import logging
import csv
import json
import os
import shutil
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from pathlib import Path
from sqlalchemy.orm import Session
from ..database.models import Patient, DentalChartRecord, DentalExamination
from ..database.database import db_manager
from .patient_service import patient_service
from .dental_service import dental_service

logger = logging.getLogger(__name__)


class ExportService:
    """Service class for data export and backup operations."""
    
    def __init__(self):
        pass
    
    def _flatten_data(self, patient: Dict, examination: Dict, chart_data: Dict) -> List[Dict]:
        """Flatten patient, examination, and chart data into a list of dictionaries for CSV export."""
        rows = []
        
        # Basic patient and examination data
        base_info = {
            'Patient ID': patient.get('patient_id', ''),
            'Full Name': patient.get('full_name', ''),
            'Phone Number': patient.get('phone_number', ''),
            'Email': patient.get('email', ''),
            'Date of Birth': patient.get('date_of_birth', ''),
            'Address': patient.get('address', ''),
            'Examination ID': examination.get('id', ''),
            'Examination Date': examination.get('examination_date', ''),
            'Chief Complaint': examination.get('chief_complaint', ''),
            'History of Presenting Illness': examination.get('history_of_presenting_illness', ''),
            'Medical History': examination.get('medical_history', ''),
            'Dental History': examination.get('dental_history', ''),
            'Examination Findings': examination.get('examination_findings', ''),
            'Diagnosis': examination.get('diagnosis', ''),
            'Treatment Plan': examination.get('treatment_plan', ''),
            'Notes': examination.get('notes', '')
        }
        
        # If no chart data for this examination, write one row with patient/exam info
        if not any(chart_data.values()):
            rows.append(base_info)
            return rows

        # If chart data exists, create a row for each tooth in the chart
        for quadrant, teeth in chart_data.items():
            for tooth in teeth:
                row = base_info.copy()
                row.update({
                    'Quadrant': quadrant,
                    'Tooth Number': tooth.get('tooth_number', ''),
                    'Tooth Diagnosis': tooth.get('diagnosis', ''),
                    'Treatment Performed': tooth.get('treatment_performed', ''),
                    'Tooth Status': tooth.get('status', '')
                })
                rows.append(row)
        
        return rows

    def export_complete_data_to_csv(self, file_path: str) -> bool:
        """
        Export complete patient, examination, and dental chart data to a single CSV file.
        """
        try:
            patients = patient_service.get_all_patients(limit=10000)
            
            if not patients:
                logger.warning("No patients found to export")
                return False
            
            headers = [
                'Patient ID', 'Full Name', 'Phone Number', 'Email', 'Date of Birth', 'Address',
                'Examination ID', 'Examination Date', 'Chief Complaint', 'History of Presenting Illness',
                'Medical History', 'Dental History', 'Examination Findings', 'Diagnosis', 'Treatment Plan', 'Notes',
                'Quadrant', 'Tooth Number', 'Tooth Diagnosis', 'Treatment Performed', 'Tooth Status'
            ]
            
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=headers)
                writer.writeheader()
                
                for patient in patients:
                    examinations = dental_service.get_all_patient_examinations(patient['patient_id'])
                    
                    if not examinations:
                        # Write basic patient info if no examinations
                        writer.writerow({
                            'Patient ID': patient.get('patient_id', ''),
                            'Full Name': patient.get('full_name', ''),
                            'Phone Number': patient.get('phone_number', ''),
                            'Email': patient.get('email', ''),
                            'Date of Birth': patient.get('date_of_birth', ''),
                            'Address': patient.get('address', '')
                        })
                        continue

                    for exam in examinations:
                        chart_data = dental_service.get_dental_chart(patient['patient_id'], exam['id'])
                        flat_data_rows = self._flatten_data(patient, exam, chart_data)
                        
                        for row in flat_data_rows:
                            writer.writerow(row)
            
            logger.info(f"Successfully exported complete data for {len(patients)} patients to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting complete data to CSV: {str(e)}")
            return False
    
    def create_complete_backup(self, backup_path: str) -> bool:
        """
        Create a complete backup of the database as a single file.
        """
        try:
            db_path = db_manager.get_database_path()
            if not os.path.exists(db_path):
                logger.error(f"Database file not found: {db_path}")
                return False
            
            backup_dir = os.path.dirname(backup_path)
            if backup_dir:
                Path(backup_dir).mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(db_path, backup_path)
            
            if os.path.exists(backup_path) and os.path.getsize(backup_path) > 0:
                logger.info(f"Complete database backup created: {backup_path}")
                return True
            else:
                logger.error("Backup file was not created or is empty")
                return False
            
        except Exception as e:
            logger.error(f"Error creating complete backup: {str(e)}")
            return False
    
    def import_patients_from_csv(self, file_path: str) -> Dict[str, Any]:
        """
        Import patients from CSV file with duplicate prevention based on phone number.
        NOTE: This function needs to be updated to handle the new export format with multiple examinations.
        """
        logger.warning("CSV import logic is not fully updated for the new data format.")
        return {'success': False, 'errors': ["Import function is disabled pending update."]}

    def get_export_statistics(self) -> Dict[str, Any]:
        """
        Get statistics for export purposes.
        """
        try:
            session = db_manager.get_session()
            
            stats = {
                'total_patients': session.query(Patient).count(),
                'total_examinations': session.query(DentalExamination).count(),
                'total_dental_records': session.query(DentalChartRecord).count(),
                'patients_with_examinations': session.query(Patient.id).join(DentalExamination).distinct().count(),
                'patients_with_charts': session.query(Patient.id).join(DentalChartRecord).distinct().count()
            }
            
            session.close()
            return stats
            
        except Exception as e:
            logger.error(f"Error getting export statistics: {str(e)}")
            return {
                'total_patients': 0,
                'total_examinations': 0,
                'total_dental_records': 0,
                'patients_with_examinations': 0,
                'patients_with_charts': 0
            }


# Global export service instance
export_service = ExportService()
