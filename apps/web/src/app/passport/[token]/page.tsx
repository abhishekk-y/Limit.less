import { PublicPassport } from '@/components/journey/learning';
export const metadata = { robots: { index: false, follow: false }, title: 'Shared Skill Passport · Limit.less' };
export default async function Page({ params }: { params: Promise<{ token: string }> }) { const { token } = await params; return <PublicPassport token={token}/>; }

