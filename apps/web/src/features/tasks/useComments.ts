import { useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/api/client';
import { useApiMutation, useApiQuery } from '@/api/hooks';
import type {
  Comment,
  CreateCommentRequest,
  ListCommentsResponse,
  OkResponse,
  UpdateCommentRequest,
} from '@/api/types';

/** Comment hooks (Phase C4). Chronological list + author-only edit/delete. */

export const commentsKey = (taskId: string) => ['task', taskId, 'comments'] as const;

export function useComments(taskId: string) {
  return useApiQuery<ListCommentsResponse>({
    queryKey: commentsKey(taskId),
    queryFn: () => apiClient.get<ListCommentsResponse>(`/tasks/${taskId}/comments`),
  });
}

export function useCreateComment(taskId: string) {
  const queryClient = useQueryClient();
  return useApiMutation<Comment, CreateCommentRequest>({
    mutationFn: (body) => apiClient.post<Comment>(`/tasks/${taskId}/comments`, body),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: commentsKey(taskId) });
      void queryClient.invalidateQueries({ queryKey: ['task', taskId] });
    },
  });
}

export function useUpdateComment(taskId: string) {
  const queryClient = useQueryClient();
  return useApiMutation<Comment, { commentId: string; body: UpdateCommentRequest }>({
    mutationFn: ({ commentId, body }) => apiClient.patch<Comment>(`/comments/${commentId}`, body),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: commentsKey(taskId) });
    },
  });
}

export function useDeleteComment(taskId: string) {
  const queryClient = useQueryClient();
  return useApiMutation<OkResponse, string>({
    mutationFn: (commentId) => apiClient.delete<OkResponse>(`/comments/${commentId}`),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: commentsKey(taskId) });
      void queryClient.invalidateQueries({ queryKey: ['task', taskId] });
    },
  });
}
