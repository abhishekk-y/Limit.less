import { useQuery } from '@tanstack/react-query';

const fetchOpportunities = async (filters: any) => {
  return [
    { id: '1', title: 'Senior Frontend Engineer', type: 'Role', matchScore: 92 },
    { id: '2', title: 'Leadership Workshop', type: 'Course', matchScore: 85 },
  ];
};

const fetchOpportunity = async (id: string) => {
  return { id, title: 'Senior Frontend Engineer', type: 'Role', matchScore: 92, description: 'Great opportunity.' };
};

export function useOpportunities(filters = {}) {
  return useQuery({
    queryKey: ['opportunities', filters],
    queryFn: () => fetchOpportunities(filters),
  });
}

export function useOpportunity(id: string) {
  return useQuery({
    queryKey: ['opportunities', id],
    queryFn: () => fetchOpportunity(id),
    enabled: !!id,
  });
}
