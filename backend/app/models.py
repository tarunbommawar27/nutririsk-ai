from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from .database import Base

class Patient(Base):
    __tablename__ = "patients"
    patient_id = Column(String, primary_key=True, index=True)
    age = Column(Integer, nullable=False)
    gender = Column(String, nullable=False)
    ethnicity = Column(String, nullable=True)
    admissions = relationship("Admission", back_populates="patient")

class Admission(Base):
    __tablename__ = "admissions"
    admission_id = Column(String, primary_key=True, index=True)
    patient_id = Column(String, ForeignKey("patients.patient_id"), nullable=False)
    admit_date = Column(Date, nullable=False)
    unit = Column(String, nullable=False)
    admission_type = Column(String, nullable=False)
    status = Column(String, default="active")
    patient = relationship("Patient", back_populates="admissions")
    risk_scores = relationship("RiskScore", back_populates="admission")

class RiskScore(Base):
    __tablename__ = "risk_scores"
    score_id = Column(Integer, primary_key=True, autoincrement=True)
    admission_id = Column(String, ForeignKey("admissions.admission_id"), index=True)
    patient_day = Column(Integer, nullable=False)
    model_version = Column(String, default="demo-v1")
    risk_score = Column(Float, nullable=False)
    risk_bucket = Column(String, nullable=False)
    top_features_json = Column(JSON, nullable=True)
    evidence_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    admission = relationship("Admission", back_populates="risk_scores")

class ClinicianAction(Base):
    __tablename__ = "clinician_actions"
    action_id = Column(Integer, primary_key=True, autoincrement=True)
    admission_id = Column(String, ForeignKey("admissions.admission_id"), index=True)
    user_name = Column(String, default="demo.clinician")
    action_type = Column(String, nullable=False)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    audit_id = Column(Integer, primary_key=True, autoincrement=True)
    user_name = Column(String, default="demo.clinician")
    action = Column(String, nullable=False)
    resource_type = Column(String, nullable=False)
    resource_id = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
