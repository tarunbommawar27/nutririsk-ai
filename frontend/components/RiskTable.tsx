import Link from 'next/link';
import { RiskPatient } from '../types';

export default function RiskTable({ patients }: { patients: RiskPatient[] }) {
  return (
    <div className="card">
      <h2>Patient Risk Queue</h2>
      <p className="muted">Ranked by latest AI malnutrition risk score.</p>
      <table>
        <thead>
          <tr>
            <th>Risk</th><th>Patient</th><th>Age</th><th>Unit</th><th>Score</th><th>Top driver</th><th>Status</th><th></th>
          </tr>
        </thead>
        <tbody>
          {patients.map((p) => (
            <tr key={p.admission_id}>
              <td><span className={`badge ${p.risk_bucket}`}>{p.risk_bucket}</span></td>
              <td>{p.patient_id}</td>
              <td>{p.age}</td>
              <td>{p.unit}</td>
              <td>{Math.round(p.risk_score * 100)}%</td>
              <td>{p.top_features?.[0]?.feature || 'N/A'}</td>
              <td>{p.status}</td>
              <td><Link className="button secondary" href={`/patients/${p.admission_id}`}>Open</Link></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
