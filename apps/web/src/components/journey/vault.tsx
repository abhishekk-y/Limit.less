'use client';
import { FormEvent, useState } from 'react';
import Link from 'next/link';
import { ResumeSkillDemand, ResumeMarket } from './resume-skill-demand';
import { FileText, Upload, Download, Trash2 } from 'lucide-react';
import api from '@/lib/api';
import { Empty, errorMessage, Message, PageTitle, Panel, State, Tag, useRefresh, useResource } from './shared';

interface Document { id: string; filename: string; skills: string[]; created_at: string; limitations: string }

export function VaultPage() {
  const query = useResource<Document[]>('/vault');
  const market = useResource<ResumeMarket>('/market/live');
  const refresh = useRefresh();
  const [file, setFile] = useState<File | null>(null);
  const [consent, setConsent] = useState(false);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [uploaded, setUploaded] = useState<{filename:string; skills:string[]} | null>(null);
  async function upload(e: FormEvent) {
    e.preventDefault(); if (!file) return;
    setPending(true); setError(''); setSuccess('');
    try {
      if (!consent) throw new Error('Please consent to storing and reading your résumé.');
      if (file.size === 0 || file.size > 2000000) throw new Error('Choose a non-empty résumé up to 2 MB.');
      if (!/\.(pdf|docx|txt)$/i.test(file.name)) throw new Error('Choose a PDF, DOCX or TXT résumé.');
      const body = new FormData(); body.append('file', file); body.append('consent', String(consent));
      const { data } = await api.post('/vault/upload', body, { headers: { 'Content-Type': 'multipart/form-data' } });
      setSuccess(`Résumé saved. ${data.skills.length} claimed skills added to your Talent Twin. These are not yet verified.`);
      setUploaded({filename:data.filename, skills:data.skills});
      await refresh();
    } catch (e) { setError(errorMessage(e)); } finally { setPending(false); }
  }
  async function download(doc: Document) {
    try { const result = await api.get(`/vault/${doc.id}/download`, { responseType: 'blob' }); const url = URL.createObjectURL(result.data); const link = document.createElement('a'); link.href = url; link.download = doc.filename; link.click(); setTimeout(() => URL.revokeObjectURL(url), 1000); } catch (e) { setError(errorMessage(e)); }
  }
  async function remove(doc: Document) {
    if (!window.confirm(`Delete ${doc.filename} and its extracted claims?`)) return;
    try { await api.delete(`/vault/${doc.id}`); await refresh(); setSuccess('Document and linked claims deleted.'); } catch (e) { setError(errorMessage(e)); }
  }
  return <div className="max-w-5xl mx-auto"><PageTitle eyebrow="Your documents. Your control." title="Application Vault" description="Keep your résumé in one place and turn your experience into the starting point for your Talent Twin."/>{uploaded && <Panel className="mb-6 border-emerald-200"><h2 className="font-semibold">Résumé uploaded: {uploaded.filename}</h2><p className="mt-2 text-sm">{uploaded.skills.length} skills extracted. These are résumé claims, not verified abilities.</p><ResumeSkillDemand skills={uploaded.skills} market={market.data} loading={market.isPending} failed={!!market.error}/>{!uploaded.skills.length && <p className="mt-3 text-sm text-amber-700">No supported skills were found. Check that the document contains readable text and review your résumé in Resume Builder.</p>}<p className="mt-3 text-xs text-slate-500">Next: compare these skills with imported jobs, review your work history, then prepare a separate résumé for each selected job. Uploading does not submit an application.</p><div className="mt-4 flex flex-wrap gap-3"><Link href="/dashboard" className="btn-secondary">See skill demand</Link><Link href="/resume-builder" className="btn-secondary">Review résumé details</Link><Link href="/live-jobs" className="btn-primary">Match live jobs</Link></div></Panel>}<div className="grid lg:grid-cols-[1fr_1.1fr] gap-6"><Panel><div className="w-12 h-12 bg-violet-50 rounded-xl flex items-center justify-center mb-5"><Upload className="text-violet-600" size={22}/></div><h2 className="font-semibold text-xl">Start with your résumé</h2><p className="text-sm text-slate-500 mt-2 mb-6">PDF, DOCX, or plain text · up to 2 MB. Original documents are encrypted before storage.</p><form onSubmit={upload} className="space-y-5"><label className="block text-sm font-medium">Choose résumé<input className="journey-input file:mr-4 file:rounded-md file:border-0 file:bg-violet-50 file:px-3 file:py-2 file:text-violet-700" type="file" accept=".pdf,.docx,.txt" required onChange={e => setFile(e.target.files?.[0] || null)}/></label><label className="flex items-start gap-3 text-sm text-slate-600"><input className="mt-1 accent-violet-600" type="checkbox" required checked={consent} onChange={e => setConsent(e.target.checked)}/>I consent to storing this document and extracting my skills for career planning.</label><button className="btn-primary w-full" disabled={pending || !file}>{pending ? 'Reading your résumé…' : 'Upload and build my Twin'}</button></form><p className="text-xs text-slate-500 mt-5 leading-relaxed">Extraction identifies claims, not verified ability. Scanned PDFs require a text version. Automated checks are limited; antivirus scanning is not configured.</p></Panel><div><State loading={query.isPending} error={query.error} retry={() => query.refetch()}/>{query.data?.length === 0 && <Empty title="A fresh start" description="Your uploaded documents will appear here. You can download or delete them at any time."/>}<div className="space-y-4">{query.data?.map(doc => <Panel key={doc.id}><div className="flex gap-3 items-start"><FileText className="text-violet-500 shrink-0" size={22}/><div className="min-w-0 flex-1"><h3 className="font-semibold break-words">{doc.filename}</h3><p className="text-xs text-slate-500 mt-1">{new Date(doc.created_at).toLocaleDateString()} · {doc.skills.length} skills extracted</p></div><Tag>Encrypted</Tag></div><ResumeSkillDemand skills={doc.skills} market={market.data} loading={market.isPending} failed={!!market.error}/><div className="flex gap-4 border-t mt-5 pt-4"><button className="text-sm flex items-center gap-2" onClick={() => download(doc)}><Download size={15}/>Download</button><button className="text-sm text-red-700 flex items-center gap-2" onClick={() => remove(doc)}><Trash2 size={15}/>Delete</button></div></Panel>)}</div></div></div><Message error={error} success={success}/></div>;
}


