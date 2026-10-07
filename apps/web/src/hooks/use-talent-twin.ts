import { useQuery } from '@tanstack/react-query';

const fetchTalentTwin = async (userId: string) => {
  return {
    userId,
    profile: {
      name: 'John Doe',
      currentRole: 'Software Engineer II',
      readinessScore: 78,
    },
    skills: [
      { name: 'React', proficiency: 4, verified: true },
      { name: 'Node.js', proficiency: 3, verified: false },
    ],
    growthAreas: ['System Design', 'Team Leadership'],
  };
};

export function useTalentTwin(userId: string) {
  return useQuery({
    queryKey: ['talent-twin', userId],
    queryFn: () => fetchTalentTwin(userId),
    enabled: !!userId,
  });
}
