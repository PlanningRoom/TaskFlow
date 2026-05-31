import { apiClient } from '@/api/client';
import { useApiQuery } from '@/api/hooks';
import type { Project } from '@/api/types';

interface ListProjectsResponse {
  projects: Project[];
}

export const PROJECTS_KEY = ['projects'] as const;

/** Projects the caller can see (sidebar list + dashboard). */
export function useProjects() {
  return useApiQuery<ListProjectsResponse>({
    queryKey: PROJECTS_KEY,
    queryFn: () => apiClient.get<ListProjectsResponse>('/projects'),
  });
}
