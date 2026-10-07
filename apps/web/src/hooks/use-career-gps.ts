import { useMutation } from '@tanstack/react-query';

const computePath = async (targetRole: string) => {
  return {
    targetRole,
    steps: [
      { id: '1', type: 'skill', name: 'Learn GraphQL', duration: '2 weeks' },
      { id: '2', type: 'experience', name: 'Lead a feature module', duration: '3 months' },
    ],
    feasibilityScore: 85,
  };
};

export function useCareerGPS() {
  const mutation = useMutation({
    mutationFn: computePath,
  });

  return { computePath: mutation.mutate, pathResult: mutation.data, isComputing: mutation.isPending };
}
