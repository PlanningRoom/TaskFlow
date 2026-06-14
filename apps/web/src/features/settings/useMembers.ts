import { useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/api/client';
import { useApiMutation, useApiQuery } from '@/api/hooks';
import type { ChangeRoleRequest, ListMembersResponse, Member, OkResponse } from '@/api/types';

/** Workspace member hooks (Phase C1): list, change role, remove. */

export const MEMBERS_KEY = ['members'] as const;

export function useMembers() {
  return useApiQuery<ListMembersResponse>({
    queryKey: MEMBERS_KEY,
    queryFn: () => apiClient.get<ListMembersResponse>('/workspaces/me/members'),
  });
}

export function useChangeRole() {
  const queryClient = useQueryClient();
  return useApiMutation<Member, { userId: string; role: ChangeRoleRequest['role'] }>({
    mutationFn: ({ userId, role }) =>
      apiClient.patch<Member>(`/workspaces/me/members/${userId}`, { role }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: MEMBERS_KEY }),
    meta: { errorToast: true },
  });
}

export function useRemoveMember() {
  const queryClient = useQueryClient();
  return useApiMutation<OkResponse, string>({
    mutationFn: (userId) => apiClient.delete<OkResponse>(`/workspaces/me/members/${userId}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: MEMBERS_KEY }),
    meta: { errorToast: true },
  });
}
