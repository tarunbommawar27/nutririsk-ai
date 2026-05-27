export type RiskPatient = {
  admission_id: string;
  patient_id: string;
  age: number;
  gender: string;
  unit: string;
  admission_type: string;
  patient_day: number;
  risk_score: number;
  risk_bucket: 'High' | 'Medium' | 'Low';
  top_features: { feature: string; impact: number; value: unknown }[];
  status: string;
  created_at: string;
};

export type Analytics = {
  patients_screened_today: number;
  high_risk_count: number;
  medium_risk_count: number;
  low_risk_count: number;
  reviewed_count: number;
  avg_risk_score: number;
  model_version: string;
};
