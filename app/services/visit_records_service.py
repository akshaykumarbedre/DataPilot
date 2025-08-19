"""
Service for managing visit records.
"""
import logging
from datetime import date, datetime, time, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_, func, text

from ..database.database import db_manager
from ..database.models import VisitRecord, Patient, DentalExamination

logger = logging.getLogger(__name__)


class VisitRecordsService:
    """Service for managing visit records."""
    
    def create_visit(self, patient_id: int, visit_data: Dict[str, Any]) -> Optional[VisitRecord]:
        """
        Create a new visit record.
        
        Args:
            patient_id: ID of the patient
            visit_data: Dictionary containing visit data
            
        Returns:
            Created VisitRecord object or None if failed
        """
        try:
            session = db_manager.get_session()
            
            visit = VisitRecord(
                patient_id=patient_id,
                examination_id=visit_data.get('examination_id'),
                visit_date=visit_data.get('visit_date', date.today()),
                visit_time=visit_data.get('visit_time'),
                visit_type=visit_data.get('visit_type', 'consultation'),
                status=visit_data.get('status', 'scheduled'),
                notes=visit_data.get('notes', ''),
                duration_minutes=visit_data.get('duration_minutes'),
                treatment_performed=visit_data.get('treatment_performed', ''),
                next_visit_date=visit_data.get('next_visit_date'),
                doctor_name=visit_data.get('doctor_name', ''),
                cost=visit_data.get('cost'),
                payment_status=visit_data.get('payment_status', 'pending')
            )
            
            session.add(visit)
            session.commit()
            
            visit_id = visit.id
            session.close()
            
            logger.info(f"Created visit {visit_id} for patient {patient_id}")
            return self.get_visit_by_id(visit_id)
            
        except Exception as e:
            logger.error(f"Error creating visit: {str(e)}")
            if session:
                session.rollback()
                session.close()
            return None
    
    def get_visit_by_id(self, visit_id: int) -> Optional[Dict[str, Any]]:
        """
        Get visit by ID.
        
        Args:
            visit_id: ID of the visit record
            
        Returns:
            Dictionary containing visit data or None if not found
        """
        try:
            session = db_manager.get_session()
            
            visit = session.query(VisitRecord).filter(
                VisitRecord.id == visit_id
            ).first()
            
            if not visit:
                session.close()
                return None
            
            result = {
                'id': visit.id,
                'patient_id': visit.patient_id,
                'examination_id': visit.examination_id,
                'visit_date': visit.visit_date,
                'visit_time': visit.visit_time,
                'visit_type': visit.visit_type,
                'status': visit.status,
                'notes': visit.notes,
                'duration_minutes': visit.duration_minutes,
                'treatment_performed': visit.treatment_performed,
                'next_visit_date': visit.next_visit_date,
                'doctor_name': visit.doctor_name,
                'cost': visit.cost,
                'payment_status': visit.payment_status,
                'created_at': visit.created_at,
                'updated_at': visit.updated_at,
                'patient_name': visit.patient.full_name if visit.patient else '',
                'examination_date': visit.examination.examination_date if visit.examination else None
            }
            
            session.close()
            return result
            
        except Exception as e:
            logger.error(f"Error getting visit {visit_id}: {str(e)}")
            if session:
                session.close()
            return None
    
    def get_patient_visits(self, patient_id: int, limit: Optional[int] = None, 
                          status: Optional[str] = None, visit_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get visits for a patient.
        
        Args:
            patient_id: ID of the patient
            limit: Optional limit on number of results
            status: Optional status filter
            visit_type: Optional visit type filter
            
        Returns:
            List of visit dictionaries
        """
        try:
            session = db_manager.get_session()
            
            query = session.query(VisitRecord).filter(VisitRecord.patient_id == patient_id)
            
            if status:
                query = query.filter(VisitRecord.status == status)
            
            if visit_type:
                query = query.filter(VisitRecord.visit_type == visit_type)
            
            query = query.order_by(desc(VisitRecord.visit_date), desc(VisitRecord.visit_time))
            
            if limit:
                query = query.limit(limit)
            
            visits = query.all()
            
            results = []
            for visit in visits:
                results.append({
                    'id': visit.id,
                    'patient_id': visit.patient_id,
                    'examination_id': visit.examination_id,
                    'visit_date': visit.visit_date,
                    'visit_time': visit.visit_time,
                    'visit_type': visit.visit_type,
                    'status': visit.status,
                    'notes': visit.notes,
                    'duration_minutes': visit.duration_minutes,
                    'treatment_performed': visit.treatment_performed,
                    'next_visit_date': visit.next_visit_date,
                    'doctor_name': visit.doctor_name,
                    'cost': visit.cost,
                    'payment_status': visit.payment_status,
                    'created_at': visit.created_at,
                    'updated_at': visit.updated_at
                })
            
            session.close()
            return results
            
        except Exception as e:
            logger.error(f"Error getting visits for patient {patient_id}: {str(e)}")
            if session:
                session.close()
            return []
    
    def get_visits_by_date_range(self, start_date: date, end_date: date, 
                                status: Optional[str] = None, doctor_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get visits within a date range.
        
        Args:
            start_date: Start date for the range
            end_date: End date for the range
            status: Optional status filter
            doctor_name: Optional doctor name filter
            
        Returns:
            List of visit dictionaries
        """
        try:
            session = db_manager.get_session()
            
            query = session.query(VisitRecord).filter(
                and_(
                    VisitRecord.visit_date >= start_date,
                    VisitRecord.visit_date <= end_date
                )
            )
            
            if status:
                query = query.filter(VisitRecord.status == status)
            
            if doctor_name:
                query = query.filter(VisitRecord.doctor_name.ilike(f'%{doctor_name}%'))
            
            visits = query.order_by(VisitRecord.visit_date, VisitRecord.visit_time).all()
            
            results = []
            for visit in visits:
                results.append({
                    'id': visit.id,
                    'patient_id': visit.patient_id,
                    'examination_id': visit.examination_id,
                    'visit_date': visit.visit_date,
                    'visit_time': visit.visit_time,
                    'visit_type': visit.visit_type,
                    'status': visit.status,
                    'notes': visit.notes,
                    'duration_minutes': visit.duration_minutes,
                    'treatment_performed': visit.treatment_performed,
                    'next_visit_date': visit.next_visit_date,
                    'doctor_name': visit.doctor_name,
                    'cost': visit.cost,
                    'payment_status': visit.payment_status,
                    'created_at': visit.created_at,
                    'updated_at': visit.updated_at,
                    'patient_name': visit.patient.full_name if visit.patient else ''
                })
            
            session.close()
            return results
            
        except Exception as e:
            logger.error(f"Error getting visits by date range: {str(e)}")
            if session:
                session.close()
            return []
    
    def get_today_visits(self, doctor_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get today's visits.
        
        Args:
            doctor_name: Optional doctor name filter
            
        Returns:
            List of today's visit dictionaries
        """
        today = date.today()
        return self.get_visits_by_date_range(today, today, doctor_name=doctor_name)
    
    def get_upcoming_visits(self, days_ahead: int = 7) -> List[Dict[str, Any]]:
        """
        Get upcoming visits within specified days.
        
        Args:
            days_ahead: Number of days to look ahead (default 7)
            
        Returns:
            List of upcoming visit dictionaries
        """
        start_date = date.today()
        end_date = start_date + timedelta(days=days_ahead)
        return self.get_visits_by_date_range(start_date, end_date, status='scheduled')
    
    def update_visit(self, visit_id: int, update_data: Dict[str, Any]) -> bool:
        """
        Update a visit record.
        
        Args:
            visit_id: ID of the visit to update
            update_data: Dictionary containing fields to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            session = db_manager.get_session()
            
            visit = session.query(VisitRecord).filter(VisitRecord.id == visit_id).first()
            
            if not visit:
                session.close()
                return False
            
            # Update allowed fields
            allowed_fields = [
                'visit_date', 'visit_time', 'visit_type', 'status', 'notes',
                'duration_minutes', 'treatment_performed', 'next_visit_date',
                'doctor_name', 'cost', 'payment_status'
            ]
            
            for field in allowed_fields:
                if field in update_data:
                    setattr(visit, field, update_data[field])
            
            visit.updated_at = datetime.now()
            session.commit()
            session.close()
            
            logger.info(f"Updated visit {visit_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating visit {visit_id}: {str(e)}")
            if session:
                session.rollback()
                session.close()
            return False
    
    def update_visit_status(self, visit_id: int, new_status: str, notes: str = '') -> bool:
        """
        Update visit status.
        
        Args:
            visit_id: ID of the visit
            new_status: New status ('scheduled', 'in_progress', 'completed', 'cancelled', 'no_show')
            notes: Optional notes about the status change
            
        Returns:
            True if successful, False otherwise
        """
        update_data = {'status': new_status}
        if notes:
            update_data['notes'] = notes
        
        return self.update_visit(visit_id, update_data)
    
    def complete_visit(self, visit_id: int, treatment_performed: str = '', 
                      duration_minutes: Optional[int] = None, cost: Optional[float] = None,
                      next_visit_date: Optional[date] = None) -> bool:
        """
        Mark a visit as completed.
        
        Args:
            visit_id: ID of the visit
            treatment_performed: Description of treatment performed
            duration_minutes: Actual duration of the visit
            cost: Cost of the visit
            next_visit_date: Date for next recommended visit
            
        Returns:
            True if successful, False otherwise
        """
        update_data = {
            'status': 'completed',
            'treatment_performed': treatment_performed
        }
        
        if duration_minutes:
            update_data['duration_minutes'] = duration_minutes
        
        if cost:
            update_data['cost'] = cost
        
        if next_visit_date:
            update_data['next_visit_date'] = next_visit_date
        
        return self.update_visit(visit_id, update_data)
    
    def delete_visit(self, visit_id: int) -> bool:
        """
        Delete a visit record.
        
        Args:
            visit_id: ID of the visit to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            session = db_manager.get_session()
            
            visit = session.query(VisitRecord).filter(VisitRecord.id == visit_id).first()
            
            if not visit:
                session.close()
                return False
            
            session.delete(visit)
            session.commit()
            session.close()
            
            logger.info(f"Deleted visit {visit_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting visit {visit_id}: {str(e)}")
            if session:
                session.rollback()
                session.close()
            return False
    
    def add_visit_record(self, visit_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a new visit record (wrapper for create_visit with success response).
        
        Args:
            visit_data: Dictionary containing visit data
            
        Returns:
            Dictionary with 'success' status and visit data
        """
        try:
            patient_id = visit_data.get('patient_id')
            if not patient_id:
                return {'success': False, 'error': 'Patient ID is required'}
            
            visit = self.create_visit(patient_id, visit_data)
            
            if visit:
                return {
                    'success': True,
                    'visit': visit,
                    'message': 'Visit record created successfully'
                }
            else:
                return {
                    'success': False, 
                    'error': 'Failed to create visit record'
                }
                
        except Exception as e:
            logger.error(f"Error adding visit record: {str(e)}")
            return {
                'success': False,
                'error': f'Error adding visit record: {str(e)}'
            }
    
    def get_visit_records(self, patient_id: Optional[int] = None, 
                         examination_id: Optional[int] = None,
                         limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get visit records with optional filters.
        
        Args:
            patient_id: Optional patient ID filter
            examination_id: Optional examination ID filter
            limit: Optional limit on results
            
        Returns:
            List of visit record dictionaries
        """
        try:
            session = db_manager.get_session()
            
            query = session.query(VisitRecord)
            
            if patient_id:
                query = query.filter(VisitRecord.patient_id == patient_id)
            
            if examination_id:
                query = query.filter(VisitRecord.examination_id == examination_id)
            
            query = query.order_by(desc(VisitRecord.visit_date), desc(VisitRecord.visit_time))
            
            if limit:
                query = query.limit(limit)
            
            visits = query.all()
            
            results = []
            for visit in visits:
                results.append({
                    'id': visit.id,
                    'patient_id': visit.patient_id,
                    'examination_id': visit.examination_id,
                    'visit_date': visit.visit_date,
                    'visit_time': visit.visit_time,
                    'visit_type': visit.visit_type,
                    'status': visit.status,
                    'notes': visit.notes,
                    'duration_minutes': visit.duration_minutes,
                    'treatment_performed': visit.treatment_performed,
                    'next_visit_date': visit.next_visit_date,
                    'doctor_name': visit.doctor_name,
                    'cost': visit.cost,
                    'payment_status': visit.payment_status,
                    'created_at': visit.created_at,
                    'updated_at': visit.updated_at,
                    'patient_name': visit.patient.full_name if visit.patient else '',
                    'examination_date': visit.examination.examination_date if visit.examination else None
                })
            
            session.close()
            return results
            
        except Exception as e:
            logger.error(f"Error getting visit records: {str(e)}")
            if session:
                session.close()
            return []

    def get_visit_statistics(self, start_date: Optional[date] = None, 
                           end_date: Optional[date] = None) -> Dict[str, Any]:
        """
        Get visit statistics.
        
        Args:
            start_date: Optional start date for statistics
            end_date: Optional end date for statistics
            
        Returns:
            Dictionary containing visit statistics
        """
        try:
            session = db_manager.get_session()
            
            query = session.query(VisitRecord)
            
            if start_date:
                query = query.filter(VisitRecord.visit_date >= start_date)
            
            if end_date:
                query = query.filter(VisitRecord.visit_date <= end_date)
            
            total_visits = query.count()
            
            # Status breakdown
            scheduled = query.filter(VisitRecord.status == 'scheduled').count()
            completed = query.filter(VisitRecord.status == 'completed').count()
            cancelled = query.filter(VisitRecord.status == 'cancelled').count()
            no_show = query.filter(VisitRecord.status == 'no_show').count()
            
            # Visit type breakdown
            consultation = query.filter(VisitRecord.visit_type == 'consultation').count()
            treatment = query.filter(VisitRecord.visit_type == 'treatment').count()
            follow_up = query.filter(VisitRecord.visit_type == 'follow_up').count()
            emergency = query.filter(VisitRecord.visit_type == 'emergency').count()
            
            # Financial statistics
            total_revenue = session.query(func.sum(VisitRecord.cost)).filter(
                VisitRecord.status == 'completed'
            ).scalar() or 0
            
            if start_date:
                total_revenue = session.query(func.sum(VisitRecord.cost)).filter(
                    and_(
                        VisitRecord.status == 'completed',
                        VisitRecord.visit_date >= start_date
                    )
                ).scalar() or 0
            
            if end_date:
                total_revenue = session.query(func.sum(VisitRecord.cost)).filter(
                    and_(
                        VisitRecord.status == 'completed',
                        VisitRecord.visit_date <= end_date
                    )
                ).scalar() or 0
            
            session.close()
            
            return {
                'total_visits': total_visits,
                'status_breakdown': {
                    'scheduled': scheduled,
                    'completed': completed,
                    'cancelled': cancelled,
                    'no_show': no_show
                },
                'visit_type_breakdown': {
                    'consultation': consultation,
                    'treatment': treatment,
                    'follow_up': follow_up,
                    'emergency': emergency
                },
                'total_revenue': float(total_revenue),
                'completion_rate': round((completed / total_visits * 100), 2) if total_visits > 0 else 0,
                'no_show_rate': round((no_show / total_visits * 100), 2) if total_visits > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting visit statistics: {str(e)}")
            if session:
                session.close()
            return {
                'total_visits': 0,
                'status_breakdown': {'scheduled': 0, 'completed': 0, 'cancelled': 0, 'no_show': 0},
                'visit_type_breakdown': {'consultation': 0, 'treatment': 0, 'follow_up': 0, 'emergency': 0},
                'total_revenue': 0.0,
                'completion_rate': 0.0,
                'no_show_rate': 0.0
            }


# Global service instance
visit_records_service = VisitRecordsService()
