import { redirect } from 'next/navigation';

// Keep the old URL working while directing users to the evidence-backed page.
// This replaces the former demo-data dashboard, which displayed unverified claims.
export default function LegacyHackathonInsightsPage() {
  redirect('/sas-research');
}
