'use client';
import { FormEvent, useState } from 'react';
import Link from 'next/link';
import api from '@/lib/api';
import { Message, Panel, Tag, errorMessage, useResource, useRefresh } from './shared';

type Run = { id: string; status: string; query: string; location: string; imported: number };
export function ApifyJobSearch() {
  const status = useResource<{ configured: boolean }>('/live-jobs/apify/status');
  const runs = useResource<Run[]>('/live-jobs/apify/runs');
  const refresh = useRefresh();
  const [query, setQuery] = useState(''); const [location, setLocation] = useState('India');
  const [employment, setEmployment] = useState('all');
  const [dataset, setDataset] = useState(''); const [approved, setApproved] = useState(false);
  const [pending, setPending] = useState(false); const [error, setError] = useState(''); const [success, setSuccess] = useState('');
  async function search(e: FormEvent) {
    e.preventDefault(); setPending(true); setError(''); setSuccess('');
    try { await api.post('/live-jobs/apify/search', { query, location, employment, limit: 20, approved: true }); await refresh(); setApproved(false); setSuccess('Apify run started. Refresh its status below to import completed results.'); }
    catch(e) { setError(errorMessage(e)); } finally { setPending(false); }
  }
  async function check(id: string) {
    setPending(true); setError('');
    try { const {data} = await api.post(`/live-jobs/apify/runs/${id}/refresh`); await refresh(); setSuccess(data.status === 'IMPORTED' ? `${data.imported} job rows imported. Use Guided match or Match my profile to rank them.` : `Provider status: ${data.status}`); }
    catch(e) { setError(errorMessage(e)); } finally { setPending(false); }
  }
  async function importDataset(e: FormEvent) {
    e.preventDefault(); setPending(true); setError('');
    try { const { data } = await api.post('/live-jobs/apify/import-dataset', { dataset_id: dataset.trim() }); await refresh(); setSuccess(`${data.imported} job rows imported from your existing Apify dataset.`); }
    catch(e) { setError(errorMessage(e)); } finally { setPending(false); }
  }
  return <Panel className="mb-6"><div className="flex justify-between gap-3"><h2 className="font-semibold">Apify · LinkedIn job discovery</h2><Tag green={status.data?.configured}>{status.data?.configured ? 'Token saved' : 'Setup needed'}</Tag></div>
    <p className="mt-2 text-sm text-slate-500">Search public LinkedIn listings or import a job dataset you already collected. Imported jobs feed your profile matcher, market watch and application queue.</p>
    {!status.data?.configured && <Link href="/settings" className="mt-3 inline-block text-sm text-violet-700 underline">Add your Apify token in Settings</Link>}
    <form onSubmit={search} className="mt-4 space-y-3"><div className="grid gap-3 sm:grid-cols-2"><label className="text-sm">LinkedIn role keywords<input className="journey-input" required minLength={2} maxLength={120} value={query} onChange={e=>setQuery(e.target.value)} placeholder="e.g. Python developer"/></label><label className="text-sm">LinkedIn job location<input className="journey-input" required minLength={2} maxLength={100} value={location} onChange={e=>setLocation(e.target.value)}/></label></div><label className="block text-sm">Employment type<select className="journey-input" value={employment} onChange={e=>setEmployment(e.target.value)}><option value="all">All employment types</option><option value="full_time">Full-time jobs</option><option value="internship">Internships</option></select></label><label className="flex gap-2 text-xs text-slate-600"><input type="checkbox" required checked={approved} onChange={e=>setApproved(e.target.checked)} className="accent-violet-600"/>Start one paid Apify run for up to 20 listings, with a $0.50 provider charge cap.</label><button className="btn-primary" disabled={!approved || !status.data?.configured || pending}>Search with Apify</button></form>
    <details className="mt-4"><summary className="cursor-pointer text-sm text-violet-700">Import an existing Apify dataset</summary><form onSubmit={importDataset} className="mt-3 flex flex-wrap items-end gap-3"><label className="flex-1 text-sm">Apify dataset ID<input required className="journey-input" pattern="[A-Za-z0-9]{5,80}" value={dataset} onChange={e=>setDataset(e.target.value)}/></label><button className="btn-secondary" disabled={!status.data?.configured || pending}>Import dataset</button></form><p className="mt-2 text-xs text-slate-500">Reads up to 250 rows from your dataset; it does not start a new scraping run.</p></details>
    <Message error={error} success={success}/><div className="mt-4 space-y-2">{runs.data?.slice(0,3).map(run=><div key={run.id} className="flex flex-wrap justify-between gap-3 rounded-xl border p-3 text-xs"><span>{run.query} · {run.location} · {run.status}{run.status==='IMPORTED' ? ` · ${run.imported} rows` : ''}</span>{!['IMPORTED','FAILED','ABORTED','TIMED-OUT'].includes(run.status) && <button className="text-violet-700 underline" disabled={pending} onClick={()=>check(run.id)}>Refresh run & import results</button>}</div>)}</div>
  </Panel>;
}

