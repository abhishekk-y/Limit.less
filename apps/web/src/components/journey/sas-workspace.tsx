'use client';
import { useState } from 'react';
import Link from 'next/link';
import api from '@/lib/api';
import { Panel, Message, useResource, errorMessage } from './shared';
export function SasWorkspace() {
 const state = useResource<{url:string; configured:boolean; execution_verified:boolean; programs:string[]}>('/sas/workspace');
 const [url,setUrl]=useState(''); const [error,setError]=useState(''); const [saved,setSaved]=useState('');
 return <Panel className="mb-6"><p className="text-xs font-semibold text-violet-700">SAS Viya for Learners</p><h2 className="mt-1 text-lg font-semibold">Your SAS workspace in Limit.less</h2><p className="mt-2 text-sm text-slate-500">Open your SAS session, run the prepared analysis programs, and explore the recorded aggregate demonstration in the dashboard. Workspace launch is available; remote execution and verified result sync need your actual SAS environment.</p><Message error={error} success={saved}/><form className="mt-4 flex flex-wrap gap-3" onSubmit={async e=>{e.preventDefault();setError('');try{await api.put('/sas/workspace',{url});await state.refetch();setSaved('SAS workspace address saved.');}catch(e){setError(errorMessage(e));}}}><label className="grow text-sm">SAS workspace URL<input type="url" required className="journey-input" placeholder={state.data?.url || 'https://vle.sas.com/vfl'} value={url} onChange={e=>setUrl(e.target.value)}/></label><button className="btn-secondary self-end">Save workspace</button></form><div className="mt-4 flex flex-wrap gap-3"><a href={state.data?.url || 'https://vle.sas.com/vfl'} target="_blank" rel="noreferrer" className="btn-primary">Open SAS Viya for Learners</a><Link href="/sas-research" className="btn-secondary">Analysis workflow & evidence</Link><Link href="/opportunities" className="btn-secondary">Demo application flow</Link></div><p className="mt-3 text-xs text-slate-500">SAS execution: not verified. Demo applications are labelled and never sent to employers.</p></Panel>;
}
