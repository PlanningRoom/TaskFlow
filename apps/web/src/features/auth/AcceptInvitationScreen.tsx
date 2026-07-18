import { zodResolver } from '@hookform/resolvers/zod';
import { Link } from '@tanstack/react-router';
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useIntl } from 'react-intl';
import { apiClient } from '@/api/client';
import { useApiMutation, useApiQuery } from '@/api/hooks';
import type {
  AcceptInvitationRequest,
  AcceptInvitationResponse,
  InvitationPreview,
} from '@/api/types';
import { Button } from '@/components/ui';
import { type AcceptInvitationValues, acceptInvitationSchema } from '@/forms/schemas';
import { AuthCard } from './AuthCard';
import { FormError, FormField } from './FormField';
import { useAuthSuccess } from './useAuthSuccess';

/**
 * Accept-invitation screen (DRD §8.2). `GET /auth/invitations/:token` resolves
 * the workspace name, inviter, role, and invited email up front, and tells us
 * whether a live account already exists for that email:
 *
 * - New user — display-name + password fields, "Create account & join".
 * - Existing user — no fields; accepting moves their account to the workspace.
 *
 * Expired / already-used / unknown tokens render a calm full-card state with a
 * way back to login.
 */
export function AcceptInvitationScreen({ token }: { token?: string }) {
  const intl = useIntl();
  const onAuthSuccess = useAuthSuccess();
  const [formError, setFormError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<AcceptInvitationValues>({ resolver: zodResolver(acceptInvitationSchema) });

  const preview = useApiQuery<InvitationPreview>({
    queryKey: ['invitation-preview', token],
    queryFn: () => apiClient.get<InvitationPreview>(`/auth/invitations/${token}`),
    enabled: Boolean(token),
    retry: false,
    staleTime: Number.POSITIVE_INFINITY,
  });

  const mutation = useApiMutation<AcceptInvitationResponse, AcceptInvitationRequest>({
    mutationFn: (body) => apiClient.post<AcceptInvitationResponse>('/auth/accept-invitation', body),
    onSuccess: (res) => onAuthSuccess(res.user),
    onError: (error) => {
      if (error.code === 'INVITATION_EXPIRED') {
        setFormError(intl.formatMessage({ id: 'auth.accept.expired' }));
      } else if (error.code === 'INVALID_TOKEN') {
        setFormError(intl.formatMessage({ id: 'auth.accept.invalid' }));
      } else {
        setFormError(intl.formatMessage({ id: 'auth.error.generic' }));
      }
    },
  });

  // No token, an unresolvable token, or an expired invitation: dead-end card.
  const blockingMessage = !token
    ? intl.formatMessage({ id: 'auth.accept.missingToken' })
    : preview.error
      ? intl.formatMessage({
          id: preview.error.code === 'INVALID_TOKEN' ? 'auth.accept.invalid' : 'auth.error.generic',
        })
      : preview.data?.status === 'expired'
        ? intl.formatMessage({ id: 'auth.accept.expired' })
        : null;
  if (blockingMessage) {
    return (
      <AuthCard title={intl.formatMessage({ id: 'auth.accept.title' })}>
        <FormError message={blockingMessage} />
        <p className="mt-2 text-center text-sm">
          <Link to="/login" className="text-primary hover:underline">
            {intl.formatMessage({ id: 'auth.accept.backToLogin' })}
          </Link>
        </p>
      </AuthCard>
    );
  }

  if (preview.isPending || !preview.data) {
    return (
      <AuthCard title={intl.formatMessage({ id: 'auth.accept.title' })}>
        <p className="text-center text-sm text-text-secondary" role="status">
          {intl.formatMessage({ id: 'auth.accept.loading' })}
        </p>
      </AuthCard>
    );
  }

  const { workspace_name, email, role, invited_by, existing_user } = preview.data;
  const inviterName = invited_by?.display_name ?? null;
  const invitedLine = inviterName
    ? intl.formatMessage(
        { id: 'auth.accept.invitedBy' },
        { inviter: inviterName, workspace: workspace_name },
      )
    : intl.formatMessage({ id: 'auth.accept.invitedNoInviter' }, { workspace: workspace_name });

  const onSubmit = handleSubmit((values) => {
    setFormError(null);
    mutation.mutate({
      token: token as string,
      display_name: values.displayName,
      password: values.password,
    });
  });

  const acceptExisting = () => {
    setFormError(null);
    mutation.mutate({ token: token as string });
  };

  return (
    <AuthCard title={intl.formatMessage({ id: 'auth.accept.title' })} subtitle={invitedLine}>
      <p className="mb-4 text-center text-sm text-text-secondary">
        {intl.formatMessage(
          { id: 'auth.accept.detailLine' },
          { email, role: intl.formatMessage({ id: `role.${role}` }) },
        )}
      </p>
      {existing_user ? (
        <>
          {formError ? <FormError message={formError} /> : null}
          <p className="mb-4 text-center text-sm text-text-secondary">
            {intl.formatMessage({ id: 'auth.accept.existingAccount' })}
          </p>
          <Button
            type="button"
            full
            onClick={acceptExisting}
            disabled={mutation.isPending}
            aria-busy={mutation.isPending}
          >
            {intl.formatMessage(
              { id: 'auth.accept.existingSubmit' },
              { workspace: workspace_name },
            )}
          </Button>
        </>
      ) : (
        <form onSubmit={onSubmit} noValidate>
          {formError ? <FormError message={formError} /> : null}
          <FormField
            label={intl.formatMessage({ id: 'auth.field.displayName' })}
            autoComplete="name"
            error={errors.displayName?.message}
            {...register('displayName')}
          />
          <FormField
            label={intl.formatMessage({ id: 'auth.field.password' })}
            type="password"
            autoComplete="new-password"
            error={errors.password?.message}
            {...register('password')}
          />
          <Button type="submit" full disabled={mutation.isPending} aria-busy={mutation.isPending}>
            {intl.formatMessage({ id: 'auth.accept.submit' })}
          </Button>
        </form>
      )}
    </AuthCard>
  );
}
