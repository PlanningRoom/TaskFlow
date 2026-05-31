import { zodResolver } from '@hookform/resolvers/zod';
import { Link } from '@tanstack/react-router';
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useIntl } from 'react-intl';
import { apiClient } from '@/api/client';
import { useApiMutation } from '@/api/hooks';
import type { SignupRequest, SignupResponse } from '@/api/types';
import { Button } from '@/components/ui';
import { type SignupValues, signupSchema } from '@/forms/schemas';
import { AuthCard } from './AuthCard';
import { FormError, FormField } from './FormField';
import { useAuthSuccess } from './useAuthSuccess';

/**
 * Signup screen (DRD §8.1, PRD §3.1). Creates a workspace + Owner via
 * `POST /auth/signup`. A duplicate email comes back 409 `EMAIL_TAKEN` and is
 * surfaced on the email field; other failures show a form-level message.
 */
export function SignupScreen() {
  const intl = useIntl();
  const onAuthSuccess = useAuthSuccess();
  const [formError, setFormError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    setError,
    formState: { errors },
  } = useForm<SignupValues>({ resolver: zodResolver(signupSchema) });

  const mutation = useApiMutation<SignupResponse, SignupRequest>({
    mutationFn: (body) => apiClient.post<SignupResponse>('/auth/signup', body),
    onSuccess: (res) => onAuthSuccess(res.user),
    onError: (error) => {
      if (error.code === 'EMAIL_TAKEN') {
        setError('email', { message: intl.formatMessage({ id: 'auth.signup.emailTaken' }) });
        return;
      }
      setFormError(intl.formatMessage({ id: 'auth.error.generic' }));
    },
  });

  const onSubmit = handleSubmit((values) => {
    setFormError(null);
    mutation.mutate({
      display_name: values.displayName,
      email: values.email,
      password: values.password,
      workspace_name: values.workspaceName,
    });
  });

  return (
    <AuthCard
      title={intl.formatMessage({ id: 'auth.signup.title' })}
      subtitle={intl.formatMessage({ id: 'auth.signup.subtitle' })}
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
          label={intl.formatMessage({ id: 'auth.field.email' })}
          type="email"
          autoComplete="email"
          error={errors.email?.message}
          {...register('email')}
        />
        <FormField
          label={intl.formatMessage({ id: 'auth.field.password' })}
          type="password"
          autoComplete="new-password"
          error={errors.password?.message}
          {...register('password')}
        />
        <FormField
          label={intl.formatMessage({ id: 'auth.field.workspaceName' })}
          autoComplete="organization"
          error={errors.workspaceName?.message}
          {...register('workspaceName')}
        />
        <Button type="submit" full disabled={mutation.isPending} aria-busy={mutation.isPending}>
          {intl.formatMessage({ id: 'auth.signup.submit' })}
        </Button>
      </form>
      <p className="mt-5 text-center text-sm text-text-secondary">
        {intl.formatMessage({ id: 'auth.signup.haveAccount' })}{' '}
        <Link to="/login" className="text-primary hover:underline">
          {intl.formatMessage({ id: 'auth.signup.loginLink' })}
        </Link>
      </p>
    </AuthCard>
  );
}
