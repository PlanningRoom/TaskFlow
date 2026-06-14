import { useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/api/client';
import { useApiMutation, useApiQuery } from '@/api/hooks';
import type {
  ListInvitationsResponse,
  ResendInvitationResponse,
  SendInvitationRequest,
  SendInvitationResponse,
} from '@/api/types';

/** Invitation hooks (Phase C1): list, send, resend. */

export const INVITATIONS_KEY = ['invitations'] as const;

export function useInvitations() {
  return useApiQuery<ListInvitationsResponse>({
    queryKey: INVITATIONS_KEY,
    queryFn: () => apiClient.get<ListInvitationsResponse>('/workspaces/me/invitations'),
  });
}

export function useSendInvitation() {
  const queryClient = useQueryClient();
  return useApiMutation<SendInvitationResponse, SendInvitationRequest>({
    mutationFn: (body) =>
      apiClient.post<SendInvitationResponse>('/workspaces/me/invitations', body),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: INVITATIONS_KEY }),
  });
}

export function useResendInvitation() {
  const queryClient = useQueryClient();
  return useApiMutation<ResendInvitationResponse, string>({
    mutationFn: (id) =>
      apiClient.post<ResendInvitationResponse>(`/workspaces/me/invitations/${id}/resend`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: INVITATIONS_KEY }),
    meta: { errorToast: true },
  });
}
