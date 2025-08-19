"""
Patient service for business logic and data operations.
"""
import logging
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, extract
from ..database.models import Patient, DentalExamination
from ..database.database import db_manager
from ..utils.constants import PATIENT_ID_PREFIX, PATIENT_ID_LENGTH

logger = logging.getLogger(__name__)


class PatientService:
    """Service class for patient-related operations."""
    
    def __init__(self):
        pass
    
    def create_patient(self, patient_data: Dict[str, Any]) -> Optional[Patient]:
        """
        Create a new patient.
        
        Args:
            patient_data: Dictionary containing patient information
            
        Returns:
            Patient object if successful, None otherwise
        """
        try:
            session = db_manager.get_session()
            
            # Generate unique patient ID
            patient_id = self._generate_patient_id(session)
            
            # Handle null date of birth
            dob = patient_data.get('date_of_birth')
            if isinstance(dob, date) and dob == date(1900, 1, 1):
                dob = None
            
            # Create patient object
            patient = Patient(
                patient_id=patient_id,
                full_name=patient_data['full_name'],
                phone_number=patient_data['phone_number'],
                date_of_birth=dob,
                email=patient_data.get('email'),
                address=patient_data.get('address')
            )
            
            session.add(patient)
            session.commit()
            
            # Refresh to get the committed data
            session.refresh(patient)
            
            logger.info(f"Created patient: {patient.patient_id} - {patient.full_name}")
            
            # Convert to dict to avoid session issues
            patient_dict = self._patient_to_dict(patient)
            session.close()
            
            return patient_dict
            
        except Exception as e:
            logger.error(f"Error creating patient: {str(e)}")
            if session:
                session.rollback()
                session.close()
            return None
    
    def get_patient_by_id(self, patient_id: str) -> Optional[Dict]:
        """Get patient by patient ID."""
        try:
            session = db_manager.get_session()
            patient = session.query(Patient).filter(Patient.patient_id == patient_id).first()
            
            if patient:
                patient_dict = self._patient_to_dict(patient)
                session.close()
                return patient_dict
            
            session.close()
            return None
            
        except Exception as e:
            logger.error(f"Error getting patient {patient_id}: {str(e)}")
            return None
    
    def get_patient_by_db_id(self, db_id: int) -> Optional[Dict]:
        """Get patient by database ID."""
        try:
            session = db_manager.get_session()
            patient = session.query(Patient).filter(Patient.id == db_id).first()
            
            if patient:
                patient_dict = self._patient_to_dict(patient)
                session.close()
                return patient_dict
            
            session.close()
            return None
            
        except Exception as e:
            logger.error(f"Error getting patient with ID {db_id}: {str(e)}")
            return None
    
    def update_patient(self, patient_id: str, patient_data: Dict[str, Any]) -> bool:
        """
        Update an existing patient.
        
        Args:
            patient_id: Patient ID to update
            patient_data: Dictionary containing updated patient information
            
        Returns:
            True if successful, False otherwise
        """
        try:
            session = db_manager.get_session()
            patient = session.query(Patient).filter(Patient.patient_id == patient_id).first()
            
            if not patient:
                logger.warning(f"Patient not found: {patient_id}")
                session.close()
                return False
            
            # Handle null date of birth
            dob = patient_data.get('date_of_birth')
            if isinstance(dob, date) and dob == date(1900, 1, 1):
                dob = None
            
            # Update patient fields
            patient.full_name = patient_data.get('full_name', patient.full_name)
            patient.phone_number = patient_data.get('phone_number', patient.phone_number)
            patient.date_of_birth = dob if 'date_of_birth' in patient_data else patient.date_of_birth
            patient.email = patient_data.get('email', patient.email)
            patient.address = patient_data.get('address', patient.address)
            patient.updated_at = datetime.utcnow()
            
            session.commit()
            session.close()
            
            logger.info(f"Updated patient: {patient_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating patient {patient_id}: {str(e)}")
            if session:
                session.rollback()
                session.close()
            return False
    
    def delete_patient(self, patient_id: str) -> bool:
        """
        Delete a patient (soft delete by marking as inactive).
        
        Args:
            patient_id: Patient ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            session = db_manager.get_session()
            patient = session.query(Patient).filter(Patient.patient_id == patient_id).first()
            
            if not patient:
                logger.warning(f"Patient not found: {patient_id}")
                session.close()
                return False
            
            # For now, we'll do a hard delete. In production, consider soft delete
            session.delete(patient)
            session.commit()
            session.close()
            
            logger.info(f"Deleted patient: {patient_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting patient {patient_id}: {str(e)}")
            if session:
                session.rollback()
                session.close()
            return False
    
    def search_patients(self, search_term: str = "", limit: int = 100) -> List[Dict]:
        """
        Search patients by name, patient ID, or phone number.
        
        Args:
            search_term: Search term to filter patients
            limit: Maximum number of results to return
            
        Returns:
            List of patient dictionaries
        """
        try:
            session = db_manager.get_session()
            query = session.query(Patient)
            
            if search_term:
                search_filter = or_(
                    Patient.full_name.ilike(f"%{search_term}%"),
                    Patient.patient_id.ilike(f"%{search_term}%"),
                    Patient.phone_number.ilike(f"%{search_term}%"),
                    Patient.email.ilike(f"%{search_term}%")
                )
                query = query.filter(search_filter)
            
            # Order by creation date (newest first)
            patients = query.order_by(Patient.created_at.desc()).limit(limit).all()
            
            patient_list = [self._patient_to_dict(patient) for patient in patients]
            session.close()
            
            logger.info(f"Found {len(patient_list)} patients for search: '{search_term}'")
            return patient_list
            
        except Exception as e:
            logger.error(f"Error searching patients: {str(e)}")
            return []
    
    def get_all_patients(self, limit: int = 1000) -> List[Dict]:
        """Get all patients."""
        return self.search_patients("", limit)
    
    def get_patient_count(self) -> int:
        """Get total number of patients."""
        try:
            session = db_manager.get_session()
            count = session.query(func.count(Patient.id)).scalar()
            session.close()
            return count or 0
        except Exception as e:
            logger.error(f"Error getting patient count: {str(e)}")
            return 0
    
    def get_recent_patients(self, limit: int = 10) -> List[Dict]:
        """Get recently added patients."""
        try:
            session = db_manager.get_session()
            patients = session.query(Patient).order_by(Patient.created_at.desc()).limit(limit).all()
            
            patient_list = [self._patient_to_dict(patient) for patient in patients]
            session.close()
            
            return patient_list
            
        except Exception as e:
            logger.error(f"Error getting recent patients: {str(e)}")
            return []
    
    def get_patients_this_month(self) -> int:
        """Get number of patients added this month."""
        try:
            from datetime import datetime
            
            session = db_manager.get_session()
            current_year = datetime.now().year
            current_month = datetime.now().month
            
            count = session.query(func.count(Patient.id)).filter(
                extract('year', Patient.created_at) == current_year,
                extract('month', Patient.created_at) == current_month
            ).scalar()
            
            session.close()
            return count or 0
            
        except Exception as e:
            logger.error(f"Error getting patients this month: {str(e)}")
            return 0
    
    def get_patients_statistics(self) -> Dict[str, int]:
        """Get comprehensive patient statistics."""
        try:
            from datetime import datetime, timedelta
            
            session = db_manager.get_session()
            
            stats = {}
            
            # Total patients
            stats['total'] = session.query(func.count(Patient.id)).scalar() or 0
            
            # Patients this month
            current_year = datetime.now().year
            current_month = datetime.now().month
            stats['this_month'] = session.query(func.count(Patient.id)).filter(
                extract('year', Patient.created_at) == current_year,
                extract('month', Patient.created_at) == current_month
            ).scalar() or 0
            
            # Patients this week
            week_ago = datetime.now() - timedelta(days=7)
            stats['this_week'] = session.query(func.count(Patient.id)).filter(
                Patient.created_at >= week_ago
            ).scalar() or 0
            
            # Patients today
            today = datetime.now().date()
            stats['today'] = session.query(func.count(Patient.id)).filter(
                func.date(Patient.created_at) == today
            ).scalar() or 0
            
            # Total examinations (count from dental_examinations table)
            stats['total_examinations'] = session.query(func.count(DentalExamination.id)).scalar() or 0
            
            # Examinations this month
            stats['examinations_this_month'] = session.query(func.count(DentalExamination.id)).filter(
                extract('year', DentalExamination.examination_date) == current_year,
                extract('month', DentalExamination.examination_date) == current_month
            ).scalar() or 0
            
            session.close()
            return stats
            
        except Exception as e:
            logger.error(f"Error getting patient statistics: {str(e)}")
            return {'total': 0, 'this_month': 0, 'this_week': 0, 'today': 0, 'total_examinations': 0, 'examinations_this_month': 0}
    
    def _generate_patient_id(self, session: Session) -> str:
        """Generate a unique patient ID."""
        try:
            # Get the highest existing patient ID number
            latest_patient = session.query(Patient).order_by(Patient.id.desc()).first()
            
            if latest_patient and latest_patient.patient_id.startswith(PATIENT_ID_PREFIX):
                try:
                    # Extract number from patient ID (e.g., "P00001" -> 1)
                    last_number = int(latest_patient.patient_id[len(PATIENT_ID_PREFIX):])
                    next_number = last_number + 1
                except (ValueError, IndexError):
                    next_number = 1
            else:
                next_number = 1
            
            # Format with leading zeros
            patient_id = f"{PATIENT_ID_PREFIX}{next_number:0{PATIENT_ID_LENGTH-1}d}"
            
            # Ensure uniqueness (in case of gaps)
            while session.query(Patient).filter(Patient.patient_id == patient_id).first():
                next_number += 1
                patient_id = f"{PATIENT_ID_PREFIX}{next_number:0{PATIENT_ID_LENGTH-1}d}"
            
            return patient_id
            
        except Exception as e:
            logger.error(f"Error generating patient ID: {str(e)}")
            # Fallback to timestamp-based ID
            import time
            return f"{PATIENT_ID_PREFIX}{int(time.time())}"
    
    def _patient_to_dict(self, patient: Patient) -> Dict:
        """Convert Patient object to dictionary."""
        return {
            'id': patient.id,
            'patient_id': patient.patient_id,
            'full_name': patient.full_name,
            'phone_number': patient.phone_number,
            'date_of_birth': patient.date_of_birth,
            'email': patient.email,
            'address': patient.address,
            'created_at': patient.created_at,
            'updated_at': patient.updated_at
        }
    
    def validate_patient_data(self, patient_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Validate patient data and return errors.
        
        Args:
            patient_data: Dictionary containing patient information
            
        Returns:
            Dictionary of field errors (empty if valid)
        """
        errors = {}
        
        # Required fields
        if not patient_data.get('full_name', '').strip():
            errors['full_name'] = "Full name is required"
        elif len(patient_data['full_name']) > 255:
            errors['full_name'] = "Full name must be less than 255 characters"
        
        if not patient_data.get('phone_number', '').strip():
            errors['phone_number'] = "Phone number is required"
        elif len(patient_data['phone_number']) > 20:
            errors['phone_number'] = "Phone number must be less than 20 characters"
        
        # Optional fields validation
        email = patient_data.get('email', '').strip()
        if email:
            if len(email) > 255:
                errors['email'] = "Email must be less than 255 characters"
            elif '@' not in email or '.' not in email:
                errors['email'] = "Please enter a valid email address"
        
        # Date of birth validation
        dob = patient_data.get('date_of_birth')
        if dob:
            # Treat our special "null" date as None
            if isinstance(dob, date) and dob == date(1900, 1, 1):
                dob = None
            elif isinstance(dob, str):
                try:
                    parsed_date = datetime.strptime(dob, '%Y-%m-%d').date()
                    if parsed_date == date(1900, 1, 1):
                        dob = None
                except ValueError:
                    errors['date_of_birth'] = "Please enter a valid date (YYYY-MM-DD)"
            
            # Only validate if we still have a real date
            if dob and isinstance(dob, date):
                if dob > date.today():
                    errors['date_of_birth'] = "Date of birth cannot be in the future"
                elif dob.year < 1900:
                    errors['date_of_birth'] = "Please enter a valid date of birth"
        
        return errors


# Global patient service instance
patient_service = PatientService()
