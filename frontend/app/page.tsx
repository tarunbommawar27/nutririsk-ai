import { getJSON } from '../lib/api';
import { Analytics, RiskPatient } from '../types';
import RiskTable from '../components/RiskTable';

export default async function Home() {
  const analytics = await getJSON<Analytics>('/api/analytics/summary');
  const patients = await getJSON<RiskPatient[]>('/api/risk-scores/today');
  const highRisk = patients.filter(p => p.risk_bucket === 'High').slice(0, 10);
  return (
    <main className="container grid">
      <section>
        <h1>Daily Malnutrition Risk Screening</h1>
        <p className="muted">Clinical decision support prototype for prioritizing inpatient nutrition review.</p>
      </section>
      <div className="alert">Research demo only. Not for diagnosis, treatment, or clinical use.</div>
      <section className="grid grid-4">
        <div className="card"><div className="muted">Screened today</div><div className="kpi">{analytics.patients_screened_today}</div></div>
        <div className="card"><div className="muted">High risk</div><div className="kpi">{analytics.high_risk_count}</div></div>
        <div className="card"><div className="muted">Reviewed</div><div className="kpi">{analytics.reviewed_count}</div></div>
        <div className="card"><div className="muted">Average score</div><div className="kpi">{Math.round(analytics.avg_risk_score * 100)}%</div></div>
      </section>
      <RiskTable patients={highRisk.length ? highRisk : patients.slice(0, 10)} />
    </main>
  );
}
