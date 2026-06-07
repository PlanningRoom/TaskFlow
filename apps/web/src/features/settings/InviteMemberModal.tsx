import { zodResolver } from '@hookform/resolvers/zod';
import { type ReactNode, useState } from 'react';
import { useForm } from 'react-hook-form';
import { useIntl } from 'react-intl';
import {
  Button,
  Dialog,
  DialogClose,
  DialogContent,
  DialogTrigger,
  FormLabel,
  Input,
  Select,
  useToast,
} from '@/components/ui';
import { FormError } from '@/features/auth/FormField';
import { type InviteMemberValues, inviteMemberSchema } from '@/forms/schemas';
import { useSendInvitation } from './useInvitations';

/** Invite Member modal (DRD §10.4): email + role (Owner is not assignable). */
export function InviteMemberModal({ trigger }: { trigger: ReactNode }) {
  const intl = useIntl();
  const toast = useToast();
  const [open, setOpen] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const mutation = useSendInvitation();

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<InviteMemberValues>({
    resolver: zodResolver(inviteMemberSchema),
    defaultValues: { role: 'member' },
  });

  const onSubmit = handleSubmit((values) => {
    setFormError(null);
    mutation.mutate(values, {
      onSuccess: () => {
        setOpen(false);
        reset({ role: 'member' });
        toast.show(intl.formatMessage({ id: 'settings.members.invited' }));
      },
      onError: (error) =>
        setFormError(
          intl.formatMessage({
            id:
              error.code === 'EMAIL_TAKEN' || error.code === 'CONFLICT'
                ? 'settings.members.inviteDuplicate'
                : 'auth.error.generic',
          }),
        ),
    });
  });

  return (
    <Dialog
      open={open}
      onOpenChange={(next) => {
        setOpen(next);
        if (!next) {
          reset({ role: 'member' });
          setFormError(null);
        }
      }}
    >
      <DialogTrigger asChild>{trigger}</DialogTrigger>
      <DialogContent title={intl.formatMessage({ id: 'settings.members.inviteTitle' })}>
        <form onSubmit={onSubmit} noValidate>
          {formError ? <FormError message={formError} /> : null}
          <div className="mb-[18px]">
            <FormLabel htmlFor="invite-email">
              {intl.formatMessage({ id: 'auth.field.email' })}
            </FormLabel>
            <Input
              id="invite-email"
              type="email"
              autoFocus
              aria-invalid={errors.email ? true : undefined}
              {...register('email')}
            />
            {errors.email ? (
              <p className="mt-1.5 text-[13px] text-semantic-error">{errors.email.message}</p>
            ) : null}
          </div>
          <div className="mb-[18px]">
            <FormLabel htmlFor="invite-role">
              {intl.formatMessage({ id: 'settings.members.role' })}
            </FormLabel>
            <Select id="invite-role" {...register('role')}>
              <option value="admin">{intl.formatMessage({ id: 'role.admin' })}</option>
              <option value="member">{intl.formatMessage({ id: 'role.member' })}</option>
              <option value="viewer">{intl.formatMessage({ id: 'role.viewer' })}</option>
            </Select>
          </div>
          <div className="mt-2 flex justify-end gap-2">
            <DialogClose asChild>
              <Button type="button" variant="ghost">
                {intl.formatMessage({ id: 'settings.cancel' })}
              </Button>
            </DialogClose>
            <Button type="submit" disabled={mutation.isPending} aria-busy={mutation.isPending}>
              {intl.formatMessage({ id: 'settings.members.sendInvite' })}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
