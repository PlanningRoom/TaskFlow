import {
  type UseMutationOptions,
  type UseMutationResult,
  type UseQueryOptions,
  type UseQueryResult,
  useMutation,
  useQuery,
} from '@tanstack/react-query';
import type { ApiError } from './client';

/**
 * Thin wrappers over TanStack Query (ADR 053) that fix the error type to
 * {@link ApiError} so screens get the ADR 043 `code`/`fields` without casting.
 * `queryFn`/`mutationFn` should call `apiClient`; errors propagate as ApiError.
 */

export function useApiQuery<TData>(
  options: UseQueryOptions<TData, ApiError>,
): UseQueryResult<TData, ApiError> {
  return useQuery<TData, ApiError>(options);
}

export function useApiMutation<TData, TVariables = void>(
  options: UseMutationOptions<TData, ApiError, TVariables>,
): UseMutationResult<TData, ApiError, TVariables> {
  return useMutation<TData, ApiError, TVariables>(options);
}
