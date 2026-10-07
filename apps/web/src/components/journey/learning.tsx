'use client';
import { FormEvent, useState } from 'react';
import Link from 'next/link';
import api from '@/lib/api';
import { errorMessage, Lineage, Message, PageTitle, Panel, Progress, State, Tag, useRefresh, useResource, Why } from './shared';

interface Assessment { skill_id: string; title: string; best_score: number | null; questions: { id: string; prompt: string; choices: string[] }[]; limitations: string }

function AssessmentCard({ assessment }: { assessment: Assessment }) {
  const [answers, setAnswers] = useState<Record<string, number>>({}); const [pending, setPending] = useState(false); const [error, setError] = useState(''); const [success, setSuccess] = useState(''); const refresh = useRefresh();
  async function submit(e: FormEvent) { e.preventDefault(); setPending(true); setError(''); try { const { data } = await api.post(`/assessments/${assessment.skill_id}/submit`, { answers }); setSuccess(`${data.correct}/${data.total} correct · ${data.score}%. Your best score has been added to your skill evidence.`); await refresh(); } catch (e) { setError(errorMessage(e)); } finally { setPending(false); } }
  return <Panel><div className="flex justify-between gap-3 items-start"><h2 className="font-semibold text-lg">{assessment.title}</h2><Tag>{assessment.best_score === null ? 'Not taken' : `Best: ${assessment.best_score}%`}</Tag></div><p className="text-xs text-slate-500 mt-2 mb-5">{assessment.limitations}</p><form onSubmit={submit} className="space-y-6">{assessment.questions.map((q, index) => <fieldset key={q.id}><legend className="text-sm font-medium mb-3">{index + 1}. {q.prompt}</legend><div className="space-y-2">{q.choices.map((c, choice) => <label key={choice} className="flex gap-3 items-center text-sm text-slate-600"><input required type="radio" name={`${assessment.skill_id}-${q.id}`} checked={answers[q.id] === choice} onChange={() => setAnswers({ ...answers, [q.id]: choice })} className="accent-violet-600"/>{c}</label>)}</div></fieldset>)}<button disabled={pending} className="btn-primary">{pending ? 'Checking…' : 'Submit assessment'}</button></form><Message error={error} success={success}/></Panel>;
}

export function AssessmentsPage() {
  const query = useResource<Assessment[]>('/assessments');
  return <div className="max-w-5xl mx-auto"><PageTitle eyebrow="A small check. A useful signal." title="Put your foundations to the test." description="Short, unproctored quizzes help you check your understanding. They contribute limited evidence and are not a professional certification."/><State loading={query.isPending} error={query.error} retry={() => query.refetch()}/><div className="grid md:grid-cols-2 gap-5">{query.data?.map(a => <AssessmentCard key={a.skill_id} assessment={a}/>)}</div></div>;
}

export function PassportSharing() {
  const query = useResource<{ id: string; expires_at: string; revoked: boolean }[]>('/passport/shares');
  const [consent, setConsent] = useState(false); const [url, setUrl] = useState(''); const [error, setError] = useState(''); const [pending, setPending] = useState(false); const refresh = useRefresh();
  async function share() { setPending(true); setError(''); try { const { data } = await api.post('/passport/share', { consent, days: 7 }); setUrl(`${window.location.origin}${data.path}`); await refresh(); } catch (e) { setError(errorMessage(e)); } finally { setPending(false); } }
  async function revoke(id: string) { try { await api.delete(`/passport/shares/${id}`); setUrl(''); await refresh(); } catch (e) { setError(errorMessage(e)); } }
  return <Panel className="mb-6"><h2 className="font-semibold">Share a snapshot of your progress</h2><p className="text-sm text-slate-500 mt-2">The link shares only your name, skill scores, verification labels and formulas. Your email, documents and project descriptions remain private. It expires after seven days.</p><label className="flex gap-3 items-start text-sm mt-4"><input className="mt-1 accent-violet-600" type="checkbox" checked={consent} onChange={e => setConsent(e.target.checked)}/>I consent to sharing this snapshot with anyone who has the link.</label><button className="btn-secondary mt-4" disabled={!consent || pending} onClick={share}>Create share link</button>{url && <label className="block text-sm mt-4">Your private share link<input readOnly className="journey-input" value={url} onFocus={e => e.target.select()}/></label>}<Message error={error}/><div className="mt-5 divide-y">{query.data?.filter(s => !s.revoked).map(s => <div key={s.id} className="py-3 flex justify-between gap-3 text-xs"><span>Expires {new Date(s.expires_at).toLocaleDateString()}</span><button className="text-red-700 underline" onClick={() => revoke(s.id)}>Revoke access</button></div>)}</div></Panel>;
}

interface SharedPassport { name: string; created_at: string; note: string; skills: { name: string; score: number; verified: boolean; lineage: Lineage }[] }
export function PublicPassport({ token }: { token: string }) {
  const query = useResource<SharedPassport>(`/public/passport/${encodeURIComponent(token)}`);
  return <main className="min-h-screen bg-[#f7f8fa] p-6 md:p-14"><div className="max-w-4xl mx-auto"><Link href="/" className="text-xl font-bold tracking-tight">Limit.less</Link><div className="mt-10"><PageTitle eyebrow="Shared with permission" title={query.data ? `${query.data.name}’s Skill Passport` : 'Skill Passport'} description={query.data?.note || 'A consent-gated snapshot of career evidence.'}/></div><State loading={query.isPending} error={query.error}/>{query.data && <><p className="text-xs text-slate-500 mb-5">Snapshot created {new Date(query.data.created_at).toLocaleDateString()}</p><div className="grid sm:grid-cols-2 gap-5">{query.data.skills.map(s => <Panel key={s.name}><div className="flex justify-between mb-5"><h2 className="font-semibold">{s.name}</h2><Tag green={s.verified}>{s.verified ? 'Verified' : 'Not independently verified'}</Tag></div><Progress label="Skill trust score" value={s.score}/><Why lineage={s.lineage}/></Panel>)}</div></>}</div></main>;
}

export function NotificationsPage() {
  const query = useResource<{ id: string; title: string; body: string; is_read: boolean; created_at: string }[]>('/notifications'); const refresh = useRefresh(); const [error, setError] = useState('');
  async function read(id: string) { try { await api.post(`/notifications/${id}/read`); await refresh(); } catch (e) { setError(errorMessage(e)); } }
  return <div className="max-w-4xl mx-auto"><PageTitle eyebrow="Stay in the loop" title="Your updates" description="Application approvals and activity from your saved workspace."/><State loading={query.isPending} error={query.error}/><Message error={error}/><div className="space-y-4">{query.data?.length === 0 && <Panel><p className="text-slate-500">You’re all caught up. New updates will appear here.</p></Panel>}{query.data?.map(n => <Panel key={n.id}><div className="flex justify-between"><h2 className="font-semibold">{n.title}</h2><Tag green>{n.is_read ? 'Read' : 'New'}</Tag></div><p className="text-sm text-slate-500 my-3">{n.body}</p>{!n.is_read && <button className="text-sm text-violet-700 underline" onClick={() => read(n.id)}>Mark as read</button>}</Panel>)}</div></div>;
}


