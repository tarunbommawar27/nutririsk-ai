# Data Dictionary

| Column | Meaning |
|---|---|
| patient_id | synthetic/deidentified patient id |
| admission_id | synthetic/deidentified admission id |
| patient_day | day number since admission |
| age | patient age |
| gender | demographic field |
| ethnicity | demographic field for fairness analysis only |
| unit | current hospital unit |
| admission_type | emergency, urgent, elective |
| bmi | body mass index |
| weight_change_pct | percent weight change since admission baseline |
| albumin_min | minimum albumin observed so far |
| hemoglobin_min | minimum hemoglobin observed so far |
| wbc_max | maximum white blood cell count observed so far |
| los_days | length of stay so far, not final LOS |
| poor_intake_flag | simulated evidence of poor intake |
| nutrition_note_terms | count of nutrition-related note terms |
| icu_flag | whether patient is/was in ICU context |
| charlson_score | simulated comorbidity score |
| prior_admissions | prior admission count |
| malnutrition_label | proxy target label |
