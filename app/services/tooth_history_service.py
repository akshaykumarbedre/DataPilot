"""
Service for managing tooth history records.
"""
import logging
from datetime import date, datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_

from ..database.database import db_manager
from ..database.models import ToothHistory, Patient, DentalExamination

logger = logging.getLogger(__name__)


class ToothHistoryService:
    """Service for managing tooth history records."""
    
    def add_tooth_history(self, patient_id: int, tooth_data: Dict[str, Any]) -> Optional[ToothHistory]:
        """
        Add a new tooth history record.
        
        Args:
            patient_id: ID of the patient
            tooth_data: Dictionary containing tooth history data
            
        Returns:
            Created ToothHistory object or None if failed
        """
        try:
            session = db_manager.get_session()
            
            tooth_history = ToothHistory(
                patient_id=patient_id,
                examination_id=tooth_data.get('examination_id'),
                tooth_number=tooth_data.get('tooth_number'),
                record_type=tooth_data.get('record_type', 'doctor_finding'),  # 'patient_problem' or 'doctor_finding'
                status=tooth_data.get('status'),
                description=tooth_data.get('description'),
                date_recorded=tooth_data.get('date_recorded', date.today())
            )
            
            session.add(tooth_history)
            session.commit()
            
            history_id = tooth_history.id
            session.close()
            
            logger.info(f"Added tooth history {history_id} for patient {patient_id}, tooth {tooth_data.get('tooth_number')}")
            return self.get_tooth_history_by_id(history_id)
            
        except Exception as e:
            logger.error(f"Error adding tooth history: {str(e)}")
            if session:
                session.rollback()
                session.close()
            return None
    
    def get_tooth_history_by_id(self, history_id: int) -> Optional[Dict[str, Any]]:
        """
        Get tooth history by ID.
        
        Args:
            history_id: ID of the tooth history record
            
        Returns:
            Dictionary containing tooth history data or None if not found
        """
        try:
            session = db_manager.get_session()
            
            history = session.query(ToothHistory).filter(
                ToothHistory.id == history_id
            ).first()
            
            if not history:
                session.close()
                return None
            
            result = {
                'id': history.id,
                'patient_id': history.patient_id,
                'examination_id': history.examination_id,
                'tooth_number': history.tooth_number,
                'record_type': history.record_type,
                'status': history.status,
                'description': history.description,
                'date_recorded': history.date_recorded,
                'created_at': history.created_at,
                'patient_name': history.patient.full_name if history.patient else '',
                'examination_date': history.examination.examination_date if history.examination else None
            }
            
            session.close()
            return result
            
        except Exception as e:
            logger.error(f"Error getting tooth history {history_id}: {str(e)}")
            if session:
                session.close()
            return None
    
    def get_tooth_history(self, patient_id: int, tooth_number: Optional[int] = None, 
                         record_type: Optional[str] = None, examination_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get tooth history records for a patient.
        
        Args:
            patient_id: ID of the patient
            tooth_number: Optional specific tooth number to filter by
            record_type: Optional record type ('patient_problem' or 'doctor_finding')
            examination_id: Optional examination ID to filter by
            
        Returns:
            List of tooth history dictionaries
        """
        try:
            session = db_manager.get_session()
            
            query = session.query(ToothHistory).filter(ToothHistory.patient_id == patient_id)
            
            if tooth_number:
                query = query.filter(ToothHistory.tooth_number == tooth_number)
            
            if record_type:
                query = query.filter(ToothHistory.record_type == record_type)
            
            if examination_id:
                query = query.filter(ToothHistory.examination_id == examination_id)
            
            histories = query.order_by(desc(ToothHistory.date_recorded)).all()
            
            results = []
            for history in histories:
                results.append({
                    'id': history.id,
                    'patient_id': history.patient_id,
                    'examination_id': history.examination_id,
                    'tooth_number': history.tooth_number,
                    'record_type': history.record_type,
                    'status': history.status,
                    'description': history.description,
                    'date_recorded': history.date_recorded,
                    'created_at': history.created_at,
                    'examination_date': history.examination.examination_date if history.examination else None
                })
            
            session.close()
            return results
            
        except Exception as e:
            logger.error(f"Error getting tooth history for patient {patient_id}: {str(e)}")
            if session:
                session.close()
            return []
    
    def get_tooth_current_status(self, patient_id: int, tooth_number: int) -> Dict[str, Any]:
        """
        Get the current status of a specific tooth.
        
        Args:
            patient_id: ID of the patient
            tooth_number: Tooth number
            
        Returns:
            Dictionary containing current tooth status information
        """
        try:
            # Get latest patient problem
            patient_problems = self.get_tooth_history(
                patient_id, tooth_number, record_type='patient_problem'
            )
            latest_patient_problem = patient_problems[0] if patient_problems else None
            
            # Get latest doctor finding
            doctor_findings = self.get_tooth_history(
                patient_id, tooth_number, record_type='doctor_finding'
            )
            latest_doctor_finding = doctor_findings[0] if doctor_findings else None
            
            # Determine current status (doctor finding takes precedence)
            current_status = 'normal'
            if latest_doctor_finding and latest_doctor_finding['status']:
                current_status = latest_doctor_finding['status']
            elif latest_patient_problem and latest_patient_problem['status']:
                current_status = latest_patient_problem['status']
            
            return {
                'tooth_number': tooth_number,
                'current_status': current_status,
                'latest_patient_problem': latest_patient_problem,
                'latest_doctor_finding': latest_doctor_finding,
                'patient_problems_count': len(patient_problems),
                'doctor_findings_count': len(doctor_findings)
            }
            
        except Exception as e:
            logger.error(f"Error getting current status for tooth {tooth_number}: {str(e)}")
            return {
                'tooth_number': tooth_number,
                'current_status': 'normal',
                'latest_patient_problem': None,
                'latest_doctor_finding': None,
                'patient_problems_count': 0,
                'doctor_findings_count': 0
            }
    
    def get_patient_tooth_summary(self, patient_id: int, examination_id: Optional[int] = None) -> Dict[int, Dict[str, Any]]:
        """
        Get a summary of all teeth status for a patient.
        
        Args:
            patient_id: ID of the patient
            examination_id: Optional examination ID to filter by
            
        Returns:
            Dictionary mapping tooth numbers to their status information
        """
        try:
            tooth_summary = {}
            
            # Standard tooth numbers (32 teeth)
            all_teeth = []
            # Upper right: 18-11
            all_teeth.extend(range(11, 19))
            # Upper left: 21-28
            all_teeth.extend(range(21, 29))
            # Lower left: 31-38
            all_teeth.extend(range(31, 39))
            # Lower right: 41-48
            all_teeth.extend(range(41, 49))
            
            for tooth_number in all_teeth:
                tooth_summary[tooth_number] = self.get_tooth_current_status(patient_id, tooth_number)
            
            return tooth_summary
            
        except Exception as e:
            logger.error(f"Error getting tooth summary for patient {patient_id}: {str(e)}")
            return {}
    
    def update_tooth_status(self, patient_id: int, tooth_number: int, new_status: str, 
                           record_type: str, description: str = '', examination_id: Optional[int] = None) -> bool:
        """
        Update tooth status by adding a new history record.
        
        Args:
            patient_id: ID of the patient
            tooth_number: Tooth number
            new_status: New status value
            record_type: Type of record ('patient_problem' or 'doctor_finding')
            description: Optional description
            examination_id: Optional examination ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            tooth_data = {
                'tooth_number': tooth_number,
                'record_type': record_type,
                'status': new_status,
                'description': description,
                'examination_id': examination_id,
                'date_recorded': date.today()
            }
            
            result = self.add_tooth_history(patient_id, tooth_data)
            return result is not None
            
        except Exception as e:
            logger.error(f"Error updating tooth {tooth_number} status: {str(e)}")
            return False
    
    def get_tooth_history_statistics(self, patient_id: Optional[int] = None) -> Dict[str, int]:
        """
        Get tooth history statistics.
        
        Args:
            patient_id: Optional patient ID to filter by
            
        Returns:
            Dictionary containing tooth history statistics
        """
        try:
            session = db_manager.get_session()
            
            query = session.query(ToothHistory)
            if patient_id:
                query = query.filter(ToothHistory.patient_id == patient_id)
            
            total_records = query.count()
            patient_problems = query.filter(ToothHistory.record_type == 'patient_problem').count()
            doctor_findings = query.filter(ToothHistory.record_type == 'doctor_finding').count()
            
            # Get recent records (last 30 days)
            from datetime import timedelta
            last_month = date.today() - timedelta(days=30)
            recent_records = query.filter(ToothHistory.date_recorded >= last_month).count()
            
            session.close()
            
            return {
                'total_records': total_records,
                'patient_problems': patient_problems,
                'doctor_findings': doctor_findings,
                'recent_records': recent_records
            }
            
        except Exception as e:
            logger.error(f"Error getting tooth history statistics: {str(e)}")
            if session:
                session.close()
            return {
                'total_records': 0,
                'patient_problems': 0,
                'doctor_findings': 0,
                'recent_records': 0
            }


# Global service instance
tooth_history_service = ToothHistoryService()
