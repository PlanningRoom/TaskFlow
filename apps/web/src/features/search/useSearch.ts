import { useEffect, useState } from 'react';
import { apiClient } from '@/api/client';
import { useApiQuery } from '@/api/hooks';
import type { SearchResponse } from '@/api/types';

/** Debounce a fast-changing value (search box keystrokes). */
export function useDebounced<T>(value: T, delayMs = 300): T {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const id = setTimeout(() => setDebounced(value), delayMs);
    return () => clearTimeout(id);
  }, [value, delayMs]);
  return debounced;
}

/**
 * Full-text task search (Phase C7). The caller passes the raw query; this
 * debounces it and only hits `/search` once a trimmed, non-empty term settles.
 */
export function useSearch(query: string) {
  const debounced = useDebounced(query.trim(), 300);
  const result = useApiQuery<SearchResponse>({
    queryKey: ['search', debounced],
    queryFn: () => apiClient.get<SearchResponse>('/search', { query: { q: debounced } }),
    enabled: debounced.length > 0,
    staleTime: 30_000,
  });
  return { ...result, query: debounced };
}
