'use client';
import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import Link from 'next/link';
import api from '@/lib/api';
import { Message, Panel, errorMessage, useResource } from './shared';

type Market = { active_postings: number; internships: number; employers: number; posting_change: number | null;
  source_refreshed_at: string | null; comparison_date: string | null; scope: string;
  skills: { id: string; name: string; in_profile: boolean; postings: number; share_percent: number; change: number | null }[];
  history: { date: string; postings: number }[] };

function Change({ value }: { value: number | null }) {
  return <span className={`text-xs font-semibold ${value === null || value === 0 ? 'text-slate-400' : value > 0 ? 'text-emerald-600' : 'text-rose-600'}`}>{value === null ? 'Building history' : `${value > 0 ? '+' : ''}${value} postings`}</span>;
}

export function MarketTicker() {
  const preference = useResource<{source: 'live' | 'hackathon' | 'hybrid'}>('/data/preferences');
  const market = useQuery<Market>({ queryKey: ['/market/live'], queryFn: async () => (await api.get('/market/live')).data, refetchInterval: 60000 });
  const [pending, setPending] = useState(false);
  const [error, setError] = useState('');
  const data = market.data;
  async function refresh() {
    setPending(true); setError('');
    try {
      const result = await api.post('/market/refresh');
      if (result.data.sources.some((source: { status: string }) => source.status === 'failed')) setError('Some employer boards could not refresh. Their previous listings remain visible.');
      await market.refetch();
    } catch (e) { setError(errorMessage(e)); } finally { setPending(false); }
  }
  const profile = data?.skills.filter(skill => skill.in_profile) ?? [];
  const values = data?.history.map(point => point.postings) ?? [];
  const low = Math.min(...values); const high = Math.max(...values);
  const sparkline = values.map((value, index) => `${index / Math.max(1, values.length - 1) * 300},${65 - (value - low) / Math.max(1, high - low) * 55}`).join(' ');
  if (preference.data?.source === 'hackathon') return <HackathonMarketView/>;
  return <>{preference.data?.source === 'hybrid' && <HackathonMarketView/>}<Panel className="mb-6 !p-5">
    <div className="flex flex-wrap justify-between gap-3"><div><p className="text-[10px] font-bold uppercase tracking-[.14em] text-violet-700">Market watch</p><h2 className="mt-1 text-lg font-semibold">Your skills in today’s job listings</h2></div><button className="btn-secondary" onClick={refresh} disabled={pending}>{pending ? 'Refreshing sources…' : 'Refresh employer boards'}</button></div>
    <Message error={error}/>
    {market.isPending ? <p className="mt-4 text-sm text-slate-500">Loading market observations…</p> : !data?.active_postings ? <p className="mt-4 text-sm text-slate-500">Import jobs to see current skill mentions and start a history. <Link href="/live-jobs" className="text-violet-700 underline">Find live jobs</Link></p> : <>
      <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-4">{[['Tracked jobs', data.active_postings], ['Internships', data.internships], ['Employers', data.employers], ['Your skills mentioned', profile.filter(skill => skill.postings > 0).length]].map(([label,value]) => <div key={String(label)} className="rounded-xl bg-slate-50 p-3"><p className="text-xs text-slate-500">{label}</p><p className="mt-1 text-2xl font-bold tabular-nums">{value}</p></div>)}</div>
      <div className="mt-4 flex gap-3 overflow-x-auto pb-2" aria-label="Job market skill ticker">{data.skills.slice(0, 10).map(skill => <div className="min-w-40 rounded-xl border p-3" key={skill.id}><div className="flex items-center gap-2"><strong className="text-sm">{skill.name}</strong>{skill.in_profile && <span className="text-[9px] text-violet-600">IN YOUR RESUME</span>}</div><p className="my-1 text-xl font-bold tabular-nums">{skill.share_percent}% <span className="text-[10px] font-normal text-slate-500">of listings</span></p><Change value={skill.change}/></div>)}</div>
      <div className="mt-5 grid gap-5 md:grid-cols-2"><div><h3 className="text-sm font-semibold">Demand for your extracted skills</h3><div className="mt-3 space-y-3">{profile.length ? profile.map(skill => <div key={skill.id}><div className="flex justify-between gap-2 text-xs"><span>{skill.name}</span><span className="tabular-nums">{skill.postings}/{data.active_postings} · {skill.share_percent}%</span></div><div className="mt-1 h-2 rounded-full bg-slate-100"><div className="h-full rounded-full bg-violet-500" style={{width:`${skill.share_percent}%`}}/></div></div>) : <p className="text-xs text-slate-500">Upload a résumé to compare your extracted skills with these listings.</p>}</div></div><div><h3 className="text-sm font-semibold">Tracked market over time</h3>{values.length > 1 ? <svg viewBox="0 0 300 75" className="mt-4 h-24 w-full" role="img" aria-label="Active job counts across saved daily snapshots"><polyline points={sparkline} fill="none" stroke="#7c3aed" strokeWidth="2.5"/></svg> : <p className="mt-3 text-xs text-slate-500">Daily snapshots will build this chart as sources are refreshed.</p>}<div className="mt-3"><Change value={data.posting_change}/>{data.comparison_date && <span className="ml-2 text-xs text-slate-500">since {data.comparison_date}</span>}</div></div></div>
      <p className="mt-4 border-t pt-3 text-[11px] text-slate-500">{data.scope} This view checks saved data every minute. Sources last refreshed {data.source_refreshed_at ? new Date(data.source_refreshed_at).toLocaleString() : 'not yet'}.</p>
    </>}
  </Panel></>;
}

function HackathonMarketView() {
  const evidence = useResource<{vfl_verification: string; provenance: {method: string; boundary: string};
    analytics_jobs: {rows: number; missing_job_descriptions: number; skill_mentions: {skill: string; mentions: number; denominator: number; rate: number}[]};
    datascience_jobs: {rows: number; unique_references: number; excess_repeated_reference_rows: number}}>('/sas-evidence/snapshot');
  const data = evidence.data;
  return <Panel className="mb-6 !p-5"><div className="flex flex-wrap justify-between gap-3"><div><p className="text-[10px] font-bold uppercase tracking-[.14em] text-amber-700">Hackathon dataset view · recorded sample</p><h2 className="mt-1 text-lg font-semibold">From source data to skill insights</h2></div><Link href="/settings" className="btn-secondary">Switch to live data</Link></div>
    {evidence.isPending ? <p className="mt-4 text-sm">Loading dataset evidence…</p> : !data ? <p role="alert" className="mt-4 text-sm text-rose-700">The hackathon evidence snapshot is unavailable.</p> : <>
      <p className="mt-3 text-xs text-slate-600">{data.provenance.method}. SAS VFL verification: {data.vfl_verification}.</p>
      <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-4">{[['Analytics rows',data.analytics_jobs.rows],['Data science rows',data.datascience_jobs.rows],['Unique references',data.datascience_jobs.unique_references],['Repeated reference rows',data.datascience_jobs.excess_repeated_reference_rows]].map(([label,value])=><div key={String(label)} className="rounded-xl bg-amber-50 p-3"><p className="text-xs text-slate-500">{label}</p><p className="mt-1 text-2xl font-bold">{value}</p></div>)}</div>
      <ol className="mt-5 grid gap-2 text-xs sm:grid-cols-4">{['1 · Inspect source files','2 · Check missing values and duplicate references','3 · Extract exact skill mentions with denominators','4 · Report descriptive findings and limitations'].map(step=><li key={step} className="rounded-xl border p-3">{step}</li>)}</ol>
      <div className="mt-5 space-y-3">{data.analytics_jobs.skill_mentions.map(skill=><div key={skill.skill}><div className="flex justify-between text-xs"><strong>{skill.skill}</strong><span>{skill.mentions}/{skill.denominator} · {(skill.rate*100).toFixed(1)}%</span></div><div className="mt-1 h-2 rounded-full bg-slate-100"><div className="h-full rounded-full bg-amber-500" style={{width:`${skill.rate*100}%`}}/></div></div>)}</div>
      <p className="mt-4 text-xs text-slate-500">{data.provenance.boundary} This view does not change job applications or live job sources.</p><Link href="/sas-research" className="mt-3 inline-block text-sm text-violet-700 underline">Open research and processing diagrams</Link><Link href="/opportunities" className="ml-4 inline-block text-sm text-violet-700 underline">Try the demo application flow · no employer contact</Link><Link href="/settings" className="ml-4 inline-block text-sm text-violet-700 underline">Open your SAS workspace</Link>
    </>}
  </Panel>;
}

