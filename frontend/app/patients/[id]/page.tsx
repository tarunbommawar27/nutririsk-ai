import { getJSON } from '../../../lib/api';
import ActionForm from './ActionForm';

type Detail = {
  patient: { patient_id: string; age: number; gender: string; ethnicity?: string };
  admission_id: string;
  admit_date: string;
  unit: string;
  admission_type: string;
  latest_score: any;
  score_timeline: { day: number; risk_score: number; risk_bucket: string }[];
  evidence: Record<string, any>;
  actions: any[];
};

export default async function PatientDetail({ params }: { params: { id: string }}) {
  const d = await getJSON<Detail>(`/api/patients/${params.id}`);
  return (
    <main className="container grid">
      <section className="grid grid-2">
        <div className="card">
          <h1>{d.patient.patient_id}</h1>
          <p className="muted">Admission {d.admission_id} · {d.unit} · Day {d.latest_score.patient_day}</p>
          <span className={`badge ${d.latest_score.risk_bucket}`}>{d.latest_score.risk_bucket} Risk</span>
          <div className="kpi">{Math.round(d.latest_score.risk_score * 100)}%</div>
        </div>
        <div className="card">
          <h2>Patient</h2>
          <p>Age: {d.patient.age}</p>
          <p>Gender: {d.patient.gender}</p>
          <p>Ethnicity: {d.patient.ethnicity || 'Unknown'}</p>
          <p>Admission type: {d.admission_type}</p>
        </div>
      </section>
      <section className="grid grid-2">
        <div className="card">
          <h2>Risk Timeline</h2>
          <div className="grid">
            {d.score_timeline.map(point => (
              <div key={point.day}>
                <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: 6}}>
                  <span>Day {point.day}</span><b>{Math.round(point.risk_score * 100)}%</b>
                </div>
                <div style={{height: 10, background: '#e2e8f0', borderRadius: 999}}>
                  <div style={{width: `${Math.round(point.risk_score * 100)}%`, height: 10, background: '#0f172a', borderRadius: 999}} />
                </div>
              </div>
            ))}
          </div>
        </div>
        <div className="card">
          <h2>Why flagged?</h2>
          {d.latest_score.top_features.map((f: any) => (
            <p key={f.raw_feature}><b>{f.feature}</b>: impact {f.impact}, value {String(f.value)}</p>
          ))}
        </div>
      </section>
      <section className="grid grid-2">
        <div className="card">
          <h2>Evidence Snapshot</h2>
          {Object.entries(d.evidence).map(([k,v]) => <p key={k}><b>{k}</b>: {String(v)}</p>)}
        </div>
        <div className="card">
          <h2>Clinician Action</h2>
          <ActionForm admissionId={d.admission_id} />
          <h3>Past actions</h3>
          {d.actions.length === 0 ? <p className="muted">No actions yet.</p> : d.actions.map(a => <p key={a.action_id}><b>{a.action_type}</b>: {a.note}</p>)}
        </div>
      </section>
    </main>
  );
}
