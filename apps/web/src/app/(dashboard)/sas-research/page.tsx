'use client';

import { useState } from 'react';
import Image from 'next/image';
import { Activity, ArrowDown, ArrowRight, BarChart3, BookOpen, Braces, CheckCircle2, CircleDashed, Database, FileSearch, FlaskConical, LockKeyhole, ShieldAlert, Sigma, Workflow } from 'lucide-react';

const lanes = [
  {
    id: 'analytics', number: '01', title: 'Analytics Jobs', badge: 'Market-posting sample', color: 'teal',
    note: 'Descriptive skill signals from job-posting records. Every rate keeps its own text-field denominator.',
    steps: ['Imported source · preserved unchanged', 'Schema, missingness & field coverage', 'Normalize title, skills & description', 'Exact-content duplicate sensitivity', 'Candidate phrase counts & co-occurrence', 'Review labels, denominator & limits'],
    outputs: 'Skill mention rates · role counts · Jaccard co-occurrence · raw vs exact-content sensitivity',
  },
  {
    id: 'datascience', number: '02', title: 'DataScience Jobs', badge: 'Weighted posting sample', color: 'blue',
    note: 'The supplied num_of_jobs value is analyzed separately from source-row counts; its meaning is checked against the data description.',
    steps: ['Imported source · independent lane', 'Validate title, weight & reference fields', 'Normalize role titles', 'Profile missing / negative weights', 'Summarize sum, median, quartiles & maximum', 'Compare total with maximum row removed'],
    outputs: 'Record counts · supplied-weight proxy · leave-one-maximum sensitivity · reference duplicates',
  },
  {
    id: 'jds', number: '03', title: 'JDS Skill Traits', badge: 'Exploratory research', color: 'violet',
    note: 'A file-local, aggregate trait analysis. A model experiment is optional and blocked until labels, fields and repeated-person grouping are verified.',
    steps: ['Inspect codebook & schema', 'Confirm outcome and numeric trait fields', 'Profile missingness and label balance', 'Descriptive group comparisons', 'Optional grouped cross-validation', 'Report uncertainty and limitations'],
    outputs: 'Aggregate associations · optional exploratory logistic model · no individual scoring',
  },
  {
    id: 'sds', number: '04', title: 'SDS Personality Traits', badge: 'Governance lane', color: 'rose',
    note: 'Kept separate for governance and research context. It is never used to screen, rank, or recommend an individual.',
    steps: ['Inspect source and permitted use', 'Keep in isolated lane', 'Aggregate-only descriptive checks', 'Document sensitive-trait limits', 'No person-level model', 'No hiring or career decision'],
    outputs: 'Separate research view · explicit no-individual-decision boundary',
  },
];

const colorMap = {
  teal: { edge: 'border-teal-200', tint: 'bg-teal-50', text: 'text-teal-800', dot: 'bg-teal-500' },
  blue: { edge: 'border-sky-200', tint: 'bg-sky-50', text: 'text-sky-800', dot: 'bg-sky-500' },
  violet: { edge: 'border-violet-200', tint: 'bg-violet-50', text: 'text-violet-800', dot: 'bg-violet-500' },
  rose: { edge: 'border-rose-200', tint: 'bg-rose-50', text: 'text-rose-800', dot: 'bg-rose-500' },
} as const;

function Formula({ name, formula, meaning }: { name: string; formula: string; meaning: string }) {
  return <article className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"><p className="text-xs font-semibold uppercase tracking-[.14em] text-violet-700">{name}</p><p className="mt-3 overflow-x-auto rounded-xl bg-slate-950 px-4 py-4 font-mono text-sm text-lime-100" aria-label={`${name} formula`}>{formula}</p><p className="mt-3 text-sm leading-6 text-slate-600">{meaning}</p></article>;
}

export default function SasResearchPage() {
  const [selected, setSelected] = useState('analytics');
  const lane = lanes.find(item => item.id === selected) ?? lanes[0];
  const palette = colorMap[lane.color as keyof typeof colorMap];

  return <div className="mx-auto max-w-7xl space-y-7 pb-10">
    <header className="relative overflow-hidden rounded-[28px] border border-slate-800 bg-[#10151e] p-6 text-white shadow-xl md:p-9">
      <div aria-hidden="true" className="absolute inset-0 opacity-25" style={{ backgroundImage: 'linear-gradient(#344154 1px,transparent 1px),linear-gradient(90deg,#344154 1px,transparent 1px)', backgroundSize: '28px 28px', maskImage: 'linear-gradient(90deg,transparent,black 20%,black 90%,transparent)' }}/>
      <div className="relative flex flex-wrap items-start justify-between gap-5">
        <div className="max-w-3xl"><div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[.2em] text-lime-300"><FlaskConical size={15}/> Limit.less · SAS Hackathon · Team 117</div><h1 className="mt-4 text-3xl font-semibold tracking-tight md:text-4xl">From raw files to defensible evidence.</h1><p className="mt-4 max-w-2xl text-sm leading-6 text-slate-300">A transparent analysis of four supplied datasets: how each file is prepared, what each calculation means, and where the evidence stops. Team Pookie Blinders · Round 2.</p></div>
        <div className="rounded-2xl border border-amber-200/20 bg-amber-300/[.08] px-4 py-3 text-xs text-amber-100"><div className="flex items-center gap-2 font-semibold"><CircleDashed size={14}/> Aggregate snapshot available</div><p className="mt-2 max-w-[240px] leading-5 text-amber-100/75">A local aggregate reproduction appears in the dashboard. VFL execution and model metrics remain unverified until an authorized run receipt exists.</p></div>
      </div>
      <div className="relative mt-8 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        {[
          { icon: Database, value: '4', label: 'Independent source files', sub: 'No cross-file joins' },
          { icon: Activity, value: '0', label: 'Verified VFL runs', sub: 'Run receipt not connected' },
          { icon: BarChart3, value: '0', label: 'Verified model metrics', sub: 'No model run claimed' },
          { icon: LockKeyhole, value: 'VFL only', label: 'Challenge data boundary', sub: 'No raw-data sync to app' },
        ].map(card => <div key={card.label} className="rounded-2xl border border-white/10 bg-white/[.04] p-4"><div className="flex items-center justify-between text-slate-400"><span className="text-[10px] font-semibold uppercase tracking-[.14em]">{card.label}</span><card.icon size={15}/></div><p className="mt-3 text-2xl font-semibold">{card.value}</p><p className="mt-1 text-[10px] text-slate-400">{card.sub}</p></div>)}
      </div>
    </header>

    <section aria-labelledby="flow-title" className="rounded-[26px] border border-slate-200 bg-white p-5 shadow-sm md:p-7">
      <div className="flex flex-wrap items-end justify-between gap-4"><div><p className="text-xs font-semibold uppercase tracking-[.17em] text-violet-700">Dataset processing map</p><h2 id="flow-title" className="mt-2 text-2xl font-semibold tracking-tight">Four files. Four controlled paths.</h2><p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">Choose a lane to inspect its processing stages. These are planned VFL steps and code contracts, not live telemetry.</p></div><span className="inline-flex items-center gap-2 rounded-full bg-slate-100 px-3 py-2 text-xs text-slate-600"><Workflow size={14}/> Read-only process view</span></div>
      <div className="mt-6 grid gap-2 sm:grid-cols-2 xl:grid-cols-4" role="tablist" aria-label="Dataset processing lanes">
        {lanes.map(item => { const c = colorMap[item.color as keyof typeof colorMap]; const active = selected === item.id; return <button key={item.id} role="tab" aria-selected={active} onClick={() => setSelected(item.id)} className={`rounded-xl border p-3 text-left transition ${active ? `${c.edge} ${c.tint} shadow-sm` : 'border-slate-200 bg-white hover:bg-slate-50'}`}><span className={`text-[10px] font-bold ${active ? c.text : 'text-slate-400'}`}>{item.number} / DATASET</span><span className="mt-1 block text-sm font-semibold text-slate-900">{item.title}</span><span className="mt-1 block text-[10px] text-slate-500">{item.badge}</span></button>; })}
      </div>
      <div role="tabpanel" className={`mt-5 rounded-2xl border ${palette.edge} ${palette.tint} p-5`}>
        <div className="flex flex-wrap items-start justify-between gap-3"><div><h3 className="text-lg font-semibold">{lane.title}</h3><p className="mt-1 max-w-3xl text-sm leading-6 text-slate-600">{lane.note}</p></div><span className={`rounded-full bg-white px-3 py-1.5 text-[10px] font-semibold ${palette.text}`}>{lane.badge}</span></div>
        <ol className="mt-5 grid gap-2 md:grid-cols-3 xl:grid-cols-6">
          {lane.steps.map((step, index) => <li key={step} className="relative rounded-xl border border-white bg-white p-3 shadow-sm"><div className="flex items-center gap-2"><span className={`grid h-6 w-6 shrink-0 place-items-center rounded-full text-[10px] font-bold ${palette.tint} ${palette.text}`}>{String(index + 1).padStart(2, '0')}</span>{index < lane.steps.length - 1 && <ArrowRight size={13} className="hidden text-slate-300 xl:block"/>}</div><p className="mt-3 text-xs font-medium leading-5 text-slate-700">{step}</p></li>)}
        </ol>
        <div className="mt-4 flex flex-wrap items-start gap-2 rounded-xl border border-white bg-white/80 p-3"><CheckCircle2 size={15} className={`mt-0.5 ${palette.text}`}/><p className="text-xs leading-5 text-slate-700"><strong>Candidate outputs:</strong> {lane.outputs}. Each remains inside the approved VFL workspace until review and transfer approval.</p></div>
      </div>
      <div className="mt-6 grid gap-4 xl:grid-cols-2">
        <figure className="overflow-hidden rounded-2xl border border-slate-200 bg-[#090d14] p-2"><Image src="/sas-research/dataset-processing-overview.png" alt="Flow diagram showing four independent SAS dataset lanes, processing, review gates and permitted aggregate actions" width={1600} height={900} className="h-auto w-full rounded-xl"/><figcaption className="px-3 py-2 text-xs text-slate-500">End-to-end data boundary and permitted-action diagram.</figcaption></figure>
        <figure className="overflow-hidden rounded-2xl border border-slate-200 bg-[#090d14] p-2"><Image src={`/sas-research/${lane.id === 'analytics' ? 'analytics-jobs-pipeline' : lane.id === 'datascience' ? 'datascience-jobs-pipeline' : 'trait-model-pipeline'}.png`} alt={`${lane.title} processing stages diagram`} width={1600} height={900} className="h-auto w-full rounded-xl"/><figcaption className="px-3 py-2 text-xs text-slate-500">Detailed processing path for {lane.title}.</figcaption></figure>
      </div>
    </section>

    <section aria-labelledby="math-title"><div className="mb-4 flex items-center gap-3"><span className="grid h-10 w-10 place-items-center rounded-xl bg-violet-100 text-violet-700"><Sigma size={20}/></span><div><p className="text-xs font-semibold uppercase tracking-[.17em] text-violet-700">Calculation contract</p><h2 id="math-title" className="mt-1 text-2xl font-semibold tracking-tight">What the numbers mean</h2></div></div><div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      <Formula name="Skill mention rate" formula="rₛ = nₛ / Nₜₑₓₜ" meaning="nₛ is the number of source records with a candidate mention of skill s. Nₜₑₓₜ is the number with usable text in that same field. This is a sample mention rate, not the share of all workers needing the skill."/>
      <Formula name="Skill co-occurrence" formula="J(A,B) = n(A∩B) / n(A∪B)" meaning="The Jaccard ratio compares records mentioning both candidate skills with records mentioning either. It describes co-mention in this sample; it does not imply a skill dependency or a causal relationship."/>
      <Formula name="Weighted demand proxy" formula="W = Σᵢ wᵢ ;  W₋ₘₐₓ = W − max(wᵢ)" meaning="wᵢ is the supplied num_of_jobs value after validity checks. We report source-row counts separately, then test how much the sum changes when the largest supplied weight is removed. It is not automatically a vacancy count."/>
      <Formula name="Exploratory logistic model" formula="logit(pᵢ) = β₀ + Σⱼ βⱼxᵢⱼ" meaning="Only for a permitted, mapped JDS outcome and numeric traits. Evaluation must hold out groups for repeated people and report out-of-fold AUC, Brier score and calibration. No VFL execution or verified metrics are currently recorded."/>
    </div></section>

    <section className="grid gap-4 lg:grid-cols-[1.15fr_.85fr]">
      <article className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm md:p-6"><div className="flex items-center gap-2"><FileSearch size={17} className="text-violet-700"/><h2 className="text-lg font-semibold">SAS VFL Data Collector & Exporter</h2></div><p className="mt-2 text-sm text-slate-600">Export your AI-scraped job listings directly into a SAS-ready dataset format. Includes auto-generated SAS Visual Analytics macro code to run inside your VFL environment.</p><div className="mt-4"><a href="/api/live-jobs/sas-vfl-export" download className="btn-primary inline-flex items-center gap-2"><Database size={16}/> Download SAS VFL Package (.zip)</a></div><div className="mt-4 rounded-xl bg-slate-950 p-4"><p className="text-xs font-semibold text-lime-400 mb-2">Auto-generated VFL Code Snippet:</p><pre className="text-[10px] text-lime-100 overflow-x-auto"><code>{`/* Upload limitless_dataset.csv to SAS VFL */
proc import datafile="/home/uXXXX/limitless_dataset.csv"
     out=work.limitless_jobs
     dbms=csv
     replace;
     getnames=yes;
run;

proc freq data=work.limitless_jobs;
     tables source_type location / out=work.job_freqs;
run;

proc print data=work.job_freqs(obs=10);
run;`}</code></pre></div></article>
      <aside className="rounded-2xl border border-amber-200 bg-amber-50 p-5 md:p-6"><div className="flex items-center gap-2 text-amber-900"><ShieldAlert size={18}/><h2 className="text-lg font-semibold">Current evidence status</h2></div><ul className="mt-4 space-y-3 text-sm leading-6 text-amber-950">{[
        'A local aggregate-only reproduction is integrated into the dashboard.',
        'The VFL Exporter allows you to safely bridge live Limit.less data into SAS VFL.',
        'No dataset-derived counts are shown on this page without explicit extraction.',
        'Keep the challenge files in VFL. Limit.less acts as the pipeline feeder.',
      ].map(item => <li key={item} className="flex gap-2"><ArrowDown size={14} className="mt-1 shrink-0"/>{item}</li>)}</ul><p className="mt-4 border-t border-amber-200 pt-3 text-xs leading-5 text-amber-900">Pitch this as a reproducible, live-data feeder pipeline into SAS VFL, turning static hackathon rules into a dynamic real-world engine.</p></aside>
    </section>

    <footer className="flex flex-wrap items-center justify-between gap-3 rounded-2xl bg-slate-950 px-5 py-4 text-xs text-slate-300"><span className="flex items-center gap-2"><BookOpen size={14}/> Team Pookie Blinders · Team ID 117</span><span className="flex items-center gap-2 text-slate-400"><Braces size={13}/> SAS code, full formulas, runbook & research notes are in the project data-processing folder</span></footer>
  </div>;
}
