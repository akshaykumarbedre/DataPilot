"""
Service for managing dental examinations.
"""
import logging
from datetime import date, datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_

from ..database.database import db_manager
from ..database.models import DentalExamination, Patient, User

logger = logging.getLogger(__name__)


class DentalExaminationService:
    """Service for managing dental examinations."""
    
    def create_examination(self, patient_id: int, examination_data: Dict[str, Any]) -> Optional[DentalExamination]:
        """
        Create a new dental examination.
        
        Args:
            patient_id: ID of the patient
            examination_data: Dictionary containing examination data
            
        Returns:
            Created DentalExamination object or None if failed
        """
        try:
            session = db_manager.get_session()
            
            examination = DentalExamination(
                patient_id=patient_id,
                examination_date=examination_data.get('examination_date', date.today()),
                chief_complaint=examination_data.get('chief_complaint', ''),
                history_of_presenting_illness=examination_data.get('history_of_presenting_illness'),
                medical_history=examination_data.get('medical_history'),
                dental_history=examination_data.get('dental_history'),
                examination_findings=examination_data.get('examination_findings'),
                diagnosis=examination_data.get('diagnosis'),
                treatment_plan=examination_data.get('treatment_plan'),
                notes=examination_data.get('notes'),
                examiner_id=examination_data.get('examiner_id')
            )
            
            session.add(examination)
            session.commit()
            
            examination_id = examination.id
            session.close()
            
            logger.info(f"Created examination {examination_id} for patient {patient_id}")
            return self.get_examination_by_id(examination_id)
            
        except Exception as e:
            logger.error(f"Error creating examination: {str(e)}")
            if session:
                session.rollback()
                session.close()
            return None
    
    def get_examination_by_id(self, examination_id: int) -> Optional[Dict[str, Any]]:
        """
        Get examination by ID.
        
        Args:
            examination_id: ID of the examination
            
        Returns:
            Dictionary containing examination data or None if not found
        """
        try:
            session = db_manager.get_session()
            
            examination = session.query(DentalExamination).filter(
                DentalExamination.id == examination_id
            ).first()
            
            if not examination:
                session.close()
                return None
            
            result = {
                'id': examination.id,
                'patient_id': examination.patient_id,
                'examination_date': examination.examination_date,
                'chief_complaint': examination.chief_complaint,
                'history_of_presenting_illness': examination.history_of_presenting_illness,
                'medical_history': examination.medical_history,
                'dental_history': examination.dental_history,
                'examination_findings': examination.examination_findings,
                'diagnosis': examination.diagnosis,
                'treatment_plan': examination.treatment_plan,
                'notes': examination.notes,
                'examiner_id': examination.examiner_id,
                'created_at': examination.created_at,
                'updated_at': examination.updated_at,
                'patient_name': examination.patient.full_name if examination.patient else '',
                'examiner_name': examination.examiner.username if examination.examiner else ''
            }
            
            session.close()
            return result
            
        except Exception as e:
            logger.error(f"Error getting examination {examination_id}: {str(e)}")
            if session:
                session.close()
            return None
    
    def get_patient_examinations(self, patient_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get all examinations for a patient.
        
        Args:
            patient_id: ID of the patient
            limit: Maximum number of examinations to return
            
        Returns:
            List of examination dictionaries
        """
        try:
            session = db_manager.get_session()
            
            examinations = session.query(DentalExamination).filter(
                DentalExamination.patient_id == patient_id
            ).order_by(desc(DentalExamination.examination_date)).limit(limit).all()
            
            results = []
            for exam in examinations:
                results.append({
                    'id': exam.id,
                    'patient_id': exam.patient_id,
                    'examination_date': exam.examination_date,
                    'chief_complaint': exam.chief_complaint,
                    'history_of_presenting_illness': exam.history_of_presenting_illness,
                    'medical_history': exam.medical_history,
                    'dental_history': exam.dental_history,
                    'examination_findings': exam.examination_findings,
                    'diagnosis': exam.diagnosis,
                    'treatment_plan': exam.treatment_plan,
                    'notes': exam.notes,
                    'examiner_id': exam.examiner_id,
                    'created_at': exam.created_at,
                    'updated_at': exam.updated_at,
                    'examiner_name': exam.examiner.username if exam.examiner else ''
                })
            
            session.close()
            return results
            
        except Exception as e:
            logger.error(f"Error getting examinations for patient {patient_id}: {str(e)}")
            if session:
                session.close()
            return []
    
    def get_latest_examination(self, patient_id: int) -> Optional[Dict[str, Any]]:
        """
        Get the most recent examination for a patient.
        
        Args:
            patient_id: ID of the patient
            
        Returns:
            Most recent examination dictionary or None
        """
        try:
            examinations = self.get_patient_examinations(patient_id, limit=1)
            return examinations[0] if examinations else None
            
        except Exception as e:
            logger.error(f"Error getting latest examination for patient {patient_id}: {str(e)}")
            return None
    
    def update_examination(self, examination_id: int, examination_data: Dict[str, Any]) -> bool:
        """
        Update an existing examination.
        
        Args:
            examination_id: ID of the examination to update
            examination_data: Dictionary containing updated examination data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            session = db_manager.get_session()
            
            examination = session.query(DentalExamination).filter(
                DentalExamination.id == examination_id
            ).first()
            
            if not examination:
                session.close()
                return False
            
            # Update fields if provided
            for field in ['chief_complaint', 'history_of_presenting_illness', 'medical_history',
                         'dental_history', 'examination_findings', 'diagnosis', 'treatment_plan',
                         'notes', 'examiner_id']:
                if field in examination_data:
                    setattr(examination, field, examination_data[field])
            
            examination.updated_at = datetime.utcnow()
            session.commit()
            session.close()
            
            logger.info(f"Updated examination {examination_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating examination {examination_id}: {str(e)}")
            if session:
                session.rollback()
                session.close()
            return False
    
    def delete_examination(self, examination_id: int) -> bool:
        """
        Delete an examination and all related records.
        
        Args:
            examination_id: ID of the examination to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            session = db_manager.get_session()
            
            examination = session.query(DentalExamination).filter(
                DentalExamination.id == examination_id
            ).first()
            
            if not examination:
                session.close()
                return False
            
            session.delete(examination)
            session.commit()
            session.close()
            
            logger.info(f"Deleted examination {examination_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting examination {examination_id}: {str(e)}")
            if session:
                session.rollback()
                session.close()
            return False
    
    def get_examination_statistics(self, patient_id: Optional[int] = None) -> Dict[str, int]:
        """
        Get examination statistics.
        
        Args:
            patient_id: Optional patient ID to filter by
            
        Returns:
            Dictionary containing examination statistics
        """
        try:
            session = db_manager.get_session()
            
            query = session.query(DentalExamination)
            if patient_id:
                query = query.filter(DentalExamination.patient_id == patient_id)
            
            total_examinations = query.count()
            
            # Get examinations by month (last 12 months)
            from datetime import datetime, timedelta
            last_month = datetime.now() - timedelta(days=30)
            recent_examinations = query.filter(
                DentalExamination.examination_date >= last_month.date()
            ).count()
            
            session.close()
            
            return {
                'total_examinations': total_examinations,
                'recent_examinations': recent_examinations
            }
            
        except Exception as e:
            logger.error(f"Error getting examination statistics: {str(e)}")
            if session:
                session.close()
            return {'total_examinations': 0, 'recent_examinations': 0}


# Global service instance
dental_examination_service = DentalExaminationService()
