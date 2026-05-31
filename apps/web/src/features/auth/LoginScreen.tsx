import { zodResolver } from '@hookform/resolvers/zod';
import { Link } from '@tanstack/react-router';
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useIntl } from 'react-intl';
import { apiClient } from '@/api/client';
import { useApiMutation } from '@/api/hooks';
import type { LoginRequest, LoginResponse } from '@/api/types';
import { Button } from '@/components/ui';
import { type LoginValues, loginSchema } from '@/forms/schemas';
import { AuthCard } from './AuthCard';
import { FormError, FormField } from './FormField';
import { useAuthSuccess } from './useAuthSuccess';

/** Login screen (DRD §8.1). Email + password → `POST /auth/login`. */
export function LoginScreen() {
  const intl = useIntl();
  const onAuthSuccess = useAuthSuccess();
  const [formError, setFormError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginValues>({ resolver: zodResolver(loginSchema) });

  const mutation = useApiMutation<LoginResponse, LoginRequest>({
    mutationFn: (body) => apiClient.post<LoginResponse>('/auth/login', body),
    onSuccess: (res) => onAuthSuccess(res.user),
    onError: (error) =>
      setFormError(
        intl.formatMessage({
          id: error.status === 401 ? 'auth.login.invalidCredentials' : 'auth.error.generic',
        }),
      ),
  });

  const onSubmit = handleSubmit((values) => {
    setFormError(null);
    mutation.mutate({ email: values.email, password: values.password });
  });

  return (
    <AuthCard
      title={intl.formatMessage({ id: 'auth.login.title' })}
      subtitle={intl.formatMessage({ id: 'auth.login.subtitle' })}
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
        <FormField
          label={intl.formatMessage({ id: 'auth.field.password' })}
          type="password"
          autoComplete="current-password"
          error={errors.password?.message}
          {...register('password')}
        />
        <Button type="submit" full disabled={mutation.isPending} aria-busy={mutation.isPending}>
          {intl.formatMessage({ id: 'auth.login.submit' })}
        </Button>
      </form>
      <p className="mt-5 text-center text-sm">
        <Link to="/forgot-password" className="text-primary hover:underline">
          {intl.formatMessage({ id: 'auth.login.forgotPassword' })}
        </Link>
      </p>
      <p className="mt-2 text-center text-sm text-text-secondary">
        {intl.formatMessage({ id: 'auth.login.noAccount' })}{' '}
        <Link to="/signup" className="text-primary hover:underline">
          {intl.formatMessage({ id: 'auth.login.signupLink' })}
        </Link>
      </p>
    </AuthCard>
  );
}
