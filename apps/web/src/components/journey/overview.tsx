'use client';
import { FormEvent, useEffect, useRef, useState } from 'react';
import Link from 'next/link';
import api from '@/lib/api';
import { DashboardWorkspace } from './dashboard-workspace';
import { ArrowUpRight, CalendarDays, ChevronLeft, ChevronRight, Trash2, CheckSquare, Plus, Clock } from 'lucide-react';
import { useAuthContext } from '@/providers/auth-provider';
import { Empty, errorMessage, Message, PageTitle, Panel, Progress, Score, State, Tag, Twin, useRefresh, useResource, Why } from './shared';

interface Dashboard { name: string; skills: number; verified: number; readiness: Score; target: { title: string }; applications: number; application_stages: Record<string, number>; application_queue: Record<string, number> & { total: number }; completed_missions: number; active_missions: number; opportunities: number }

type CalendarEvent = { id: string; title: string; starts_at: string; kind: string; packet_id: string; job_title: string };
type CalendarPacket = { id: string; title: string; status: string };

function localDateKey(date: Date) { return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`; }

function CareerCalendar() {
  const query = useResource<CalendarEvent[]>('/career-calendar'); const packets = useResource<CalendarPacket[]>('/apply-queue'); const refresh = useRefresh();
  const today = new Date(); const [month, setMonth] = useState(new Date(today.getFullYear(), today.getMonth(), 1)); const [selected, setSelected] = useState(localDateKey(today));
  const [title, setTitle] = useState(''); const [when, setWhen] = useState(''); const [kind, setKind] = useState('reminder'); const [packet, setPacket] = useState(''); const [error, setError] = useState(''); const [pending, setPending] = useState(false);
  const firstWeekday = new Date(month.getFullYear(), month.getMonth(), 1).getDay(); const days = new Date(month.getFullYear(), month.getMonth() + 1, 0).getDate();
  const eventDates = new Set((query.data ?? []).map(item => localDateKey(new Date(item.starts_at))));
  const events = (query.data ?? []).filter(item => localDateKey(new Date(item.starts_at)) === selected).sort((a, b) => a.starts_at.localeCompare(b.starts_at));
  async function addEvent(e: FormEvent) { e.preventDefault(); setPending(true); setError(''); try { const starts = new Date(when); await api.post('/career-calendar', { title, starts_at: starts.toISOString(), kind, packet_id: packet }); setTitle(''); setWhen(''); await refresh(); } catch (e) { setError(errorMessage(e)); } finally { setPending(false); } }
  async function removeEvent(id: string) { setPending(true); setError(''); try { await api.delete(`/career-calendar/${id}`); await refresh(); } catch (e) { setError(errorMessage(e)); } finally { setPending(false); } }
  return <Panel className="!p-4 sm:!p-5"><div className="flex flex-wrap items-center justify-between gap-3"><div className="flex items-center gap-3"><span className="grid h-10 w-10 place-items-center rounded-xl bg-violet-100 text-violet-700"><CalendarDays size={20}/></span><div><h2 className="font-semibold">Career calendar</h2><p className="text-xs text-slate-500">Interviews, deadlines and reminders.</p></div></div><div className="flex items-center gap-2"><button aria-label="Previous month" onClick={() => setMonth(new Date(month.getFullYear(), month.getMonth() - 1, 1))} className="rounded-lg p-2 hover:bg-slate-100"><ChevronLeft size={17}/></button><span className="min-w-32 text-center text-sm font-medium">{month.toLocaleDateString(undefined, { month: 'long', year: 'numeric' })}</span><button aria-label="Next month" onClick={() => setMonth(new Date(month.getFullYear(), month.getMonth() + 1, 1))} className="rounded-lg p-2 hover:bg-slate-100"><ChevronRight size={17}/></button></div></div><div className="mt-4 grid gap-3"><div><div className="grid grid-cols-7 text-center text-[11px] font-semibold text-slate-400">{['Sun','Mon','Tue','Wed','Thu','Fri','Sat'].map(day => <span key={day} className="py-1">{day}</span>)}</div><div className="grid grid-cols-7 gap-1">{Array.from({ length: firstWeekday }, (_, index) => <span key={`blank-${index}`} className="aspect-square"/>)}{Array.from({ length: days }, (_, index) => { const day = index + 1; const key = localDateKey(new Date(month.getFullYear(), month.getMonth(), day)); const active = key === selected; const isToday = key === localDateKey(today); return <button key={key} onClick={() => setSelected(key)} aria-pressed={active} className={`relative aspect-square rounded-lg text-xs transition-colors ${active ? 'bg-violet-700 text-white' : isToday ? 'border border-violet-300 bg-violet-50 text-violet-800' : 'hover:bg-slate-100'}`}>{day}{eventDates.has(key) && <span className={`absolute bottom-1.5 left-1/2 h-1 w-1 -translate-x-1/2 rounded-full ${active ? 'bg-[#d8ff69]' : 'bg-violet-600'}`}/>}</button>; })}</div></div><div className="min-w-0 rounded-xl bg-slate-50 p-4"><h3 className="text-sm font-semibold">{new Date(`${selected}T12:00:00`).toLocaleDateString(undefined, { weekday: 'long', month: 'short', day: 'numeric' })}</h3><div className="mt-3 space-y-2">{events.map(item => <div key={item.id} className="flex items-start gap-3 rounded-lg bg-white p-3"><span className="mt-1 h-2 w-2 rounded-full bg-violet-600"/><div className="min-w-0 flex-1"><p className="text-sm font-medium">{item.title}</p><p className="mt-1 text-xs text-slate-500">{new Date(item.starts_at).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })}{item.job_title ? ` · ${item.job_title}` : ` · ${item.kind.replace('_',' ')}`}</p></div><button onClick={() => void removeEvent(item.id)} disabled={pending} aria-label={`Remove ${item.title}`} className="text-slate-400 hover:text-rose-600"><Trash2 size={14}/></button></div>)}{!events.length && <p className="py-3 text-xs text-slate-500">Nothing scheduled. Add an interview, follow-up or reminder below.</p>}</div></div></div><details className="mt-3 border-t border-slate-100 pt-3"><summary className="cursor-pointer text-xs font-semibold text-violet-800">Add an event or reminder</summary><form onSubmit={addEvent} className="mt-3 grid items-end gap-3 sm:grid-cols-2"><label className="text-xs">Reminder<input required maxLength={160} value={title} onChange={e => setTitle(e.target.value)} className="journey-input" placeholder="Interview with Acme"/></label><label className="text-xs">Date & time<input required type="datetime-local" value={when} onChange={e => setWhen(e.target.value)} className="journey-input"/></label><label className="text-xs">Type<select value={kind} onChange={e => setKind(e.target.value)} className="journey-input"><option value="interview">Interview</option><option value="follow_up">Follow-up</option><option value="deadline">Deadline</option><option value="reminder">Reminder</option></select></label><label className="text-xs">Related role<select value={packet} onChange={e => setPacket(e.target.value)} className="journey-input"><option value="">General reminder</option>{packets.data?.map(item => <option key={item.id} value={item.id}>{item.title}</option>)}</select></label><button disabled={pending || !when} className="btn-primary">Add reminder</button></form></details>{error && <p role="alert" className="mt-3 text-xs text-rose-700">{error}</p>}</Panel>;

}

function DailyChecklist() {
  const [tasks, setTasks] = useState<{id: string, text: string, done: boolean}[]>([]);
  const [sleepTime, setSleepTime] = useState('');
  const [startTime, setStartTime] = useState('');
  const [newTask, setNewTask] = useState('');
  const todayKey = localDateKey(new Date());
  
  useEffect(() => {
    const saved = localStorage.getItem(`daily-checklist-${todayKey}`);
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        setTasks(parsed.tasks || []);
        setSleepTime(parsed.sleepTime || '');
        setStartTime(parsed.startTime || '');
      } catch (e) {}
    } else {
      setTasks([
        { id: '1', text: 'Review new job matches', done: false },
        { id: '2', text: 'Work on a project mission', done: false },
        { id: '3', text: 'Follow up on applications', done: false }
      ]);
    }
  }, [todayKey]);

  useEffect(() => {
    if (tasks.length > 0) {
      localStorage.setItem(`daily-checklist-${todayKey}`, JSON.stringify({ tasks, sleepTime, startTime }));
    }
  }, [tasks, sleepTime, startTime, todayKey]);

  const toggleTask = (id: string) => setTasks(tasks.map(t => t.id === id ? { ...t, done: !t.done } : t));
  const removeTask = (id: string) => setTasks(tasks.filter(t => t.id !== id));
  const addTask = (e: FormEvent) => {
    e.preventDefault();
    if (!newTask.trim()) return;
    setTasks([...tasks, { id: Math.random().toString(), text: newTask.trim(), done: false }]);
    setNewTask('');
  };

  const progress = tasks.length ? Math.round((tasks.filter(t => t.done).length / tasks.length) * 100) : 0;

  return <Panel className="!p-4 sm:!p-5">
    <div className="flex items-center gap-3"><span className="grid h-10 w-10 place-items-center rounded-xl bg-emerald-100 text-emerald-700"><CheckSquare size={20}/></span><div><h2 className="font-semibold">Daily routine</h2><p className="text-xs text-slate-500">Track essentials & habits.</p></div></div>
    
    <div className="mt-4 grid grid-cols-2 gap-3 border-b border-slate-100 pb-4">
      <label className="text-[10px] font-semibold text-slate-500">Sleep time <Clock size={12} className="inline ml-1 mb-0.5"/><input type="time" value={sleepTime} onChange={e => setSleepTime(e.target.value)} className="mt-1 block w-full rounded-md border-slate-200 text-xs shadow-sm focus:border-violet-500 focus:ring-violet-500"/></label>
      <label className="text-[10px] font-semibold text-slate-500">Start time <Clock size={12} className="inline ml-1 mb-0.5"/><input type="time" value={startTime} onChange={e => setStartTime(e.target.value)} className="mt-1 block w-full rounded-md border-slate-200 text-xs shadow-sm focus:border-violet-500 focus:ring-violet-500"/></label>
    </div>

    <div className="mt-4">
      <div className="mb-2 flex items-center justify-between text-xs"><span className="font-medium text-slate-700">Tasks</span><span className="font-bold text-emerald-600">{progress}%</span></div>
      <div className="h-1.5 w-full overflow-hidden rounded-full bg-slate-100"><div className="h-full bg-emerald-500 transition-all" style={{ width: `${progress}%` }}/></div>
      <div className="mt-3 space-y-1">
        {tasks.map(t => (
          <div key={t.id} className="group flex items-center gap-2 rounded-md p-1 hover:bg-slate-50">
            <input type="checkbox" checked={t.done} onChange={() => toggleTask(t.id)} className="h-4 w-4 rounded border-slate-300 text-emerald-600 focus:ring-emerald-600"/>
            <span className={`min-w-0 flex-1 truncate text-xs ${t.done ? 'text-slate-400 line-through' : 'text-slate-700'}`}>{t.text}</span>
            <button type="button" onClick={() => removeTask(t.id)} className="opacity-0 transition-opacity group-hover:opacity-100 text-slate-400 hover:text-rose-600"><Trash2 size={12}/></button>
          </div>
        ))}
      </div>
      <form onSubmit={addTask} className="mt-3 flex items-center gap-2">
        <input value={newTask} onChange={e => setNewTask(e.target.value)} placeholder="Add a new task..." className="h-7 w-full rounded-md border-slate-200 text-xs shadow-sm focus:border-violet-500 focus:ring-violet-500"/>
        <button type="submit" disabled={!newTask.trim()} className="grid h-7 w-7 shrink-0 place-items-center rounded-md bg-slate-100 text-slate-600 hover:bg-slate-200 disabled:opacity-50"><Plus size={14}/></button>
      </form>
    </div>
  </Panel>;
}

export function DashboardPage() {
  const query = useResource<Dashboard>('/dashboard');
  const { user } = useAuthContext();
  const automation = useResource<{ auto_prepare_matched: boolean }>('/automation/preferences');
  const runOnce = useRef(false);
  const [automationPending, setAutomationPending] = useState(false);
  const [automationMessage, setAutomationMessage] = useState('');
  useEffect(() => {
    if (!automation.data?.auto_prepare_matched || runOnce.current) return;
    runOnce.current = true;
    api.post('/automation/prepare-matches').then(({ data }) => {
      setAutomationMessage(data.prepared ? `Prepared ${data.prepared} matching application packet${data.prepared === 1 ? '' : 's'} for review.` : (data.message || 'No new matching roles need preparation.'));
    }).catch(error => setAutomationMessage(errorMessage(error)));
  }, [automation.data?.auto_prepare_matched]);
  async function setAutoPrepare(enabled: boolean) {
    setAutomationPending(true);
    setAutomationMessage('');
    try {
      await api.put('/automation/preferences', { auto_prepare_matched: enabled });
      if (!enabled) runOnce.current = false;
      await automation.refetch();
      if (!enabled) setAutomationMessage('Automatic draft preparation is paused. Your existing packets are unchanged.');
    } catch (error) { setAutomationMessage(errorMessage(error)); }
    finally { setAutomationPending(false); }
  }
  if (!query.data) return <State loading={query.isPending} error={query.error} retry={() => query.refetch()}/>;
  const d = query.data;
  return <DashboardWorkspace name={d.name} skills={d.skills} autoPrepare={!!automation.data?.auto_prepare_matched} automationPending={automationPending} automationMessage={automationMessage} onAutoPrepare={setAutoPrepare} calendar={<><CareerCalendar/><DailyChecklist/></>}/>;
}

export function TwinPage({ passport = false }: { passport?: boolean }) {
  const query = useResource<Twin>('/talent-twin');
  return <div className="max-w-6xl mx-auto"><PageTitle eyebrow={passport ? 'Your evidence, together' : 'Understand your starting point'} title={passport ? 'Skill Passport' : 'Your Talent Twin'} description="A résumé tells your story. Evidence shows what you can do. Your scores keep that distinction clear." action={<Link href="/vault" className="btn-primary">Add résumé <ArrowUpRight size={16}/></Link>}/><State loading={query.isPending} error={query.error} retry={() => query.refetch()}/>{query.data && <><div className="flex gap-3 mb-6"><Tag>{query.data.claimed_count} claimed skills</Tag><Tag green>{query.data.verified_count} independently verified</Tag></div>{!query.data.skills.length ? <Empty title="Your story starts here" description="Upload your résumé to extract skills. Claims begin at zero trust until you add evidence." href="/vault" label="Upload my résumé"/> : <div className="grid sm:grid-cols-2 xl:grid-cols-3 gap-5">{query.data.skills.map(skill => <Panel key={skill.id}><div className="flex justify-between gap-2 items-center"><h2 className="font-semibold text-lg">{skill.name}</h2><Tag green={skill.verified}>{skill.verified ? 'Verified' : 'Self-reported'}</Tag></div><div className="my-5"><Progress value={skill.score} label="Skill trust score"/></div><details className="text-sm"><summary className="cursor-pointer text-slate-600">{skill.evidence.length} evidence item{skill.evidence.length !== 1 ? 's' : ''}</summary><ul className="mt-3 space-y-3">{skill.evidence.map(e => <li key={e.id} className="rounded-lg bg-slate-50 p-3 text-xs"><strong>{e.title}</strong><p className="mt-1 text-slate-500">{e.kind.replace('_', ' ')} · {e.verified ? 'verified' : 'not independently verified'}</p>{e.description && <p className="mt-2">{e.description}</p>}{e.artifact_url && <a className="mt-2 block text-violet-700 underline" href={e.artifact_url} target="_blank" rel="noreferrer">View project ↗</a>}</li>)}</ul></details><Why lineage={skill.lineage}/></Panel>)}</div>}</>}</div>;
}

