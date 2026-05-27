import argparse, json
from pathlib import Path
import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, average_precision_score, accuracy_score, recall_score, precision_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
try:
    from xgboost import XGBClassifier
    HAS_XGB = True
except Exception:
    HAS_XGB = False

DROP_COLS = {"patient_id", "admission_id", "malnutrition_label"}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True)
    parser.add_argument("--out", default="ml/models")
    parser.add_argument("--use-xgboost", action="store_true", help="Use XGBoost if installed; default uses faster RandomForest.")
    args = parser.parse_args()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(args.data)
    y = df["malnutrition_label"].astype(int)
    X = df.drop(columns=[c for c in DROP_COLS if c in df.columns])
    cat_cols = X.select_dtypes(include=["object"]).columns.tolist()
    num_cols = [c for c in X.columns if c not in cat_cols]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.2, random_state=42, stratify=y)
    pre = ColumnTransformer([
        ("num", StandardScaler(), num_cols),
        ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols),
    ])
    if args.use_xgboost and HAS_XGB:
        clf = XGBClassifier(
            n_estimators=120,
            max_depth=4,
            learning_rate=.05,
            subsample=.9,
            colsample_bytree=.9,
            eval_metric="logloss",
            random_state=42,
        )
    else:
        clf = RandomForestClassifier(n_estimators=120, max_depth=8, class_weight="balanced", random_state=42, n_jobs=-1)
    pipe = Pipeline([("preprocess", pre), ("model", clf)])
    pipe.fit(X_train, y_train)
    proba = pipe.predict_proba(X_test)[:, 1]
    pred = (proba >= .5).astype(int)
    metrics = {
        "model_version": "demo-v1",
        "auroc": round(float(roc_auc_score(y_test, proba)), 4),
        "auprc": round(float(average_precision_score(y_test, proba)), 4),
        "accuracy": round(float(accuracy_score(y_test, pred)), 4),
        "recall": round(float(recall_score(y_test, pred, zero_division=0)), 4),
        "precision": round(float(precision_score(y_test, pred, zero_division=0)), 4),
        "f1": round(float(f1_score(y_test, pred, zero_division=0)), 4),
    }
    joblib.dump(pipe, out / "nutririsk_model.joblib")
    (out / "feature_columns.json").write_text(json.dumps(X.columns.tolist(), indent=2))
    (out / "metrics.json").write_text(json.dumps(metrics, indent=2))
    print(json.dumps(metrics, indent=2))

if __name__ == "__main__":
    main()
