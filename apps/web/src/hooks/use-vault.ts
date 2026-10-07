import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

const fetchDocuments = async () => {
  return [
    { id: '1', title: 'Resume 2023', type: 'resume', url: '#' },
    { id: '2', title: 'AWS Certification', type: 'certificate', url: '#' },
  ];
};

const uploadDocument = async (file: File) => {
  return { id: Math.random().toString(), title: file.name, type: 'other', url: '#' };
};

export function useVault() {
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: ['vault-documents'],
    queryFn: fetchDocuments,
  });

  const uploadMutation = useMutation({
    mutationFn: uploadDocument,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['vault-documents'] });
    },
  });

  return { documents: query.data, isLoading: query.isLoading, upload: uploadMutation.mutate, isUploading: uploadMutation.isPending };
}
