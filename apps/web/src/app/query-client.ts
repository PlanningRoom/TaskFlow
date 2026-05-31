import { QueryClient } from '@tanstack/react-query';

/**
 * Single application-wide TanStack Query client (ADR 053). Defaults are
 * conservative for now; per-query tuning lands with the screens that consume
 * the API (Part G). Retries are disabled by default so that 4xx error
 * envelopes (ADR 043) surface immediately rather than being retried.
 */
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
      refetchOnWindowFocus: false,
      staleTime: 30_000,
    },
  },
});
