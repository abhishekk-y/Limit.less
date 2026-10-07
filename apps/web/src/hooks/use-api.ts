'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import * as endpoints from '@/lib/endpoints';

// --- Talent Twin ---
export function useTalentTwin() {
  return useQuery({
    queryKey: ['talent-twin'],
    queryFn: endpoints.getTalentTwin,
  });
}

// --- Skills & Roles ---
export function useSkills() {
  return useQuery({
    queryKey: ['skills'],
    queryFn: endpoints.getSkills,
  });
}

export function useRoles() {
  return useQuery({
    queryKey: ['roles'],
    queryFn: endpoints.getRoles,
  });
}

// --- Vault ---
export function useVaultDocuments() {
  return useQuery({
    queryKey: ['vault'],
    queryFn: endpoints.getVaultDocuments,
  });
}

export function useUploadDocument() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ file, docType, consent }: { file: File; docType: string; consent: boolean }) =>
      endpoints.uploadDocument(file, docType, consent),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['vault'] });
      qc.invalidateQueries({ queryKey: ['talent-twin'] });
    },
  });
}

export function useDeleteDocument() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => endpoints.deleteVaultDocument(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['vault'] }),
  });
}

// --- Career GPS ---
export function useCareerGPS() {
  return useMutation({
    mutationFn: (data: { role_id: string; hours?: number; what_if_skills?: string[] }) =>
      endpoints.computeCareerGPS(data),
  });
}

// --- Missions ---
export function useMissions() {
  return useQuery({
    queryKey: ['missions'],
    queryFn: endpoints.getMissions,
  });
}

export function useCreateMission() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: { skill_id: string }) =>
      endpoints.createMission(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['missions'] }),
  });
}

export function useCompleteMission() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ missionId, evidence }: { missionId: string; evidence: { artifact_url: string; description: string; hours_spent: number } }) =>
      endpoints.completeMission(missionId, evidence),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['missions'] });
      qc.invalidateQueries({ queryKey: ['talent-twin'] });
    },
  });
}

// --- Opportunities ---
export function useOpportunities() {
  return useQuery({
    queryKey: ['opportunities'],
    queryFn: endpoints.getOpportunities,
  });
}

export function useOpportunity(id: string) {
  return useQuery({
    queryKey: ['opportunities', id],
    queryFn: () => endpoints.getOpportunity(id),
    enabled: !!id,
  });
}

// --- Applications ---
export function useApplications() {
  return useQuery({
    queryKey: ['applications'],
    queryFn: endpoints.getApplications,
  });
}

export function useCreateApplication() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: { opportunity_id: string }) => endpoints.createApplication(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['applications'] });
      qc.invalidateQueries({ queryKey: ['opportunities'] });
    },
  });
}

export function useApproveApplication() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, approved, resume_version }: { id: string; approved: true; resume_version: number }) => endpoints.approveApplication(id, { approved, resume_version }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['applications'] }),
  });
}
