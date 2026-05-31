import { zodResolver } from '@hookform/resolvers/zod';
import { Link } from '@tanstack/react-router';
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useIntl } from 'react-intl';
import { apiClient } from '@/api/client';
import { useApiMutation } from '@/api/hooks';
import type { OkResponse, PasswordResetConfirm } from '@/api/types';
import { Button } from '@/components/ui';
import { type PasswordResetConfirmValues, passwordResetConfirmSchema } from '@/forms/schemas';
import { AuthCard } from './AuthCard';
import { FormError, FormField } from './FormField';

/**
 * Password-reset confirm screen, reached from the emailed link
 * `/reset-password?token=…` (token arrives via the query string). Submits to
 * `POST /auth/password-reset/confirm`; an invalid/expired/used token returns
 * 400 `INVALID_TOKEN` and we offer a path to request a fresh link. On success
 * the backend has revoked all sessions, so we send the user to log in afresh.
 */
export function PasswordResetConfirmScreen({ token }: { token?: string }) {
  const intl = useIntl();
  const [done, setDone] = useState(false);
  const [tokenError, setTokenError] = useState<string | null>(null);
  const [formError, setFormError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<PasswordResetConfirmValues>({ resolver: zodResolver(passwordResetConfirmSchema) });

  const mutation = useApiMutation<OkResponse, PasswordResetConfirm>({
    mutationFn: (body) => apiClient.post<OkResponse>('/auth/password-reset/confirm', body),
    onSuccess: () => setDone(true),
    onError: (error) => {
      if (error.code === 'INVALID_TOKEN') {
        setTokenError(intl.formatMessage({ id: 'auth.newPassword.invalidToken' }));
      } else {
        setFormError(intl.formatMessage({ id: 'auth.error.generic' }));
      }
    },
  });

  if (done) {
    return (
      <AuthCard
        title={intl.formatMessage({ id: 'auth.newPassword.doneTitle' })}
        subtitle={intl.formatMessage({ id: 'auth.newPassword.done' })}
      >
        <p className="text-center text-sm">
          <Link to="/login" className="text-primary hover:underline">
            {intl.formatMessage({ id: 'auth.newPassword.loginLink' })}
          </Link>
        </p>
      </AuthCard>
    );
  }

  const blockingMessage = !token
    ? intl.formatMessage({ id: 'auth.newPassword.missingToken' })
    : tokenError;
  if (!token || blockingMessage) {
    return (
      <AuthCard title={intl.formatMessage({ id: 'auth.newPassword.title' })}>
        <FormError
          message={blockingMessage ?? intl.formatMessage({ id: 'auth.newPassword.invalidToken' })}
        />
        <p className="mt-2 text-center text-sm">
          <Link to="/forgot-password" className="text-primary hover:underline">
            {intl.formatMessage({ id: 'auth.newPassword.requestNew' })}
          </Link>
        </p>
      </AuthCard>
    );
  }

  const onSubmit = handleSubmit((values) => {
    setFormError(null);
    mutation.mutate({ token, new_password: values.newPassword });
  });

  return (
    <AuthCard
      title={intl.formatMessage({ id: 'auth.newPassword.title' })}
      subtitle={intl.formatMessage({ id: 'auth.newPassword.subtitle' })}
    >
      <form onSubmit={onSubmit} noValidate>
        {formError ? <FormError message={formError} /> : null}
        <FormField
          label={intl.formatMessage({ id: 'auth.field.newPassword' })}
          type="password"
          autoComplete="new-password"
          error={errors.newPassword?.message}
          {...register('newPassword')}
        />
        <FormField
          label={intl.formatMessage({ id: 'auth.field.confirmPassword' })}
          type="password"
          autoComplete="new-password"
          error={errors.confirmPassword?.message}
          {...register('confirmPassword')}
        />
        <Button type="submit" full disabled={mutation.isPending} aria-busy={mutation.isPending}>
          {intl.formatMessage({ id: 'auth.newPassword.submit' })}
        </Button>
      </form>
    </AuthCard>
  );
}
