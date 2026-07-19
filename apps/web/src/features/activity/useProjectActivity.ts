import { apiClient } from '@/api/client';
import { useApiQuery } from '@/api/hooks';
import type { ListActivityResponse } from '@/api/types';

/**
 * Project-scope activity feed (PRD §14.2 / C5), first page only — mirrors the
 * dashboard's workspace-scope hook. The `['activity', …]` key prefix keeps it
 * refreshed by the realtime dispatcher's activity invalidation.
 */
export function useProjectActivity(projectId: string, enabled = true) {
  return useApiQuery<ListActivityResponse>({
    queryKey: ['activity', 'project', projectId],
    queryFn: () =>
      apiClient.get<ListActivityResponse>('/activity', { query: { project_id: projectId } }),
    enabled,
  });
}
