'use client';

import React from 'react';
import Link from 'next/link';
import axios from 'axios';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import api from '@/lib/api';

export interface Lineage { source: string; period: string; record_count: number; formula: string; confidence: string; limitations: string }
export interface Score { score: number; lineage: Lineage; breakdown?: Record<string, number>; missing_skills?: string[] }
export interface Evidence { id: string; kind: string; title: string; description?: string; artifact_url?: string; verified: boolean }
export interface TwinSkill { id: string; name: string; score: number; verified: boolean; evidence: Evidence[]; lineage: Lineage }
export interface Twin { name: string; skills: TwinSkill[]; claimed_count: number; verified_count: number }
export interface Role { id: string; title: string; skills: string[] }
export interface Skill { id: string; name: string; hours: number; prerequisites: string[] }
export interface Opportunity { id: string; title: string; organization: string; type: string; location: string; skills: string[]; description: string; is_demo: boolean; match: Score; eligibility: { status: string; reasons: string[]; missing: string[] } }
export interface Mission { id: string; title: string; skill_id: string; status: string; hours: number; checklist: string[] }
export interface Application { id: string; title: string; organization: string; status: string; resume_version: number; outcome?: string; match: Score; eligibility: Opportunity['eligibility']; resume: { name: string; email: string; target: string; guard: string; note: string; bullets: { skill: string; text: string; evidence_id: string; artifact_url: string; verified: boolean }[] } }

export function useResource<T>(path: string) {
  return useQuery<T>({ queryKey: [path], queryFn: async () => (await api.get<T>(path)).data, retry: 1 });
}

export function useRefresh() {
  const client = useQueryClient();
  return () => client.invalidateQueries();
}

export function errorMessage(error: unknown) {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail;
    if (typeof detail === 'string') return detail;
    if (Array.isArray(detail)) return detail.map((e: { msg: string }) => e.msg).join('. ');
    if (!error.response) return 'Unable to reach the server. Check your connection and try again.';
  }
  return 'Something went wrong. Please try again.';
}

export function PageTitle({ eyebrow, title, description, action }: { eyebrow: string; title: string; description: string; action?: React.ReactNode }) {
  return <div className="flex flex-wrap items-end justify-between gap-5 mb-8"><div><p className="text-xs tracking-[.18em] uppercase font-bold text-violet-600 mb-3">{eyebrow}</p><h1 className="text-3xl md:text-4xl font-bold tracking-tight text-slate-950 dark:text-white">{title}</h1><p className="text-slate-500 mt-3 max-w-2xl leading-relaxed">{description}</p></div>{action}</div>;
}

export function Panel({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return <section className={`rounded-2xl border border-slate-200 bg-white p-6 dark:bg-slate-900 dark:border-slate-800 ${className}`}>{children}</section>;
}

export function Tag({ children, green = false }: { children: React.ReactNode; green?: boolean }) {
  return <span className={`inline-flex rounded-md px-2 py-1 text-xs font-medium ${green ? 'bg-emerald-50 text-emerald-800' : 'bg-violet-50 text-violet-800'}`}>{children}</span>;
}

export function Progress({ value, label }: { value: number; label: string }) {
  return <div><div className="flex justify-between text-xs mb-2"><span>{label}</span><strong>{value.toFixed(0)}%</strong></div><div role="progressbar" aria-label={label} aria-valuemin={0} aria-valuemax={100} aria-valuenow={value} className="h-1.5 bg-slate-100 rounded-full overflow-hidden"><div className="h-full bg-emerald-600 rounded-full transition-all" style={{ width: `${Math.max(0, Math.min(100, value))}%` }} /></div></div>;
}

export function Why({ lineage }: { lineage: Lineage }) {
  return <details className="text-xs mt-4 border-t border-slate-100 pt-3"><summary className="cursor-pointer font-semibold text-violet-700">Why this score?</summary><dl className="mt-3 space-y-2 text-slate-600"><div><dt className="font-semibold">Source</dt><dd>{lineage.source} · {lineage.period} · {lineage.record_count} records</dd></div><div><dt className="font-semibold">Calculation</dt><dd>{lineage.formula}</dd></div><div><dt className="font-semibold">Confidence: {lineage.confidence}</dt><dd>{lineage.limitations}</dd></div></dl></details>;
}

export function State({ loading, error, retry }: { loading?: boolean; error?: unknown; retry?: () => void }) {
  if (loading) return <div role="status" className="p-12 text-center text-slate-500 animate-pulse">Loading your workspace…</div>;
  if (error) return <Panel><p role="alert" className="text-red-700">{errorMessage(error)}</p>{retry && <button onClick={retry} className="btn-secondary mt-4">Try again</button>}</Panel>;
  return null;
}

export function Empty({ title, description, href, label }: { title: string; description: string; href?: string; label?: string }) {
  return <Panel className="text-center py-14"><div className="mx-auto w-12 h-12 rounded-2xl bg-violet-50 text-violet-600 flex items-center justify-center text-xl mb-4">↗</div><h2 className="font-semibold text-lg">{title}</h2><p className="text-sm text-slate-500 max-w-md mx-auto mt-2 mb-5">{description}</p>{href && <Link href={href} className="btn-primary">{label}</Link>}</Panel>;
}

export function Message({ error, success }: { error?: string; success?: string }) {
  return <>{error && <p role="alert" className="rounded-xl bg-red-50 text-red-800 p-4 my-4 text-sm">{error}</p>}{success && <p role="status" className="rounded-xl bg-emerald-50 text-emerald-800 p-4 my-4 text-sm">{success}</p>}</>;
}
