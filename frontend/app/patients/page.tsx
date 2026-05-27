import { getJSON } from '../../lib/api';
import { RiskPatient } from '../../types';
import RiskTable from '../../components/RiskTable';

export default async function PatientsPage() {
  const patients = await getJSON<RiskPatient[]>('/api/patients');
  return <main className="container"><RiskTable patients={patients} /></main>;
}
