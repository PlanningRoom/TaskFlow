import { zodResolver } from '@hookform/resolvers/zod';
import { useQueryClient } from '@tanstack/react-query';
import { useNavigate } from '@tanstack/react-router';
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useIntl } from 'react-intl';
import { z } from 'zod';
import {
  Avatar,
  Button,
  Dialog,
  DialogClose,
  DialogContent,
  DialogTrigger,
  FormLabel,
  Input,
  useToast,
} from '@/components/ui';
import { FormError } from '@/features/auth/FormField';
import {
  type ChangePasswordValues,
  changePasswordSchema,
  type DeleteAccountValues,
  deleteAccountSchema,
  displayNameSchema,
} from '@/forms/schemas';
import { useCurrentUser } from '@/hooks/useCurrentUser';
import { useChangePassword, useDeleteAccount, useUpdateProfile } from './useProfile';

/** Profile settings tab (DRD §8.10): display name, change password, delete account. */
export function ProfileTab() {
  const { data: user } = useCurrentUser();

  return (
    <div className="flex max-w-md flex-col gap-10">
      <section className="flex items-center gap-3">
        {user ? (
          <Avatar size="lg" initials={user.initials} color={user.avatar_color} id={user.id} />
        ) : null}
        <div>
          <div className="text-[13px] font-medium text-text-primary">{user?.display_name}</div>
          <div className="text-[11px] text-text-tertiary">{user?.email}</div>
        </div>
      </section>

      <DisplayNameForm initialName={user?.display_name ?? ''} />
      <ChangePasswordForm />
      <DangerZone />
    </div>
  );
}

const nameSchema = z.object({ displayName: displayNameSchema });
type NameValues = z.infer<typeof nameSchema>;

function DisplayNameForm({ initialName }: { initialName: string }) {
  const intl = useIntl();
  const toast = useToast();
  const mutation = useUpdateProfile();
  const [formError, setFormError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<NameValues>({
    resolver: zodResolver(nameSchema),
    values: { displayName: initialName },
  });

  const onSubmit = handleSubmit((values) => {
    setFormError(null);
    mutation.mutate(
      { display_name: values.displayName },
      {
        onSuccess: () => toast.show(intl.formatMessage({ id: 'settings.profile.saved' })),
        onError: () => setFormError(intl.formatMessage({ id: 'auth.error.generic' })),
      },
    );
  });

  return (
    <form onSubmit={onSubmit} noValidate>
      <h2 className="mb-3 text-[15px] font-semibold text-text-primary">
        {intl.formatMessage({ id: 'settings.profile.heading' })}
      </h2>
      {formError ? <FormError message={formError} /> : null}
      <div className="mb-[18px]">
        <FormLabel htmlFor="display-name">
          {intl.formatMessage({ id: 'auth.field.displayName' })}
        </FormLabel>
        <Input
          id="display-name"
          aria-invalid={errors.displayName ? true : undefined}
          {...register('displayName')}
        />
        {errors.displayName ? (
          <p className="mt-1.5 text-[13px] text-semantic-error">{errors.displayName.message}</p>
        ) : null}
      </div>
      <Button type="submit" disabled={mutation.isPending} aria-busy={mutation.isPending}>
        {intl.formatMessage({ id: 'settings.save' })}
      </Button>
    </form>
  );
}

function ChangePasswordForm() {
  const intl = useIntl();
  const toast = useToast();
  const mutation = useChangePassword();
  const [formError, setFormError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<ChangePasswordValues>({ resolver: zodResolver(changePasswordSchema) });

  const onSubmit = handleSubmit((values) => {
    setFormError(null);
    mutation.mutate(
      { current_password: values.currentPassword, new_password: values.newPassword },
      {
        onSuccess: () => {
          reset({ currentPassword: '', newPassword: '' });
          toast.show(intl.formatMessage({ id: 'settings.profile.passwordChanged' }));
        },
        onError: (error) =>
          setFormError(
            intl.formatMessage({
              id:
                error.status === 401 || error.code === 'INVALID_CREDENTIALS'
                  ? 'settings.profile.wrongPassword'
                  : 'auth.error.generic',
            }),
          ),
      },
    );
  });

  return (
    <form onSubmit={onSubmit} noValidate>
      <h2 className="mb-3 text-[15px] font-semibold text-text-primary">
        {intl.formatMessage({ id: 'settings.profile.passwordHeading' })}
      </h2>
      {formError ? <FormError message={formError} /> : null}
      <div className="mb-[18px]">
        <FormLabel htmlFor="current-password">
          {intl.formatMessage({ id: 'settings.profile.currentPassword' })}
        </FormLabel>
        <Input
          id="current-password"
          type="password"
          autoComplete="current-password"
          aria-invalid={errors.currentPassword ? true : undefined}
          {...register('currentPassword')}
        />
        {errors.currentPassword ? (
          <p className="mt-1.5 text-[13px] text-semantic-error">{errors.currentPassword.message}</p>
        ) : null}
      </div>
      <div className="mb-[18px]">
        <FormLabel htmlFor="new-password">
          {intl.formatMessage({ id: 'auth.field.newPassword' })}
        </FormLabel>
        <Input
          id="new-password"
          type="password"
          autoComplete="new-password"
          aria-invalid={errors.newPassword ? true : undefined}
          {...register('newPassword')}
        />
        {errors.newPassword ? (
          <p className="mt-1.5 text-[13px] text-semantic-error">{errors.newPassword.message}</p>
        ) : null}
      </div>
      <Button type="submit" disabled={mutation.isPending} aria-busy={mutation.isPending}>
        {intl.formatMessage({ id: 'settings.profile.updatePassword' })}
      </Button>
    </form>
  );
}

function DangerZone() {
  const intl = useIntl();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const mutation = useDeleteAccount();
  const [open, setOpen] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<DeleteAccountValues>({ resolver: zodResolver(deleteAccountSchema) });

  const onSubmit = handleSubmit((values) => {
    setFormError(null);
    mutation.mutate(
      { password: values.password },
      {
        onSuccess: () => {
          queryClient.clear();
          navigate({ to: '/login' });
        },
        onError: (error) =>
          setFormError(
            intl.formatMessage({
              id:
                error.status === 401 || error.code === 'INVALID_CREDENTIALS'
                  ? 'settings.profile.wrongPassword'
                  : 'auth.error.generic',
            }),
          ),
      },
    );
  });

  return (
    <section>
      <h2 className="mb-3 text-[15px] font-semibold text-semantic-error">
        {intl.formatMessage({ id: 'settings.profile.dangerHeading' })}
      </h2>
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogTrigger asChild>
          <Button type="button" variant="destructive">
            {intl.formatMessage({ id: 'settings.profile.deleteAccount' })}
          </Button>
        </DialogTrigger>
        <DialogContent title={intl.formatMessage({ id: 'settings.profile.deleteTitle' })}>
          <form onSubmit={onSubmit} noValidate>
            <p className="mb-4 text-[13px] leading-relaxed text-text-secondary">
              {intl.formatMessage({ id: 'settings.profile.deleteBody' })}
            </p>
            {formError ? <FormError message={formError} /> : null}
            <div className="mb-[18px]">
              <FormLabel htmlFor="delete-password">
                {intl.formatMessage({ id: 'settings.profile.confirmPassword' })}
              </FormLabel>
              <Input
                id="delete-password"
                type="password"
                autoComplete="current-password"
                aria-invalid={errors.password ? true : undefined}
                {...register('password')}
              />
              {errors.password ? (
                <p className="mt-1.5 text-[13px] text-semantic-error">{errors.password.message}</p>
              ) : null}
            </div>
            <div className="mt-2 flex justify-end gap-2">
              <DialogClose asChild>
                <Button type="button" variant="ghost">
                  {intl.formatMessage({ id: 'settings.cancel' })}
                </Button>
              </DialogClose>
              <Button
                type="submit"
                variant="destructive"
                disabled={mutation.isPending}
                aria-busy={mutation.isPending}
              >
                {intl.formatMessage({ id: 'settings.profile.deleteConfirm' })}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </section>
  );
}
