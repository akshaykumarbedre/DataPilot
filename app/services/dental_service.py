"""
Dental service for examination and chart operations.
"""
import logging
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_
from ..database.models import Patient, DentalChartRecord, DentalExamination
from ..database.database import db_manager

logger = logging.getLogger(__name__)


class DentalService:
    """Service class for dental examination and chart operations."""
    
    def __init__(self):
        pass

    def create_examination(self, patient_id: str, examination_data: Dict[str, Any]) -> Optional[Dict]:
        """Create a new dental examination for a patient."""
        try:
            session = db_manager.get_session()
            
            patient = session.query(Patient).filter(Patient.patient_id == patient_id).first()
            if not patient:
                logger.warning(f"Patient not found: {patient_id}")
                session.close()
                return None

            new_exam = DentalExamination(
                patient_id=patient.id,
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
            
            session.add(new_exam)
            session.commit()

            # Initialize a dental chart for this new examination
            self._initialize_dental_chart(session, patient.id, new_exam.id)
            
            session.commit()
            
            exam_dict = {
                'id': new_exam.id,
                'patient_id': patient.patient_id,
                'examination_date': new_exam.examination_date,
                'chief_complaint': new_exam.chief_complaint
            }
            
            session.close()
            logger.info(f"Created new examination {new_exam.id} for patient {patient_id}")
            return exam_dict

        except Exception as e:
            logger.error(f"Error creating examination for patient {patient_id}: {str(e)}")
            if session:
                session.rollback()
                session.close()
            return None

    def get_all_patient_examinations(self, patient_id: str) -> List[Dict]:
        """Get all examination data for a patient."""
        try:
            session = db_manager.get_session()
            
            patient = session.query(Patient).filter(Patient.patient_id == patient_id).first()
            if not patient:
                session.close()
                return []

            examinations = session.query(DentalExamination).filter(DentalExamination.patient_id == patient.id).all()
            
            examination_list = []
            for exam in examinations:
                examination_list.append({
                    'id': exam.id,
                    'patient_id': patient.patient_id,
                    'examination_date': exam.examination_date,
                    'chief_complaint': exam.chief_complaint,
                    'history_of_presenting_illness': exam.history_of_presenting_illness,
                    'medical_history': exam.medical_history,
                    'dental_history': exam.dental_history,
                    'examination_findings': exam.examination_findings,
                    'diagnosis': exam.diagnosis,
                    'treatment_plan': exam.treatment_plan,
                    'notes': exam.notes
                })
            
            session.close()
            return examination_list
            
        except Exception as e:
            logger.error(f"Error getting all examinations for patient {patient_id}: {str(e)}")
            return []

    def get_dental_chart(self, patient_id: str, examination_id: int = None) -> Dict[str, List[Dict]]:
        """Get dental chart records for a patient, optionally filtered by examination."""
        try:
            session = db_manager.get_session()
            
            patient = session.query(Patient).filter(Patient.patient_id == patient_id).first()
            if not patient:
                session.close()
                return {}

            query = session.query(DentalChartRecord).filter(DentalChartRecord.patient_id == patient.id)
            
            if examination_id:
                logger.info(f"Filtering chart by examination_id: {examination_id}")
                query = query.filter(DentalChartRecord.examination_id == examination_id)
            
            chart_records = query.all()
            logger.info(f"Found {len(chart_records)} chart records for patient {patient_id}, exam {examination_id}")
            
            chart_data = {
                'upper_right': [], 'upper_left': [],
                'lower_right': [], 'lower_left': []
            }
            
            for record in chart_records:
                quadrant = record.quadrant
                if quadrant in chart_data:
                    chart_data[quadrant].append(self._chart_record_to_dict(record))
            
            for quadrant in chart_data:
                chart_data[quadrant].sort(key=lambda x: x['tooth_number'])
            
            logger.info(f"Returning chart data: {chart_data}")
            session.close()
            return chart_data
            
        except Exception as e:
            logger.error(f"Error getting dental chart for patient {patient_id}: {str(e)}")
            return {}

    def update_tooth_record(self, patient_id: str, examination_id: int, quadrant: str, tooth_number: int, 
                           tooth_data: Dict[str, Any]) -> bool:
        """Update a specific tooth record for a given examination."""
        try:
            session = db_manager.get_session()
            
            patient = session.query(Patient).filter(Patient.patient_id == patient_id).first()
            if not patient:
                logger.warning(f"Patient not found: {patient_id}")
                session.close()
                return False
            
            record = session.query(DentalChartRecord).filter(
                and_(
                    DentalChartRecord.patient_id == patient.id,
                    DentalChartRecord.examination_id == examination_id,
                    DentalChartRecord.quadrant == quadrant,
                    DentalChartRecord.tooth_number == tooth_number
                )
            ).first()
            
            if record:
                record.diagnosis = tooth_data.get('diagnosis', record.diagnosis)
                record.treatment_performed = tooth_data.get('treatment_performed', record.treatment_performed)
                record.status = tooth_data.get('status', record.status)
                record.updated_at = datetime.utcnow()
            else:
                # This case should ideally not be hit if chart is initialized with examination
                record = DentalChartRecord(
                    patient_id=patient.id,
                    examination_id=examination_id,
                    quadrant=quadrant,
                    tooth_number=tooth_number,
                    diagnosis=tooth_data.get('diagnosis', ''),
                    treatment_performed=tooth_data.get('treatment_performed', ''),
                    status=tooth_data.get('status', 'normal')
                )
                session.add(record)
            
            session.commit()
            session.close()
            
            logger.info(f"Updated tooth record: {quadrant} #{tooth_number} for patient {patient_id}, exam {examination_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating tooth record: {str(e)}")
            if session:
                session.rollback()
                session.close()
            return False

    def _initialize_dental_chart(self, session: Session, patient_id: int, examination_id: int):
        """Initialize empty dental chart for a specific examination."""
        quadrants = ['upper_right', 'upper_left', 'lower_right', 'lower_left']
        
        for quadrant in quadrants:
            for tooth_number in range(1, 9):  # 8 teeth per quadrant
                record = DentalChartRecord(
                    patient_id=patient_id,
                    examination_id=examination_id,
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
            'examination_id': record.examination_id,
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
