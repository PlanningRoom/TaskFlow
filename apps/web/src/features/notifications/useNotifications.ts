import { useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/api/client';
import { useApiMutation, useApiQuery } from '@/api/hooks';
import type {
  ListNotificationsResponse,
  Notification,
  OkResponse,
  UnreadCountResponse,
} from '@/api/types';

/** Notification hooks (Phase C6). List + unread badge + mark-read mutations. */

export const NOTIFICATIONS_KEY = ['notifications'] as const;
export const UNREAD_COUNT_KEY = ['notifications', 'unread-count'] as const;

export function useNotifications() {
  return useApiQuery<ListNotificationsResponse>({
    queryKey: NOTIFICATIONS_KEY,
    queryFn: () => apiClient.get<ListNotificationsResponse>('/notifications'),
  });
}

/** Unread count for the header bell badge. Polls periodically as a stopgap until
 * the real-time bridge (Phase H1) pushes updates. */
export function useUnreadCount() {
  return useApiQuery<UnreadCountResponse>({
    queryKey: UNREAD_COUNT_KEY,
    queryFn: () => apiClient.get<UnreadCountResponse>('/notifications/unread-count'),
    refetchInterval: 60_000,
  });
}

function invalidate(queryClient: ReturnType<typeof useQueryClient>) {
  void queryClient.invalidateQueries({ queryKey: NOTIFICATIONS_KEY });
}

export function useMarkRead() {
  const queryClient = useQueryClient();
  return useApiMutation<Notification, string>({
    mutationFn: (id) => apiClient.post<Notification>(`/notifications/${id}/read`),
    onSuccess: () => invalidate(queryClient),
  });
}

export function useMarkAllRead() {
  const queryClient = useQueryClient();
  return useApiMutation<OkResponse, void>({
    mutationFn: () => apiClient.post<OkResponse>('/notifications/mark-all-read'),
    onSuccess: () => invalidate(queryClient),
  });
}
