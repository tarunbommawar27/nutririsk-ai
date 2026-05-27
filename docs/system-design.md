# System Design

## Workflow

```text
EHR/FHIR data source
  -> daily feature extraction
  -> risk model inference
  -> risk score database
  -> clinician dashboard
  -> clinician action tracking
  -> audit logs and monitoring
```

## Services

- Next.js frontend
- FastAPI backend
- PostgreSQL database
- Redis/Celery background jobs
- ML training/inference pipeline
- MLflow-compatible experiment tracking hook

## Data model

- patients
- admissions
- patient_daily_features
- risk_scores
- clinician_actions
- audit_logs
- model_versions

## Security considerations

- authentication
- role-based access
- audit logs
- encrypted transport
- environment-based secrets
- no PHI in public demo

## Production improvements

- FHIR integration
- model registry
- asynchronous screening jobs
- model drift monitoring
- calibration monitoring
- human feedback loop
- alert fatigue tracking
