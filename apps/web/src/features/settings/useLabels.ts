import { useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/api/client';
import { useApiMutation, useApiQuery } from '@/api/hooks';
import type {
  CreateLabelRequest,
  Label,
  ListLabelsResponse,
  OkResponse,
  UpdateLabelRequest,
} from '@/api/types';

/** Label hooks (Phase C1): workspace-wide label CRUD. */

export const LABELS_KEY = ['labels'] as const;

export function useLabels() {
  return useApiQuery<ListLabelsResponse>({
    queryKey: LABELS_KEY,
    queryFn: () => apiClient.get<ListLabelsResponse>('/labels'),
  });
}

export function useCreateLabel() {
  const queryClient = useQueryClient();
  return useApiMutation<Label, CreateLabelRequest>({
    mutationFn: (body) => apiClient.post<Label>('/labels', body),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: LABELS_KEY }),
  });
}

export function useUpdateLabel() {
  const queryClient = useQueryClient();
  return useApiMutation<Label, { labelId: string; body: UpdateLabelRequest }>({
    mutationFn: ({ labelId, body }) => apiClient.patch<Label>(`/labels/${labelId}`, body),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: LABELS_KEY }),
  });
}

export function useDeleteLabel() {
  const queryClient = useQueryClient();
  return useApiMutation<OkResponse, string>({
    mutationFn: (labelId) => apiClient.delete<OkResponse>(`/labels/${labelId}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: LABELS_KEY }),
  });
}
