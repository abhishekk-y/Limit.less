import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

const fetchSkills = async () => {
  return [{ id: '1', name: 'React', level: 'Advanced' }, { id: '2', name: 'TypeScript', level: 'Intermediate' }];
};

const fetchSkill = async (id: string) => {
  return { id, name: 'React', level: 'Advanced', description: 'Frontend library' };
};

const addSkill = async (data: { name: string, level: string }) => {
  return { id: Math.random().toString(), ...data };
};

export function useSkills() {
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: ['skills'],
    queryFn: fetchSkills,
  });

  const mutation = useMutation({
    mutationFn: addSkill,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['skills'] });
    },
  });

  return { ...query, addSkill: mutation.mutate, isAdding: mutation.isPending };
}

export function useSkill(id: string) {
  return useQuery({
    queryKey: ['skills', id],
    queryFn: () => fetchSkill(id),
    enabled: !!id,
  });
}
