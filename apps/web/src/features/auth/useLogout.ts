import { useQueryClient } from '@tanstack/react-query';
import { useNavigate } from '@tanstack/react-router';
import { apiClient } from '@/api/client';
import { useApiMutation } from '@/api/hooks';
import type { OkResponse } from '@/api/types';

/**
 * Sign out (Phase B4 — `POST /auth/logout`): deletes the session server-side,
 * then clears the entire query cache and returns to `/login`. Mirrors the
 * delete-account teardown in `ProfileTab` so no stale authed data lingers.
 */
export function useLogout() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  return useApiMutation<OkResponse, void>({
    mutationFn: () => apiClient.post<OkResponse>('/auth/logout'),
    onSuccess: () => {
      queryClient.clear();
      navigate({ to: '/login' });
    },
  });
}
