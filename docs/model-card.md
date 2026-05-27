# Model Card — NutriRisk AI Demo Model

## Intended use

This model predicts a research/demo malnutrition-risk score from synthetic or MIMIC-style EHR patient-day features. It is designed for portfolio demonstration and clinical workflow prototyping only.

## Not intended use

- Diagnosis
- Treatment recommendation
- Real clinical triage
- Automated decision-making
- Use with identifiable patient data in public deployments

## Target definition

The demo target is an admission-level proxy label indicating whether a patient eventually receives a malnutrition-related code. In real MIMIC-IV use, map ICD-9/ICD-10 malnutrition diagnosis codes and predict early from available patient-day features.

## Features

- demographics
- unit/admission type
- BMI
- weight change
- albumin
- hemoglobin
- WBC
- length of stay so far
- poor intake flag
- nutrition note term count
- ICU flag
- comorbidity score
- prior admissions

## Leakage warnings

Do not include final discharge diagnosis, final billing codes, discharge disposition, total length of stay, or nutrition consult outcome as features for early prediction.

## Evaluation

Report AUROC, AUPRC, sensitivity, specificity, precision, recall, F1, calibration, Brier score, and subgroup performance.

## Safety

The model output should be presented as decision support. Clinicians must review evidence and make final decisions.
