'use client';
import Link from 'next/link';

export type ResumeMarket = {
  active_postings: number;
  source_refreshed_at: string | null;
  skills: {id: string; name: string; postings: number; share_percent: number; change: number | null}[];
};

export function ResumeSkillDemand({skills, market, loading, failed}: {
  skills: string[]; market?: ResumeMarket; loading: boolean; failed: boolean;
}) {
  const extracted = new Set(skills);
  const missing = market?.skills.filter(skill => skill.postings > 0 && !extracted.has(skill.id)).slice(0, 10) ?? [];
  const hasJobs = !!market?.active_postings;
  const missingText = failed ? 'Job demand could not load. Try refreshing the page.' : loading ? 'Loading job demand…' : !hasJobs ? 'Import live job listings to identify in-demand skills missing from this résumé.' : missing.length ? missing.map(skill => `${skill.name}: ${skill.share_percent}% demand · ${skill.postings} of ${market!.active_postings} listings${skill.change === null ? '' : ` · ${skill.change >= 0 ? '+' : ''}${skill.change} listings since the previous comparable snapshot`}`).join('\n') : 'No additional supported skills were found in the imported job sample.';
  return <div className="mt-4">
    <h4 className="text-sm font-semibold">Extracted skills & job demand</h4>
    <div className="mt-3 grid gap-2 sm:grid-cols-2">{skills.map(id => {
      const item = market?.skills.find(skill => skill.id === id);
      return <div key={id} className="rounded-xl border border-slate-200 p-3"><div className="flex justify-between gap-2 text-sm"><strong>{item?.name ?? id.replaceAll('_', ' ')}</strong><span className="font-semibold text-violet-700">{failed ? 'Unavailable' : loading ? '…' : hasJobs ? `${item?.share_percent ?? 0}% demand` : 'No sample yet'}</span></div><p className="mt-1 text-xs text-slate-500">{hasJobs && !failed && !loading ? `${item?.postings ?? 0} of ${market!.active_postings} job listings` : 'Based on imported live job listings'}</p>{hasJobs && !failed && !loading && <p className="mt-1 text-xs text-slate-500">{item?.change == null ? 'Increase/decrease: collecting comparable history' : `Change: ${item.change >= 0 ? '+' : ''}${item.change} listings`}</p>}</div>;
    })}</div>
    <label className="mt-4 block text-sm font-semibold">In-demand skills missing from this résumé<textarea className="journey-input !text-xs !font-normal" readOnly rows={Math.max(3, Math.min(8, missing.length))} value={missingText}/></label>
    <p className="mt-2 text-xs text-slate-500">Demand = listings mentioning the skill ÷ imported live listings. Missing means not extracted from this document; review before adding any skill. {market?.source_refreshed_at && `Sources refreshed ${new Date(market.source_refreshed_at).toLocaleString()}.`}</p>
    {!hasJobs && !loading && <Link href="/live-jobs" className="mt-2 inline-block text-xs text-violet-700 underline">Import jobs to see demand</Link>}
  </div>;
}
