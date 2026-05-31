import { ApiError, apiClient } from '@/api/client';
import { useApiQuery } from '@/api/hooks';
import type { CurrentUser } from '@/api/types';

/** Query key for the authenticated user (shared so mutations can invalidate it). */
export const CURRENT_USER_KEY = ['auth', 'me'] as const;

/**
 * Load the authenticated user from `GET /auth/me` (Phase B4). A 401 means "not
 * signed in" — it's surfaced as `error` (an {@link ApiError} with status 401)
 * rather than retried, so callers/route guards can redirect to /login.
 */
export function useCurrentUser() {
  return useApiQuery<CurrentUser>({
    queryKey: CURRENT_USER_KEY,
    queryFn: () => apiClient.get<CurrentUser>('/auth/me'),
    retry: false,
    staleTime: 5 * 60_000,
  });
}

/** Narrowing helper: true when the query failed specifically with a 401. */
export function isUnauthenticated(error: unknown): boolean {
  return error instanceof ApiError && error.status === 401;
}
