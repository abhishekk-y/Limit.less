export interface User {
  id: string;
  name: string;
  email: string;
  role: string;
  avatar_url?: string;
  tenant_id: string;
  tenant_type: 'individual' | 'organization' | 'institution';
  workspace_name: string;
  is_demo: boolean;
  profile: Record<string, unknown>;
}

export interface Skill {
  id: string;
  name: string;
  category: string;
}

export interface PersonSkill {
  id: string;
  skill_id: string;
  skill: Skill;
  confidence: string;
  sts_score: number;
}
