# NutriRisk AI — Clinical Malnutrition Risk Screening Prototype

A production-style full-stack clinical decision support prototype inspired by daily EHR screening workflows. It screens inpatient records, predicts malnutrition risk, explains why patients are flagged, and gives clinicians a review/action dashboard.

> Safety: This is a research/demo prototype only. It is not a medical device, does not diagnose malnutrition, and must not be used for clinical care.

## What is included

- **Backend:** FastAPI, SQLAlchemy, PostgreSQL/SQLite-compatible models, authentication-lite demo endpoints, audit logs, risk score APIs.
- **ML:** Synthetic EHR generator, training pipeline, XGBoost/RandomForest fallback, SHAP-compatible explanation fallback, model artifact saving.
- **Frontend:** Next.js + TypeScript + Tailwind-style CSS dashboard, patient queue, patient detail page, analytics page.
- **Infra:** Docker Compose for backend, frontend, Postgres, Redis.
- **Docs:** model card, clinical safety note, system design, data dictionary.

## Project structure

```text
nutririsk-ai/
├── backend/              # FastAPI API server
├── frontend/             # Next.js UI
├── ml/                   # data generation + training + inference utilities
├── data/demo/            # generated synthetic demo data
├── docs/                 # model card, safety, architecture notes
├── infra/                # Dockerfiles and compose
└── scripts/              # helper scripts
```

## Fast local start: backend + ML demo

### 1. Create Python environment

```bash
cd nutririsk-ai
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r backend/requirements.txt
pip install -r ml/requirements.txt
```

### 2. Generate synthetic EHR data

```bash
python ml/src/generate_synthetic_ehr.py --out data/demo --n-patients 1200
```

### 3. Train the model

```bash
python ml/src/train.py --data data/demo/patient_day_features.csv --out ml/models
```

### 4. Initialize the backend database

```bash
cd backend
cp .env.example .env
python -m app.seed_demo
uvicorn app.main:app --reload --port 8000
```

Open API docs:

```text
http://localhost:8000/docs
```

## Frontend start

In another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open:

```text
http://localhost:3000
```

By default the frontend expects:

```text
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

You can create `frontend/.env.local`:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

## Docker Compose start

```bash
cd nutririsk-ai
python ml/src/generate_synthetic_ehr.py --out data/demo --n-patients 1200
python ml/src/train.py --data data/demo/patient_day_features.csv --out ml/models
cd infra
docker compose up --build
```

Then open:

```text
Frontend: http://localhost:3000
Backend:  http://localhost:8000/docs
```

## Main API endpoints

```text
GET  /health
GET  /api/patients
GET  /api/patients/{admission_id}
GET  /api/risk-scores/today
POST /api/screen/run
POST /api/actions
GET  /api/analytics/summary
GET  /api/model/metrics
```

## How to replace synthetic data with MIMIC-IV

1. Get credentialed access to MIMIC-IV through PhysioNet.
2. Export admission-level and patient-day features into the same schema as `data/demo/patient_day_features.csv`.
3. Keep the target label as a separate column named `malnutrition_label`.
4. Do not include future diagnosis, discharge disposition, or final billing outcomes as model features.
5. Re-run:

```bash
python ml/src/train.py --data path/to/mimic_patient_day_features.csv --out ml/models
```

## Suggested demo script

1. Open dashboard and show “patients screened today.”
2. Filter to high-risk patients.
3. Open a patient detail page.
4. Explain the evidence timeline and top risk drivers.
5. Mark the patient as “Needs dietitian consult.”
6. Show analytics/model monitoring page.
7. Explain safety: decision support only, not diagnosis.

## Resume bullet

Built NutriRisk AI, a production-style clinical decision support platform that screens inpatient EHR records daily for malnutrition risk using XGBoost, SHAP-style explainability, FastAPI, PostgreSQL, and a Next.js clinician dashboard; implemented patient risk queues, evidence timelines, audit logging, model monitoring, and synthetic EHR demo data for safe public deployment.
