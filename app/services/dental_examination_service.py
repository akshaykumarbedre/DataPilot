"""
Service for managing dental examinations.
"""
import logging
import json
from datetime import date, datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_

from ..database.database import db_manager
from ..database.models import DentalExamination, Patient, User

logger = logging.getLogger(__name__)


class DentalExaminationService:
    """Service for managing dental examinations."""
    
    def create_examination(self, examination_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new dental examination.
        
        Args:
            examination_data: Dictionary containing examination data including patient_id
            
        Returns:
            Dictionary with success status and examination data
        """
        try:
            session = db_manager.get_session()
            
            # Extract patient_id from examination_data
            patient_id = examination_data.get('patient_id')
            if not patient_id:
                return {'success': False, 'error': 'Patient ID is required'}
            
            # Serialize complex fields to JSON strings
            examination_findings = examination_data.get('examination_findings')
            if isinstance(examination_findings, dict):
                examination_findings = json.dumps(examination_findings)
            
            vital_signs = examination_data.get('vital_signs')
            if isinstance(vital_signs, dict):
                # Store vital signs in notes field for now since there's no dedicated field
                notes = examination_data.get('notes', '')
                if vital_signs:
                    vital_signs_text = f"Vital Signs: {json.dumps(vital_signs)}"
                    notes = f"{notes}\n{vital_signs_text}".strip()
                examination_data['notes'] = notes
            
            examination = DentalExamination(
                patient_id=patient_id,
                examination_date=examination_data.get('examination_date', date.today()),
                chief_complaint=examination_data.get('chief_complaint', ''),
                history_of_presenting_illness=examination_data.get('present_illness'),  # Map present_illness to history_of_presenting_illness
                medical_history=examination_data.get('medical_history'),
                dental_history=examination_data.get('dental_history'),
                examination_findings=examination_findings,  # Use serialized JSON string
                diagnosis=examination_data.get('diagnosis'),
                treatment_plan=examination_data.get('treatment_plan'),
                notes=examination_data.get('notes'),
                examiner_id=examination_data.get('examiner_id')
                # Note: examination_type is not stored in database model, only used in UI
            )
            
            session.add(examination)
            session.commit()
            
            examination_id = examination.id
            session.close()
            
            logger.info(f"Created examination {examination_id} for patient {patient_id}")
            
            # Get the created examination data
            created_exam = self.get_examination_by_id(examination_id)
            
            return {
                'success': True,
                'examination': created_exam
            }
            
        except Exception as e:
            logger.error(f"Error creating examination: {str(e)}")
            if 'session' in locals() and session:
                session.rollback()
                session.close()
            return {'success': False, 'error': str(e)}
    
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
            
            # Deserialize JSON fields back to dictionaries
            examination_findings = examination.examination_findings
            if examination_findings and isinstance(examination_findings, str):
                try:
                    examination_findings = json.loads(examination_findings)
                except (json.JSONDecodeError, TypeError):
                    examination_findings = {}
            
            result = {
                'id': examination.id,
                'patient_id': examination.patient_id,
                'examination_date': examination.examination_date,
                'chief_complaint': examination.chief_complaint,
                'present_illness': examination.history_of_presenting_illness,  # Map back to present_illness for UI
                'medical_history': examination.medical_history,
                'dental_history': examination.dental_history,
                'examination_findings': examination_findings or {},
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
                # Deserialize JSON fields
                examination_findings = exam.examination_findings
                if examination_findings and isinstance(examination_findings, str):
                    try:
                        examination_findings = json.loads(examination_findings)
                    except (json.JSONDecodeError, TypeError):
                        examination_findings = {}
                
                results.append({
                    'id': exam.id,
                    'patient_id': exam.patient_id,
                    'examination_date': exam.examination_date,
                    'chief_complaint': exam.chief_complaint,
                    'present_illness': exam.history_of_presenting_illness,  # Map back to present_illness for UI
                    'medical_history': exam.medical_history,
                    'dental_history': exam.dental_history,
                    'examination_findings': examination_findings or {},
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
    
    def update_examination(self, examination_id: int, examination_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing examination.
        
        Args:
            examination_id: ID of the examination to update
            examination_data: Dictionary containing updated examination data
            
        Returns:
            Dictionary with success status and examination data
        """
        try:
            session = db_manager.get_session()
            
            examination = session.query(DentalExamination).filter(
                DentalExamination.id == examination_id
            ).first()
            
            if not examination:
                session.close()
                return {'success': False, 'error': 'Examination not found'}
            
            # Update fields if provided with JSON serialization for complex fields
            if 'chief_complaint' in examination_data:
                examination.chief_complaint = examination_data['chief_complaint']
            if 'present_illness' in examination_data:
                examination.history_of_presenting_illness = examination_data['present_illness']
            if 'medical_history' in examination_data:
                examination.medical_history = examination_data['medical_history']
            if 'dental_history' in examination_data:
                examination.dental_history = examination_data['dental_history']
            if 'examination_findings' in examination_data:
                findings = examination_data['examination_findings']
                if isinstance(findings, dict):
                    findings = json.dumps(findings)
                examination.examination_findings = findings
            if 'diagnosis' in examination_data:
                examination.diagnosis = examination_data['diagnosis']
            if 'treatment_plan' in examination_data:
                examination.treatment_plan = examination_data['treatment_plan']
            if 'notes' in examination_data:
                examination.notes = examination_data['notes']
            if 'examiner_id' in examination_data:
                examination.examiner_id = examination_data['examiner_id']
            
            examination.updated_at = datetime.utcnow()
            session.commit()
            session.close()
            
            logger.info(f"Updated examination {examination_id}")
            
            # Get the updated examination data
            updated_exam = self.get_examination_by_id(examination_id)
            
            return {
                'success': True,
                'examination': updated_exam
            }
            
        except Exception as e:
            logger.error(f"Error updating examination {examination_id}: {str(e)}")
            if 'session' in locals() and session:
                session.rollback()
                session.close()
            return {'success': False, 'error': str(e)}
    
    def delete_examination(self, examination_id: int) -> Dict[str, Any]:
        """
        Delete an examination and all related records.
        
        Args:
            examination_id: ID of the examination to delete
            
        Returns:
            Dictionary with success status
        """
        try:
            session = db_manager.get_session()
            
            examination = session.query(DentalExamination).filter(
                DentalExamination.id == examination_id
            ).first()
            
            if not examination:
                session.close()
                return {'success': False, 'error': 'Examination not found'}
            
            session.delete(examination)
            session.commit()
            session.close()
            
            logger.info(f"Deleted examination {examination_id}")
            return {'success': True}
            
        except Exception as e:
            logger.error(f"Error deleting examination {examination_id}: {str(e)}")
            if 'session' in locals() and session:
                session.rollback()
                session.close()
            return {'success': False, 'error': str(e)}
    
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
