'use client';
import { FormEvent, useMemo, useState } from 'react';
import Link from 'next/link';
import { ArrowLeft, ArrowUpRight, Check, Eye, EyeOff, ShieldCheck, Sparkles } from 'lucide-react';
import api from '@/lib/api';
import { setToken } from '@/lib/auth';
import { errorMessage, Message } from './shared';

export function AuthForm({ register = false }: { register?: boolean }) {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [tenant, setTenant] = useState('individual');
  const [consent, setConsent] = useState(false);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState('');
  const passwordScore = useMemo(() => [password.length >= 12, /[A-Z]/.test(password) && /[a-z]/.test(password), /\d/.test(password), /[^A-Za-z0-9]/.test(password)].filter(Boolean).length, [password]);

  async function submit(event: FormEvent) {
    event.preventDefault(); setPending(true); setError('');
    try {
      const { data } = await api.post(`/auth/${register ? 'register' : 'login'}`, register ? { name, email, password, tenant_type: tenant, consent } : { email, password });
      setToken(data.access_token, data.refresh_token);
      window.location.assign(!register && data.user?.role === 'superadmin' ? '/admin' : '/dashboard');
    } catch (e) { setError(errorMessage(e)); } finally { setPending(false); }
  }

  return <div className="auth-page min-h-screen text-[#17151b]">
    <header className="auth-header mx-auto flex h-[76px] max-w-[1440px] items-center justify-between px-5 md:px-10 xl:px-14">
      <Link href="/" className="auth-wordmark" aria-label="Limit.less home">Limit.less<span>*</span></Link>
      <Link href="/" className="auth-back"><ArrowLeft size={15}/> Back to home</Link>
    </header>
    <main className="auth-layout mx-auto grid max-w-[1440px] items-center gap-8 px-5 pb-8 pt-3 md:px-10 lg:min-h-[calc(100vh-76px)] lg:grid-cols-[1.04fr_.96fr] lg:gap-14 xl:px-14">
      <section className="auth-story relative flex min-h-[250px] flex-col justify-between overflow-hidden rounded-[30px] border border-black/10 bg-[#ded4f4] p-6 sm:min-h-[330px] sm:p-9 lg:min-h-[640px] lg:p-12">
        <div className="relative z-10 flex items-center gap-2 text-[10px] font-semibold uppercase tracking-[.17em]"><span className="h-2 w-2 rounded-full bg-violet-600"/>A little less noise. A lot more you.</div>
        <div className="auth-artwork" aria-hidden="true"><div className="auth-art-grid"/><div className="auth-orbit auth-orbit-one"/><div className="auth-orbit auth-orbit-two"/><div className="auth-orbit auth-orbit-three"/><div className="auth-chrome-core"><i/><b/></div><span className="auth-art-spark">✳</span><span className="auth-art-chip auth-chip-top">YOUR NEXT ERA ↗</span><span className="auth-art-chip auth-chip-bottom">WORK IN PROGRESS</span></div>
        <div className="auth-copy relative z-10 mt-5 max-w-[560px] lg:mt-0"><p className="mb-3 text-xs font-semibold uppercase tracking-[.15em] text-violet-800">Less limits. More possibility.</p><h1 className="max-w-[590px] text-[clamp(2.6rem,6vw,5.3rem)] font-black leading-[.91] tracking-[-.075em]">Your next chapter<br/>starts with <span className="auth-highlight">proof.</span></h1><p className="mt-5 max-w-md text-sm leading-relaxed text-[#554d60] sm:text-base">Build on the skills you have. Make work you can show. Find a direction that feels like yours.</p><div className="mt-6 hidden flex-wrap gap-x-5 gap-y-2 text-xs font-medium text-[#403b48] sm:flex">{['Evidence you can understand','A plan that fits your life','Your choices stay yours'].map(item => <span key={item} className="inline-flex items-center gap-2"><Check size={14} className="text-violet-700"/>{item}</span>)}</div></div>
        <span className="auth-coordinate absolute bottom-5 right-6 z-10 font-mono text-[9px] tracking-widest text-[#6b6373] lg:bottom-8 lg:right-9">LIMIT.LESS / 01</span>
      </section>

      <section className="auth-form-wrap mx-auto w-full max-w-[510px] py-5 lg:px-3 lg:py-12">
        <div className="auth-form-card rounded-[28px] border border-black/10 bg-[#fffefa] p-6 shadow-[0_20px_70px_rgba(36,26,52,.09)] sm:p-9 md:p-11">
          <div className="mb-8 flex items-center gap-2 text-xs font-semibold text-[#756c7e]"><span className="grid h-8 w-8 place-items-center rounded-xl bg-[#eae2f8] text-violet-800"><Sparkles size={15}/></span>{register ? 'A good place to begin' : 'Welcome back to your workspace'}</div>
          <p className="text-[10px] font-bold uppercase tracking-[.18em] text-violet-700">{register ? 'Make it yours' : 'Pick up where you left off'}</p>
          <h2 className="mt-2 text-3xl font-bold tracking-[-.05em] sm:text-[2.5rem]">{register ? 'Make room for what’s next.' : 'Good to have you back.'}</h2>
          <p className="mt-3 text-sm leading-relaxed text-slate-500">{register ? 'Create your private career workspace. Your next move can start small.' : 'Sign in to get back to the work you’re building.'}</p>

          <Message error={error}/>
          <form onSubmit={submit} className="mt-7 space-y-4">
            {register && <>
              <label className="auth-label">Your name<input required minLength={2} maxLength={160} className="auth-input" value={name} onChange={e => setName(e.target.value)} autoComplete="name" placeholder="How should we call you?"/></label>
              <label className="auth-label">Workspace<select className="auth-input" value={tenant} onChange={e => setTenant(e.target.value)}><option value="individual">Just me · individual</option><option value="organization">My organization</option><option value="institution">My institution</option></select></label>
            </>}
            <label className="auth-label">Email address<input type="email" required className="auth-input" value={email} onChange={e => setEmail(e.target.value)} autoComplete="email" placeholder="you@example.com"/></label>
            <div className="auth-label"><label htmlFor="auth-password">Password</label><span className="auth-password"><input id="auth-password" type={showPassword ? 'text' : 'password'} required minLength={register ? 12 : 1} maxLength={128} className="auth-input" value={password} onChange={e => setPassword(e.target.value)} autoComplete={register ? 'new-password' : 'current-password'} placeholder={register ? 'At least 12 characters' : 'Enter your password'}/><button type="button" aria-label={showPassword ? 'Hide password' : 'Show password'} onClick={() => setShowPassword(value => !value)}>{showPassword ? <EyeOff size={17}/> : <Eye size={17}/>}</button></span>{register && <span className="mt-2 block"><span className="flex gap-1" aria-hidden="true">{[0,1,2,3].map(index => <i key={index} className={`h-1 flex-1 rounded-full ${passwordScore > index ? 'bg-violet-500' : 'bg-[#e9e5ee]'}`}/>)}</span><span className="mt-1 block text-[11px] font-normal text-slate-500">Use 12+ characters with a mix of letters, numbers and symbols.</span></span>}</div>
            {register && <label className="auth-consent"><input type="checkbox" required checked={consent} onChange={e => setConsent(e.target.checked)}/><span>I agree to store my profile for career planning. I can export or delete my data in Settings.</span></label>}
            <button className="auth-submit" disabled={pending}>{pending ? 'One moment…' : register ? 'Create workspace' : 'Sign in'}<ArrowUpRight size={17}/></button>
          </form>
          <p className="mt-6 text-center text-sm text-slate-500">{register ? 'Already have an account?' : 'New to Limit.less?'} <Link className="font-semibold text-violet-800 underline decoration-violet-300 underline-offset-4 hover:decoration-violet-700" href={register ? '/login' : '/register'}>{register ? 'Sign in' : 'Create an account'}</Link></p>
          <div className="mt-7 flex items-center justify-center gap-2 border-t border-black/5 pt-5 text-[11px] text-slate-500"><ShieldCheck size={14} className="text-violet-600"/>Your career. Your data. Your decisions.</div>
        </div>
        <p className="mx-auto mt-4 max-w-sm text-center text-[10px] leading-relaxed text-slate-400">The current opportunity catalog is fictional demo data. Limit.less never sends applications without your review.</p>
      </section>
    </main>
  </div>;
}
