'use client';

import { useMemo, useState } from 'react';
import { Activity, AlertTriangle, ArrowDownRight, ArrowUpRight, Boxes, Check, ChevronRight, Circle, Clock3, Database, FileClock, Gauge, GitBranch, HardDrive, LockKeyhole, Network, RefreshCw, ShieldCheck, SlidersHorizontal, Workflow, Zap } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { useAuthContext } from '@/providers/auth-provider';
import api from '@/lib/api';
import { SasControlPlane } from '@/components/admin/sas-control-plane';

type Telemetry = {
  generated_at: number;
  api: { status: string; uptime_seconds: number };
  database: { status: string; accounts: number | null; workspaces: number | null; audit_events_24h: number | null };
  redis: { status: string };
  workers: { status: string; count: number | null; active_tasks: number | null };
  queue: { name: string; depth: number | null };
  integrations: { sas_vfl: { status: string; challenge_data_transfer_enabled: boolean }; cost_metering: { status: string } };
};

type Stage = { id: string; title: string; subtitle: string; icon: typeof Database; color: string; state: string; detail: string; checks: string[] };

const stages: Stage[] = [
  { id: 'sources', title: 'Source boundary', subtitle: 'SAS VFL · employer boards', icon: Database, color: '#55e5d1', state: 'Not connected', detail: 'Source registry and access policy. SAS challenge data stays inside VFL; no raw-data route to the hosted app is configured.', checks: ['VFL connection: not configured', 'Public board connectors: separately managed', 'Outbound challenge-data path: blocked by design'] },
  { id: 'ingest', title: 'Intake & manifest', subtitle: 'Schema · version · hashes', icon: FileClock, color: '#a78bfa', state: 'Awaiting source', detail: 'A run should begin with an immutable source manifest, schema check, timestamp, consent/policy context, and source-specific record counts.', checks: ['Run manifest: not available', 'Schema contract: draft', 'Input fingerprint: unavailable'] },
  { id: 'prepare', title: 'Preparation', subtitle: 'Normalize · deduplicate', icon: SlidersHorizontal, color: '#f4bd68', state: 'Design only', detail: 'Separate deterministic cleanup from inference. Preserve missingness and keep deduplication decisions reversible and auditable.', checks: ['Transformation ledger: not connected', 'Duplicate review queue: not connected', 'Row-level audit: VFL only'] },
  { id: 'extract', title: 'Skill intelligence', subtitle: 'Phrase → taxonomy ID', icon: Network, color: '#55a5ff', state: 'Design only', detail: 'Exact aliases first; semantic retrieval may suggest candidates, with abstention and human review. ESCO version and mappings must be pinned.', checks: ['Taxonomy package: not installed', 'Annotation benchmark: not available', 'Quality metrics: not measured'] },
  { id: 'quality', title: 'Quality gates', subtitle: 'Coverage · drift · review', icon: ShieldCheck, color: '#78df89', state: 'No observations', detail: 'Gate publication on schema, missingness, denominator reconciliation, duplicate sensitivity, and approved aggregate-only output checks.', checks: ['Input checks: no live run', 'Extraction audit: no labels', 'Release gate: not executed'] },
  { id: 'analysis', title: 'Analysis & models', subtitle: 'Descriptive · exploratory', icon: Activity, color: '#f078ba', state: 'No run recorded', detail: 'Keep the job files and the small outcome workbooks separate. Report sample-based frequencies and exploratory uncertainty; no individual success scoring.', checks: ['VFL analysis: not executed here', 'Model registry: not connected', 'External validation: unavailable'] },
  { id: 'review', title: 'Human review', subtitle: 'Adjudicate · approve', icon: Check, color: '#ff8f70', state: 'Not configured', detail: 'Review uncertain mappings and release candidates before any approved aggregate is used in a product demonstration.', checks: ['Reviewer queue: not connected', 'Approval record: unavailable', 'Export approval: required'] },
  { id: 'outputs', title: 'Evidence outputs', subtitle: 'Versioned · aggregate only', icon: Boxes, color: '#c5df68', state: 'No release', detail: 'Publish only approved, versioned summaries with source, denominator, method, caveats, and refresh date. Combined mode remains locked pending organizer approval.', checks: ['Release bundle: none', 'Limit.less sync: disabled', 'Synthetic demo: available'] },
];

const edges = [
  [80, 110, 245, 100], [80, 120, 430, 177], [245, 100, 430, 177], [245, 100, 615, 108], [430, 177, 615, 108], [430, 177, 800, 176], [615, 108, 800, 176], [615, 108, 800, 286], [800, 176, 985, 105], [800, 286, 985, 105], [800, 286, 985, 286], [985, 105, 1175, 177], [985, 286, 1175, 177],
];
const nodes = [
  { x: 80, y: 110, w: 164, h: 90, id: 'sources' }, { x: 245, y: 100, w: 164, h: 90, id: 'ingest' }, { x: 430, y: 177, w: 164, h: 90, id: 'prepare' }, { x: 615, y: 108, w: 164, h: 90, id: 'extract' }, { x: 800, y: 176, w: 164, h: 90, id: 'quality' }, { x: 985, y: 105, w: 164, h: 90, id: 'analysis' }, { x: 985, y: 286, w: 164, h: 90, id: 'review' }, { x: 1175, y: 177, w: 164, h: 90, id: 'outputs' },
];

function PipelineMap({ selected, onSelect }: { selected: string; onSelect: (id: string) => void }) {
  const stageMap = useMemo(() => new Map(stages.map(stage => [stage.id, stage])), []);
  return <div className="relative overflow-hidden rounded-2xl border border-white/[.08] bg-[#090d14]">
    <div className="absolute inset-0 opacity-40" style={{ backgroundImage: 'linear-gradient(#233043 1px, transparent 1px), linear-gradient(90deg, #233043 1px, transparent 1px)', backgroundSize: '32px 32px', maskImage: 'linear-gradient(90deg, transparent, black 15%, black 88%, transparent)' }} />
    <div className="relative overflow-x-auto">
      <svg viewBox="0 0 1400 440" className="block min-w-[1040px] w-full" role="img" aria-label="Illustrative data pipeline map. Connections are not live telemetry.">
        <defs>
          <linearGradient id="pipeline-edge" x1="0" x2="1"><stop offset="0" stopColor="#55e5d1" stopOpacity=".58"/><stop offset=".52" stopColor="#a78bfa" stopOpacity=".55"/><stop offset="1" stopColor="#f078ba" stopOpacity=".7"/></linearGradient>
          <filter id="pipeline-glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
        </defs>
        {edges.map(([x1, y1, x2, y2], i) => <g key={i}><path d={`M ${x1} ${y1} C ${(x1 + x2) / 2} ${y1}, ${(x1 + x2) / 2} ${y2}, ${x2} ${y2}`} fill="none" stroke="url(#pipeline-edge)" strokeWidth="1.2" strokeOpacity=".54"/><path className="pipeline-flow-line" d={`M ${x1} ${y1} C ${(x1 + x2) / 2} ${y1}, ${(x1 + x2) / 2} ${y2}, ${x2} ${y2}`} fill="none" stroke="#e7fbff" strokeWidth="1.4" strokeDasharray="2 20" strokeLinecap="round" style={{ animationDelay: `${i * -0.72}s` }}/></g>)}
        {nodes.map(node => {
          const stage = stageMap.get(node.id)!; const Icon = stage.icon; const active = selected === node.id;
          return <g key={node.id} tabIndex={0} role="button" aria-label={`Inspect ${stage.title}`} onClick={() => onSelect(node.id)} onKeyDown={e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onSelect(node.id); } }} className="cursor-pointer">
            <rect x={node.x - 72} y={node.y - 35} width={node.w} height={node.h} rx="12" fill={active ? '#182334' : '#111923'} stroke={active ? stage.color : '#344150'} strokeWidth={active ? 2 : 1} filter={active ? 'url(#pipeline-glow)' : undefined}/>
            <rect x={node.x - 72} y={node.y - 35} width={node.w} height="6" rx="3" fill={stage.color}/>
            <foreignObject x={node.x - 62} y={node.y - 18} width="144" height="70"><div className="text-left text-[10px] leading-4 text-slate-200"><div className="flex items-center gap-1.5 font-semibold"><span style={{ color: stage.color }}><Icon size={12}/></span><span>{stage.title}</span></div><div className="mt-1 text-[8px] text-slate-400">{stage.subtitle}</div><div className="mt-1.5 flex items-center gap-1 text-[8px]" style={{ color: stage.color }}><span className="h-1.5 w-1.5 rounded-full" style={{ background: stage.color }}/>{stage.state}</div></div></foreignObject>
          </g>;
        })}
      </svg>
    </div>
    <div className="flex flex-wrap items-center justify-between gap-3 border-t border-white/[.07] px-4 py-3 text-[10px] text-slate-400"><span className="flex items-center gap-2"><span className="h-2 w-2 rounded-full bg-amber-300"/>Architecture preview · connection telemetry is not wired</span><span>Click a stage to inspect its contract</span></div>
  </div>;
}

function Metric({ icon: Icon, label, value, note, tone = 'text-slate-100' }: { icon: typeof Activity; label: string; value: string; note: string; tone?: string }) {
  return <div className="rounded-2xl border border-white/[.08] bg-[#111722] p-4"><div className="flex items-center justify-between text-slate-400"><span className="text-[10px] font-semibold uppercase tracking-[.16em]">{label}</span><Icon size={15}/></div><div className={`mt-3 text-2xl font-semibold tracking-tight ${tone}`}>{value}</div><p className="mt-1 text-[10px] text-slate-500">{note}</p></div>;
}

export default function AdminConsolePage() {
  const { user } = useAuthContext();
  const [selected, setSelected] = useState('sources');
  const [workspaceMode, setWorkspaceMode] = useState<'sas' | 'platform'>('sas');
  const telemetry = useQuery<Telemetry>({ queryKey: ['superadmin-observability'], queryFn: async () => (await api.get('/admin/observability')).data, enabled: user?.role === 'superadmin', refetchInterval: 10_000, refetchIntervalInBackground: false, retry: 1 });
  const activeStage = stages.find(stage => stage.id === selected) || stages[0];
  const StageIcon = activeStage.icon;

  if (user?.role !== 'superadmin') return <main className="min-h-[70vh] bg-[#080b11] p-6 text-slate-100"><div className="mx-auto mt-16 max-w-lg rounded-2xl border border-white/10 bg-[#111722] p-7 text-center"><LockKeyhole className="mx-auto text-amber-300"/><h1 className="mt-4 text-xl font-semibold">Superadmin access required</h1><p className="mt-2 text-sm text-slate-400">Sign in with a platform superadmin account. Regular Limit.less accounts cannot view operational telemetry.</p></div></main>;

  if (workspaceMode === 'sas') return <main className="min-h-screen bg-[#080b11] px-4 py-5 text-slate-100 sm:px-6 lg:px-8"><div className="mx-auto max-w-[1600px] space-y-4"><div className="flex flex-wrap items-center justify-between gap-3"><div className="inline-flex rounded-xl border border-white/[.09] bg-[#0c1118] p-1" aria-label="Superadmin workspace mode"><button type="button" onClick={() => setWorkspaceMode('sas')} aria-pressed="true" className="rounded-lg bg-cyan-300/[.12] px-3 py-2 text-[10px] font-semibold text-cyan-100">SAS Research</button><button type="button" onClick={() => setWorkspaceMode('platform')} aria-pressed="false" className="rounded-lg px-3 py-2 text-[10px] text-slate-400 hover:bg-white/[.04] hover:text-white">Platform health</button></div><span className="text-[9px] text-slate-600">Superadmin · research workspace</span></div><SasControlPlane/></div></main>;

  return <main className="min-h-screen bg-[#080b11] px-4 py-5 text-slate-100 sm:px-6 lg:px-8">
    <div className="mx-auto max-w-[1600px] space-y-5">
      <header className="flex flex-wrap items-start justify-between gap-4">
        <div><div className="mb-2 flex items-center gap-2 text-[10px] font-semibold uppercase tracking-[.22em] text-violet-300"><span className="h-1.5 w-1.5 rounded-full bg-violet-300"/>Platform operations <ChevronRight size={12}/> Superadmin</div><h1 className="text-2xl font-semibold tracking-tight sm:text-3xl">Pipeline observatory</h1><p className="mt-1 max-w-2xl text-sm text-slate-400">Trace every source, transformation, quality gate and evidence release across the Limit.less data platform.</p></div>
        <div className="flex flex-wrap items-center gap-2"><span className="flex items-center gap-2 rounded-xl border border-emerald-300/20 bg-emerald-300/[.06] px-3 py-2 text-[11px] text-emerald-100"><span className="h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-300"/>Live API check · {telemetry.data?.api.status ?? (telemetry.isPending ? 'checking' : 'unavailable')}</span><button type="button" onClick={() => void telemetry.refetch()} className="flex items-center gap-2 rounded-xl border border-white/10 px-3 py-2 text-[11px] text-slate-300 hover:bg-white/[.05]"><RefreshCw size={13} className={telemetry.isFetching ? 'animate-spin' : ''}/> Refresh</button></div>
      </header>

      <div className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-white/[.07] bg-[#0d121b] p-2"><span className="px-2 text-[9px] text-slate-500">Choose an isolated admin view</span><div className="inline-flex rounded-lg border border-white/[.08] bg-[#080b11] p-1"><button type="button" onClick={() => setWorkspaceMode('sas')} className="rounded-md px-3 py-1.5 text-[10px] text-slate-400 hover:bg-white/[.05] hover:text-white">SAS Research</button><button type="button" aria-pressed="true" className="rounded-md bg-violet-300/[.1] px-3 py-1.5 text-[10px] font-semibold text-violet-100">Platform health</button></div></div>

      <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4" aria-label="Pipeline status summary">
        <Metric icon={Boxes} label="Accounts" value={telemetry.data?.database.accounts?.toLocaleString() ?? '—'} note={`${telemetry.data?.database.workspaces?.toLocaleString() ?? '—'} workspaces · aggregate only`} tone="text-violet-200"/>
        <Metric icon={Activity} label="Worker heartbeats" value={telemetry.data?.workers.count == null ? '—' : String(telemetry.data.workers.count)} note={telemetry.data?.workers.status ?? 'Waiting for API telemetry'} tone="text-cyan-200"/>
        <Metric icon={Workflow} label="Celery queue" value={telemetry.data?.queue.depth == null ? '—' : String(telemetry.data.queue.depth)} note={`${telemetry.data?.redis.status ?? 'Redis status unavailable'} · pending tasks`} tone="text-emerald-200"/>
        <Metric icon={Database} label="Database" value={telemetry.data?.database.status ?? '—'} note={telemetry.data ? `${Math.floor(telemetry.data.api.uptime_seconds / 60)}m API uptime` : 'Waiting for health check'} tone="text-amber-200"/>
      </section>
      {telemetry.isError && <div role="status" className="rounded-xl border border-rose-300/20 bg-rose-300/[.06] px-4 py-3 text-xs text-rose-100"><AlertTriangle size={14} className="mr-2 inline"/>Operational API is unreachable. The diagram below remains an architecture view; no live counts are being shown.</div>}

      <section className="grid gap-5 2xl:grid-cols-[minmax(0,1.7fr)_minmax(310px,.8fr)]">
        <div className="rounded-2xl border border-white/[.08] bg-[#0d121b] p-4 sm:p-5"><div className="mb-4 flex flex-wrap items-start justify-between gap-3"><div><p className="text-[10px] font-semibold uppercase tracking-[.18em] text-slate-500">System map · logical flow</p><h2 className="mt-1 text-base font-semibold">Data pipeline topology</h2></div><span className="inline-flex items-center gap-1.5 rounded-lg border border-white/[.08] px-2.5 py-1.5 text-[10px] text-slate-400"><GitBranch size={12}/> VFL boundary enforced</span></div>
          <PipelineMap selected={selected} onSelect={setSelected}/>
        </div>

        <aside className="rounded-2xl border border-white/[.08] bg-[#0d121b] p-4 sm:p-5"><div className="flex items-start justify-between gap-3"><div><p className="text-[10px] font-semibold uppercase tracking-[.18em] text-slate-500">Stage inspection</p><h2 className="mt-1 text-base font-semibold">{activeStage.title}</h2></div><span className="grid h-9 w-9 place-items-center rounded-xl border border-white/10 bg-white/[.03]" style={{ color: activeStage.color }}><StageIcon size={17}/></span></div><p className="mt-4 text-xs leading-5 text-slate-400">{activeStage.detail}</p><div className="mt-5 space-y-2">{activeStage.checks.map(check => <div key={check} className="flex items-start gap-2 rounded-lg bg-white/[.025] px-3 py-2 text-[10px] leading-4 text-slate-300"><Circle size={10} className="mt-0.5 shrink-0 text-slate-600"/>{check}</div>)}</div><div className="mt-5 rounded-xl border border-violet-300/15 bg-violet-300/[.05] p-3"><p className="text-[9px] font-semibold uppercase tracking-[.17em] text-violet-200">Release contract</p><p className="mt-1 text-[10px] leading-4 text-slate-400">No stage may publish challenge-derived output to Limit.less until the organizer approves the exact aggregate export.</p></div></aside>
      </section>

      <section className="grid gap-5 xl:grid-cols-[1.25fr_.75fr]">
        <div className="rounded-2xl border border-white/[.08] bg-[#0d121b] p-4 sm:p-5"><div className="mb-4 flex items-center justify-between gap-3"><div><p className="text-[10px] font-semibold uppercase tracking-[.18em] text-slate-500">Observability</p><h2 className="mt-1 text-base font-semibold">Run ledger</h2></div><span className="rounded-lg bg-white/[.04] px-2.5 py-1.5 text-[10px] text-slate-500">Awaiting first connected run</span></div><div className="overflow-x-auto"><table className="w-full min-w-[650px] text-left text-[10px]"><thead className="border-y border-white/[.07] text-[9px] uppercase tracking-[.14em] text-slate-500"><tr><th className="py-3 pr-4">Run / source</th><th className="py-3 pr-4">Execution</th><th className="py-3 pr-4">Quality</th><th className="py-3 pr-4">Release</th><th className="py-3">State</th></tr></thead><tbody><tr><td className="py-5 pr-4 text-slate-400" colSpan={5}><div className="flex items-center justify-center gap-2"><FileClock size={14}/> No run records available. Connect an authorized telemetry source to populate this ledger.</div></td></tr></tbody></table></div><div className="mt-4 grid gap-2 sm:grid-cols-3"><div className="rounded-lg bg-white/[.025] p-3"><p className="text-[9px] uppercase tracking-wider text-slate-500">Required run fields</p><p className="mt-1 text-[10px] text-slate-300">run ID · commit · source hash</p></div><div className="rounded-lg bg-white/[.025] p-3"><p className="text-[9px] uppercase tracking-wider text-slate-500">Quality contract</p><p className="mt-1 text-[10px] text-slate-300">schema · nulls · duplicates</p></div><div className="rounded-lg bg-white/[.025] p-3"><p className="text-[9px] uppercase tracking-wider text-slate-500">Release contract</p><p className="mt-1 text-[10px] text-slate-300">approver · aggregate · version</p></div></div></div>

        <div className="rounded-2xl border border-white/[.08] bg-[#0d121b] p-4 sm:p-5"><div className="mb-4"><p className="text-[10px] font-semibold uppercase tracking-[.18em] text-slate-500">Signal desk</p><h2 className="mt-1 text-base font-semibold">What needs instrumentation</h2></div><div className="space-y-2">{[
          { icon: Zap, title: 'Job workers', note: 'Heartbeat, queue depth, retry and dead-letter counts', color: '#f4bd68' },
          { icon: Gauge, title: 'Data quality', note: 'Schema drift, missingness, dedup and annotation metrics', color: '#55e5d1' },
          { icon: HardDrive, title: 'Storage & provenance', note: 'Manifest, hash, retention, access and lineage events', color: '#a78bfa' },
          { icon: LockKeyhole, title: 'Policy boundary', note: 'VFL execution identity and approved aggregate exports', color: '#78df89' },
        ].map(item => <div key={item.title} className="flex items-start gap-3 rounded-xl border border-white/[.06] bg-white/[.02] p-3"><span className="mt-0.5" style={{ color: item.color }}><item.icon size={15}/></span><div><p className="text-[11px] font-medium text-slate-200">{item.title}</p><p className="mt-1 text-[10px] leading-4 text-slate-500">{item.note}</p></div><span className="ml-auto shrink-0 rounded-full bg-slate-800 px-2 py-1 text-[8px] uppercase tracking-wider text-slate-400">Pending</span></div>)}</div><p className="mt-4 border-t border-white/[.07] pt-3 text-[10px] leading-4 text-slate-500">Next engineering step: add signed, append-only run events at the worker boundary; expose a read-only, role-protected summary endpoint. Never send raw challenge rows to this console.</p></div>
      </section>

      <footer className="flex flex-wrap items-center justify-between gap-2 px-1 pb-3 text-[9px] text-slate-600"><span className="flex items-center gap-1.5"><LockKeyhole size={11}/> Challenge datasets and row-level outputs are not rendered in this interface.</span><span>{telemetry.data ? `Last health check ${new Date(telemetry.data.generated_at * 1000).toLocaleTimeString()}` : 'No health response received'} · usage cost not instrumented</span></footer>
    </div>
  </main>;
}
