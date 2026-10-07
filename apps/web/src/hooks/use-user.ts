import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

// Dummy API calls
const fetchUser = async () => {
  return { id: '1', name: 'John Doe', role: 'Engineer', department: 'Engineering' };
};

const updateUser = async (data: any) => {
  return { ...data, id: '1' };
};

export function useUser() {
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: ['user', 'me'],
    queryFn: fetchUser,
  });

  const mutation = useMutation({
    mutationFn: updateUser,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['user', 'me'] });
    },
  });

  return { ...query, updateProfile: mutation.mutate, isUpdating: mutation.isPending };
}
