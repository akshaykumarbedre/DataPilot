"""
Database models for the Dental Practice Management System.
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, ForeignKey, Boolean, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    """User model for authentication."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relationships
    examinations = relationship("DentalExamination", back_populates="examiner")
    custom_statuses = relationship("CustomStatus", back_populates="created_by_user")
    
    def __repr__(self):
        return f"<User(username='{self.username}')>"


class Patient(Base):
    """Patient model for patient management."""
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(String(20), unique=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    phone_number = Column(String(20), nullable=False)
    date_of_birth = Column(Date)
    email = Column(String(255))
    address = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    chart_records = relationship("DentalChartRecord", back_populates="patient", cascade="all, delete-orphan")
    examinations = relationship("DentalExamination", back_populates="patient", cascade="all, delete-orphan")
    tooth_histories = relationship("ToothHistory", back_populates="patient", cascade="all, delete-orphan")
    visit_records = relationship("VisitRecord", back_populates="patient", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Patient(patient_id='{self.patient_id}', name='{self.full_name}')>"


class DentalExamination(Base):
    """Dental examination model for recording examination sessions."""
    __tablename__ = "dental_examinations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    examination_date = Column(Date, nullable=False)
    chief_complaint = Column(Text, nullable=False)
    history_of_presenting_illness = Column(Text)
    medical_history = Column(Text)
    dental_history = Column(Text)
    examination_findings = Column(Text)
    diagnosis = Column(Text)
    treatment_plan = Column(Text)
    notes = Column(Text)
    examiner_id = Column(Integer, ForeignKey("users.id"))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    patient = relationship("Patient", back_populates="examinations")
    examiner = relationship("User", back_populates="examinations")
    tooth_histories = relationship("ToothHistory", back_populates="examination", cascade="all, delete-orphan")
    visit_records = relationship("VisitRecord", back_populates="examination", cascade="all, delete-orphan")
    chart_records = relationship("DentalChartRecord", back_populates="examination")
    
    def __repr__(self):
        return f"<DentalExamination(patient_id={self.patient_id}, date='{self.examination_date}')>"


class ToothHistory(Base):
    """Tooth history model for tracking tooth-specific changes over time."""
    __tablename__ = "tooth_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    examination_id = Column(Integer, ForeignKey("dental_examinations.id"))
    tooth_number = Column(Integer, nullable=False)  # Full tooth number (11-18, 21-28, 31-38, 41-48)
    record_type = Column(String(20), nullable=False)  # 'patient_problem' or 'doctor_finding'
    
    # JSON fields for storing history as lists
    status_history = Column(Text)  # JSON list of status entries
    description_history = Column(Text)  # JSON list of description entries  
    date_history = Column(Text)  # JSON list of date entries
    
    # Keep single fields for backward compatibility
    status = Column(String(50))  # Current/latest status
    description = Column(Text)  # Current/latest description
    date_recorded = Column(Date, nullable=False)  # Current/latest date
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    patient = relationship("Patient", back_populates="tooth_histories")
    examination = relationship("DentalExamination", back_populates="tooth_histories")
    
    def __repr__(self):
        return f"<ToothHistory(patient_id={self.patient_id}, tooth={self.tooth_number}, type='{self.record_type}')>"


class VisitRecord(Base):
    """Visit record model for tracking patient visits and treatments."""
    __tablename__ = "visit_records"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    examination_id = Column(Integer, ForeignKey("dental_examinations.id"))
    visit_date = Column(Date, nullable=False)
    visit_time = Column(String(10))  # Added visit_time for more detailed scheduling
    visit_type = Column(String(50), default='consultation')  # Added visit_type
    status = Column(String(20), default='scheduled')  # Added status
    notes = Column(Text)  # Added notes
    duration_minutes = Column(Integer)  # Added duration tracking
    treatment_performed = Column(Text)
    next_visit_date = Column(Date)  # Added next visit scheduling
    doctor_name = Column(String(100))  # Added doctor name
    cost = Column(DECIMAL(10, 2))  # Renamed from amount_paid to cost
    amount_paid = Column(DECIMAL(10, 2), default=0)  # Keep for backward compatibility
    payment_status = Column(String(20), default='pending')  # Added payment status
    chief_complaint = Column(Text)
    diagnosis = Column(Text)
    advice = Column(Text)
    affected_teeth = Column(Text)  # JSON array of tooth numbers
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Added updated_at
    
    # Relationships
    patient = relationship("Patient", back_populates="visit_records")
    examination = relationship("DentalExamination", back_populates="visit_records")
    
    def __repr__(self):
        return f"<VisitRecord(patient_id={self.patient_id}, date='{self.visit_date}', type='{self.visit_type}')>"


class CustomStatus(Base):
    """Custom status model for user-defined tooth statuses."""
    __tablename__ = "custom_statuses"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    status_name = Column(String(50), unique=True, nullable=False)  # Added status_name
    status_code = Column(String(50), unique=True, nullable=False)
    display_name = Column(String(100), nullable=False)
    description = Column(Text)  # Added description
    color = Column(String(7), nullable=False)  # Renamed from color_code to color
    color_code = Column(String(7), nullable=False)  # Keep for backward compatibility
    category = Column(String(50), default='custom')  # Added category
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)  # Added sort_order
    icon_name = Column(String(50))  # Added icon_name
    created_by = Column(Integer, ForeignKey("users.id"))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Added updated_at
    
    # Relationships
    created_by_user = relationship("User", back_populates="custom_statuses")
    
    def __repr__(self):
        return f"<CustomStatus(status_name='{self.status_name}', display_name='{self.display_name}')>"


class DentalChartRecord(Base):
    """Dental chart record model for individual tooth data."""
    __tablename__ = "dental_chart_records"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    examination_id = Column(Integer, ForeignKey("dental_examinations.id"))
    quadrant = Column(String(20), nullable=False)  # 'upper_right', 'upper_left', 'lower_right', 'lower_left'
    tooth_number = Column(Integer, nullable=False)  # 1-8
    diagnosis = Column(Text)
    treatment_performed = Column(Text)
    status = Column(String(20), default="normal")  # Current tooth status
    current_status = Column(String(50), default="normal")  # Enhanced status
    last_patient_complaint = Column(Text)
    last_doctor_finding = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    patient = relationship("Patient", back_populates="chart_records")
    examination = relationship("DentalExamination", back_populates="chart_records")
    
    def __repr__(self):
        return f"<DentalChartRecord(patient_id={self.patient_id}, quadrant='{self.quadrant}', tooth={self.tooth_number})>"
