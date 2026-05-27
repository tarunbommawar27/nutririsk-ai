from pathlib import Path
import joblib
import pandas as pd

from .config import get_settings


class RiskModelService:
    def __init__(self):
        self.settings = get_settings()
        self.model = None

    def load(self):
        if self.model is not None:
            return

        model_path = Path(self.settings.model_path)

        if not model_path.exists():
            raise FileNotFoundError(
                f"Model not found at {model_path}. Run ml/src/train.py first."
            )

        self.model = joblib.load(model_path)

    def predict_one(self, features: dict) -> dict:
        self.load()

        expected_defaults = {
            "age": 65,
            "gender": "F",
            "ethnicity": "UNKNOWN",
            "admission_type": "EMERGENCY",
            "unit": "MED",

            "patient_day": 1,
            "los_days": 1,

            "bmi": 25.0,
            "weight_kg": 75.0,
            "weight_change_pct": 0.0,

            "albumin_min": 3.8,
            "hemoglobin_min": 12.5,
            "wbc_max": 8.0,
            "creatinine_max": 1.0,
            "sodium_min": 138.0,
            "heart_rate_max": 85.0,
            "systolic_bp_min": 120.0,

            "prior_admissions": 0,
            "charlson_score": 2,
            "icu_flag": 0,
            "has_diabetes": 0,
            "has_chf": 0,
            "has_ckd": 0,
            "has_cancer": 0,

            "poor_intake_flag": 0,
            "nutrition_note_terms": 0,
        }

        clean_features = {}

        for key, default in expected_defaults.items():
            value = features.get(key, default)

            if value is None:
                value = default

            clean_features[key] = value

        x = pd.DataFrame([clean_features])
        score = float(self.model.predict_proba(x)[0, 1])

        if score >= 0.75:
            bucket = "High"
        elif score >= 0.45:
            bucket = "Medium"
        else:
            bucket = "Low"

        top_features = [
            {
                "feature": "albumin_min",
                "impact": round(abs(3.8 - float(clean_features["albumin_min"])) * 0.12, 3),
            },
            {
                "feature": "bmi",
                "impact": round(abs(25.0 - float(clean_features["bmi"])) * 0.03, 3),
            },
            {
                "feature": "los_days",
                "impact": round(float(clean_features["los_days"]) * 0.02, 3),
            },
            {
                "feature": "has_cancer",
                "impact": round(float(clean_features["has_cancer"]) * 0.18, 3),
            },
            {
                "feature": "has_chf",
                "impact": round(float(clean_features["has_chf"]) * 0.12, 3),
            },
        ]

        top_features = sorted(
            top_features,
            key=lambda item: item["impact"],
            reverse=True,
        )[:3]

        return {
            "risk_score": round(score, 4),
            "risk_bucket": bucket,
            "top_features": top_features,
        }


risk_model_service = RiskModelService()