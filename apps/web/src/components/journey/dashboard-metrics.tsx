'use client';
import Link from 'next/link';
import { ArrowUpRight, Briefcase, CheckCircle2, GraduationCap, Radar } from 'lucide-react';
import type { ReactNode } from 'react';
import { Score } from './shared';

type Metrics = { readiness: Score; target: { title: string }; applications: number; application_stages: Record<string, number>; application_queue?: Record<string, number> & { total: number }; completed_missions: number; active_missions: number; skills: number; verified: number };

function MetricCard({ href, label, value, detail, icon: Icon, tone, children }: { href: string; label: string; value: string | number; detail: string; icon: typeof Radar; tone: string; children?: ReactNode }) {
  return <Link href={href} className="dashboard-metric group block rounded-[20px] border border-[#e9e6ed] bg-white p-4 transition duration-200 hover:-translate-y-0.5 hover:border-violet-200 hover:shadow-[0_12px_30px_#34204d0d] sm:p-5"><div className="flex items-start justify-between gap-3"><span className="grid h-10 w-10 place-items-center rounded-[13px]" style={{ background: tone }}><Icon size={19} strokeWidth={1.8}/></span><ArrowUpRight size={17} className="mt-1 text-slate-300 transition group-hover:-translate-y-0.5 group-hover:translate-x-0.5 group-hover:text-violet-700"/></div><p className="mt-4 text-[10px] font-bold uppercase tracking-[.13em] text-slate-500">{label}</p><p className="mt-1 text-[2rem] font-bold leading-none tracking-[-.06em] text-[#17151b]">{value}</p><p className="mt-2 truncate text-xs text-slate-500">{detail}</p>{children}</Link>;
}

export function DashboardMetrics({ data }: { data: Metrics }) {
  const running = data.active_missions;
  const queue = data.application_queue ?? { total: 0 };
  const activeApplications = Math.max(0, queue.total - (queue.rejected ?? 0) - (queue.withdrawn ?? 0));
  const reviewReady = queue.ready_for_review ?? 0;
  const progressed = ['approved_for_handoff','submitted','interview','offer'].reduce((sum, status) => sum + (queue[status] ?? 0), 0);
  return <section aria-label="Career snapshot" className="mb-8"><div className="mb-3 flex items-end justify-between gap-3"><div><p className="text-[10px] font-bold uppercase tracking-[.17em] text-violet-700">Your snapshot</p><h2 className="mt-1 text-lg font-semibold tracking-tight text-[#211e27]">Progress you can build on</h2></div><details className="relative text-right"><summary className="cursor-pointer text-[11px] text-slate-500 hover:text-violet-700">How readiness works</summary><p className="absolute right-0 z-20 mt-2 w-72 rounded-xl border border-slate-200 bg-white p-4 text-left text-xs leading-relaxed text-slate-600 shadow-xl">{data.readiness.lineage.formula} {data.readiness.lineage.limitations}</p></details></div><div className="grid grid-cols-2 gap-3 sm:gap-4 xl:grid-cols-4">
    <MetricCard href="/talent-twin" label="Role readiness" value={`${Math.round(data.readiness.score)}%`} detail={`Evidence for ${data.target.title}`} icon={Radar} tone="#eee7fb"><div className="mt-3 h-1.5 overflow-hidden rounded-full bg-[#eeeaf4]"><div className="h-full rounded-full bg-violet-500" style={{ width: `${Math.max(0, Math.min(100, data.readiness.score))}%` }}/></div></MetricCard>
    <MetricCard href="/skill-passport" label="Skills in your profile" value={data.skills} detail={`${data.verified} independently verified`} icon={CheckCircle2} tone="#e7f1d9"><div className="mt-3 h-1.5 overflow-hidden rounded-full bg-[#edf0e9]"><div className="h-full rounded-full bg-[#8db95e]" style={{ width: `${data.skills ? Math.min(100, data.verified / data.skills * 100) : 0}%` }}/></div></MetricCard>
    <MetricCard href="/missions" label="Learning in motion" value={running} detail={`${data.completed_missions} mission${data.completed_missions === 1 ? '' : 's'} completed`} icon={GraduationCap} tone="#e2f1ef"><div className="mt-3 text-[10px] font-semibold text-emerald-800">{running ? 'Keep your momentum going' : 'Choose a mission to begin'}</div></MetricCard>
    <MetricCard href="/apply-queue" label="Applications in play" value={activeApplications} detail={`${reviewReady} to review · ${progressed} progressed`} icon={Briefcase} tone="#f4e8d9"><div className="mt-3 flex gap-1">{['ready_for_review','approved_for_handoff','submitted','interview','offer'].map((key, index) => <span key={key} className={`h-1.5 flex-1 rounded-full ${((queue[key] ?? 0) > 0) ? ['bg-violet-400','bg-violet-600','bg-[#a3d977]','bg-emerald-400','bg-emerald-600'][index] : 'bg-slate-100'}`}/>)}</div></MetricCard>
  </div></section>;
}
