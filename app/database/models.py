"""
Database models for the Dental Practice Management System.
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, ForeignKey
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
    
    def __repr__(self):
        return f"<User(username='{self.username}')>"


class Patient(Base):
    """Patient model for patient management with examination data."""
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(String(20), unique=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    phone_number = Column(String(20), nullable=False)
    date_of_birth = Column(Date)
    email = Column(String(255))
    address = Column(Text)
    
    # Examination fields (flattened from DentalExamination)
    examination_date = Column(Date)
    chief_complaint = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    chart_records = relationship("DentalChartRecord", back_populates="patient", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Patient(patient_id='{self.patient_id}', name='{self.full_name}')>"


class DentalChartRecord(Base):
    """Dental chart record model for individual tooth data."""
    __tablename__ = "dental_chart_records"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)  # Direct reference to patient
    quadrant = Column(String(20), nullable=False)  # 'upper_right', 'upper_left', 'lower_right', 'lower_left'
    tooth_number = Column(Integer, nullable=False)  # 1-8
    diagnosis = Column(Text)
    treatment_performed = Column(Text)
    status = Column(String(20), default="normal")  # 'normal', 'treated', 'selected'
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    patient = relationship("Patient", back_populates="chart_records")
    
    def __repr__(self):
        return f"<DentalChartRecord(patient_id={self.patient_id}, quadrant='{self.quadrant}', tooth={self.tooth_number})>"
