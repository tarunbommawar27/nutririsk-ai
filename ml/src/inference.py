import json
from pathlib import Path
import joblib
import pandas as pd

class NutriRiskPredictor:
    def __init__(self, model_path="ml/models/nutririsk_model.joblib"):
        self.model = joblib.load(model_path)

    def predict_csv(self, csv_path: str):
        df = pd.read_csv(csv_path)
        drop_cols = [c for c in ["patient_id", "admission_id", "malnutrition_label"] if c in df.columns]
        X = df.drop(columns=drop_cols)
        scores = self.model.predict_proba(X)[:, 1]
        out = df[[c for c in ["patient_id", "admission_id", "patient_day"] if c in df.columns]].copy()
        out["risk_score"] = scores
        out["risk_bucket"] = pd.cut(scores, bins=[-1, .4, .7, 2], labels=["Low", "Medium", "High"])
        return out
