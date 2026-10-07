import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

const fetchMissions = async () => {
  return [
    { id: '1', title: 'Onboarding Quest', progress: 100, status: 'completed' },
    { id: '2', title: 'Cloud Native Pioneer', progress: 40, status: 'in-progress' },
  ];
};

const completeMission = async (missionId: string) => {
  return { id: missionId, progress: 100, status: 'completed' };
};

export function useMissions() {
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: ['missions'],
    queryFn: fetchMissions,
  });

  const completeMutation = useMutation({
    mutationFn: completeMission,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['missions'] });
    },
  });

  return { missions: query.data, isLoading: query.isLoading, complete: completeMutation.mutate };
}
