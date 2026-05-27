import { getJSON } from '../../lib/api';
import { Analytics } from '../../types';

type Metrics = {
  model_version: string;
  auroc?: number; auprc?: number; accuracy?: number; recall?: number; precision?: number; f1?: number;
  note: string;
};

export default async function AnalyticsPage() {
  const a = await getJSON<Analytics>('/api/analytics/summary');
  const m = await getJSON<Metrics>('/api/model/metrics');
  return (
    <main className="container grid">
      <h1>Analytics & Model Monitoring</h1>
      <div className="grid grid-4">
        <div className="card"><div className="muted">High</div><div className="kpi">{a.high_risk_count}</div></div>
        <div className="card"><div className="muted">Medium</div><div className="kpi">{a.medium_risk_count}</div></div>
        <div className="card"><div className="muted">Low</div><div className="kpi">{a.low_risk_count}</div></div>
        <div className="card"><div className="muted">Model</div><div className="kpi">{a.model_version}</div></div>
      </div>
      <div className="card">
        <h2>Latest Model Metrics</h2>
        <p className="muted">{m.note}</p>
        <table><tbody>
          {Object.entries(m).filter(([k]) => !['note','model_version'].includes(k)).map(([k,v]) => <tr key={k}><td>{k.toUpperCase()}</td><td>{String(v ?? 'N/A')}</td></tr>)}
        </tbody></table>
      </div>
      <div className="alert">Monitoring ideas to add next: missing feature rate, prediction drift, calibration, subgroup performance, and alert review latency.</div>
    </main>
  );
}
