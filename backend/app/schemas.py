from datetime import datetime, date
from typing import Any, Optional
from pydantic import BaseModel

class PatientOut(BaseModel):
    patient_id: str
    age: int
    gender: str
    ethnicity: Optional[str] = None

class AdmissionRiskOut(BaseModel):
    admission_id: str
    patient_id: str
    age: int
    gender: str
    unit: str
    admission_type: str
    patient_day: int
    risk_score: float
    risk_bucket: str
    top_features: list[dict[str, Any]] = []
    status: str = "New"
    created_at: datetime

class PatientDetailOut(BaseModel):
    patient: PatientOut
    admission_id: str
    admit_date: date
    unit: str
    admission_type: str
    latest_score: AdmissionRiskOut
    score_timeline: list[dict[str, Any]]
    evidence: dict[str, Any]
    actions: list[dict[str, Any]]

class ActionIn(BaseModel):
    admission_id: str
    action_type: str
    note: str | None = None
    user_name: str = "demo.clinician"

class ActionOut(BaseModel):
    action_id: int
    admission_id: str
    action_type: str
    note: str | None = None
    created_at: datetime

class AnalyticsOut(BaseModel):
    patients_screened_today: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    reviewed_count: int
    avg_risk_score: float
    model_version: str

class ModelMetricsOut(BaseModel):
    model_version: str
    auroc: float | None = None
    auprc: float | None = None
    accuracy: float | None = None
    recall: float | None = None
    precision: float | None = None
    f1: float | None = None
    note: str
