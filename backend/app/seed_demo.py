from datetime import date, timedelta
from pathlib import Path

import pandas as pd

from .database import Base, engine, SessionLocal
from .models import Patient, Admission, RiskScore
from .config import get_settings
from .ml_service import risk_model_service


settings = get_settings()

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


def main():
    data_path = Path(settings.demo_data_path)

    if not data_path.exists():
        raise FileNotFoundError(
            f"Demo data not found: {data_path}. Run ml/src/generate_synthetic_ehr.py first."
        )

    df = pd.read_csv(data_path)

    # Seed latest 250 admissions only for a snappy demo.
    keep_adms = df["admission_id"].drop_duplicates().head(250).tolist()
    df = df[df["admission_id"].isin(keep_adms)].copy()

    db = SessionLocal()

    try:
        for _, row in df.drop_duplicates("patient_id").iterrows():
            db.add(
                Patient(
                    patient_id=row.patient_id,
                    age=int(row.age),
                    gender=str(row.gender),
                    ethnicity=str(row.ethnicity),
                )
            )

        db.commit()

        for _, row in df.drop_duplicates("admission_id").iterrows():
            db.add(
                Admission(
                    admission_id=row.admission_id,
                    patient_id=row.patient_id,
                    admit_date=date.today() - timedelta(days=int(row.patient_day)),
                    unit=str(row.unit),
                    admission_type=str(row.admission_type),
                )
            )

        db.commit()

        for _, row in df.iterrows():
            features = {
                "age": int(row.get("age", 65)),
                "gender": str(row.get("gender", "F")),
                "ethnicity": str(row.get("ethnicity", "UNKNOWN")),
                "admission_type": str(row.get("admission_type", "EMERGENCY")),
                "unit": str(row.get("unit", "MED")),

                "patient_day": int(row.get("patient_day", 1)),
                "los_days": int(row.get("los_days", 1)),

                "bmi": float(row.get("bmi", 25.0)),
                "weight_kg": float(row.get("weight_kg", 75.0)),
                "weight_change_pct": float(row.get("weight_change_pct", 0.0)),

                "albumin_min": float(row.get("albumin_min", 3.8)),
                "hemoglobin_min": float(row.get("hemoglobin_min", 12.5)),
                "wbc_max": float(row.get("wbc_max", 8.0)),
                "creatinine_max": float(row.get("creatinine_max", 1.0)),
                "sodium_min": float(row.get("sodium_min", 138.0)),
                "heart_rate_max": float(row.get("heart_rate_max", 85.0)),
                "systolic_bp_min": float(row.get("systolic_bp_min", 120.0)),

                "prior_admissions": int(row.get("prior_admissions", 0)),
                "charlson_score": int(row.get("charlson_score", 2)),
                "icu_flag": int(row.get("icu_flag", 0)),
                "has_diabetes": int(row.get("has_diabetes", 0)),
                "has_chf": int(row.get("has_chf", 0)),
                "has_ckd": int(row.get("has_ckd", 0)),
                "has_cancer": int(row.get("has_cancer", 0)),

                "poor_intake_flag": int(row.get("poor_intake_flag", 0)),
                "nutrition_note_terms": int(row.get("nutrition_note_terms", 0)),
            }

            pred = risk_model_service.predict_one(features)

            evidence = {
                "bmi": float(row.get("bmi", 25.0)),
                "weight_change_pct": float(row.get("weight_change_pct", 0.0)),
                "albumin_min": float(row.get("albumin_min", 3.8)),
                "hemoglobin_min": float(row.get("hemoglobin_min", 12.5)),
                "wbc_max": float(row.get("wbc_max", 8.0)),
                "poor_intake_flag": int(row.get("poor_intake_flag", 0)),
                "nutrition_note_terms": int(row.get("nutrition_note_terms", 0)),
                "los_days": int(row.get("los_days", 1)),
                "demo_label": int(row.get("malnutrition_label", 0)),
            }

            db.add(
                RiskScore(
                    admission_id=row.admission_id,
                    patient_day=int(row.patient_day),
                    risk_score=pred["risk_score"],
                    risk_bucket=pred["risk_bucket"],
                    top_features_json=pred["top_features"],
                    evidence_json=evidence,
                )
            )

        db.commit()

        print(f"Seeded {len(keep_adms)} admissions and {len(df)} patient-day scores.")

    finally:
        db.close()


if __name__ == "__main__":
    main()