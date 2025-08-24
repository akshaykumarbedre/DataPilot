"""
Migration script to associate orphan DentalChartRecords with an examination.
"""
import logging
from app.database.database import db_manager
from app.database.models import Patient, DentalExamination, DentalChartRecord

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migration():
    """Assigns orphan dental chart records to the first examination of the patient."""
    session = db_manager.get_session()
    
    try:
        logger.info("Starting migration to fix orphan dental chart records...")
        
        # Find all chart records with no examination_id
        orphan_charts = session.query(DentalChartRecord).filter(DentalChartRecord.examination_id == None).all()
        
        logger.info(f"Found {len(orphan_charts)} orphan chart records to migrate.")
        
        migrated_count = 0
        for chart in orphan_charts:
            patient = session.query(Patient).filter(Patient.id == chart.patient_id).first()
            if not patient:
                logger.warning(f"Could not find patient with id {chart.patient_id} for chart record {chart.id}. Skipping.")
                continue

            # Find the first examination for this patient
            first_exam = session.query(DentalExamination).filter(DentalExamination.patient_id == patient.id).order_by(DentalExamination.examination_date).first()
            
            if first_exam:
                chart.examination_id = first_exam.id
                migrated_count += 1
                logger.info(f"Assigning chart record {chart.id} to examination {first_exam.id} for patient {patient.patient_id}")
            else:
                logger.warning(f"Patient {patient.patient_id} has no examinations. Cannot assign chart record {chart.id}. Skipping.")

        if migrated_count > 0:
            session.commit()
            logger.info(f"Successfully migrated {migrated_count} orphan chart records.")
        else:
            logger.info("No chart records were migrated.")
            
    except Exception as e:
        logger.error(f"An error occurred during migration: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    run_migration()
