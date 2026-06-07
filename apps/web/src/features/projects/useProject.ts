import { useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/api/client';
import { useApiMutation, useApiQuery } from '@/api/hooks';
import type {
  GrantProjectAccessResponse,
  ListProjectAccessResponse,
  OkResponse,
  Project,
  UpdateProjectRequest,
} from '@/api/types';
import { PROJECTS_KEY } from '@/hooks/useProjects';

/** Single-project + project-access hooks (Phase C2). */

export const projectKey = (projectId: string) => ['project', projectId] as const;
export const projectAccessKey = (projectId: string) => ['project', projectId, 'access'] as const;

export function useProject(projectId: string) {
  return useApiQuery<Project>({
    queryKey: projectKey(projectId),
    queryFn: () => apiClient.get<Project>(`/projects/${projectId}`),
  });
}

export function useUpdateProject(projectId: string) {
  const queryClient = useQueryClient();
  return useApiMutation<Project, UpdateProjectRequest>({
    mutationFn: (body) => apiClient.patch<Project>(`/projects/${projectId}`, body),
    onSuccess: (project) => {
      queryClient.setQueryData(projectKey(projectId), project);
      void queryClient.invalidateQueries({ queryKey: PROJECTS_KEY });
    },
  });
}

export function useProjectAccess(projectId: string) {
  return useApiQuery<ListProjectAccessResponse>({
    queryKey: projectAccessKey(projectId),
    queryFn: () => apiClient.get<ListProjectAccessResponse>(`/projects/${projectId}/access`),
  });
}

export function useGrantProjectAccess(projectId: string) {
  const queryClient = useQueryClient();
  return useApiMutation<GrantProjectAccessResponse, string>({
    mutationFn: (userId) =>
      apiClient.post<GrantProjectAccessResponse>(`/projects/${projectId}/access`, {
        user_id: userId,
      }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: projectAccessKey(projectId) }),
  });
}

export function useRevokeProjectAccess(projectId: string) {
  const queryClient = useQueryClient();
  return useApiMutation<OkResponse, string>({
    mutationFn: (userId) => apiClient.delete<OkResponse>(`/projects/${projectId}/access/${userId}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: projectAccessKey(projectId) }),
  });
}
