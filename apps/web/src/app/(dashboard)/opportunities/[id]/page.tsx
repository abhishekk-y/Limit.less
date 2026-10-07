import { OpportunitiesPage } from '@/components/journey/opportunities';
export default async function Detail({ params }: { params: Promise<{ id: string }> }) { const { id } = await params; return <OpportunitiesPage id={id}/>; }
