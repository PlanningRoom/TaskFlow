import { zodResolver } from '@hookform/resolvers/zod';
import { Link } from '@tanstack/react-router';
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useIntl } from 'react-intl';
import { apiClient } from '@/api/client';
import { useApiMutation } from '@/api/hooks';
import type { AcceptInvitationRequest, AcceptInvitationResponse } from '@/api/types';
import { Button } from '@/components/ui';
import { type AcceptInvitationValues, acceptInvitationSchema } from '@/forms/schemas';
import { AuthCard } from './AuthCard';
import { FormError, FormField } from './FormField';
import { useAuthSuccess } from './useAuthSuccess';

/**
 * Accept-invitation screen (DRD §8.2), built as a "blind" accept form: the
 * backend exposes no invitation-preview endpoint, so we can't show the
 * workspace/role/inviter or branch new-vs-existing up front. We collect a
 * display name + password and submit the token; the backend resolves existing
 * vs new user internally (existing users keep their details and just switch
 * workspace). Expired / already-used tokens render a calm full-card state.
 */
export function AcceptInvitationScreen({ token }: { token?: string }) {
  const intl = useIntl();
  const onAuthSuccess = useAuthSuccess();
  const [tokenError, setTokenError] = useState<string | null>(null);
  const [formError, setFormError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<AcceptInvitationValues>({ resolver: zodResolver(acceptInvitationSchema) });

  const mutation = useApiMutation<AcceptInvitationResponse, AcceptInvitationRequest>({
    mutationFn: (body) => apiClient.post<AcceptInvitationResponse>('/auth/accept-invitation', body),
    onSuccess: (res) => onAuthSuccess(res.user),
    onError: (error) => {
      if (error.code === 'INVITATION_EXPIRED') {
        setTokenError(intl.formatMessage({ id: 'auth.accept.expired' }));
      } else if (error.code === 'INVALID_TOKEN') {
        setTokenError(intl.formatMessage({ id: 'auth.accept.invalid' }));
      } else {
        setFormError(intl.formatMessage({ id: 'auth.error.generic' }));
      }
    },
  });

  // No token in the URL, or the token was rejected: dead-end with a way back.
  const blockingMessage = !token
    ? intl.formatMessage({ id: 'auth.accept.missingToken' })
    : tokenError;
  if (!token || blockingMessage) {
    return (
      <AuthCard title={intl.formatMessage({ id: 'auth.accept.title' })}>
        <FormError message={blockingMessage ?? intl.formatMessage({ id: 'auth.accept.invalid' })} />
        <p className="mt-2 text-center text-sm">
          <Link to="/login" className="text-primary hover:underline">
            {intl.formatMessage({ id: 'auth.accept.backToLogin' })}
          </Link>
        </p>
      </AuthCard>
    );
  }

  const onSubmit = handleSubmit((values) => {
    setFormError(null);
    mutation.mutate({
      token,
      display_name: values.displayName,
      password: values.password,
    });
  });

  return (
    <AuthCard
      title={intl.formatMessage({ id: 'auth.accept.title' })}
      subtitle={intl.formatMessage({ id: 'auth.accept.subtitle' })}
    >
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
    </AuthCard>
  );
}
