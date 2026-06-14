import { MutationCache, QueryClient } from '@tanstack/react-query';
import { notifyMutationError } from '@/lib/mutationErrorToast';

/**
 * Single application-wide TanStack Query client (ADR 053). Defaults are
 * conservative for now; per-query tuning lands with the screens that consume
 * the API (Part G). Retries are disabled by default so that 4xx error
 * envelopes (ADR 043) surface immediately rather than being retried.
 *
 * The MutationCache fires a standardized error toast (DRD §18.2) for any
 * mutation that opts in with `meta: { errorToast: true }` — used by mutations
 * that would otherwise fail silently (board status rollback, member/label admin
 * actions). Inline-error forms simply omit the meta. The toast is surfaced via
 * the {@link notifyMutationError} bridge so this module stays React-free.
 */
export const queryClient = new QueryClient({
  mutationCache: new MutationCache({
    onError: (_error, _variables, _context, mutation) => {
      if (mutation.meta?.errorToast) notifyMutationError();
    },
  }),
  defaultOptions: {
    queries: {
      retry: false,
      refetchOnWindowFocus: false,
      staleTime: 30_000,
    },
  },
});
