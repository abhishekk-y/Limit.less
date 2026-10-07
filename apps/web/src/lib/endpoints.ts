import api from '@/lib/api';

// --- Auth ---
export async function registerUser(data: {
  email: string;
  password: string;
  name: string;
  tenant_type: 'individual' | 'organization' | 'institution';
  workspace_name?: string;
  consent: true;
}) {
  const res = await api.post('/auth/register', data);
  return res.data;
}

export async function loginUser(data: { email: string; password: string }) {
  const res = await api.post('/auth/login', data);
  return res.data;
}

export async function refreshSession(refreshToken: string) {
  const res = await api.post('/auth/refresh', { refresh_token: refreshToken });
  return res.data;
}

export async function logoutUser() {
  await api.post('/auth/logout');
}

export async function getMe() {
  const res = await api.get('/auth/me');
  return res.data;
}

// --- Talent Twin ---
export async function getTalentTwin() {
  const res = await api.get('/talent-twin');
  return res.data;
}

export async function updateProfile(data: Record<string, unknown>) {
  const res = await api.patch('/users/me', data);
  return res.data;
}

// --- Skills & Roles ---
export async function getSkills() {
  const res = await api.get('/skills');
  return res.data;
}

export async function getRoles() {
  const res = await api.get('/roles');
  return res.data;
}

// --- Vault ---
export async function uploadDocument(file: File, docType: string, consent: boolean) {
  const form = new FormData();
  form.append('file', file);
  form.append('doc_type', docType);
  form.append('consent', consent ? 'true' : 'false');
  const res = await api.post('/vault/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return res.data;
}

export async function getVaultDocuments() {
  const res = await api.get('/vault');
  return res.data;
}

export async function deleteVaultDocument(id: string) {
  await api.delete(`/vault/${id}`);
}

// --- Career GPS ---
export async function computeCareerGPS(data: { role_id: string; hours?: number; what_if_skills?: string[] }) {
  const res = await api.post('/career-gps', data);
  return res.data;
}

// --- Missions ---
export async function getMissions() {
  const res = await api.get('/missions');
  return res.data;
}

export async function createMission(data: { skill_id: string }) {
  const res = await api.post('/missions', data);
  return res.data;
}

export async function completeMission(missionId: string, evidence: { artifact_url: string; description: string; hours_spent: number }) {
  const res = await api.post(`/missions/${missionId}/complete`, evidence);
  return res.data;
}

// --- Opportunities ---
export async function getOpportunities() {
  const res = await api.get('/opportunities');
  return res.data;
}

export async function getOpportunity(id: string) {
  const res = await api.get(`/opportunities/${id}`);
  return res.data;
}

// --- Applications ---
export async function getApplications() {
  const res = await api.get('/applications');
  return res.data;
}

export async function createApplication(data: { opportunity_id: string }) {
  const res = await api.post('/applications', data);
  return res.data;
}

export async function approveApplication(applicationId: string, approval: { approved: true; resume_version: number }) {
  const res = await api.post(`/applications/${applicationId}/approve`, approval);
  return res.data;
}

export async function refreshApplication(applicationId: string) {
  const res = await api.post(`/applications/${applicationId}/refresh`);
  return res.data;
}

export async function updateApplicationOutcome(applicationId: string, data: { outcome: string; notes?: string }) {
  const res = await api.patch(`/applications/${applicationId}/outcome`, data);
  return res.data;
}
