import { useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/api/client';
import { useApiMutation, useApiQuery } from '@/api/hooks';
import type { UpdateWorkspaceRequest, Workspace } from '@/api/types';

/** Workspace hooks (Phase C1). Read + rename (Owner/Admin). */

export const WORKSPACE_KEY = ['workspace'] as const;

export function useWorkspace() {
  return useApiQuery<Workspace>({
    queryKey: WORKSPACE_KEY,
    queryFn: () => apiClient.get<Workspace>('/workspaces/me'),
  });
}

export function useUpdateWorkspace() {
  const queryClient = useQueryClient();
  return useApiMutation<Workspace, UpdateWorkspaceRequest>({
    mutationFn: (body) => apiClient.patch<Workspace>('/workspaces/me', body),
    onSuccess: (workspace) => queryClient.setQueryData(WORKSPACE_KEY, workspace),
  });
}
