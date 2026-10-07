'use client';
import { FormEvent, useState } from 'react';
import Link from 'next/link';
import { ArrowDownToLine, ArrowRight, BookOpen, CheckCircle2, Clock3, ExternalLink, Flag, Target } from 'lucide-react';
import api from '@/lib/api';
import { Empty, errorMessage, Lineage, Message, Mission, PageTitle, Panel, Role, Skill, State, Tag, useRefresh, useResource, Why } from './shared';

interface Plan { role: { id: string; title: string; skills: string[] }; steps: Skill[]; hours: number; budget: number; current_score: number; projected_score: number; lineage: Lineage; projection_note: string }
interface RoadmapJob { id: string; title: string; organization: string; skills?: string[] }

export function GPSPage() {
  const roles = useResource<Role[]>('/roles');
  const jobs = useResource<RoadmapJob[]>('/live-jobs');
  const missions = useResource<Mission[]>('/missions');
  const [role, setRole] = useState('software-engineer');
  const [hours, setHours] = useState(40);
  const [plan, setPlan] = useState<Plan | null>(null);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const refresh = useRefresh();
  async function calculate(e: FormEvent) {
    e.preventDefault(); setPending(true); setError(''); setSuccess('');
    try {
      const jobId = role.startsWith('job:') ? role.slice(4) : '';
      if (!jobId) await api.patch('/users/me', { target_role: role });
      const result = await api.post<Plan>('/career-gps', jobId ? { job_id: jobId, hours } : { role_id: role, hours });
      setPlan(result.data); await refresh();
    } catch (e) { setError(errorMessage(e)); } finally { setPending(false); }
  }
  async function start(skill: Skill) {
    try { await api.post('/missions', { skill_id: skill.id }); await refresh(); setSuccess(`${skill.name} mission is ready. Open Missions to begin.`); } catch (e) { setError(errorMessage(e)); }
  }
  const activeSkills = new Set((missions.data || []).filter(m => m.status === 'in_progress').map(m => m.skill_id));
  const completedSkills = new Set((missions.data || []).filter(m => m.status === 'completed').map(m => m.skill_id));
  const doneCount = plan?.steps.filter(step => completedSkills.has(step.id)).length ?? 0;
  function downloadPlan() {
    if (!plan) return;
    const roleTitle = plan.role.title || roles.data?.find(item => item.id === role)?.title || 'Career path';
    const lines = [
      `# My ${roleTitle} learning route`, '',
      `Planned learning time: ${plan.hours} of ${plan.budget} hours`,
      `Current evidence coverage: ${plan.current_score.toFixed(0)}%`,
      `Projected scenario: ${plan.projected_score.toFixed(0)}%`, '',
      'This is a planning estimate based on the skills and demo role data currently available in Limit.less. It is not a certification or a guarantee of employment.', '',
      ...plan.steps.flatMap((step, index) => [
        `## ${index + 1}. ${step.name} · ${step.hours} hours`,
        step.prerequisites.length ? `Prerequisites: ${step.prerequisites.join(', ')}` : 'Start here: foundational skill',
        `Progress: ${completedSkills.has(step.id) ? 'Completed' : activeSkills.has(step.id) ? 'In progress' : 'Not started'}`,
        `Practice: Build a small, original project that demonstrates ${step.name}; document what you did and link the work in your portfolio.`,
        `Learning resource: ${resourceFor(step.id).label} — ${resourceFor(step.id).url}`,
        '',
      ]),
      `\n${plan.projection_note}`,
    ];
    const blob = new Blob([lines.join('\n')], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a'); anchor.href = url; anchor.download = `limitless-${roleTitle.toLowerCase().replace(/[^a-z0-9]+/g, '-')}-roadmap.md`; anchor.click(); URL.revokeObjectURL(url);
  }
  return <div className="max-w-6xl mx-auto">
    <PageTitle eyebrow="A direction, not a guess" title="Your next steps, made practical." description="Choose the role you want and the time you have. Limit.less builds a skill-by-skill route from your current evidence, then turns each step into a project you can show." action={<a href="https://roadmap.sh/frontend" target="_blank" rel="noreferrer" className="btn-secondary">Explore a public frontend guide <ExternalLink size={15}/></a>}/>
    <Panel className="border-violet-100 bg-gradient-to-br from-white to-violet-50/60">
      <form onSubmit={calculate} className="grid gap-5 items-end md:grid-cols-[1fr_190px_auto]">
        <label className="text-sm font-medium">Where do you want to go?<select className="journey-input" value={role} onChange={e => setRole(e.target.value)}><optgroup label="Curated role guides">{roles.data?.map(r => <option key={r.id} value={r.id}>{r.title}</option>)}</optgroup>{jobs.data?.some(job => job.skills?.length) && <optgroup label="Your imported real job postings">{jobs.data.filter(job => job.skills?.length).map(job => <option key={job.id} value={`job:${job.id}`}>{job.title} · {job.organization}</option>)}</optgroup>}</select><span className="mt-1 block text-xs font-normal text-slate-500">Use an imported employer posting for a role-specific skill plan.</span></label>
        <label className="text-sm font-medium">Time you can invest<input className="journey-input" type="number" min={1} max={160} required value={hours} onChange={e => setHours(Number(e.target.value))}/><span className="mt-1 block text-xs font-normal text-slate-500">Hours for this learning plan</span></label>
        <button disabled={pending || !roles.data} className="btn-primary mb-0.5">{pending ? 'Building your route…' : 'Build my roadmap'}<ArrowRight size={16}/></button>
      </form>
    </Panel>
    <State error={roles.error || jobs.error || missions.error} retry={() => { void roles.refetch(); void jobs.refetch(); void missions.refetch(); }}/>
    <Message error={error} success={success}/>
    {plan && <>
      <div className="my-6 grid gap-4 sm:grid-cols-3">
        <Panel><div className="flex items-center gap-2 text-sm text-slate-500"><Target size={16}/>Current evidence coverage</div><p className="mt-3 text-3xl font-semibold">{plan.current_score.toFixed(0)}%</p><p className="mt-1 text-xs text-slate-500">Based on skills currently in your profile</p></Panel>
        <Panel className="!border-lime-200 !bg-[#f4f9e9]"><div className="flex items-center gap-2 text-sm text-slate-600"><Flag size={16}/>Projected scenario</div><p className="mt-3 text-3xl font-semibold">{plan.projected_score.toFixed(0)}%</p><p className="mt-1 text-xs text-slate-600">A planning estimate if you build these skills</p></Panel>
        <Panel><div className="flex items-center gap-2 text-sm text-slate-500"><Clock3 size={16}/>Learning route</div><p className="mt-3 text-3xl font-semibold">{plan.hours}<span className="text-lg text-slate-400"> / {plan.budget}h</span></p><p className="mt-1 text-xs text-slate-500">{doneCount} of {plan.steps.length} planned skills evidenced</p></Panel>
      </div>
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3"><div><p className="text-xs font-bold uppercase tracking-[.16em] text-violet-600">Your personalized path</p><h2 className="mt-1 text-xl font-semibold">{plan.role.title} · {plan.steps.length} {plan.steps.length === 1 ? 'milestone' : 'milestones'}</h2><p className="mt-1 text-xs text-slate-500">Target skills: {plan.role.skills.map(skill => skill.replaceAll('_', ' ')).join(' · ')}</p></div><button className="btn-secondary" onClick={downloadPlan} disabled={!plan.steps.length}><ArrowDownToLine size={16}/>Download roadmap</button></div>
      {plan.steps.length ? <ol className="relative space-y-4 before:absolute before:left-5 before:top-7 before:h-[calc(100%-3.5rem)] before:w-px before:bg-violet-100">{plan.steps.map((step, index) => {
        const complete = completedSkills.has(step.id); const active = activeSkills.has(step.id); const resource = resourceFor(step.id);
        return <li key={step.id} className="relative"><Panel className={complete ? 'border-emerald-200' : active ? 'border-violet-200' : ''}><div className="flex flex-wrap items-start gap-4"><span className={`z-10 flex h-10 w-10 shrink-0 items-center justify-center rounded-full border-4 border-white font-semibold ${complete ? 'bg-emerald-100 text-emerald-700' : active ? 'bg-violet-100 text-violet-700' : 'bg-slate-100 text-slate-600'}`}>{complete ? <CheckCircle2 size={18}/> : String(index + 1).padStart(2, '0')}</span><div className="min-w-0 flex-1"><div className="flex flex-wrap items-center gap-2"><h3 className="text-lg font-semibold">{step.name}</h3><Tag green={complete}>{complete ? 'Evidence added' : active ? 'Mission in progress' : step.prerequisites.length ? 'Build on foundations' : 'Start here'}</Tag></div><p className="mt-2 text-sm leading-relaxed text-slate-600">Learn the essentials, then build a small original project that demonstrates {step.name}. Add a short README and link your work to make the skill visible to employers.</p>{step.prerequisites.length > 0 && <p className="mt-2 text-xs text-slate-500">Builds on: {step.prerequisites.join(', ')}</p>}<a href={resource.url} target="_blank" rel="noreferrer" className="mt-3 inline-flex items-center gap-2 text-sm font-medium text-violet-700 hover:underline"><BookOpen size={15}/> {resource.label}<ExternalLink size={13}/></a>{resource.source === 'SAS' && <p className="mt-1 text-[11px] leading-5 text-slate-500">Matched to this skill gap from the official SAS course catalog. Course progress is not synced to Limit.less; sign-in or a subscription may be required.</p>}</div><div className="flex items-center gap-2 text-sm text-slate-500"><Clock3 size={15}/>{step.hours}h</div></div><div className="mt-4 flex justify-end">{complete ? <Link className="btn-secondary" href="/missions">View your evidence</Link> : <button className="btn-secondary" onClick={() => start(step)}>{active ? 'Continue mission' : 'Start project mission'}<ArrowRight size={15}/></button>}</div></Panel></li>;
      })}</ol> : <Empty title="No additional route fits this time" description="Add more hours or choose a different role to see useful next steps."/>}
      <Panel className="mt-5"><p className="text-sm leading-relaxed text-slate-600">{plan.projection_note}</p><p className="mt-3 text-xs text-slate-500">Roadmap and role catalog are currently a curated demo. The projected score is an estimate, not a certification or hiring promise.</p><Why lineage={plan.lineage}/></Panel>
      <div className="mt-5 flex flex-wrap gap-3"><Link href="/missions" className="btn-primary">Open my project missions <ArrowRight size={16}/></Link><Link href="/opportunities" className="btn-secondary">Explore matching opportunities</Link></div>
    </>}
  </div>;
}

function resourceFor(skillId: string): { label: string; url: string; source?: string } {
  const resources: Record<string, { label: string; url: string; source?: string }> = {
    sas_foundations: { label: 'SAS Programming Quick Start for Developers · free · 2h 45m + hands-on', url: 'https://learn.sas.com/course/view.php?id=8797', source: 'SAS' },
    statistics: { label: 'Statistics You Need to Know for Machine Learning · 7h 33m + hands-on', url: 'https://learn.sas.com/course/view.php?id=439', source: 'SAS' },
    machine_learning: { label: 'Machine Learning Using SAS Viya · official SAS course', url: 'https://learn.sas.com/course/view.php?id=343', source: 'SAS' },
    python: { label: 'Python official tutorial', url: 'https://docs.python.org/3/tutorial/' },
    sql: { label: 'PostgreSQL tutorial', url: 'https://www.postgresql.org/docs/current/tutorial.html' },
    git: { label: 'Pro Git book', url: 'https://git-scm.com/book/en/v2' },
    linux: { label: 'Linux Journey', url: 'https://linuxjourney.com/' },
    docker: { label: 'Docker getting started', url: 'https://docs.docker.com/get-started/' },
    aws: { label: 'AWS Skill Builder', url: 'https://skillbuilder.aws/' },
    kubernetes: { label: 'Kubernetes basics', url: 'https://kubernetes.io/docs/tutorials/kubernetes-basics/' },
    javascript: { label: 'MDN JavaScript guide', url: 'https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Scripting' },
    typescript: { label: 'TypeScript handbook', url: 'https://www.typescriptlang.org/docs/handbook/intro.html' },
    react: { label: 'React Learn', url: 'https://react.dev/learn' },
    html: { label: 'MDN HTML', url: 'https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Structuring_content' },
    css: { label: 'MDN CSS', url: 'https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Styling_basics' },
    pandas: { label: 'pandas getting started', url: 'https://pandas.pydata.org/docs/getting_started/intro_tutorials/' },
    fastapi: { label: 'FastAPI tutorial', url: 'https://fastapi.tiangolo.com/tutorial/' },
    testing: { label: 'Playwright getting started', url: 'https://playwright.dev/docs/intro' },
    figma: { label: 'Figma Learn', url: 'https://help.figma.com/hc/en-us/categories/360002051613-Get-started' },
    excel: { label: 'Microsoft Excel help', url: 'https://support.microsoft.com/excel' },
    power_bi: { label: 'Microsoft Learn · Power BI', url: 'https://learn.microsoft.com/training/powerplatform/power-bi' },
    cybersecurity: { label: 'CISA cybersecurity resources', url: 'https://www.cisa.gov/cybersecurity' },
    networking: { label: 'Cisco Skills for All', url: 'https://skillsforall.com/' },
  };
  return resources[skillId] || { label: 'Search learning resources', url: `https://www.google.com/search?q=${encodeURIComponent(`${skillId.replaceAll('_', ' ')} official documentation`)}` };
}

function MissionCard({ mission }: { mission: Mission }) {
  const [url, setUrl] = useState(''); const [description, setDescription] = useState(''); const [hours, setHours] = useState(mission.hours);
  const [pending, setPending] = useState(false); const [error, setError] = useState(''); const refresh = useRefresh();
  async function complete(e: FormEvent) { e.preventDefault(); setPending(true); setError(''); try { await api.post(`/missions/${mission.id}/complete`, { artifact_url: url, description, hours_spent: hours }); await refresh(); } catch (e) { setError(errorMessage(e)); } finally { setPending(false); } }
  return <Panel><div className="flex justify-between gap-3"><h2 className="font-semibold text-lg">{mission.title}</h2><Tag green={mission.status === 'completed'}>{mission.status === 'completed' ? 'Completed' : 'In progress'}</Tag></div><ul className="space-y-2 my-5">{mission.checklist.map(c => <li key={c} className="flex gap-2 text-sm text-slate-500"><CheckCircle2 size={16} className="text-emerald-600"/>{c}</li>)}</ul>{mission.status !== 'completed' ? <form onSubmit={complete} className="space-y-4"><label className="block text-sm font-medium">Original project link<input className="journey-input" type="url" placeholder="https://github.com/you/project" required value={url} onChange={e => setUrl(e.target.value)}/></label><label className="block text-sm font-medium">What did you build?<textarea className="journey-input" minLength={30} maxLength={3000} required rows={3} value={description} onChange={e => setDescription(e.target.value)} placeholder="Describe your own contribution and what it demonstrates."/></label><label className="block text-sm font-medium">Hours spent<input className="journey-input" type="number" min={0.1} step={0.1} max={1000} required value={hours} onChange={e => setHours(Number(e.target.value))}/></label><p className="text-xs text-slate-500">Submitted projects are self-reported until independently reviewed. Your match scores update immediately.</p><button className="btn-primary" disabled={pending}>{pending ? 'Saving…' : 'Complete mission'}</button><Message error={error}/></form> : <p className="text-sm text-emerald-700">Evidence added to your Talent Twin. Opportunity scores now include your submitted project.</p>}</Panel>;
}

export function MissionsPage() {
  const query = useResource<Mission[]>('/missions');
  return <div className="max-w-5xl mx-auto"><PageTitle eyebrow="Learn it. Build it. Show it." title="Work that speaks for you." description="Practical missions turn learning into original evidence. Give each new skill something to stand on." action={<Link className="btn-primary" href="/career-gps">Find my next mission</Link>}/><State loading={query.isPending} error={query.error} retry={() => query.refetch()}/>{query.data?.length === 0 && <Empty title="Your next project is waiting" description="Build a career route and choose a skill mission to start." href="/career-gps" label="Open Career GPS"/>}<div className="grid md:grid-cols-2 gap-5">{query.data?.map(m => <MissionCard key={m.id} mission={m}/>)}</div></div>;
}
