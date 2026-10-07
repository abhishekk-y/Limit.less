'use client';
import { useEffect, useState } from 'react';
import Link from 'next/link';
import api from '@/lib/api';
import { errorMessage, Message, Panel, Tag, useResource } from './shared';

type Status = { ready: boolean; enabled: boolean; gemini_configured: boolean; browser_installed: boolean; note: string };
type Run = { id: string; status: string; message: string; items: { job_id: string; title: string; organization: string; status: string; note?: string; confirmation?: string }[] };
const terminal = new Set(['completed', 'cancelled', 'failed', 'interrupted']);

export function LocalAutoApply({ jobIds = [] }: { jobIds?: string[] }) {
  const status = useResource<Status>('/automation/local-status');
  const runs = useResource<Run[]>('/automation/runs');
  const [approved, setApproved] = useState(false);
  const [discover, setDiscover] = useState(true);
  const [boards, setBoards] = useState('cloudflare');
  const [limit, setLimit] = useState(1);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState('');
  const active = runs.data?.find(run => !terminal.has(run.status));
  const refetch = runs.refetch;
  useEffect(() => {
    if (!active) return;
    const timer = setInterval(() => { void refetch(); }, 3000);
    return () => clearInterval(timer);
  }, [active, refetch]);
  async function start() {
    setPending(true); setError('');
    try {
      await api.post('/automation/runs', { approved: true, consent: true, discover,
        boards: boards.split(',').map(board => board.trim().toLowerCase()).filter(Boolean),
        job_ids: discover ? [] : jobIds.slice(0, 5), max_jobs: limit });
      setApproved(false); await refetch();
    } catch (e) { setError(errorMessage(e)); } finally { setPending(false); }
  }
  async function cancel(id: string) {
    try { await api.post(`/automation/runs/${id}/cancel`); await refetch(); }
    catch (e) { setError(errorMessage(e)); }
  }
  return <Panel className="mb-6">
    <div className="flex flex-wrap items-center justify-between gap-3"><h2 className="text-lg font-semibold">Auto-Apply with Gemini</h2><Tag green={status.data?.ready}>{status.data?.ready ? 'Local worker ready' : 'Setup needed'}</Tag></div>
    <p className="mt-2 text-sm text-slate-600">Find matching jobs, tailor a résumé for each one, and fill supported employer forms. Each run uses a fresh private browser. Login, CAPTCHA and missing required answers pause the application for your input.</p>
    {!status.data?.ready && <p className="mt-3 text-sm text-amber-800">{!status.data?.enabled ? 'The local worker is disabled. Start the API with LOCAL_AUTO_APPLY_ENABLED=true. ' : ''}{!status.data?.gemini_configured ? 'Connect Gemini in Settings. ' : ''}{!status.data?.browser_installed ? 'Install the local automation dependencies. ' : ''}<Link href="/settings" className="underline">Open Settings</Link></p>}
    <div className="mt-4 grid gap-3 sm:grid-cols-3">
      <label className="text-sm">Job source<select className="journey-input" value={discover ? 'discover' : 'selected'} onChange={e => setDiscover(e.target.value === 'discover')}><option value="discover">Discover and rank employer jobs</option><option value="selected">Selected jobs ({jobIds.length})</option></select></label>
      {discover && <label className="text-sm">Greenhouse employer boards<input className="journey-input" value={boards} onChange={e => setBoards(e.target.value)} placeholder="cloudflare, stripe" maxLength={300}/></label>}
      <label className="text-sm">Maximum applications<select className="journey-input" value={limit} onChange={e => setLimit(Number(e.target.value))}>{[1,2,3,4,5].map(value => <option key={value} value={value}>{value}</option>)}</select></label>
    </div>
    <label className="mt-4 flex gap-3 text-sm text-slate-600"><input type="checkbox" checked={approved} onChange={e => setApproved(e.target.checked)} className="mt-1 accent-violet-600"/><span>I approve this run to share my résumé with Gemini and submit up to {limit} {discover ? 'profile-ranked jobs from these employer boards' : 'selected jobs'}. I have reviewed my profile for accuracy.</span></label>
    <button className="btn-primary mt-4" onClick={start} disabled={!status.data?.ready || !approved || pending || !!active || (!discover && !jobIds.length)}>{pending ? 'Starting…' : 'Start Auto-Apply'}</button>
    <Message error={error}/>
    <div className="mt-5 space-y-3" aria-live="polite">{runs.data?.slice(0, 3).map(run => <div className="rounded-xl border p-4" key={run.id}>
      <div className="flex justify-between gap-3"><strong className="text-sm">{run.status.replaceAll('_', ' ')}</strong>{!terminal.has(run.status) && <button className="text-sm underline" onClick={() => cancel(run.id)}>Cancel run</button>}</div>
      <p className="mt-1 text-xs text-slate-600">{run.message}</p>
      {run.items.map(item => <div key={item.job_id} className="mt-3 border-t pt-3 text-sm"><strong>{item.title}</strong><span className="ml-2 text-xs text-slate-500">{item.organization} · {item.status.replaceAll('_', ' ')}</span>{item.note && <p className="mt-1 text-xs text-slate-600">{item.note}</p>}{item.confirmation && <p className="mt-1 text-xs text-emerald-700">Employer confirmation: {item.confirmation}</p>}</div>)}
      <Link href="/apply-queue" className="mt-3 inline-block text-xs text-violet-700 underline">Review application packets</Link>
    </div>)}</div>
  </Panel>;
}
