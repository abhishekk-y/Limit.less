'use client';

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { Activity, ArrowDownRight, BookOpenCheck, Database, Download, Expand, FileClock, Info, LockKeyhole, Maximize2, Pause, Play, Search, ShieldAlert, ShieldCheck, Waypoints, ZoomIn, ZoomOut } from 'lucide-react';
import type { Core } from 'cytoscape';

type Lane = 'market' | 'weighted' | 'jds' | 'sds';
type NodeState = 'not_verified' | 'needs_review' | 'blocked' | 'not_available';
type EvidenceNode = {
  id: string; label: string; subtitle: string; lane: Lane; state: NodeState;
  kind: string; detail: string; evidence: string; next: string;
};

const laneInfo: Record<Lane, { label: string; color: string; tint: string; description: string }> = {
  market: { label: 'Analytics Jobs', color: '#55d8c3', tint: 'rgba(85,216,195,.08)', description: 'Market skills · posting text' },
  weighted: { label: 'DataScience Jobs', color: '#f0b65f', tint: 'rgba(240,182,95,.08)', description: 'Weighted demand · row totals separate' },
  jds: { label: 'JDS traits', color: '#a78bfa', tint: 'rgba(167,139,250,.08)', description: 'Development hypotheses · descriptive only' },
  sds: { label: 'SDS traits', color: '#ef7ba8', tint: 'rgba(239,123,168,.08)', description: 'Governance research · isolated lane' },
};

const phases = ['Source', 'Profile', 'Prepare', 'Analyze', 'Gate', 'Output'];
const rows: Array<{ lane: Lane; values: Array<[string, string, NodeState, string, string]> }> = [
  { lane: 'market', values: [
    ['Analytics Jobs', 'CSV source · VFL only', 'not_verified', 'Source boundary', 'Source table is not connected to this application. Challenge files and rows remain in VFL.'],
    ['Coverage profile', 'Field missingness', 'not_verified', 'Quality profile', 'The SAS package can calculate per-field coverage after the source table is imported and mapped. No observed values are shown here.'],
    ['Text fields split', 'key_skills / description', 'not_verified', 'Preparation rule', 'The two text fields keep separate denominators. Their contents are never combined for counts.'],
    ['Phrase counts', '33 candidate phrases', 'not_verified', 'Analysis method', 'Transparent phrase matching is implemented as a candidate extractor. It is not a trained NLP model or validated taxonomy.'],
    ['Human audit', 'Precision / recall pending', 'needs_review', 'Validation gate', 'Reviewer labels and an adjudicated sample are required before any skill claim can be called validated.'],
    ['Market passport', 'No approved release', 'not_available', 'Evidence output', 'A passport needs a reproduced VFL run, denominator, method, caveats, reviewer, and organizer transfer approval.'],
  ] },
  { lane: 'weighted', values: [
    ['DataScience Jobs', 'CSV source · VFL only', 'not_verified', 'Source boundary', 'This file stays independent from Analytics Jobs and both trait workbooks.'],
    ['Schema + weights', 'num_of_jobs parsing', 'not_verified', 'Quality profile', 'Missing, negative, or unparseable weights are counted as invalid; the source table is not silently altered.'],
    ['Title normalization', 'Simple text normalization', 'not_verified', 'Preparation rule', 'Normalized titles are not a validated role taxonomy and are not deduplicated into unique vacancies.'],
    ['Row + weighted totals', 'Separate measures', 'not_verified', 'Analysis method', 'Source row count and the sum of num_of_jobs answer different questions and must remain separate.'],
    ['Sensitivity check', 'Leave-one-maximum', 'not_verified', 'Validation gate', 'A weighted total without its distribution and maximum-row sensitivity can be misleading.'],
    ['Demand passport', 'No approved release', 'not_available', 'Evidence output', 'No national demand forecast or salary estimate is available from this unrun source snapshot.'],
  ] },
  { lane: 'jds', values: [
    ['JDS Skill Traits', 'Trait / outcome workbook', 'not_verified', 'Source boundary', 'The file-local outcome and trait fields must be confirmed against VFL metadata and the organizer codebook.'],
    ['Label + ID review', 'Field semantics pending', 'not_verified', 'Quality profile', 'Repeated identifiers are diagnostics only. Their meaning must be verified before any grouping rule.'],
    ['No record linkage', 'JDS stays isolated', 'not_verified', 'Preparation rule', 'No joins to either job dataset or SDS are permitted.'],
    ['Group descriptions', 'Exploratory only', 'not_verified', 'Analysis method', 'The prepared SAS script computes descriptive group summaries only; it does not fit person-level predictions.'],
    ['Interpretation review', 'No causal claim', 'needs_review', 'Validation gate', 'Small observational data cannot establish that a skill causes salary growth or career success.'],
    ['JDS passport', 'No approved release', 'not_available', 'Evidence output', 'Any market-to-JDS concept mapping must be reviewer-approved, aggregate-only, and non-causal.'],
  ] },
  { lane: 'sds', values: [
    ['SDS Personality Traits', 'Governance-only source', 'not_verified', 'Source boundary', 'SDS remains isolated from career recommendations, candidate profiles, hiring, ranking, and promotion decisions.'],
    ['Codebook review', 'Label semantics pending', 'not_verified', 'Quality profile', 'Exact trait and outcome meanings must be confirmed before aggregate descriptions are interpreted.'],
    ['No person-level path', 'No joins / no scoring', 'blocked', 'Policy boundary', 'No data linkage or individual-level inference from SDS is allowed in this system.'],
    ['Separate description', 'Research-only summary', 'not_verified', 'Analysis method', 'If approved, only a separate aggregate governance view may be computed.'],
    ['Policy stop', 'Individual use blocked', 'blocked', 'Enforced boundary', 'Any attempted path from SDS into an individual decision stops here.'],
    ['No action output', 'Not a product signal', 'blocked', 'Evidence output', 'SDS cannot generate a learner action, candidate score, or employment recommendation.'],
  ] },
];

const graphNodes: EvidenceNode[] = rows.flatMap(({ lane, values }) => values.map(([label, subtitle, state, kind, detail], index) => ({
  id: `${lane}-${index}`, label, subtitle, state, lane, kind, detail,
  evidence: 'No VFL run receipt is connected. This screen does not contain challenge-derived counts.',
  next: state === 'blocked' ? 'Keep the policy stop in place.' : state === 'needs_review' ? 'Collect reviewer labels and record the review.' : 'Run the corresponding SAS program in the approved VFL workspace, then record its run receipt.',
})));

function stateLabel(state: NodeState) {
  return state === 'not_verified' ? 'NOT VERIFIED' : state === 'needs_review' ? 'REVIEW' : state === 'blocked' ? 'BLOCKED' : 'NO RELEASE';
}

function stateClass(state: NodeState) {
  return state === 'blocked' ? 'border-rose-300/20 bg-rose-300/[.07] text-rose-200' : state === 'needs_review' ? 'border-amber-300/20 bg-amber-300/[.07] text-amber-200' : state === 'not_available' ? 'border-slate-300/15 bg-white/[.035] text-slate-400' : 'border-cyan-300/15 bg-cyan-300/[.06] text-cyan-100';
}

export function SasControlPlane() {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<Core | null>(null);
  const [selectedId, setSelectedId] = useState('market-0');
  const [search, setSearch] = useState('');
  const [laneFilter, setLaneFilter] = useState<Lane | 'all'>('all');
  const [stateFilter, setStateFilter] = useState<'all' | NodeState>('all');
  const [motion, setMotion] = useState(false);
  const [dock, setDock] = useState<'gates' | 'events' | 'passport'>('gates');
  const selected = graphNodes.find(node => node.id === selectedId) ?? graphNodes[0];
  const selectedPhaseIndex = Number(selected.id.split('-').at(-1) ?? 0);

  const elements = useMemo(() => {
    const nodes = graphNodes.map((node, index) => {
      const laneIndex = rows.findIndex(row => row.lane === node.lane);
      const phaseIndex = index % phases.length;
      return { data: { ...node }, position: { x: 96 + phaseIndex * 211, y: 56 + laneIndex * 112 }, classes: node.state };
    });
    const edges = rows.flatMap(({ lane, values }) => values.slice(0, -1).map((value, index) => ({ data: { id: `${lane}-edge-${index}`, source: `${lane}-${index}`, target: `${lane}-${index + 1}` }, classes: lane === 'sds' && index >= 3 ? 'blocked-edge' : 'proposed-edge' })));
    return [...nodes, ...edges];
  }, []);

  useEffect(() => {
    let destroyed = false;
    let instance: Core | null = null;
    import('cytoscape').then(({ default: cytoscape }) => {
      if (destroyed || !containerRef.current) return;
      instance = cytoscape({
        container: containerRef.current,
        elements,
        minZoom: 0.45,
        maxZoom: 1.65,
        wheelSensitivity: 0.18,
        layout: { name: 'preset', fit: true, padding: 36, animate: motion, animationDuration: 620 },
        style: ([
          { selector: 'node', style: { 'background-color': '#111923', 'border-width': 1, 'border-color': '#334353', 'shape': 'round-rectangle', 'width': 174, 'height': 72, 'label': 'data(label)', 'text-wrap': 'wrap', 'text-max-width': 150, 'text-valign': 'center', 'text-halign': 'center', 'color': '#e5edf5', 'font-size': 10, 'font-weight': 650, 'font-family': 'Inter, ui-sans-serif, system-ui', 'text-margin-y': -8, 'overlay-opacity': 0, 'transition-property': 'border-color, border-width, background-color, opacity', 'transition-duration': 180 } },
          { selector: 'node:active', style: { 'overlay-opacity': 0.08, 'overlay-color': '#75ead4' } },
          { selector: 'node.not_verified', style: { 'border-color': '#3c8590', 'background-color': '#102026' } },
          { selector: 'node.needs_review', style: { 'border-color': '#a67b36', 'background-color': '#241e13' } },
          { selector: 'node.blocked', style: { 'border-color': '#a34869', 'background-color': '#271520', 'line-style': 'dashed' } },
          { selector: 'node.not_available', style: { 'border-color': '#47515d', 'background-color': '#15191f', 'color': '#a3adb9' } },
          { selector: 'node:selected', style: { 'border-width': 2, 'border-color': '#d8ff69', 'background-color': '#202b27', 'shadow-blur': 18, 'shadow-color': '#d8ff69', 'shadow-opacity': 0.22 } },
          { selector: 'edge', style: { 'width': 1.4, 'curve-style': 'bezier', 'target-arrow-shape': 'triangle', 'arrow-scale': 0.8, 'line-color': '#596979', 'target-arrow-color': '#596979', 'opacity': 0.65 } },
          { selector: 'edge.proposed-edge', style: { 'line-style': 'dashed', 'line-dash-pattern': [6, 5], 'line-color': '#627c86', 'target-arrow-color': '#627c86' } },
          { selector: 'edge.blocked-edge', style: { 'line-style': 'dashed', 'line-color': '#bb5777', 'target-arrow-color': '#bb5777', 'opacity': 0.85 } },
          { selector: '.dimmed', style: { 'opacity': 0.12 } },
          { selector: '.highlighted', style: { 'opacity': 1, 'z-index': 10 } },
        ] as never),
      });
      cyRef.current = instance;
      instance.on('tap', 'node', event => {
        instance?.nodes().unselect();
        event.target.select();
        setSelectedId(event.target.id());
      });
      instance.on('dbltap', 'node', event => {
        const node = event.target;
        instance?.elements().addClass('dimmed').removeClass('highlighted');
        node.closedNeighborhood().removeClass('dimmed').addClass('highlighted');
        instance?.animate({ center: { eles: node }, zoom: 1.15 }, { duration: 360 });
      });
    });
    return () => { destroyed = true; instance?.destroy(); cyRef.current = null; };
  }, [elements, motion]);

  useEffect(() => {
    const preference = window.matchMedia('(prefers-reduced-motion: reduce)');
    setMotion(!preference.matches);
    const handleChange = (event: MediaQueryListEvent) => { if (event.matches) setMotion(false); };
    preference.addEventListener('change', handleChange);
    return () => preference.removeEventListener('change', handleChange);
  }, []);

  useEffect(() => {
    const cy = cyRef.current;
    if (!cy) return;
    cy.elements().removeClass('dimmed highlighted');
    cy.nodes().forEach(node => {
      const data = node.data() as EvidenceNode;
      const visible = (laneFilter === 'all' || data.lane === laneFilter) && (stateFilter === 'all' || data.state === stateFilter);
      if (!visible) node.addClass('dimmed');
    });
    const term = search.trim().toLowerCase();
    if (term) {
      const match = cy.nodes().filter(node => {
        const data = node.data() as EvidenceNode;
        const inFilters = (laneFilter === 'all' || data.lane === laneFilter) && (stateFilter === 'all' || data.state === stateFilter);
        return inFilters && `${data.label} ${data.subtitle} ${data.kind}`.toLowerCase().includes(term);
      });
      cy.nodes().not(match).addClass('dimmed');
      match.removeClass('dimmed').addClass('highlighted');
      if (match.length === 1) cy.animate({ center: { eles: match }, zoom: Math.max(cy.zoom(), 1) }, { duration: 300 });
    }
  }, [laneFilter, stateFilter, search]);

  const focusSelected = useCallback(() => {
    const cy = cyRef.current;
    const node = cy?.getElementById(selectedId);
    if (!cy || !node?.length) return;
    cy.elements().addClass('dimmed').removeClass('highlighted');
    node.closedNeighborhood().removeClass('dimmed').addClass('highlighted');
    cy.animate({ center: { eles: node }, zoom: 1.12 }, { duration: 320 });
  }, [selectedId]);

  const exportSnapshot = useCallback(() => {
    const cy = cyRef.current;
    if (!cy) return;
    const uri = cy.png({ full: true, scale: 1.4, bg: '#080b11' });
    const anchor = document.createElement('a');
    anchor.href = uri;
    anchor.download = 'limitless-sas-evidence-map.png';
    anchor.click();
  }, []);

  const resetFilters = () => { setLaneFilter('all'); setStateFilter('all'); setSearch(''); cyRef.current?.elements().removeClass('dimmed highlighted'); };

  return <div className="space-y-5">
    <div className="relative overflow-hidden rounded-[24px] border border-white/[.09] bg-[#0c121a] p-5 sm:p-6">
      <div aria-hidden="true" className="pointer-events-none absolute inset-0 opacity-40" style={{ backgroundImage: 'linear-gradient(rgba(95,141,145,.12) 1px,transparent 1px),linear-gradient(90deg,rgba(95,141,145,.12) 1px,transparent 1px)', backgroundSize: '28px 28px', maskImage: 'linear-gradient(90deg,transparent,#000 20%,#000 80%,transparent)' }}/>
      <div className="relative flex flex-wrap items-start justify-between gap-5">
        <div><div className="flex items-center gap-2 text-[10px] font-semibold uppercase tracking-[.2em] text-cyan-200"><Waypoints size={14}/> Limit.less / SignalBridge <span className="text-slate-600">/</span> SAS research</div><h1 className="mt-3 text-2xl font-semibold tracking-tight text-white sm:text-3xl">Evidence Control Plane</h1><p className="mt-2 max-w-2xl text-sm leading-6 text-slate-400">A separate research lane for the SAS challenge. Limit.less career data and SAS challenge files are not merged.</p></div>
        <div className="flex flex-wrap gap-2"><span className="inline-flex items-center gap-2 rounded-full border border-amber-300/20 bg-amber-300/[.07] px-3 py-2 text-[10px] text-amber-100"><span className="h-1.5 w-1.5 rounded-full bg-amber-300"/>VFL not connected</span><span className="inline-flex items-center gap-2 rounded-full border border-white/[.08] bg-white/[.025] px-3 py-2 text-[10px] text-slate-300"><LockKeyhole size={12}/>Read-only · no release</span></div>
      </div>
      <div className="relative mt-6 grid gap-2 sm:grid-cols-2 xl:grid-cols-4">
        <SummaryCard icon={Database} label="Independent sources" value="4" detail="4 separate source contracts" tone="text-cyan-200"/>
        <SummaryCard icon={Activity} label="Verified VFL runs" value="0" detail="No run receipt connected" tone="text-amber-200"/>
        <SummaryCard icon={ShieldCheck} label="Passed analysis gates" value="0" detail="No gates have been evaluated" tone="text-slate-200"/>
        <SummaryCard icon={ShieldAlert} label="Data transfer" value="Blocked" detail="Organizer approval not recorded" tone="text-rose-200"/>
      </div>
    </div>

    <section className="rounded-[22px] border border-white/[.08] bg-[#0c1118] p-3 sm:p-4" aria-labelledby="graph-title">
      <div className="flex flex-wrap items-center justify-between gap-3 px-1 pb-3">
        <div><p className="text-[9px] font-semibold uppercase tracking-[.2em] text-slate-500">Lineage · source to permitted action</p><h2 id="graph-title" className="mt-1 text-base font-semibold">Four isolated evidence lanes</h2></div>
        <div className="flex flex-wrap items-center gap-1.5 text-[9px] text-slate-400"><span className="mr-1">Legend</span><LegendDot color="#55d8c3" label="Market"/><LegendDot color="#f0b65f" label="Weighted"/><LegendDot color="#a78bfa" label="JDS"/><LegendDot color="#ef7ba8" label="SDS boundary"/></div>
      </div>
      <div className="mb-3 flex flex-wrap items-center gap-2">
        <label className="flex min-w-[190px] flex-1 items-center gap-2 rounded-lg border border-white/[.09] bg-[#080c12] px-3 py-2 text-slate-400"><Search size={13}/><input value={search} onChange={event => setSearch(event.target.value)} placeholder="Find a dataset, gate, or claim" className="w-full bg-transparent text-[11px] text-slate-100 outline-none placeholder:text-slate-600"/></label>
        <select aria-label="Filter by source lane" value={laneFilter} onChange={event => setLaneFilter(event.target.value as Lane | 'all')} className="rounded-lg border border-white/[.09] bg-[#101720] px-2.5 py-2 text-[10px] text-slate-300"><option value="all">All lanes</option>{Object.entries(laneInfo).map(([id, info]) => <option value={id} key={id}>{info.label}</option>)}</select>
        <select aria-label="Filter by gate state" value={stateFilter} onChange={event => setStateFilter(event.target.value as 'all' | NodeState)} className="rounded-lg border border-white/[.09] bg-[#101720] px-2.5 py-2 text-[10px] text-slate-300"><option value="all">All states</option><option value="not_verified">Not verified</option><option value="needs_review">Review</option><option value="blocked">Blocked</option><option value="not_available">No release</option></select>
        <button onClick={() => cyRef.current?.zoom(cyRef.current.zoom() * 1.18)} title="Zoom in" className="grid h-9 w-9 place-items-center rounded-lg border border-white/[.09] text-slate-300 hover:bg-white/[.05]"><ZoomIn size={14}/></button>
        <button onClick={() => cyRef.current?.zoom(cyRef.current.zoom() / 1.18)} title="Zoom out" className="grid h-9 w-9 place-items-center rounded-lg border border-white/[.09] text-slate-300 hover:bg-white/[.05]"><ZoomOut size={14}/></button>
        <button onClick={() => { cyRef.current?.fit(undefined, 36); resetFilters(); }} title="Fit graph" className="grid h-9 w-9 place-items-center rounded-lg border border-white/[.09] text-slate-300 hover:bg-white/[.05]"><Maximize2 size={13}/></button>
        <button onClick={() => { const shell = containerRef.current?.parentElement?.parentElement; if (shell?.requestFullscreen) void shell.requestFullscreen(); }} title="Open graph fullscreen" className="grid h-9 w-9 place-items-center rounded-lg border border-white/[.09] text-slate-300 hover:bg-white/[.05]"><Expand size={13}/></button>
        <button onClick={() => setMotion(value => !value)} title={motion ? 'Pause graph motion' : 'Resume graph motion'} className="inline-flex h-9 items-center gap-1.5 rounded-lg border border-white/[.09] px-2.5 text-[10px] text-slate-300 hover:bg-white/[.05]">{motion ? <Pause size={12}/> : <Play size={12}/>} {motion ? 'Pause' : 'Play'}</button>
        <button onClick={exportSnapshot} title="Export graph snapshot" className="grid h-9 w-9 place-items-center rounded-lg border border-white/[.09] text-slate-300 hover:bg-white/[.05]"><Download size={13}/></button>
      </div>
      <div className="overflow-x-auto rounded-xl border border-white/[.06] bg-[#080c11]">
        <div className="relative min-w-[1320px]">
          <div className="pointer-events-none absolute inset-0 z-0" aria-hidden="true">{rows.map(({ lane }, index) => <div key={lane} className="absolute left-0 right-0 border-b border-white/[.06]" style={{ top: `${index * 112}px`, height: '112px', background: laneInfo[lane].tint }}/>)}</div>
          <div className="relative z-10 grid grid-cols-6 px-[72px] pt-3 text-[8px] font-semibold uppercase tracking-[.16em] text-slate-600">{phases.map(phase => <span key={phase}>{phase}</span>)}</div>
          <div className="relative h-[466px]">
            {rows.map(({ lane }, index) => <div key={lane} className="pointer-events-none absolute left-3 top-0 z-10 flex h-[112px] w-[68px] flex-col justify-center border-r border-white/[.07] pr-2"><span className="text-[8px] font-bold uppercase leading-3" style={{ color: laneInfo[lane].color }}>{laneInfo[lane].label}</span><span className="mt-1 text-[7px] leading-3 text-slate-600">{index === 3 ? 'policy only' : 'isolated source'}</span></div>)}
            <div ref={containerRef} className="absolute inset-0 left-[78px] h-full" aria-label="Interactive SAS evidence graph. Nodes are unverified until a VFL run is connected." role="application"/>
          </div>
        </div>
      </div>
      <div className="flex flex-wrap items-center justify-between gap-2 px-1 pt-3 text-[9px] text-slate-500"><span className="inline-flex items-center gap-1.5"><Info size={11}/> Dashed links are proposed dependencies, not run telemetry.</span><span>Drag to pan · scroll to zoom · click to inspect · double-click to focus</span></div>
    </section>

    <section className="grid gap-3 md:grid-cols-[1fr_auto_1fr]" aria-label="Limit.less and SAS evidence source boundary">
      <div className="rounded-xl border border-cyan-300/10 bg-cyan-300/[.025] p-4"><p className="flex items-center gap-2 text-[9px] font-bold uppercase tracking-[.16em] text-cyan-100"><Database size={13}/> Limit.less · current job discovery</p><p className="mt-2 text-[10px] leading-5 text-slate-400">Existing job search connectors include public Greenhouse and Lever boards plus the Adzuna India search route. Their live availability is not polled by this SAS view.</p></div>
      <div className="hidden items-center text-slate-600 md:flex"><ArrowDownRight size={17} className="rotate-[-45deg]"/></div>
      <div className="rounded-xl border border-violet-300/10 bg-violet-300/[.025] p-4"><p className="flex items-center gap-2 text-[9px] font-bold uppercase tracking-[.16em] text-violet-100"><BookOpenCheck size={13}/> SAS · research and evidence</p><p className="mt-2 text-[10px] leading-5 text-slate-400">VFL analysis can add broader, clearly scoped evidence. Shared skill definitions or aggregates require review and organizer approval before product use.</p></div>
    </section>

    <div className="grid gap-4 xl:grid-cols-[minmax(0,1.25fr)_minmax(300px,.75fr)]">
      <section className="overflow-hidden rounded-[22px] border border-white/[.08] bg-[#0c1118]">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-white/[.07] px-4 py-3"><div className="flex items-center gap-2"><div className="grid h-8 w-8 place-items-center rounded-lg bg-cyan-300/[.08] text-cyan-200"><Activity size={15}/></div><div><h2 className="text-[12px] font-semibold">Evidence operations dock</h2><p className="text-[9px] text-slate-500">No live events · no VFL connection</p></div></div><span className="rounded-md border border-slate-500/20 bg-white/[.025] px-2 py-1 text-[8px] uppercase tracking-wider text-slate-500">Waiting for first run</span></div>
        <div className="flex gap-1 border-b border-white/[.06] px-3 pt-2">{(['gates','events','passport'] as const).map(tab => <button key={tab} onClick={() => setDock(tab)} className={`rounded-t-md px-3 py-2 text-[9px] capitalize ${dock === tab ? 'border-b-2 border-lime-300 text-lime-100' : 'text-slate-500 hover:text-slate-300'}`}>{tab === 'gates' ? 'Gate summary' : tab === 'events' ? 'Event stream' : 'Evidence passport'}</button>)}</div>
        <div className="min-h-[180px] p-4">
          {dock === 'gates' && <div className="space-y-2">{[['Source import','NOT RUN'],['Schema + coverage','NOT RUN'],['Preparation','NOT RUN'],['Skill audit','REVIEW REQUIRED'],['Analysis validation','NOT RUN'],['Aggregate release','BLOCKED']].map(([name,status], index) => <div key={name} className="grid grid-cols-[24px_1fr_auto] items-center gap-2 rounded-lg border border-white/[.05] bg-white/[.015] px-3 py-2"><span className={`grid h-5 w-5 place-items-center rounded-full text-[8px] ${status === 'BLOCKED' ? 'bg-rose-300/10 text-rose-200' : status.includes('REVIEW') ? 'bg-amber-300/10 text-amber-200' : 'bg-slate-700/50 text-slate-400'}`}>{index+1}</span><span className="text-[10px] text-slate-300">{name}</span><span className={`rounded-full border px-2 py-1 text-[8px] ${status === 'BLOCKED' ? 'border-rose-300/20 text-rose-200' : status.includes('REVIEW') ? 'border-amber-300/20 text-amber-200' : 'border-white/[.07] text-slate-500'}`}>{status}</span></div>)}</div>}
          {dock === 'events' && <div className="flex min-h-[145px] flex-col items-center justify-center text-center"><FileClock size={20} className="text-slate-600"/><p className="mt-3 text-[11px] font-medium text-slate-300">No event history available</p><p className="mt-1 max-w-md text-[9px] leading-4 text-slate-500">Events will appear here only after a real VFL run receipt or audited platform event is connected. No simulated activity is being shown.</p></div>}
          {dock === 'passport' && <div className="flex min-h-[145px] flex-col items-center justify-center text-center"><BookOpenCheck size={20} className="text-slate-600"/><p className="mt-3 text-[11px] font-medium text-slate-300">No evidence passports yet</p><p className="mt-1 max-w-md text-[9px] leading-4 text-slate-500">A claim needs its source release, observation unit, denominator, method, coverage, review status, limitation, and approved wording before release.</p></div>}
        </div>
      </section>

      <aside className="rounded-[22px] border border-white/[.08] bg-[#0c1118] p-4">
        <div className="flex items-start justify-between gap-3"><div><p className="text-[8px] font-bold uppercase tracking-[.2em] text-slate-500">Node inspector</p><h2 className="mt-1 text-sm font-semibold text-white">{selected.label}</h2></div><span className={`shrink-0 rounded-full border px-2 py-1 text-[8px] font-bold tracking-wider ${stateClass(selected.state)}`}>{stateLabel(selected.state)}</span></div>
        <p className="mt-1 text-[9px] text-slate-500">{selected.kind} · {laneInfo[selected.lane].label}</p>
        <div className="mt-4 space-y-3">
          <InspectorRow label="Lineage" value={`${selected.lane.toUpperCase()} lane · phase ${selectedPhaseIndex + 1}: ${phases[selectedPhaseIndex] ?? 'source'}`} />
          <InspectorRow label="Version / run" value="No VFL run receipt" />
          <InspectorRow label="Evidence" value={selected.evidence}/>
          <InspectorRow label="Interpretation" value={selected.detail}/>
          <InspectorRow label="Next safe step" value={selected.next}/>
        </div>
        <button onClick={focusSelected} className="mt-4 inline-flex w-full items-center justify-center gap-2 rounded-lg border border-white/[.09] bg-white/[.025] px-3 py-2.5 text-[10px] font-medium text-slate-300 hover:bg-white/[.05]"><ArrowDownRight size={13}/>Focus dependency path</button>
        {selected.lane === 'sds' && <div className="mt-3 flex items-start gap-2 rounded-lg border border-rose-300/15 bg-rose-300/[.04] p-3 text-[9px] leading-4 text-rose-100"><ShieldAlert size={13} className="mt-0.5 shrink-0"/>SDS is governance research only. It has no path to a person-level career or employment decision.</div>}
      </aside>
    </div>

    <footer className="flex flex-wrap items-center justify-between gap-2 px-1 pb-2 text-[9px] text-slate-600"><span>Local architecture view · no SAS challenge results or row-level data in this app</span><span>{graphNodes.length} configured nodes · {rows.reduce((sum, row) => sum + row.values.length - 1, 0)} proposed links · transfer blocked until written approval</span></footer>
  </div>;
}

function SummaryCard({ icon: Icon, label, value, detail, tone }: { icon: typeof Database; label: string; value: string; detail: string; tone: string }) {
  return <div className="rounded-xl border border-white/[.075] bg-[#080c12]/80 p-3"><div className="flex items-center justify-between text-[9px] uppercase tracking-[.14em] text-slate-500"><span>{label}</span><Icon size={13}/></div><div className={`mt-2 text-xl font-semibold tracking-tight ${tone}`}>{value}</div><p className="mt-1 text-[9px] text-slate-600">{detail}</p></div>;
}

function LegendDot({ color, label }: { color: string; label: string }) { return <span className="inline-flex items-center gap-1.5 rounded-full border border-white/[.06] px-2 py-1"><i className="h-1.5 w-1.5 rounded-full" style={{ backgroundColor: color }}/>{label}</span>; }

function InspectorRow({ label, value }: { label: string; value: string }) { return <div className="border-t border-white/[.06] pt-2.5"><p className="text-[8px] font-semibold uppercase tracking-[.15em] text-slate-600">{label}</p><p className="mt-1 text-[9px] leading-[1.55] text-slate-300">{value}</p></div>; }
