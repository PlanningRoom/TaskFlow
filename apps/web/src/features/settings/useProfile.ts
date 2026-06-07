import { useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/api/client';
import { useApiMutation } from '@/api/hooks';
import type {
  ChangePasswordRequest,
  CurrentUser,
  DeleteAccountRequest,
  OkResponse,
  UpdateProfileRequest,
} from '@/api/types';
import { CURRENT_USER_KEY } from '@/hooks/useCurrentUser';

/** Profile hooks (Phase B4): display-name, change-password, delete-account. */

export function useUpdateProfile() {
  const queryClient = useQueryClient();
  return useApiMutation<CurrentUser, UpdateProfileRequest>({
    mutationFn: (body) => apiClient.patch<CurrentUser>('/auth/me', body),
    onSuccess: (user) => queryClient.setQueryData(CURRENT_USER_KEY, user),
  });
}

export function useChangePassword() {
  return useApiMutation<OkResponse, ChangePasswordRequest>({
    mutationFn: (body) => apiClient.post<OkResponse>('/auth/change-password', body),
  });
}

export function useDeleteAccount() {
  return useApiMutation<OkResponse, DeleteAccountRequest>({
    mutationFn: (body) => apiClient.delete<OkResponse>('/auth/me', body),
  });
}
