#!/usr/bin/env bash
set -e
python ml/src/generate_synthetic_ehr.py --out data/demo --n-patients 1200
python ml/src/train.py --data data/demo/patient_day_features.csv --out ml/models
cd backend
cp -n .env.example .env || true
python -m app.seed_demo
uvicorn app.main:app --reload --port 8000
