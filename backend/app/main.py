from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from .config import get_settings
from .database import Base, engine, get_db
from .models import Patient, Admission, RiskScore, ClinicianAction, AuditLog
from .schemas import AdmissionRiskOut, PatientDetailOut, ActionIn, ActionOut, AnalyticsOut, ModelMetricsOut
from .ml_service import risk_model_service

settings = get_settings()
Base.metadata.create_all(bind=engine)

app = FastAPI(title="NutriRisk AI API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok", "service": "nutririsk-api"}


def _latest_rows(db: Session):
    subq = db.query(
        RiskScore.admission_id,
        func.max(RiskScore.created_at).label("max_created")
    ).group_by(RiskScore.admission_id).subquery()
    rows = db.query(RiskScore, Admission, Patient).join(
        subq,
        (RiskScore.admission_id == subq.c.admission_id) & (RiskScore.created_at == subq.c.max_created)
    ).join(Admission, Admission.admission_id == RiskScore.admission_id).join(Patient, Patient.patient_id == Admission.patient_id).all()
    return rows


def _risk_out(rs: RiskScore, adm: Admission, p: Patient):
    latest_action = None
    return AdmissionRiskOut(
        admission_id=adm.admission_id,
        patient_id=p.patient_id,
        age=p.age,
        gender=p.gender,
        unit=adm.unit,
        admission_type=adm.admission_type,
        patient_day=rs.patient_day,
        risk_score=round(rs.risk_score, 4),
        risk_bucket=rs.risk_bucket,
        top_features=rs.top_features_json or [],
        status=latest_action or "New",
        created_at=rs.created_at,
    )

@app.get("/api/risk-scores/today", response_model=list[AdmissionRiskOut])
def risk_scores_today(db: Session = Depends(get_db)):
    rows = _latest_rows(db)
    return sorted([_risk_out(rs, adm, p) for rs, adm, p in rows], key=lambda x: x.risk_score, reverse=True)

@app.get("/api/patients", response_model=list[AdmissionRiskOut])
def patients(db: Session = Depends(get_db)):
    return risk_scores_today(db)

@app.get("/api/patients/{admission_id}", response_model=PatientDetailOut)
def patient_detail(admission_id: str, db: Session = Depends(get_db)):
    adm = db.query(Admission).filter(Admission.admission_id == admission_id).first()
    if not adm:
        raise HTTPException(404, "Admission not found")
    p = db.query(Patient).filter(Patient.patient_id == adm.patient_id).first()
    scores = db.query(RiskScore).filter(RiskScore.admission_id == admission_id).order_by(RiskScore.patient_day.asc()).all()
    if not scores:
        raise HTTPException(404, "No risk scores found")
    latest = scores[-1]
    actions = db.query(ClinicianAction).filter(ClinicianAction.admission_id == admission_id).order_by(desc(ClinicianAction.created_at)).all()
    db.add(AuditLog(action="view_patient", resource_type="admission", resource_id=admission_id))
    db.commit()
    return PatientDetailOut(
        patient={"patient_id": p.patient_id, "age": p.age, "gender": p.gender, "ethnicity": p.ethnicity},
        admission_id=adm.admission_id,
        admit_date=adm.admit_date,
        unit=adm.unit,
        admission_type=adm.admission_type,
        latest_score=_risk_out(latest, adm, p),
        score_timeline=[{"day": s.patient_day, "risk_score": round(s.risk_score, 4), "risk_bucket": s.risk_bucket} for s in scores],
        evidence=latest.evidence_json or {},
        actions=[{"action_id": a.action_id, "action_type": a.action_type, "note": a.note, "created_at": a.created_at} for a in actions],
    )

@app.post("/api/actions", response_model=ActionOut)
def create_action(action: ActionIn, db: Session = Depends(get_db)):
    if not db.query(Admission).filter(Admission.admission_id == action.admission_id).first():
        raise HTTPException(404, "Admission not found")
    obj = ClinicianAction(**action.model_dump())
    db.add(obj)
    db.add(AuditLog(user_name=action.user_name, action=f"clinician_action:{action.action_type}", resource_type="admission", resource_id=action.admission_id))
    db.commit()
    db.refresh(obj)
    return obj

@app.post("/api/screen/run")
def run_screening(db: Session = Depends(get_db)):
    # In production this would pull new patient-day features from EHR/FHIR.
    # Demo endpoint returns current scores and confirms worker integration point.
    return {"status": "completed", "message": "Demo screening job is seeded. Use seed_demo to regenerate scores."}

@app.get("/api/analytics/summary", response_model=AnalyticsOut)
def analytics(db: Session = Depends(get_db)):
    rows = _latest_rows(db)
    scores = [rs.risk_score for rs, _, _ in rows]
    buckets = [rs.risk_bucket for rs, _, _ in rows]
    reviewed = db.query(ClinicianAction.admission_id).distinct().count()
    return AnalyticsOut(
        patients_screened_today=len(rows),
        high_risk_count=buckets.count("High"),
        medium_risk_count=buckets.count("Medium"),
        low_risk_count=buckets.count("Low"),
        reviewed_count=reviewed,
        avg_risk_score=round(sum(scores) / len(scores), 4) if scores else 0,
        model_version="demo-v1",
    )

@app.get("/api/model/metrics", response_model=ModelMetricsOut)
def model_metrics():
    import json
    from pathlib import Path
    metrics_path = Path("../ml/models/metrics.json")
    if metrics_path.exists():
        m = json.loads(metrics_path.read_text())
        return ModelMetricsOut(**m, note="Metrics from latest local training run on synthetic/demo data.")
    return ModelMetricsOut(model_version="demo-v1", note="No metrics.json found. Run ml/src/train.py first.")
