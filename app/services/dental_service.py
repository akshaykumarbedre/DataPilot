"""
Dental service for examination and chart operations.
"""
import logging
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_
from ..database.models import Patient, DentalChartRecord
from ..database.database import db_manager

logger = logging.getLogger(__name__)


class DentalService:
    """Service class for dental examination and chart operations."""
    
    def __init__(self):
        pass
    
    def update_patient_examination(self, patient_id: str, examination_data: Dict[str, Any]) -> bool:
        """
        Update patient examination data.
        
        Args:
            patient_id: Patient ID
            examination_data: Dictionary containing examination information
            
        Returns:
            True if successful, False otherwise
        """
        try:
            session = db_manager.get_session()
            
            # Get patient by patient_id
            patient = session.query(Patient).filter(Patient.patient_id == patient_id).first()
            if not patient:
                logger.warning(f"Patient not found: {patient_id}")
                session.close()
                return False
            
            # Update examination fields
            if 'examination_date' in examination_data:
                patient.examination_date = examination_data['examination_date']
            if 'chief_complaint' in examination_data:
                patient.chief_complaint = examination_data['chief_complaint']
            
            patient.updated_at = datetime.utcnow()
            
            # Initialize empty dental chart if not exists
            if not patient.chart_records:
                self._initialize_dental_chart(session, patient.id)
            
            session.commit()
            session.close()
            
            logger.info(f"Updated examination for patient: {patient_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating examination: {str(e)}")
            if session:
                session.rollback()
                session.close()
            return False
    
    def get_patient_examination(self, patient_id: str) -> Optional[Dict]:
        """Get patient examination data."""
        try:
            session = db_manager.get_session()
            
            # Get patient by patient_id
            patient = session.query(Patient).filter(Patient.patient_id == patient_id).first()
            if not patient:
                session.close()
                return None
            
            examination_dict = {
                'id': patient.id,
                'patient_id': patient.patient_id,
                'full_name': patient.full_name,
                'examination_date': patient.examination_date,
                'chief_complaint': patient.chief_complaint,
                'created_at': patient.created_at,
                'updated_at': patient.updated_at
            }
            
            session.close()
            return examination_dict
            
        except Exception as e:
            logger.error(f"Error getting examination for patient {patient_id}: {str(e)}")
            return None
    
    def get_dental_chart(self, patient_id: str) -> Dict[str, List[Dict]]:
        """Get dental chart records for a patient."""
        try:
            session = db_manager.get_session()
            
            # Get patient by patient_id
            patient = session.query(Patient).filter(Patient.patient_id == patient_id).first()
            if not patient:
                session.close()
                return {
                    'upper_right': [],
                    'upper_left': [],
                    'lower_right': [],
                    'lower_left': []
                }
            
            chart_records = session.query(DentalChartRecord).filter(
                DentalChartRecord.patient_id == patient.id
            ).all()
            
            # Organize by quadrants
            chart_data = {
                'upper_right': [],
                'upper_left': [],
                'lower_right': [],
                'lower_left': []
            }
            
            for record in chart_records:
                quadrant = record.quadrant
                if quadrant in chart_data:
                    chart_data[quadrant].append(self._chart_record_to_dict(record))
            
            # Sort teeth by tooth number within each quadrant
            for quadrant in chart_data:
                chart_data[quadrant].sort(key=lambda x: x['tooth_number'])
            
            session.close()
            return chart_data
            
        except Exception as e:
            logger.error(f"Error getting dental chart for patient {patient_id}: {str(e)}")
            return {
                'upper_right': [],
                'upper_left': [],
                'lower_right': [],
                'lower_left': []
            }
    
    def update_tooth_record(self, patient_id: str, quadrant: str, tooth_number: int, 
                           tooth_data: Dict[str, Any]) -> bool:
        """Update a specific tooth record."""
        try:
            session = db_manager.get_session()
            
            # Get patient by patient_id
            patient = session.query(Patient).filter(Patient.patient_id == patient_id).first()
            if not patient:
                logger.warning(f"Patient not found: {patient_id}")
                session.close()
                return False
            
            # Find existing record or create new one
            record = session.query(DentalChartRecord).filter(
                and_(
                    DentalChartRecord.patient_id == patient.id,
                    DentalChartRecord.quadrant == quadrant,
                    DentalChartRecord.tooth_number == tooth_number
                )
            ).first()
            
            if record:
                # Update existing record
                record.diagnosis = tooth_data.get('diagnosis', record.diagnosis)
                record.treatment_performed = tooth_data.get('treatment_performed', record.treatment_performed)
                record.status = tooth_data.get('status', record.status)
                record.updated_at = datetime.utcnow()
            else:
                # Create new record
                record = DentalChartRecord(
                    patient_id=patient.id,
                    quadrant=quadrant,
                    tooth_number=tooth_number,
                    diagnosis=tooth_data.get('diagnosis', ''),
                    treatment_performed=tooth_data.get('treatment_performed', ''),
                    status=tooth_data.get('status', 'normal')
                )
                session.add(record)
            
            session.commit()
            session.close()
            
            logger.info(f"Updated tooth record: {quadrant} #{tooth_number} for patient {patient_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating tooth record: {str(e)}")
            if session:
                session.rollback()
                session.close()
            return False
    
    def get_tooth_record(self, patient_id: str, quadrant: str, tooth_number: int) -> Optional[Dict]:
        """Get specific tooth record."""
        try:
            session = db_manager.get_session()
            
            # Get patient by patient_id
            patient = session.query(Patient).filter(Patient.patient_id == patient_id).first()
            if not patient:
                session.close()
                return None
            
            record = session.query(DentalChartRecord).filter(
                and_(
                    DentalChartRecord.patient_id == patient.id,
                    DentalChartRecord.quadrant == quadrant,
                    DentalChartRecord.tooth_number == tooth_number
                )
            ).first()
            
            if record:
                record_dict = self._chart_record_to_dict(record)
                session.close()
                return record_dict
            
            session.close()
            return None
            
        except Exception as e:
            logger.error(f"Error getting tooth record: {str(e)}")
            return None
    
    def _initialize_dental_chart(self, session: Session, patient_id: int):
        """Initialize empty dental chart with all 32 teeth."""
        quadrants = ['upper_right', 'upper_left', 'lower_right', 'lower_left']
        
        for quadrant in quadrants:
            for tooth_number in range(1, 8):  # 7 teeth per quadrant
                record = DentalChartRecord(
                    patient_id=patient_id,
                    quadrant=quadrant,
                    tooth_number=tooth_number,
                    diagnosis='',
                    treatment_performed='',
                    status='normal'
                )
                session.add(record)
    
    def _chart_record_to_dict(self, record: DentalChartRecord) -> Dict:
        """Convert DentalChartRecord object to dictionary."""
        return {
            'id': record.id,
            'patient_id': record.patient_id,
            'quadrant': record.quadrant,
            'tooth_number': record.tooth_number,
            'diagnosis': record.diagnosis or '',
            'treatment_performed': record.treatment_performed or '',
            'status': record.status,
            'created_at': record.created_at,
            'updated_at': record.updated_at
        }


# Global dental service instance
dental_service = DentalService()
