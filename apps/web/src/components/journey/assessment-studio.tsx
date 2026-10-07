'use client';

import { useEffect, useRef, useState } from 'react';
import { ArrowRight, Camera, Check, Clock3, Mic, Monitor, ShieldCheck, X, AlertCircle, GraduationCap, Trophy, ExternalLink } from 'lucide-react';
import api from '@/lib/api';
import { errorMessage, Message, Panel, State, useRefresh, useResource } from './shared';

type Assessment = { skill_id: string; title: string; best_score: number | null; platform_credential?: { credential_id: string; title: string; score: number; issuer: string; scope: string; verification: string; not_sas_issued: boolean } | null; questions: { id: string; prompt: string; choices: string[] }[] };
type Session = { id: string; questions: Assessment['questions']; expires_at: number; mode: 'practice' | 'monitored' };
type Result = { score: number; correct: number; total: number; status: string; evidence_added: boolean; platform_credential?: Assessment['platform_credential']; events: { type: string; at: number }[] };
type Attempt = { id: string; skill_id: string; mode: string; status: string; started_at: number; result?: Result };

function credentialFor(skillId: string, score: number | null) {
  if (skillId === 'sas_foundations') return { name: 'SAS Foundations · Limit.less assessment badge', level: 'Limit.less-issued · not SAS-issued', href: 'https://www.sas.com/en_us/certification.html', label: 'Explore official SAS credentials', note: 'This platform badge records a server-graded Limit.less knowledge check only. Official SAS certifications require assessment and issuance by SAS.' };
  if (skillId === 'python') return score !== null && score >= 75
    ? { name: 'PCAP · Certified Associate Python Programmer', level: 'Next step after strong foundations', href: 'https://pythoninstitute.org/pcap', label: 'Explore PCAP', note: 'Covers intermediate, multi-module and object-oriented Python. Check current exam version and fees with the issuer.' }
    : { name: 'PCEP · Certified Entry-Level Python Programmer', level: 'Start here', href: 'https://pythoninstitute.org/pcep', label: 'Explore PCEP', note: 'A vendor-issued Python credential. Limit.less practice scores are not exam eligibility or a pass.' };
  if (skillId === 'sql') return { name: 'HackerRank SQL Skills Certification', level: 'Timed external skills test', href: 'https://www.hackerrank.com/skills-verification/sql_basic', label: 'Open SQL skills test', note: 'HackerRank offers timed SQL skill tests and certificates. The test is hosted and scored by HackerRank.' };
  if (skillId === 'git') return { name: 'GitHub Foundations', level: 'Official GitHub certification', href: 'https://learn.github.com/certifications/GHF', label: 'Explore GitHub Foundations', note: 'Covers GitHub collaboration, products, Git basics and repositories. Registration and exam terms are set by GitHub.' };
  if (skillId === 'linux') return { name: 'Linux Foundation Certified IT Associate', level: 'Entry-level credential', href: 'https://training.linuxfoundation.org/certification/certified-it-associate/', label: 'Explore LFCA', note: 'A Linux Foundation credential for foundational IT and cloud concepts. Check current exam details with the issuer.' };
  return null;
}

export function AssessmentsPage() {
  const catalog = useResource<Assessment[]>('/assessments');
  const history = useResource<Attempt[]>('/assessment-sessions');
  const [selected, setSelected] = useState<Assessment | null>(null);
  const [mode, setMode] = useState<'practice' | 'monitored'>('monitored');
  const [consent, setConsent] = useState(false);
  const [ready, setReady] = useState(false);
  const [session, setSession] = useState<Session | null>(null);
  const [result, setResult] = useState<Result | null>(null);
  const [answers, setAnswers] = useState<Record<string, number>>({});
  const [index, setIndex] = useState(0);
  const [remaining, setRemaining] = useState(600);
  const [error, setError] = useState('');
  const [warning, setWarning] = useState('');
  const [pending, setPending] = useState(false);
  const [level, setLevel] = useState(0);
  const stream = useRef<MediaStream | null>(null);
  const deviceRequest = useRef(0);
  const modal = useRef<HTMLDivElement>(null);
  const video = useRef<HTMLVideoElement>(null);
  const audio = useRef<AudioContext | null>(null);
  const events = useRef<string[]>([]);
  const saving = useRef(false);
  const finishing = useRef(false);
  const answerRef = useRef(answers); answerRef.current = answers;
  const refresh = useRefresh();

  function release() {
    deviceRequest.current += 1;
    stream.current?.getTracks().forEach(track => track.stop()); stream.current = null;
    if (audio.current && audio.current.state !== 'closed') void audio.current.close(); audio.current = null;
    setReady(false); setLevel(0);
  }
  useEffect(() => () => { deviceRequest.current += 1; stream.current?.getTracks().forEach(track => track.stop()); if (audio.current && audio.current.state !== 'closed') void audio.current.close(); }, []);
  useEffect(() => { if (video.current && stream.current) video.current.srcObject = stream.current; }, [ready, session]);
  useEffect(() => {
    if (!ready || !stream.current) return;
    const context = new AudioContext(); audio.current = context;
    const analyser = context.createAnalyser(); analyser.fftSize = 256;
    context.createMediaStreamSource(stream.current).connect(analyser);
    const buffer = new Uint8Array(analyser.frequencyBinCount);
    const interval = setInterval(() => { analyser.getByteFrequencyData(buffer); setLevel(Math.min(100, Math.round(buffer.reduce((sum, value) => sum + value, 0) / buffer.length * 2))); }, 250);
    return () => { clearInterval(interval); if (context.state !== 'closed') void context.close(); };
  }, [ready]);
  async function devices() {
    setError(''); setPending(true);
    try { release(); const request = deviceRequest.current; const media = await navigator.mediaDevices.getUserMedia({ video: { width: 320, height: 240 }, audio: true }); if (request !== deviceRequest.current) { media.getTracks().forEach(track => track.stop()); return; } stream.current = media; setReady(true); }
    catch { setError('Camera or microphone access was unavailable. Allow both in browser settings, or choose practice mode.'); }
    finally { setPending(false); }
  }
  async function start() {
    setPending(true); setError('');
    try {
      if (mode === 'monitored') {
        if (!ready || !stream.current?.getTracks().every(track => track.readyState === 'live')) throw new Error('Please check your camera and microphone first.');
        await document.documentElement.requestFullscreen();
      }
      const { data } = await api.post<Session>(`/assessments/${selected!.skill_id}/sessions`, { mode, consent, camera: ready, microphone: ready, fullscreen: !!document.fullscreenElement });
      setAnswers({}); setIndex(0); events.current = []; setWarning(''); setRemaining(Math.max(0, Math.ceil(data.expires_at - Date.now() / 1000))); setSession(data);
    } catch (e) { setError(e instanceof Error && !('response' in e) ? e.message : errorMessage(e)); if (document.fullscreenElement) await document.exitFullscreen().catch(() => {}); }
    finally { setPending(false); }
  }
  async function finish() {
    if (!session || saving.current) return;
    saving.current = true; finishing.current = true; setPending(true); setError('');
    const batch = events.current.splice(0);
    try {
      const { data } = await api.post<Result>(`/assessment-sessions/${session.id}/submit`, { answers: answerRef.current, events: batch });
      setSession(null); setResult(data); release();
      if (document.fullscreenElement) await document.exitFullscreen().catch(() => {});
      await refresh();
    } catch (e) { events.current.unshift(...batch); setError(errorMessage(e)); }
    finally { saving.current = false; finishing.current = false; setPending(false); }
  }
  const finishRef = useRef(finish); finishRef.current = finish;
  useEffect(() => {
    if (!session) return;
    const flag = (type: string) => { if (finishing.current || session.mode !== 'monitored') return; events.current.push(type); setWarning('A session interruption was recorded. You can continue; the result will be held for review, not automatically marked as cheating.'); };
    const visibility = () => { if (document.hidden) flag('tab_hidden'); };
    const fullscreen = () => { if (!document.fullscreenElement) flag('fullscreen_exit'); };
    const blur = () => flag('focus_lost');
    const beforeUnload = (event: BeforeUnloadEvent) => { event.preventDefault(); };
    document.addEventListener('visibilitychange', visibility); document.addEventListener('fullscreenchange', fullscreen); window.addEventListener('blur', blur); window.addEventListener('beforeunload', beforeUnload);
    const tracks = stream.current?.getTracks() || [];
    const trackListeners = tracks.map(track => { const ended = () => { setReady(false); flag(track.kind === 'video' ? 'camera_lost' : 'microphone_lost'); }; track.addEventListener('ended', ended); track.addEventListener('mute', ended); return () => { track.removeEventListener('ended', ended); track.removeEventListener('mute', ended); }; });
    const heartbeat = setInterval(async () => {
      if (saving.current) return;
      saving.current = true; const batch = events.current.splice(0);
      try { await api.post(`/assessment-sessions/${session.id}/signals`, { events: batch }); }
      catch { events.current.unshift(...batch); setWarning('Connection interrupted. Keep this page open and retry submission when connected.'); }
      finally { saving.current = false; }
    }, 15000);
    const timer = setInterval(() => { const seconds = Math.max(0, Math.ceil(session.expires_at - Date.now() / 1000)); setRemaining(seconds); if (!seconds) void finishRef.current(); }, 1000);
    return () => { clearInterval(timer); clearInterval(heartbeat); document.removeEventListener('visibilitychange', visibility); document.removeEventListener('fullscreenchange', fullscreen); window.removeEventListener('blur', blur); window.removeEventListener('beforeunload', beforeUnload); trackListeners.forEach(remove => remove()); };
  }, [session]);

  useEffect(() => {
    if (!selected) return;
    const previous = document.activeElement as HTMLElement | null;
    const container = modal.current;
    const focusable = () => Array.from(container?.querySelectorAll<HTMLElement>('button:not([disabled]),input:not([disabled]),a[href]') || []).filter(element => element.getClientRects().length);
    focusable()[0]?.focus();
    const key = (event: KeyboardEvent) => {
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k') { event.preventDefault(); event.stopImmediatePropagation(); }
      if (event.key !== 'Tab') return;
      const elements = focusable(); const first = elements[0]; const last = elements[elements.length - 1];
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last?.focus(); }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first?.focus(); }
    };
    window.addEventListener('keydown', key, true);
    const overflow = document.body.style.overflow; document.body.style.overflow = 'hidden';
    return () => { window.removeEventListener('keydown', key, true); document.body.style.overflow = overflow; previous?.focus(); };
  }, [selected, session]);
  const close = () => { release(); setSelected(null); setResult(null); setConsent(false); setError(''); };
  if (session) {
    const question = session.questions[index];
    return <div ref={modal} role="dialog" aria-modal="true" aria-label="Assessment attempt" className="fixed inset-0 z-[80] overflow-y-auto bg-[#f7f7f2] text-slate-950"><header className="border-b border-slate-200 bg-white px-5 md:px-10 h-20 flex justify-between items-center gap-3"><span className="text-xl font-extrabold tracking-tighter">Limit.less<span className="text-violet-500">↗</span></span><span className="hidden sm:inline text-sm text-slate-500">{selected?.title}</span><span role="timer" className={`flex gap-2 items-center font-mono text-sm border rounded-full px-4 py-2 ${remaining < 60 ? 'text-red-700 border-red-200' : 'bg-white'}`}><Clock3 size={16}/>{Math.floor(remaining / 60)}:{String(remaining % 60).padStart(2, '0')}</span></header><div className="max-w-6xl mx-auto p-5 md:p-10 grid lg:grid-cols-[1fr_260px] gap-7"><div><div className="flex justify-between text-xs text-slate-500 mb-3"><span>QUESTION {index + 1} OF {session.questions.length}</span><span>{Object.keys(answers).length} answered</span></div><div className="h-1.5 bg-slate-200 rounded-full mb-8"><div className="h-full bg-violet-500 rounded-full" style={{ width: `${Object.keys(answers).length / session.questions.length * 100}%` }}/></div><Panel className="!p-7 md:!p-10"><p className="text-xs font-semibold uppercase tracking-widest text-violet-700 mb-5">{session.mode === 'monitored' ? 'Monitored attempt' : 'Practice attempt'}</p><h1 className="text-2xl md:text-3xl leading-snug text-slate-950 mb-8">{question.prompt}</h1><fieldset className="space-y-3"><legend className="sr-only">Choose one answer</legend>{question.choices.map((choice, n) => <label key={n} className={`flex cursor-pointer items-center gap-4 rounded-xl border p-5 text-sm transition ${answers[question.id] === n ? 'border-violet-500 bg-violet-50 text-violet-950' : 'border-slate-200 hover:border-slate-400 bg-white'}`}><input type="radio" name={question.id} checked={answers[question.id] === n} onChange={() => setAnswers({ ...answers, [question.id]: n })} className="accent-violet-600"/><span className="flex-1">{choice}</span>{answers[question.id] === n && <Check size={18}/>}</label>)}</fieldset><div className="flex justify-between gap-3 mt-8"><button className="btn-secondary" disabled={index === 0 || pending} onClick={() => setIndex(index - 1)}>Previous</button>{index < session.questions.length - 1 ? <button className="btn-primary" onClick={() => setIndex(index + 1)}>Next question <ArrowRight size={16}/></button> : <button className="btn-primary" disabled={pending} onClick={finish}>{pending ? 'Saving…' : 'Submit assessment'}</button>}</div><Message error={error}/></Panel>{warning && <div role="status" className="mt-5 rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-950">{warning}{!document.fullscreenElement && session.mode === 'monitored' && <button className="block underline mt-2" onClick={() => document.documentElement.requestFullscreen().catch(() => setError('Fullscreen is unavailable. You may finish with the interruption recorded.'))}>Return to fullscreen</button>}</div>}</div><aside className="space-y-5"><Panel><h2 className="font-semibold text-sm mb-4">Session check</h2>{session.mode === 'monitored' ? <><video ref={video} autoPlay muted playsInline aria-label="Local camera preview" className="w-full aspect-video rounded-lg bg-slate-900 object-cover"/><p className="text-xs text-slate-600 mt-3">{ready ? 'Camera and microphone connected' : 'Device interrupted'}</p><div className="h-1 mt-3 bg-slate-100 rounded-full" aria-label={`Microphone activity ${level}%`}><div className="h-full bg-emerald-500 rounded-full" style={{ width: `${level}%` }}/></div><p className="text-[11px] text-slate-500 mt-3">Preview and audio levels stay on your device. No video or audio is recorded.</p></> : <p className="text-xs text-slate-500">Practice mode · no camera or microphone required.</p>}</Panel><Panel><h2 className="font-semibold text-sm mb-3">Question navigator</h2><div className="flex flex-wrap gap-2">{session.questions.map((q, n) => <button key={q.id} aria-label={`Go to question ${n + 1}`} aria-current={index === n ? 'step' : undefined} onClick={() => setIndex(n)} className={`w-10 h-10 rounded-lg border text-sm ${index === n ? 'border-violet-500 ring-2 ring-violet-100' : ''} ${answers[q.id] !== undefined ? 'bg-violet-100 text-violet-800' : 'bg-white'}`}>{n + 1}</button>)}</div></Panel><button onClick={finish} disabled={pending} className="text-xs text-slate-500 underline">End attempt and save current answers</button></aside></div></div>;
  }
  return <div className="max-w-6xl mx-auto"><div className="flex items-center gap-2 text-xs text-slate-500 mb-6"><GraduationCap size={15}/> THE ASSESSMENT STUDIO</div><div className="grid md:grid-cols-[1fr_auto] gap-6 items-end mb-9"><div><h1 className="text-4xl md:text-5xl font-bold tracking-tight text-slate-950 leading-[1.1]">Less guessing.<br/><span className="text-violet-600">More knowing.</span></h1><p className="text-slate-600 max-w-lg mt-5 leading-relaxed">A focused space to test your foundations. Choose a skill, settle in, and see where you stand.</p></div><div className="rounded-2xl bg-[#d5f8a9] p-5 max-w-xs"><ShieldCheck size={25} className="mb-3"/><p className="font-semibold text-sm">Clear results. Honest evidence.</p><p className="text-xs leading-relaxed mt-2 text-slate-700">Browser monitoring records interruptions. It does not verify identity or certify professional competence.</p></div></div><State loading={catalog.isPending} error={catalog.error}/><div className="grid sm:grid-cols-2 gap-5">{catalog.data?.map((a, n) => <section key={a.skill_id} className="rounded-2xl border border-slate-200 bg-white p-7 hover:border-violet-300 transition-colors"><div className="flex justify-between items-start"><span className={`w-12 h-12 grid place-items-center rounded-xl font-bold text-lg ${n % 2 ? 'bg-[#e9f4dc] text-emerald-900' : 'bg-[#eee8fa] text-violet-900'}`}>{a.skill_id === 'sas_foundations' ? 'SAS' : ['Py', 'SQL', 'Git', '>_'][n]}</span><span className="text-[11px] rounded-full border border-slate-200 px-3 py-1.5 text-slate-500">{a.best_score === null ? 'Ready when you are' : `Best practice evidence: ${a.best_score}%`}</span></div>{a.platform_credential && <div className="mt-3 rounded-lg bg-emerald-50 px-3 py-2 text-xs text-emerald-900">Limit.less assessment badge earned | {a.platform_credential.credential_id} | not a SAS Institute credential</div>}<h2 className="text-xl font-semibold mt-6 text-slate-950">{a.title}</h2><p className="text-sm text-slate-500 mt-2">An introductory knowledge check, with a focused question-by-question flow.</p><div className="flex items-center gap-4 text-xs text-slate-500 my-6"><span>{a.questions.length} questions</span><span className="flex items-center gap-1"><Clock3 size={13}/>10 minutes</span><span>Foundations</span></div><div className="mt-5 grid grid-cols-2 gap-2 border-t border-slate-100 pt-4"><button onClick={() => { setSelected(a); setMode('practice'); setConsent(false); setResult(null); }} className="inline-flex items-center justify-center gap-1 rounded-lg bg-[#d8ff69] px-2 py-2.5 text-[11px] font-bold text-slate-900">Skill sprint <Trophy size={13}/></button><button onClick={() => { setSelected(a); setMode('monitored'); setConsent(false); setResult(null); }} className="inline-flex items-center justify-center gap-1 rounded-lg border border-slate-200 px-2 py-2.5 text-[11px] font-semibold text-slate-700">Monitored check <ArrowRight size={13}/></button></div></section>)}</div><section className="mt-10 rounded-2xl border border-slate-200 bg-[#222029] p-6 text-white sm:p-7"><div className="flex items-start gap-3"><span className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-[#d8ff69] text-slate-950"><Trophy size={19}/></span><div><p className="text-[10px] font-bold uppercase tracking-[.14em] text-[#d8ff69]">Skill Arena</p><h2 className="mt-1 text-xl font-semibold">Train here. Prove it with the issuer.</h2><p className="mt-2 max-w-2xl text-sm leading-relaxed text-slate-300">Skill sprints are short, timed practice rounds that save your personal best. They use no AI calls. For an external certificate or ranked contest, follow the provider link below; Limit.less does not issue or verify those credentials.</p></div></div><div className="mt-5 grid gap-3 sm:grid-cols-2">{(catalog.data ?? []).map(item => { const credential = credentialFor(item.skill_id, item.best_score); return credential && <article key={item.skill_id} className="rounded-xl border border-white/10 bg-white/[.04] p-4"><div className="flex items-start justify-between gap-3"><div><p className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">{item.title.replace(/ foundations$/i, "")}</p><h3 className="mt-1 text-sm font-semibold">{credential.name}</h3></div><span className="shrink-0 rounded-full bg-white/10 px-2 py-1 text-[9px] text-slate-300">{credential.level}</span></div><p className="mt-2 text-[11px] leading-relaxed text-slate-300">{credential.note}</p><a href={credential.href} target="_blank" rel="noreferrer" className="mt-3 inline-flex items-center gap-1.5 text-[11px] font-semibold text-[#d8ff69] hover:underline">{credential.label}<ExternalLink size={12}/></a></article>; })}</div><p className="mt-4 text-[10px] text-slate-400">External exam availability, eligibility and fees can change. Confirm details with the issuer before registering.</p></section><section className="mt-10"><h2 className="text-lg font-semibold mb-4">Your recent attempts</h2>{!history.data?.length ? <p className="text-sm text-slate-500 p-6 rounded-xl border border-dashed border-slate-300">Your attempts will appear here. No scores yet—just a fresh start.</p> : <div className="rounded-xl border border-slate-200 bg-white divide-y">{history.data.slice(0, 8).map(a => <div key={a.id} className="p-4 flex flex-wrap items-center justify-between gap-3 text-sm"><div><span className="capitalize font-medium">{a.skill_id}</span><span className="text-xs text-slate-500 ml-3">{a.mode} · {new Date(a.started_at * 1000).toLocaleDateString()}</span></div><span className="text-xs rounded-full bg-slate-100 px-3 py-1.5">{a.status.replaceAll('_', ' ')}{a.result ? ` · ${a.result.score}%` : ''}</span></div>)}</div>}</section>
    {selected && <div ref={modal} className="fixed inset-0 z-[75] bg-slate-950/40 backdrop-blur-sm overflow-y-auto p-5 flex items-start justify-center"><section role="dialog" aria-modal="true" aria-labelledby="assessment-setup-title" className="my-8 bg-white rounded-2xl p-7 md:p-9 w-full max-w-2xl shadow-xl"><div className="flex justify-between items-start"><p className="text-xs text-violet-600 font-semibold uppercase tracking-widest">{result ? 'Your result' : 'Before you begin'}</p><button onClick={close} aria-label="Close assessment setup" className="p-1 text-slate-500"><X size={20}/></button></div><h2 id="assessment-setup-title" className="text-2xl font-semibold mt-4">{selected.title}</h2>{result ? <><p className="text-6xl font-semibold tracking-tight mt-7">{result.score}<span className="text-xl text-slate-400"> /100</span></p><p className="text-sm text-slate-500 mt-3">{result.correct} of {result.total} correct · {result.status.replaceAll('_', ' ')}</p><p className="mt-6 text-sm leading-relaxed text-slate-600">{result.platform_credential ? <>Limit.less issued a SAS Foundations assessment badge after the server-graded pass threshold. It verifies this quiz result only; it is not identity-verified, proctored, or issued by SAS.<p className="mt-3 rounded-lg bg-emerald-50 p-3 text-xs text-emerald-900">Badge ID: {result.platform_credential.credential_id}</p></> : result.evidence_added ? 'Limited assessment evidence was added to your profile. It is not independently verified or a professional certification.' : 'This attempt was saved without adding skill evidence. Interruptions are review signals, not a finding of misconduct.'}</p><button className="btn-primary mt-7" onClick={close}>Back to assessments</button></> : <><p className="text-sm text-slate-500 mt-3">10 minutes. Randomized question and answer order. Your score is calculated on the server.</p><div className="grid grid-cols-2 gap-3 my-6">{(['monitored', 'practice'] as const).map(value => <button key={value} onClick={() => { setMode(value); release(); setConsent(false); }} aria-pressed={mode === value} className={`rounded-xl border p-4 text-left ${mode === value ? 'border-violet-500 bg-violet-50' : 'border-slate-200'}`}><span className="font-semibold text-sm capitalize">{value}</span><span className="block text-xs text-slate-500 mt-2">{value === 'monitored' ? 'Fullscreen + device checks' : 'Accessible, no devices needed'}</span></button>)}</div><div className="rounded-xl bg-slate-50 p-5 text-sm space-y-3">{(mode === 'monitored' ? [[Monitor, 'Leaving fullscreen or switching tabs records an interruption.'], [Camera, 'Camera preview stays local. No facial recognition or AI cheating inference.'], [Mic, 'Microphone activity is shown locally. No audio recording or speech analysis.']] : [[GraduationCap, 'Practice is available without monitoring. Results remain explicitly unverified.']]).map(([Icon, text], n) => { const Component = Icon as typeof Monitor; return <p key={n} className="flex gap-3 text-slate-600"><Component size={18} className="shrink-0 mt-0.5"/>{text as string}</p>; })}</div><label className="flex gap-3 text-sm text-slate-600 mt-5"><input type="checkbox" checked={consent} onChange={e => setConsent(e.target.checked)} className="mt-1 accent-violet-600"/>{mode === 'monitored' ? 'I consent to local camera/microphone checks and saving session interruption timestamps with my attempt. I can end the attempt at any time.' : 'I understand this is a practice attempt with limited evidence value.'}</label>{mode === 'monitored' && <div className="mt-5">{ready ? <div className="flex gap-4 items-center"><video ref={video} muted autoPlay playsInline aria-label="Local camera preview" className="w-32 aspect-video bg-slate-900 rounded-lg object-cover"/><div><p className="text-xs text-emerald-700">Devices connected</p><div className="h-1.5 w-32 bg-slate-100 mt-3 rounded-full"><div className="h-full bg-emerald-500 rounded-full" style={{ width: `${level}%` }}/></div><p className="text-[11px] text-slate-500 mt-2">Microphone activity</p></div></div> : <button disabled={!consent || pending} onClick={devices} className="btn-secondary">Check camera & microphone</button>}</div>}<Message error={error}/><button disabled={!consent || pending || (mode === 'monitored' && !ready)} onClick={start} className="btn-primary w-full justify-center mt-6">{pending ? 'Preparing…' : mode === 'monitored' ? 'Enter fullscreen & begin' : 'Begin practice'}<ArrowRight size={16}/></button><p className="mt-4 text-[11px] text-slate-500 flex gap-2"><AlertCircle size={14} className="shrink-0"/>Monitoring is browser-reported and can be bypassed. It is not a secure exam environment. Attempt data can be removed through account deletion in Settings.</p></>}</section></div>}
  </div>;
}


