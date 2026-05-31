import { useQueryClient } from '@tanstack/react-query';
import { useNavigate } from '@tanstack/react-router';
import { useCallback } from 'react';
import type { CurrentUser } from '@/api/types';
import { CURRENT_USER_KEY } from '@/hooks/useCurrentUser';

/**
 * Post-authentication handler shared by login / signup / accept-invitation.
 * The backend has already set the session + CSRF cookies on the response, so we
 * just seed the `/auth/me` cache with the returned user (avoids an immediate
 * refetch and lets the shell guard pass synchronously) and route to the
 * dashboard, replacing history so Back doesn't return to the auth screen.
 */
export function useAuthSuccess() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  return useCallback(
    (user: CurrentUser) => {
      queryClient.setQueryData(CURRENT_USER_KEY, user);
      void navigate({ to: '/dashboard', replace: true });
    },
    [queryClient, navigate],
  );
}
