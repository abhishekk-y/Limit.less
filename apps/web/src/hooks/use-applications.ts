import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

const fetchApplications = async () => {
  return [
    { id: '1', opportunityId: 'opp1', status: 'Pending', dateApplied: '2023-10-25' },
    { id: '2', opportunityId: 'opp2', status: 'Accepted', dateApplied: '2023-09-12' },
  ];
};

const applyToOpportunity = async (opportunityId: string) => {
  return { id: Math.random().toString(), opportunityId, status: 'Pending', dateApplied: new Date().toISOString() };
};

export function useApplications() {
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: ['applications'],
    queryFn: fetchApplications,
  });

  const applyMutation = useMutation({
    mutationFn: applyToOpportunity,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['applications'] });
    },
  });

  return { ...query, apply: applyMutation.mutate, isApplying: applyMutation.isPending };
}
