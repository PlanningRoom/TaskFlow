import { zodResolver } from '@hookform/resolvers/zod';
import { Link } from '@tanstack/react-router';
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useIntl } from 'react-intl';
import { apiClient } from '@/api/client';
import { useApiMutation } from '@/api/hooks';
import type { OkResponse, PasswordResetRequest } from '@/api/types';
import { Button } from '@/components/ui';
import { type PasswordResetRequestValues, passwordResetRequestSchema } from '@/forms/schemas';
import { AuthCard } from './AuthCard';
import { FormError, FormField } from './FormField';

/**
 * Password-reset request screen. Posts an email to
 * `POST /auth/password-reset/request`, which always returns 200 (no account
 * enumeration). On success we show the same neutral confirmation regardless of
 * whether the email exists.
 */
export function PasswordResetRequestScreen() {
  const intl = useIntl();
  const [sent, setSent] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<PasswordResetRequestValues>({ resolver: zodResolver(passwordResetRequestSchema) });

  const mutation = useApiMutation<OkResponse, PasswordResetRequest>({
    mutationFn: (body) => apiClient.post<OkResponse>('/auth/password-reset/request', body),
    onSuccess: () => setSent(true),
    onError: () => setFormError(intl.formatMessage({ id: 'auth.error.generic' })),
  });

  const onSubmit = handleSubmit((values) => {
    setFormError(null);
    mutation.mutate({ email: values.email });
  });

  if (sent) {
    return (
      <AuthCard
        title={intl.formatMessage({ id: 'auth.reset.sentTitle' })}
        subtitle={intl.formatMessage({ id: 'auth.reset.sent' })}
      >
        <p className="text-center text-sm">
          <Link to="/login" className="text-primary hover:underline">
            {intl.formatMessage({ id: 'auth.reset.backToLogin' })}
          </Link>
        </p>
      </AuthCard>
    );
  }

  return (
    <AuthCard
      title={intl.formatMessage({ id: 'auth.reset.title' })}
      subtitle={intl.formatMessage({ id: 'auth.reset.subtitle' })}
    >
      <form onSubmit={onSubmit} noValidate>
        {formError ? <FormError message={formError} /> : null}
        <FormField
          label={intl.formatMessage({ id: 'auth.field.email' })}
          type="email"
          autoComplete="email"
          error={errors.email?.message}
          {...register('email')}
        />
        <Button type="submit" full disabled={mutation.isPending} aria-busy={mutation.isPending}>
          {intl.formatMessage({ id: 'auth.reset.submit' })}
        </Button>
      </form>
      <p className="mt-5 text-center text-sm">
        <Link to="/login" className="text-primary hover:underline">
          {intl.formatMessage({ id: 'auth.reset.backToLogin' })}
        </Link>
      </p>
    </AuthCard>
  );
}
