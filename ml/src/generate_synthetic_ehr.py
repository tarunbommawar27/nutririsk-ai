import argparse
from pathlib import Path
import numpy as np
import pandas as pd

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def generate(n_patients: int, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    units = ["Med-Surg", "ICU", "Cardiology", "Oncology", "Stepdown"]
    ad_types = ["Emergency", "Urgent", "Elective"]
    ethnicities = ["White", "Black", "Asian", "Hispanic", "Other", "Unknown"]
    for i in range(n_patients):
        patient_id = f"P{i+100000}"
        admission_id = f"A{i+500000}"
        age = int(np.clip(rng.normal(64, 17), 18, 95))
        gender = rng.choice(["F", "M"])
        ethnicity = rng.choice(ethnicities, p=[.42,.18,.12,.14,.08,.06])
        unit = rng.choice(units, p=[.42,.16,.14,.14,.14])
        admission_type = rng.choice(ad_types, p=[.62,.28,.10])
        icu_flag = 1 if unit == "ICU" else int(rng.random() < .08)
        charlson = int(np.clip(rng.poisson(2.1 + age/70 + icu_flag), 0, 10))
        prior_adm = int(np.clip(rng.poisson(0.7 + charlson/5), 0, 8))
        base_bmi = float(np.clip(rng.normal(27 - charlson*.45 - icu_flag*1.1, 5.5), 14, 45))
        max_days = int(rng.integers(2, 9))
        malnutrition_risk_latent = -3.2 + (65-age)*-0.006 + max(0, 21-base_bmi)*0.23 + charlson*.18 + icu_flag*.55 + prior_adm*.08
        ever_positive = rng.random() < sigmoid(malnutrition_risk_latent)
        for day in range(1, max_days + 1):
            los_days = day
            weight_change_pct = float(rng.normal(-0.35*day if ever_positive else -0.08*day, 1.1))
            bmi = float(np.clip(base_bmi * (1 + weight_change_pct/100), 13, 46))
            albumin_min = float(np.clip(rng.normal(3.7 - ever_positive*.55 - icu_flag*.25 - day*.035, .35), 1.7, 5.0))
            hemoglobin_min = float(np.clip(rng.normal(12.1 - charlson*.18 - icu_flag*.3, 1.6), 6.5, 16.5))
            wbc_max = float(np.clip(rng.normal(8.2 + icu_flag*2.2 + charlson*.25, 3.0), 2.0, 30.0))
            poor_intake = int(rng.random() < sigmoid(-2.2 + ever_positive*1.4 + max(0,21-bmi)*.12 + day*.1))
            nutrition_terms = int(np.clip(rng.poisson((0.4 + ever_positive*1.2 + poor_intake*1.4 + max(0,21-bmi)*.08)), 0, 9))
            # Label is admission-level eventual diagnosis proxy.
            label_prob = sigmoid(-3.0 + max(0, 21-bmi)*.28 + max(0, -weight_change_pct)*.18 + (3.5-albumin_min)*1.1 + poor_intake*.9 + nutrition_terms*.22 + icu_flag*.35 + charlson*.12)
            label = int(ever_positive or (rng.random() < label_prob*.35))
            rows.append({
                "patient_id": patient_id,
                "admission_id": admission_id,
                "patient_day": day,
                "age": age,
                "gender": gender,
                "ethnicity": ethnicity,
                "unit": unit,
                "admission_type": admission_type,
                "bmi": round(bmi, 2),
                "weight_change_pct": round(weight_change_pct, 2),
                "albumin_min": round(albumin_min, 2),
                "hemoglobin_min": round(hemoglobin_min, 2),
                "wbc_max": round(wbc_max, 2),
                "los_days": los_days,
                "poor_intake_flag": poor_intake,
                "nutrition_note_terms": nutrition_terms,
                "icu_flag": icu_flag,
                "charlson_score": charlson,
                "prior_admissions": prior_adm,
                "malnutrition_label": label,
            })
    return pd.DataFrame(rows)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="data/demo")
    parser.add_argument("--n-patients", type=int, default=1200)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    df = generate(args.n_patients, args.seed)
    df.to_csv(out / "patient_day_features.csv", index=False)
    print(f"Wrote {len(df):,} patient-day rows to {out / 'patient_day_features.csv'}")
