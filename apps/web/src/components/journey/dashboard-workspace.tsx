'use client';

import { useMemo, useState } from 'react';
import Link from 'next/link';
import { ArrowUpRight, Briefcase, CalendarClock, CheckCircle2, CircleDashed, FileText, FlaskConical, Search, ShieldAlert, Sparkles, TrendingUp, ArrowRight, type LucideIcon } from 'lucide-react';
import api from '@/lib/api';
import { MarketTicker } from './market-ticker';
import { errorMessage, Message, Panel, State, useRefresh, useResource } from './shared';

// ... (keep types and helper functions the same up to NotificationsPanel)
type Job = { id: string; title: string; organization: string; location: string; url: string; source: string; imported_at: string };
type Packet = { id: string; job_id: string; title: string; organization: string; status: string; created_at: string };
type Notice = { id: string; title: string; body: string; created_at: string; is_read: boolean };
type MarketSnapshot = {
  date: string; captured_at: string; active_postings: number; internship_postings: number;
  skill_coverage_percent: number; role_counts: Record<string, number>; location_counts: Record<string, number>;
  organization_counts: Record<string, number>; skill_counts: Record<string, number>;
  sources: string[]; source_checks: { provider: string; board: string; checked_at: string; active_count: number }[];
};
type MarketInsights = {
  current: MarketSnapshot | null; history: { date: string; active_postings: number }[];
  trend: { change_percent: number | null; baseline_observations: number; recent_observations: number; window_days: number; interpretation: string } | null;
  trend_status: string; trend_note: string;
  skill_trends: { skill: string; baseline_avg_postings: number; recent_avg_postings: number; change_percent: number | null; status: string }[] | null;
  skill_trend_note: string; forecast: null; forecast_note: string; lineage: string;
};

type SasEvidence = {
  status: string; vfl_verification: string;
  provenance: { source: string; method: string; boundary: string };
  analytics_jobs: { rows: number; skill_text_denominator: number; missing_job_descriptions: number; top_locations: [string, number][]; skill_mentions: { skill: string; mentions: number; denominator: number; rate: number }[] };
  datascience_jobs: { rows: number; unique_references: number; excess_repeated_reference_rows: number; supplied_weight_sum: number; supplied_weight_median: number; supplied_weight_max: number; top_titles: [string, number][] };
  jds: { rows: number; positive_label_count: number; associations: { field: string; point_biserial_r: number; cohens_d_pooled: number }[] };
  sds: { rows: number; positive_label_count: number; use_restriction: string };
};

function formatStatus(status: string) {
  return status.replaceAll('_', ' ').replace(/\b\w/g, letter => letter.toUpperCase());
}

function statusStyle(status: string) {
  if (['interview', 'offer', 'submitted'].includes(status)) return 'bg-emerald-50 text-emerald-800 border-emerald-200';
  if (status === 'ready_for_review') return 'bg-violet-50 text-violet-800 border-violet-200';
  if (status === 'rejected' || status === 'withdrawn') return 'bg-slate-100 text-slate-600 border-slate-200';
  return 'bg-amber-50 text-amber-800 border-amber-200';
}

function NotificationsPanel() {
  const query = useResource<Notice[]>('/notifications');
  const notices = [...(query.data ?? [])].sort((a, b) => b.created_at.localeCompare(a.created_at)).slice(0, 4);
  return <Panel className="!p-4 bg-gradient-to-b from-white to-slate-50/50"><div className="flex items-center justify-between gap-3"><div><p className="text-[10px] font-bold uppercase tracking-[.14em] text-violet-700">Stay in the loop</p><h2 className="mt-1 text-sm font-semibold">Notifications</h2></div><Link href="/notifications" className="text-[10px] font-semibold text-violet-800 hover:underline">See all</Link></div><State loading={query.isPending} error={query.error}/>{notices.length ? <div className="mt-3 space-y-2">{notices.map(notice=><div key={notice.id} className="flex gap-2.5 rounded-xl border border-slate-100 bg-white p-2.5 shadow-sm transition hover:shadow-md"><span className={`mt-0.5 grid h-7 w-7 shrink-0 place-items-center rounded-lg ${notice.is_read ? 'bg-slate-100 text-slate-500' : 'bg-gradient-to-br from-[#eff3d8] to-[#e4ebb8] text-[#667a37]'}`}><Sparkles size={14}/></span><div className="min-w-0"><p className="text-[11px] font-semibold leading-snug">{notice.title}</p><p className="mt-1 line-clamp-2 text-[10px] leading-relaxed text-slate-500">{notice.body}</p><time className="mt-1 block text-[9px] text-slate-400">{new Date(notice.created_at).toLocaleDateString()}</time></div></div>)}</div> : !query.isPending && <p className="mt-3 rounded-xl bg-slate-50 p-3 text-[11px] leading-relaxed text-slate-500">You’re all caught up. We’ll show application and workspace updates here.</p>}</Panel>;
}

function OpportunityPulse() {
  const query = useResource<MarketInsights>('/market-insights');
  const current = query.data?.current;
  const grouped = Object.entries(current?.role_counts ?? {}).map(([title, count]) => ({ title, count }))
    .sort((a, b) => b.count - a.count || a.title.localeCompare(b.title)).slice(0, 5);
  const maxCount = Math.max(1, ...grouped.map(role => role.count));
  const skills = Object.entries(current?.skill_counts ?? {}).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0])).slice(0, 5);
  const locations = Object.entries(current?.location_counts ?? {}).sort((a, b) => b[1] - a[1]).slice(0, 3);
  const observedPoints = query.data?.history.length ?? 0;
  return <Panel className="!p-4 sm:!p-5 bg-gradient-to-b from-white to-slate-50/50">
    <div className="flex flex-wrap items-start justify-between gap-3">
      <div className="flex items-start gap-3"><span className="grid h-9 w-9 place-items-center rounded-xl bg-gradient-to-br from-[#edf3d8] to-[#dde8b2] text-[#627b2e] shadow-sm"><TrendingUp size={17}/></span><div><p className="text-[10px] font-bold uppercase tracking-[.14em] text-[#667a37]">Opportunity pulse</p><h2 className="mt-1 text-sm font-semibold">Demand in your job feed</h2></div></div>
      <Link href="/live-jobs" className="inline-flex items-center gap-1 text-[10px] font-semibold text-violet-800 hover:underline">Manage job sources <ArrowUpRight size={12}/></Link>
    </div>
    <p className="mt-2 text-[10px] leading-relaxed text-slate-500">Current role and skill signals from the real employer boards you chose to import.</p>
    {query.isPending ? <p role="status" className="mt-5 animate-pulse text-xs text-slate-500">Reading dated job-board snapshots…</p>
      : query.error ? <p role="alert" className="mt-4 text-xs text-rose-700">Your imported job signals are unavailable right now.</p>
      : current && grouped.length ? <>
        <div className="mt-4 grid grid-cols-2 gap-2"><div className="rounded-xl bg-gradient-to-br from-[#f7f8f0] to-[#f0f2e1] p-3 shadow-inner"><p className="text-[9px] font-semibold uppercase tracking-wide text-slate-500">Active listings</p><p className="mt-1 text-2xl font-bold tabular-nums text-[#17151b]">{current.active_postings}</p><p className="mt-1 text-[9px] text-slate-500">{current.internship_postings} tagged as internships</p></div><div className="rounded-xl bg-gradient-to-br from-violet-50/70 to-indigo-50/70 p-3 shadow-inner"><p className="text-[9px] font-semibold uppercase tracking-wide text-slate-500">Skill coverage</p><p className="mt-1 text-2xl font-bold tabular-nums text-[#17151b]">{current.skill_coverage_percent}%</p><p className="mt-1 text-[9px] text-slate-500">postings with a taxonomy match</p></div></div>
        <div className="mt-4 space-y-3">
          {grouped.map((role, index) => <div key={role.title} className="grid grid-cols-[minmax(0,1fr)_64px] items-center gap-x-3 gap-y-1.5">
            <span className="truncate text-[11px] font-medium text-slate-700">{role.title}</span>
            <span className="text-right text-[10px] font-semibold tabular-nums text-slate-600">{role.count} roles</span>
            <div className="col-span-2 h-1.5 overflow-hidden rounded-full bg-slate-100"><div className={`h-full rounded-full transition-[width] duration-700 ${index === 0 ? 'bg-gradient-to-r from-[#9dbd50] to-[#aed458]' : 'bg-gradient-to-r from-violet-400 to-indigo-400'}`} style={{ width: `${Math.max(8, role.count / maxCount * 100)}%` }}/></div>
          </div>)}
        </div>
        {skills.length > 0 && <div className="mt-4 border-t border-slate-100 pt-3"><p className="text-[9px] font-bold uppercase tracking-[.12em] text-slate-500">Skills mentioned in active postings</p><div className="mt-2 flex flex-wrap gap-1.5">{skills.map(([skill, count]) => <span key={skill} className="rounded-md bg-white border border-violet-100 shadow-sm px-2 py-1 text-[9px] font-medium text-violet-800">{skill.replaceAll('_', ' ')} · {count}</span>)}</div></div>}
        {locations.length > 0 && <div className="mt-3"><p className="text-[9px] font-bold uppercase tracking-[.12em] text-slate-500">Posting locations</p><div className="mt-1.5 flex flex-wrap gap-1.5">{locations.map(([location, count]) => <span key={location} className="rounded-md bg-white border border-slate-200 shadow-sm px-2 py-1 text-[9px] text-slate-700">{location} · {count}</span>)}</div></div>}
        <div className="mt-4 rounded-xl border border-slate-100 bg-white p-3 shadow-sm"><div className="flex items-center justify-between gap-2"><p className="text-[9px] font-bold uppercase tracking-[.12em] text-slate-500">Observed movement</p><span className="rounded-md bg-slate-100 px-2 py-1 text-[9px] font-medium text-slate-600">{observedPoints} dated snapshots</span></div>{query.data?.trend ? <><p className="mt-2 text-lg font-bold tabular-nums text-slate-800">{query.data.trend.change_percent === null ? 'Baseline is zero' : `${query.data.trend.change_percent > 0 ? '+' : ''}${query.data.trend.change_percent}%`}</p><p className="text-[9px] leading-relaxed text-slate-500">Average active listings across matched 28-day windows in your selected boards.</p>{query.data.skill_trends?.length ? <div className="mt-2 border-t border-slate-100 pt-2"><p className="text-[9px] font-semibold text-slate-600">Skill movement</p>{query.data.skill_trends.slice(0, 3).map(item => <div key={item.skill} className="mt-1 flex justify-between gap-2 text-[9px]"><span className="truncate text-slate-600">{item.skill.replaceAll('_', ' ')}</span><span className="shrink-0 font-semibold text-slate-700">{item.change_percent === null ? 'Newly observed' : `${item.change_percent > 0 ? '+' : ''}${item.change_percent}%`}</span></div>)}</div> : null}</> : <p className="mt-2 text-[9px] leading-relaxed text-slate-500">{query.data?.trend_note}</p>}</div>
        <p className="mt-3 text-[9px] text-slate-400">As of {new Date(current.captured_at).toLocaleString()} · {current.sources.length} selected source{current.sources.length === 1 ? '' : 's'} · {current.source_checks.map(source => `${source.provider}/${source.board}`).join(', ')}</p>
      </> : <div className="mt-4 rounded-xl bg-slate-50 p-4"><p className="text-xs font-semibold text-slate-700">Connect a public job board to see demand signals</p><p className="mt-1 text-[10px] leading-relaxed text-slate-500">Import postings from supported Greenhouse or Lever employer boards. Limit.less will summarize roles and skill mentions from those listings.</p><Link href="/live-jobs" className="mt-3 inline-flex items-center gap-1 text-[10px] font-semibold text-violet-800">Import real employer postings <ArrowUpRight size={12}/></Link></div>}
    <div className="mt-4 border-t border-slate-100 pt-3"><p className="text-[9px] leading-relaxed text-slate-400">{query.data?.forecast_note ?? 'Based only on the employer boards you import; this is not market-wide labor demand.'} {query.data?.lineage}</p></div>
  </Panel>;
}

function SasEvidencePanel() {
  const query = useResource<SasEvidence>('/sas-evidence/snapshot');
  const snapshot = query.data;
  const skillRate = (rate: number) => `${(rate * 100).toFixed(1)}%`;
  const jdsSignal = snapshot?.jds.associations.slice().sort((a, b) => Math.abs(b.point_biserial_r) - Math.abs(a.point_biserial_r))[0];
  return <Panel className="!p-4 sm:!p-5 bg-gradient-to-b from-white to-slate-50/50">
    <div className="flex items-start justify-between gap-3"><div className="flex gap-3"><span className="grid h-9 w-9 place-items-center rounded-xl bg-gradient-to-br from-cyan-50 to-teal-50 text-cyan-800 shadow-sm"><FlaskConical size={17}/></span><div><p className="text-[10px] font-bold uppercase tracking-[.14em] text-cyan-800">SAS evidence layer</p><h2 className="mt-1 text-sm font-semibold">Hackathon dataset snapshot</h2></div></div><span className="rounded-full bg-amber-50 px-2 py-1 text-[9px] font-semibold text-amber-800 ring-1 ring-amber-200">VFL verification pending</span></div>
    {query.isPending ? <p role="status" className="mt-4 animate-pulse text-xs text-slate-500">Loading aggregate evidence…</p>
      : query.error || !snapshot ? <p role="alert" className="mt-4 text-xs text-rose-700">The SAS evidence snapshot is unavailable.</p>
      : <><p className="mt-2 text-[10px] leading-relaxed text-slate-500">{snapshot.provenance.method}</p>
        <div className="mt-4 grid grid-cols-2 gap-2"><div className="rounded-xl bg-gradient-to-br from-cyan-50/70 to-teal-50/70 p-3 shadow-inner"><p className="text-[9px] font-semibold uppercase tracking-wide text-slate-500">Analytics Jobs</p><p className="mt-1 text-xl font-bold tabular-nums text-slate-800">{snapshot.analytics_jobs.rows.toLocaleString()}</p><p className="mt-1 text-[9px] text-slate-500">source rows</p></div><div className="rounded-xl bg-gradient-to-br from-violet-50/70 to-fuchsia-50/70 p-3 shadow-inner"><p className="text-[9px] font-semibold uppercase tracking-wide text-slate-500">DataScience Jobs</p><p className="mt-1 text-xl font-bold tabular-nums text-slate-800">{snapshot.datascience_jobs.rows.toLocaleString()}</p><p className="mt-1 text-[9px] text-slate-500">source rows</p></div></div>
        <div className="mt-4"><p className="text-[9px] font-bold uppercase tracking-[.12em] text-slate-500">Observed skill mentions · Analytics Jobs</p><div className="mt-2 space-y-2">{snapshot.analytics_jobs.skill_mentions.slice(0, 5).map(signal => <div key={signal.skill} className="grid grid-cols-[minmax(0,1fr)_42px] items-center gap-3"><span className="truncate text-[10px] font-medium text-slate-700">{signal.skill}</span><span className="text-right text-[10px] font-semibold tabular-nums text-slate-700">{skillRate(signal.rate)}</span><div className="col-span-2 h-1.5 overflow-hidden rounded-full bg-slate-100"><div className="h-full rounded-full bg-gradient-to-r from-cyan-400 to-teal-400" style={{ width: `${Math.max(7, signal.rate * 100)}%` }}/></div></div>)}</div></div>
        <div className="mt-4 rounded-xl border border-slate-200 bg-white p-3 shadow-sm"><p className="text-[9px] font-bold uppercase tracking-[.12em] text-slate-500">Research-only lanes</p><p className="mt-1 text-[10px] leading-relaxed text-slate-600">JDS: {snapshot.jds.rows} records{jdsSignal ? ` · strongest unadjusted association: ${jdsSignal.field.replaceAll('_', ' ')} (r = ${jdsSignal.point_biserial_r.toFixed(2)})` : ''}. SDS: {snapshot.sds.rows} records and is isolated from all individual decisions.</p></div>
        <div className="mt-3 flex items-start gap-2 border-t border-slate-100 pt-3 text-[9px] leading-relaxed text-slate-500"><ShieldAlert size={13} className="mt-0.5 shrink-0 text-amber-600"/>{snapshot.provenance.boundary}</div>
        <Link href="/sas-research" className="mt-3 inline-flex items-center gap-1 text-[10px] font-semibold text-violet-800 hover:underline">Inspect methods, denominators & limits <ArrowUpRight size={12}/></Link>
      </>}
  </Panel>;
}

function Metric({ label, value, note, icon: Icon, tint }: { label: string; value: number; note: string; icon: LucideIcon; tint: string }) {
  return <Panel className="!p-4 sm:!p-5 bg-gradient-to-b from-white to-slate-50/50 hover:shadow-md transition-shadow"><div className="flex items-start justify-between gap-3"><div><p className="text-[10px] font-semibold uppercase tracking-[.1em] text-slate-500">{label}</p><p className="mt-2 text-3xl font-bold leading-none tracking-tight text-[#17151b]">{value}</p></div><span className={`grid h-9 w-9 place-items-center rounded-xl shadow-sm ${tint}`}><Icon size={17}/></span></div><p className="mt-3 text-[10px] text-slate-500">{note}</p></Panel>;
}

export function DashboardWorkspace({ name, skills, autoPrepare, automationPending, automationMessage, onAutoPrepare, calendar }: { name: string; skills: number; autoPrepare: boolean; automationPending: boolean; automationMessage: string; onAutoPrepare: (enabled: boolean) => void; calendar: React.ReactNode }) {
  const jobs = useResource<Job[]>('/live-jobs');
  const packets = useResource<Packet[]>('/apply-queue');
  const refresh = useRefresh();
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState('all');
  const [preparing, setPreparing] = useState(false);
  const [prepareMessage, setPrepareMessage] = useState('');
  const [prepareError, setPrepareError] = useState('');
  const [progress, setProgress] = useState('');
  const packetJobIds = useMemo(() => new Set((packets.data ?? []).map(packet => packet.job_id)), [packets.data]);
  const missingJobs = (jobs.data ?? []).filter(job => !packetJobIds.has(job.id));
  const rows = useMemo(() => [...(packets.data ?? [])].filter(packet => {
    const matchesSearch = `${packet.title} ${packet.organization}`.toLowerCase().includes(search.trim().toLowerCase());
    const matchesFilter = filter === 'all' || (filter === 'review' ? packet.status === 'ready_for_review' : filter === 'active' ? ['approved_for_handoff', 'submitted', 'interview'].includes(packet.status) : ['offer', 'rejected', 'withdrawn'].includes(packet.status));
    return matchesSearch && matchesFilter;
  }).sort((a, b) => b.created_at.localeCompare(a.created_at)), [packets.data, search, filter]);
  const interviews = (packets.data ?? []).filter(packet => packet.status === 'interview').length;
  const offers = (packets.data ?? []).filter(packet => packet.status === 'offer').length;
  const underReview = (packets.data ?? []).filter(packet => packet.status === 'ready_for_review').length;
  const progressed = (packets.data ?? []).filter(packet => ['approved_for_handoff', 'submitted', 'interview', 'offer'].includes(packet.status)).length;

  async function prepareMissing() {
    const unique = Array.from(new Map(missingJobs.map(job => [job.id, job])).values());
    if (!unique.length) return;
    setPreparing(true); setPrepareMessage(''); setPrepareError('');
    let created = 0;
    try {
      for (let offset = 0; offset < unique.length; offset += 250) {
        const batch = unique.slice(offset, offset + 250);
        setProgress(`Preparing ${Math.min(offset + batch.length, unique.length)} of ${unique.length} saved roles…`);
        const { data } = await api.post('/apply-queue/prepare-all', { job_ids: batch.map(job => job.id) });
        created += data.created ?? 0;
      }
      await refresh();
      setPrepareMessage(`Prepared ${created} new role-specific draft${created === 1 ? '' : 's'}. Existing job packets were skipped; nothing was submitted.`);
    } catch (error) {
      await refresh();
      setPrepareError(errorMessage(error));
    } finally { setPreparing(false); setProgress(''); }
  }

  return <div className="mx-auto max-w-[1440px] pb-8 relative">
    <div className="absolute top-0 left-0 right-0 h-96 bg-gradient-to-b from-violet-100/50 to-transparent -z-10 rounded-3xl" />
    <div className="mb-8 flex flex-wrap items-center justify-between gap-6 pt-4"><div><p className="text-[10px] font-bold uppercase tracking-[.16em] text-violet-700">Your career workspace</p><h1 className="mt-1 text-3xl font-bold tracking-tight text-[#17151b] sm:text-4xl">Welcome back, {name.split(' ')[0]} <span aria-hidden="true" className="text-violet-600">✳</span></h1><p className="mt-2 text-sm text-slate-500">Here’s a clear view of your job search progress.</p></div><div className="flex flex-wrap items-center gap-3"><Link href="/live-jobs" className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-violet-700 to-indigo-800 px-5 py-2.5 text-xs font-semibold text-white shadow-md transition hover:-translate-y-0.5 hover:shadow-lg hover:from-violet-800 hover:to-indigo-900"><Briefcase size={15}/>Add or find jobs</Link></div></div>

    <section aria-label="Job search overview" className="mb-6"><div className="mb-3 flex items-center justify-between gap-3"><h2 className="text-sm font-semibold text-slate-800">Your job hunt progress</h2><span className="text-[10px] font-medium text-slate-400 uppercase tracking-wider">Based on roles saved</span></div><div className="grid grid-cols-2 gap-4 xl:grid-cols-4"><Metric label="Saved roles" value={jobs.data?.length ?? 0} note="Imported employer postings" icon={Briefcase} tint="bg-gradient-to-br from-violet-100 to-fuchsia-100 text-violet-800"/><Metric label="Drafts to review" value={underReview} note="You decide what to send" icon={FileText} tint="bg-gradient-to-br from-[#eef2d7] to-[#e4e9b1] text-[#687c39]"/><Metric label="Interviews" value={interviews} note={`${progressed} applications in progress`} icon={CalendarClock} tint="bg-gradient-to-br from-sky-100 to-cyan-100 text-sky-800"/><Metric label="Offers" value={offers} note={`${skills} skills in your profile`} icon={CheckCircle2} tint="bg-gradient-to-br from-emerald-100 to-teal-100 text-emerald-800"/></div></section>

    <MarketTicker/>
    <div className="grid items-start gap-5 xl:grid-cols-[minmax(0,1.55fr)_minmax(310px,.75fr)]">
      <section className="min-w-0 rounded-2xl border border-slate-200 bg-white p-4 shadow-[0_8px_30px_rgb(0,0,0,0.04)] sm:p-6 transition-all">
        <div className="flex flex-wrap items-start justify-between gap-3"><div><p className="text-[10px] font-bold uppercase tracking-[.14em] text-violet-700">Keep every opportunity in view</p><h2 className="mt-1 text-xl font-bold tracking-tight text-slate-900">Applications & saved roles</h2><p className="mt-1 text-xs text-slate-500">One tailored draft per saved role. Existing packets are never duplicated.</p></div><button type="button" onClick={prepareMissing} disabled={preparing || jobs.isPending || packets.isPending || missingJobs.length === 0} className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-[#d8ff69] to-[#c6f047] px-4 py-2.5 text-[11px] font-bold text-[#17151b] shadow-sm transition hover:-translate-y-0.5 hover:shadow-md disabled:cursor-not-allowed disabled:opacity-50"><Sparkles size={14}/>{preparing ? 'Preparing…' : `Prepare missing drafts · ${missingJobs.length}`}</button></div>
        <div className="mt-6 flex flex-wrap items-center gap-3"><div className="flex min-w-48 flex-1 items-center gap-2 rounded-xl border border-slate-200 bg-slate-50/50 px-3 transition-colors focus-within:border-violet-300 focus-within:bg-white"><Search size={16} className="shrink-0 text-slate-400"/><input aria-label="Search applications" value={search} onChange={e=>setSearch(e.target.value)} placeholder="Search company or role" className="h-10 min-w-0 flex-1 border-0 bg-transparent text-sm outline-none placeholder:text-slate-400"/></div><div className="flex gap-1 rounded-xl bg-slate-100/80 p-1" role="group" aria-label="Filter applications">{[['all','All'],['review','Needs review'],['active','In progress'],['closed','Closed']].map(([id,label])=><button key={id} type="button" onClick={()=>setFilter(id)} aria-pressed={filter===id} className={`rounded-lg px-3 py-2 text-xs font-medium transition-all ${filter===id?'bg-white text-violet-900 shadow-sm ring-1 ring-slate-200/50':'text-slate-500 hover:text-slate-800'}`}>{label}</button>)}</div></div>
        <div className="mt-4"><State loading={jobs.isPending || packets.isPending} error={jobs.error || packets.error} retry={()=>{void jobs.refetch();void packets.refetch();}}/></div>
        {progress && <p role="status" className="mt-3 text-xs font-medium text-violet-700">{progress}</p>}
        <div className="mt-1"><Message error={prepareError} success={prepareMessage}/></div>
        <div className="mt-4 overflow-x-auto rounded-xl border border-slate-200 shadow-sm"><table className="w-full min-w-[650px] border-collapse text-left"><thead className="bg-slate-50/80 text-[10px] font-semibold uppercase tracking-[.08em] text-slate-500"><tr><th className="px-4 py-3">Company & role</th><th className="px-4 py-3">Status</th><th className="px-4 py-3">Added</th><th className="px-4 py-3">Next step</th></tr></thead><tbody className="divide-y divide-slate-100">{rows.map(packet=><tr key={packet.id} className="transition-colors hover:bg-slate-50/50"><td className="px-4 py-3.5"><p className="max-w-[260px] truncate text-sm font-semibold text-slate-800">{packet.organization}</p><p className="mt-0.5 max-w-[260px] truncate text-xs text-slate-500">{packet.title}</p></td><td className="px-4 py-3.5"><span className={`inline-flex rounded-md border px-2.5 py-1 text-[10px] font-bold tracking-wide ${statusStyle(packet.status)}`}>{formatStatus(packet.status)}</span></td><td className="whitespace-nowrap px-4 py-3.5 text-xs text-slate-500">{new Date(packet.created_at).toLocaleDateString()}</td><td className="px-4 py-3.5">{packet.status==='ready_for_review'?<Link href="/apply-queue" className="inline-flex items-center gap-1 text-xs font-semibold text-violet-700 hover:text-violet-900">Review draft <ArrowRight size={12}/></Link>:<Link href="/application-tracker" className="inline-flex items-center gap-1 text-xs text-slate-500 hover:text-violet-700">Track progress <ArrowUpRight size={12}/></Link>}</td></tr>)}</tbody></table>{!rows.length && <div className="px-4 py-10 text-center">{packets.data?.length ? <><p className="text-sm font-semibold text-slate-700">No roles match this view.</p><p className="mt-1 text-xs text-slate-500">Try another filter or search term.</p></> : <><span className="mx-auto grid h-12 w-12 place-items-center rounded-2xl bg-violet-50 text-violet-700"><CircleDashed size={20}/></span><p className="mt-3 text-sm font-bold text-slate-800">Your search starts here</p><p className="mt-1 text-xs text-slate-500">Find roles, then prepare reviewable drafts from your saved list.</p><Link href="/live-jobs" className="mt-4 inline-flex items-center gap-1 text-xs font-semibold text-violet-700 hover:text-violet-900">Find your first role <ArrowRight size={14}/></Link></>}</div>}</div>
        <div className="mt-5 flex flex-wrap items-center justify-between gap-3 border-t border-slate-100 pt-5"><p className="text-xs font-medium text-slate-500">{missingJobs.length} saved role{missingJobs.length===1?'':'s'} without a draft <span className="mx-2 text-slate-300">|</span> {packets.data?.length ?? 0} packet{packets.data?.length===1?'':'s'} saved</p><Link href="/application-tracker" className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-600 hover:text-violet-800">Open full tracker <ArrowUpRight size={14}/></Link></div>
        <div className="mt-4 flex flex-wrap items-center justify-between gap-4 rounded-xl bg-gradient-to-r from-slate-50 to-white border border-slate-100 px-4 py-3.5 shadow-sm"><div><p className="text-sm font-semibold text-slate-800">{autoPrepare ? 'Auto-prep matched jobs' : 'Manual review'}</p><p className="mt-1 text-xs text-slate-500 max-w-sm">{autoPrepare ? 'Limit.less prepares matched drafts for your review automatically.' : 'Prepare each role when you choose. You stay in control.'} Applications are never submitted without your review.</p></div><div className="flex items-center gap-3"><span className="text-xs font-semibold text-slate-500">{automationPending?'Saving…':autoPrepare?'Auto-prep':'Manual'}</span><button type="button" role="switch" aria-label="Automatically prepare matched application drafts" aria-checked={autoPrepare} disabled={automationPending} onClick={()=>onAutoPrepare(!autoPrepare)} className={`relative h-7 w-12 rounded-full transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-violet-600 disabled:opacity-60 shadow-inner ${autoPrepare?'bg-violet-600':'bg-slate-300'}`}><span className={`absolute left-0.5 top-0.5 h-6 w-6 rounded-full bg-white shadow-md transition-transform ${autoPrepare?'translate-x-5':''}`}/></button></div></div>
        {automationMessage && <p role="status" className="mt-3 text-xs font-medium leading-relaxed text-violet-700">{automationMessage}</p>}
      </section>
      <aside className="space-y-5"><SasEvidencePanel/><OpportunityPulse/><NotificationsPanel/>{calendar}<Panel className="!p-5 bg-gradient-to-br from-violet-50 to-indigo-50 border-violet-100"><p className="text-[10px] font-bold uppercase tracking-[.14em] text-violet-800">Build your profile</p><p className="mt-1 text-sm font-semibold text-slate-900">Make your experience easier to review.</p><p className="mt-1 text-xs leading-relaxed text-slate-600">{skills} skills in your workspace. Add context and evidence before sharing.</p><Link href="/resume-builder" className="mt-4 inline-flex items-center gap-1.5 text-xs font-bold text-violet-800 hover:text-violet-900">Open résumé studio <ArrowRight size={14}/></Link></Panel></aside>
    </div>
  </div>;
}
