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
from ..database.models import Patient, DentalChartRecord
from ..database.database import db_manager
from .patient_service import patient_service
from .dental_service import dental_service

logger = logging.getLogger(__name__)


class ExportService:
    """Service class for data export and backup operations."""
    
    def __init__(self):
        pass
    
    def _flatten_data(self, patient: Dict, chart_data: Dict) -> str:
        """Flatten patient and chart data into a single string."""
        flat_data = []
        flat_data.append(f"Patient ID: {patient.get('patient_id', '')}")
        flat_data.append(f"Full Name: {patient.get('full_name', '')}")
        flat_data.append(f"Phone Number: {patient.get('phone_number', '')}")
        flat_data.append(f"Email: {patient.get('email', '')}")
        flat_data.append(f"Date of Birth: {patient.get('date_of_birth', '')}")
        flat_data.append(f"Address: {patient.get('address', '')}")
        flat_data.append(f"Examination Date: {patient.get('examination_date', '')}")
        flat_data.append(f"Chief Complaint: {patient.get('chief_complaint', '')}")

        for quadrant, teeth in chart_data.items():
            for tooth in teeth:
                flat_data.append(f"Quadrant: {quadrant}")
                flat_data.append(f"Tooth Number: {tooth.get('tooth_number', '')}")
                flat_data.append(f"Diagnosis: {tooth.get('diagnosis', '')}")
                flat_data.append(f"Treatment Performed: {tooth.get('treatment_performed', '')}")
                flat_data.append(f"Tooth Status: {tooth.get('status', '')}")

        return "; ".join(flat_data)

    def export_complete_data_to_csv(self, file_path: str) -> bool:
        """
        Export complete patient and dental chart data to a single CSV file.
        
        Args:
            file_path: Path to save the CSV file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            session = db_manager.get_session()
            
            # Get all patients with their dental chart records
            patients = patient_service.get_all_patients(limit=10000)
            
            if not patients:
                logger.warning("No patients found to export")
                session.close()
                return False
            
            # Define comprehensive CSV headers
            headers = ['Patient Data']
            
            # Write to CSV
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)
                
                for patient in patients:
                    # Get dental chart for this patient
                    chart_data = dental_service.get_dental_chart(patient['patient_id'])
                    
                    # Flatten data and write to a single column
                    flat_data = self._flatten_data(patient, chart_data)
                    writer.writerow([flat_data])
            
            session.close()
            logger.info(f"Successfully exported complete data for {len(patients)} patients to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting complete data to CSV: {str(e)}")
            if session:
                session.close()
            return False
    

    def create_complete_backup(self, backup_path: str) -> bool:
        """
        Create a complete backup of the database as a single file.
        
        Args:
            backup_path: Full path where to save the backup file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get database file path
            db_path = db_manager.get_database_path()
            if not os.path.exists(db_path):
                logger.error(f"Database file not found: {db_path}")
                return False
            
            # Create backup directory if it doesn't exist
            backup_dir = os.path.dirname(backup_path)
            if backup_dir:
                Path(backup_dir).mkdir(parents=True, exist_ok=True)
            
            # Copy database file
            shutil.copy2(db_path, backup_path)
            
            # Verify backup was created and has content
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
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            Dictionary with import results
        """
        try:
            results = {
                'success': False,
                'imported_count': 0,
                'updated_count': 0,
                'skipped_count': 0,
                'error_count': 0,
                'dental_records_imported': 0,
                'errors': []
            }
            
            if not os.path.exists(file_path):
                results['errors'].append(f"File not found: {file_path}")
                return results
            
            with open(file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                for row_num, row in enumerate(reader, start=1):
                    try:
                        # Extract phone number for duplicate checking
                        phone_number = row.get('Phone Number', '').strip()
                        if not phone_number:
                            results['errors'].append(f"Row {row_num}: Missing phone number")
                            results['error_count'] += 1
                            continue
                        
                        # Check if patient with this phone number already exists
                        existing_patients = patient_service.search_patients(phone_number)
                        existing_patient = None
                        
                        # Look for exact phone number match
                        for patient in existing_patients:
                            if patient.get('phone_number', '').strip() == phone_number:
                                existing_patient = patient
                                break
                        
                        # Prepare patient data
                        patient_data = {
                            'full_name': row.get('Full Name', '').strip(),
                            'phone_number': phone_number,
                            'email': row.get('Email', '').strip(),
                            'address': row.get('Address', '').strip()
                        }
                        
                        # Handle date of birth
                        dob_str = row.get('Date of Birth', '').strip()
                        if dob_str:
                            try:
                                patient_data['date_of_birth'] = datetime.strptime(dob_str, '%Y-%m-%d').date()
                            except ValueError:
                                try:
                                    patient_data['date_of_birth'] = datetime.strptime(dob_str, '%d/%m/%Y').date()
                                except ValueError:
                                    patient_data['date_of_birth'] = None
                        
                        # Handle examination data if present
                        if 'Examination Date' in row:
                            exam_date_str = row.get('Examination Date', '').strip()
                            if exam_date_str:
                                try:
                                    patient_data['examination_date'] = datetime.strptime(exam_date_str, '%Y-%m-%d').date()
                                except ValueError:
                                    try:
                                        patient_data['examination_date'] = datetime.strptime(exam_date_str, '%d/%m/%Y').date()
                                    except ValueError:
                                        pass
                        
                        if 'Chief Complaint' in row:
                            patient_data['chief_complaint'] = row.get('Chief Complaint', '').strip()
                        
                        # Validate required fields
                        if not patient_data['full_name']:
                            results['errors'].append(f"Row {row_num}: Missing patient name")
                            results['error_count'] += 1
                            continue
                        
                        patient_id = None
                        if existing_patient:
                            # Update existing patient
                            success = patient_service.update_patient(
                                existing_patient['patient_id'], 
                                patient_data
                            )
                            if success:
                                patient_id = existing_patient['patient_id']
                                results['updated_count'] += 1
                                logger.info(f"Updated existing patient: {existing_patient['patient_id']} - {patient_data['full_name']}")
                            else:
                                results['errors'].append(f"Row {row_num}: Failed to update existing patient with phone {phone_number}")
                                results['error_count'] += 1
                        else:
                            # Create new patient
                            created_patient = patient_service.create_patient(patient_data)
                            if created_patient:
                                patient_id = created_patient['patient_id']
                                results['imported_count'] += 1
                                logger.info(f"Created new patient: {created_patient['patient_id']} - {patient_data['full_name']}")
                            else:
                                results['errors'].append(f"Row {row_num}: Failed to create new patient")
                                results['error_count'] += 1
                        
                        # Process dental chart data if patient was created/updated successfully and dental data exists
                        if patient_id and any(row.get(col, '').strip() for col in ['Quadrant', 'Tooth Number', 'Diagnosis', 'Treatment Performed', 'Tooth Status']):
                            quadrant = row.get('Quadrant', '').strip().lower().replace(' ', '_')
                            tooth_number_str = row.get('Tooth Number', '').strip()
                            
                            # Validate quadrant and tooth number
                            valid_quadrants = ['upper_right', 'upper_left', 'lower_right', 'lower_left']
                            if quadrant in valid_quadrants and tooth_number_str.isdigit():
                                tooth_number = int(tooth_number_str)
                                if 1 <= tooth_number <= 8:  # Valid tooth numbers
                                    dental_data = {
                                        'diagnosis': row.get('Diagnosis', '').strip(),
                                        'treatment_performed': row.get('Treatment Performed', '').strip(),
                                        'status': row.get('Tooth Status', '').strip() or 'normal'
                                    }
                                    
                                    # Update dental chart record
                                    dental_success = dental_service.update_tooth_record(
                                        patient_id, quadrant, tooth_number, dental_data
                                    )
                                    if dental_success:
                                        results['dental_records_imported'] += 1
                                        logger.info(f"Updated dental record for patient {patient_id}: {quadrant} tooth #{tooth_number}")
                                    else:
                                        logger.warning(f"Failed to update dental record for patient {patient_id}: {quadrant} tooth #{tooth_number}")
                                else:
                                    logger.warning(f"Row {row_num}: Invalid tooth number: {tooth_number_str}")
                            elif quadrant and tooth_number_str:  # Only warn if data was provided
                                logger.warning(f"Row {row_num}: Invalid quadrant ({quadrant}) or tooth number ({tooth_number_str})")
                    
                    except Exception as e:
                        results['errors'].append(f"Row {row_num}: {str(e)}")
                        results['error_count'] += 1
            
            # Mark as successful if at least one patient was imported or updated
            results['success'] = (results['imported_count'] + results['updated_count']) > 0
            
            summary = f"Import completed: {results['imported_count']} new patients, {results['updated_count']} updated patients, {results['dental_records_imported']} dental records, {results['error_count']} errors"
            logger.info(summary)
            
            return results
            
        except Exception as e:
            logger.error(f"Error importing patients from CSV: {str(e)}")
            return {
                'success': False,
                'imported_count': 0,
                'updated_count': 0,
                'skipped_count': 0,
                'error_count': 1,
                'errors': [str(e)]
            }
    
    def get_export_statistics(self) -> Dict[str, Any]:
        """
        Get statistics for export purposes.
        
        Returns:
            Dictionary containing export statistics
        """
        try:
            session = db_manager.get_session()
            
            stats = {
                'total_patients': session.query(Patient).count(),
                'total_dental_records': session.query(DentalChartRecord).count(),
                'patients_with_examinations': session.query(Patient).filter(
                    Patient.examination_date.isnot(None)
                ).count(),
                'patients_with_charts': session.query(Patient).join(
                    DentalChartRecord, Patient.id == DentalChartRecord.patient_id
                ).distinct().count()
            }
            
            session.close()
            return stats
            
        except Exception as e:
            logger.error(f"Error getting export statistics: {str(e)}")
            return {
                'total_patients': 0,
                'total_dental_records': 0,
                'patients_with_examinations': 0,
                'patients_with_charts': 0
            }


# Global export service instance
export_service = ExportService()
