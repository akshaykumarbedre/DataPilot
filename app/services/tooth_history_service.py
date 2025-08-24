"""
Service for managing tooth history records.
"""
import logging
import json
from datetime import date, datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_

from ..database.database import db_manager
from ..database.models import ToothHistory, Patient, DentalExamination

logger = logging.getLogger(__name__)


class ToothHistoryService:
    """Service for managing tooth history records."""
    
    def _parse_history_field(self, field_value: str) -> List[Any]:
        """Parse JSON history field, return empty list if invalid."""
        if not field_value:
            return []
        try:
            return json.loads(field_value)
        except (json.JSONDecodeError, TypeError):
            return []
    
    def _serialize_history_field(self, field_list: List[Any]) -> str:
        """Serialize list to JSON string."""
        try:
            return json.dumps(field_list) if field_list else "[]"
        except (TypeError, ValueError):
            return "[]"
    
    def add_tooth_history_entry(self, patient_id: int, tooth_number: int, record_type: str, 
                               status: str, description: str = "", examination_id: Optional[int] = None) -> bool:
        """
        Add a new entry to existing tooth history or create new record.
        
        Args:
            patient_id: ID of the patient
            tooth_number: Tooth number
            record_type: 'patient_problem' or 'doctor_finding'
            status: Status value
            description: Description text
            examination_id: Optional examination ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            session = db_manager.get_session()
            current_date = date.today().isoformat()
            
            # Find existing record for this patient, tooth, and record type
            existing_record = session.query(ToothHistory).filter(
                and_(
                    ToothHistory.patient_id == patient_id,
                    ToothHistory.tooth_number == tooth_number,
                    ToothHistory.record_type == record_type
                )
            ).first()
            
            if existing_record:
                # Update existing record by adding to history
                status_history = self._parse_history_field(existing_record.status_history)
                description_history = self._parse_history_field(existing_record.description_history)
                date_history = self._parse_history_field(existing_record.date_history)
                
                # Add new entries
                status_history.append(status)
                description_history.append(description)
                date_history.append(current_date)
                
                # Update the record
                existing_record.status_history = self._serialize_history_field(status_history)
                existing_record.description_history = self._serialize_history_field(description_history)
                existing_record.date_history = self._serialize_history_field(date_history)
                
                # Update latest/current fields
                existing_record.status = status
                existing_record.description = description
                existing_record.date_recorded = date.today()
                
            else:
                # Create new record
                tooth_history = ToothHistory(
                    patient_id=patient_id,
                    examination_id=examination_id,
                    tooth_number=tooth_number,
                    record_type=record_type,
                    status_history=self._serialize_history_field([status]),
                    description_history=self._serialize_history_field([description]),
                    date_history=self._serialize_history_field([current_date]),
                    status=status,
                    description=description,
                    date_recorded=date.today()
                )
                session.add(tooth_history)
            
            session.commit()
            session.close()
            
            logger.info(f"Added tooth history entry for patient {patient_id}, tooth {tooth_number}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding tooth history entry: {str(e)}")
            if session:
                session.rollback()
                session.close()
            return False
    
    def get_tooth_history_by_id(self, history_id: int) -> Optional[Dict[str, Any]]:
        """
        Get tooth history by ID with full history data.
        
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
                'current_status': history.status,
                'current_description': history.description,
                'current_date': history.date_recorded,
                'status_history': self._parse_history_field(history.status_history),
                'description_history': self._parse_history_field(history.description_history),
                'date_history': self._parse_history_field(history.date_history),
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
    
    def get_tooth_full_history(self, patient_id: int, tooth_number: int, record_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Get complete history for a specific tooth.
        
        Args:
            patient_id: ID of the patient
            tooth_number: Tooth number
            record_type: Optional record type filter
            
        Returns:
            Dictionary containing complete tooth history
        """
        try:
            session = db_manager.get_session()
            
            query = session.query(ToothHistory).filter(
                and_(
                    ToothHistory.patient_id == patient_id,
                    ToothHistory.tooth_number == tooth_number
                )
            )
            
            if record_type:
                query = query.filter(ToothHistory.record_type == record_type)
            
            records = query.all()
            
            result = {
                'tooth_number': tooth_number,
                'patient_id': patient_id,
                'patient_problems': [],
                'doctor_findings': []
            }
            
            for record in records:
                history_data = {
                    'id': record.id,
                    'examination_id': record.examination_id,
                    'current_status': record.status,
                    'current_description': record.description,
                    'current_date': record.date_recorded,
                    'status_history': self._parse_history_field(record.status_history),
                    'description_history': self._parse_history_field(record.description_history),
                    'date_history': self._parse_history_field(record.date_history),
                    'created_at': record.created_at
                }
                
                if record.record_type == 'patient_problem':
                    result['patient_problems'].append(history_data)
                elif record.record_type == 'doctor_finding':
                    result['doctor_findings'].append(history_data)
            
            session.close()
            return result
            
        except Exception as e:
            logger.error(f"Error getting full tooth history for tooth {tooth_number}: {str(e)}")
            if session:
                session.close()
            return {
                'tooth_number': tooth_number,
                'patient_id': patient_id,
                'patient_problems': [],
                'doctor_findings': []
            }
    
    def get_tooth_history(self, patient_id: int, tooth_number: Optional[int] = None, 
                         record_type: Optional[str] = None, examination_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get tooth history records for a patient (backward compatibility method).
        
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
                    'status_history': self._parse_history_field(history.status_history),
                    'description_history': self._parse_history_field(history.description_history),
                    'date_history': self._parse_history_field(history.date_history),
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
        Update tooth status by adding a new history entry.
        
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
            return self.add_tooth_history_entry(
                patient_id=patient_id,
                tooth_number=tooth_number,
                record_type=record_type,
                status=new_status,
                description=description,
                examination_id=examination_id
            )
            
        except Exception as e:
            logger.error(f"Error updating tooth {tooth_number} status: {str(e)}")
            return False
    
    def add_tooth_history(self, patient_id: int, tooth_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Add a new tooth history record (backward compatibility method).
        
        Args:
            patient_id: ID of the patient
            tooth_data: Dictionary containing tooth history data
            
        Returns:
            Created record data or None if failed
        """
        try:
            success = self.add_tooth_history_entry(
                patient_id=patient_id,
                tooth_number=tooth_data.get('tooth_number'),
                record_type=tooth_data.get('record_type', 'doctor_finding'),
                status=tooth_data.get('status', '') ,
                description=tooth_data.get('description', ''),
                examination_id=tooth_data.get('examination_id')
            )
            
            if success:
                # Return the updated record
                records = self.get_tooth_history(
                    patient_id=patient_id,
                    tooth_number=tooth_data.get('tooth_number'),
                    record_type=tooth_data.get('record_type', 'doctor_finding')
                )
                return records[0] if records else None
            
            return None
            
        except Exception as e:
            logger.error(f"Error adding tooth history: {str(e)}")
            return None
    
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
    
    def get_tooth_timeline(self, patient_id: int, tooth_number: int) -> List[Dict[str, Any]]:
        """
        Get complete timeline of a tooth including all history entries.
        
        Args:
            patient_id: ID of the patient
            tooth_number: Tooth number
            
        Returns:
            List of timeline entries sorted by date (newest first)
        """
        try:
            full_history = self.get_tooth_full_history(patient_id, tooth_number)
            timeline = []
            
            # Process patient problems
            for problem_record in full_history['patient_problems']:
                status_history = problem_record['status_history']
                description_history = problem_record['description_history']
                date_history = problem_record['date_history']
                
                for i, date_str in enumerate(date_history):
                    timeline.append({
                        'date': date_str,
                        'type': 'patient_problem',
                        'status': status_history[i] if i < len(status_history) else '',
                        'description': description_history[i] if i < len(description_history) else '',
                        'record_id': problem_record['id']
                    })
            
            # Process doctor findings
            for finding_record in full_history['doctor_findings']:
                status_history = finding_record['status_history']
                description_history = finding_record['description_history']
                date_history = finding_record['date_history']
                
                for i, date_str in enumerate(date_history):
                    timeline.append({
                        'date': date_str,
                        'type': 'doctor_finding',
                        'status': status_history[i] if i < len(status_history) else '',
                        'description': description_history[i] if i < len(description_history) else '',
                        'record_id': finding_record['id']
                    })
            
            # Sort by date (newest first)
            timeline.sort(key=lambda x: x['date'], reverse=True)
            
            return timeline
            
        except Exception as e:
            logger.error(f"Error getting tooth timeline for tooth {tooth_number}: {str(e)}")
            return []

    def delete_last_tooth_history_entry(self, patient_id: int, tooth_number: int, record_type: str) -> bool:
        """Deletes the last entry from a tooth's history."""
        try:
            session = db_manager.get_session()
            
            record = session.query(ToothHistory).filter(
                and_(
                    ToothHistory.patient_id == patient_id,
                    ToothHistory.tooth_number == tooth_number,
                    ToothHistory.record_type == record_type
                )
            ).first()
            
            if record:
                status_history = self._parse_history_field(record.status_history)
                description_history = self._parse_history_field(record.description_history)
                date_history = self._parse_history_field(record.date_history)
                
                if len(status_history) > 1:
                    # More than one entry, so pop the last one
                    status_history.pop()
                    description_history.pop()
                    date_history.pop()
                    
                    record.status_history = self._serialize_history_field(status_history)
                    record.description_history = self._serialize_history_field(description_history)
                    record.date_history = self._serialize_history_field(date_history)
                    
                    record.status = status_history[-1]
                    record.description = description_history[-1]
                    record.date_recorded = date.fromisoformat(date_history[-1])
                else:
                    # Only one entry, so delete the whole record
                    session.delete(record)
                
                session.commit()
                session.close()
                return True
            
            session.close()
            return False # No record found
            
        except Exception as e:
            logger.error(f"Error deleting last tooth history entry: {str(e)}")
            if session:
                session.rollback()
                session.close()
            return False


# Global service instance
tooth_history_service = ToothHistoryService()
