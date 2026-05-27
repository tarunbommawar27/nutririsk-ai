'use client';
import { useState } from 'react';
import { postJSON } from '../../../lib/api';

export default function ActionForm({ admissionId }: { admissionId: string }) {
  const [action, setAction] = useState('Needs dietitian consult');
  const [note, setNote] = useState('');
  const [saved, setSaved] = useState(false);
  async function submit() {
    await postJSON('/api/actions', { admission_id: admissionId, action_type: action, note });
    setSaved(true);
  }
  return (
    <div className="grid">
      <select value={action} onChange={e => setAction(e.target.value)}>
        <option>Reviewed</option>
        <option>Needs dietitian consult</option>
        <option>Already under nutrition care</option>
        <option>Dismissed / false positive</option>
      </select>
      <textarea placeholder="Add clinical workflow note" value={note} onChange={e => setNote(e.target.value)} />
      <button onClick={submit}>Save Action</button>
      {saved && <p className="muted">Saved. Refresh to see action history.</p>}
    </div>
  );
}
