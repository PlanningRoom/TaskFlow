import { zodResolver } from '@hookform/resolvers/zod';
import { useNavigate } from '@tanstack/react-router';
import { type ReactNode, useId, useState } from 'react';
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
  Textarea,
  useToast,
} from '@/components/ui';
import { FormError } from '@/features/auth/FormField';
import { type CreateProjectValues, createProjectSchema } from '@/forms/schemas';
import { useCreateProject } from './useDashboard';

/**
 * Create Project modal (DRD §10.1). Self-contained: the caller supplies the
 * `trigger` element (the sidebar `+`, the dashboard empty-state button, …),
 * which Radix wires up via `DialogTrigger asChild`. On success it closes, shows
 * a toast, and routes to the new project's board. Reused across G2/G3/H2.
 */
export function CreateProjectModal({ trigger }: { trigger: ReactNode }) {
  const intl = useIntl();
  const navigate = useNavigate();
  const toast = useToast();
  const [open, setOpen] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const descriptionId = useId();
  const descriptionErrorId = `${descriptionId}-error`;

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<CreateProjectValues>({ resolver: zodResolver(createProjectSchema) });

  const mutation = useCreateProject();

  function close() {
    setOpen(false);
    setFormError(null);
    reset();
  }

  const onSubmit = handleSubmit((values) => {
    setFormError(null);
    mutation.mutate(
      { name: values.name, description: values.description?.trim() || null },
      {
        onSuccess: (project) => {
          close();
          toast.show(intl.formatMessage({ id: 'dashboard.createProject.success' }));
          void navigate({ to: '/projects/$projectId/board', params: { projectId: project.id } });
        },
        onError: () => setFormError(intl.formatMessage({ id: 'auth.error.generic' })),
      },
    );
  });

  return (
    <Dialog
      open={open}
      onOpenChange={(next) => {
        setOpen(next);
        if (!next) {
          setFormError(null);
          reset();
        }
      }}
    >
      <DialogTrigger asChild>{trigger}</DialogTrigger>
      <DialogContent title={intl.formatMessage({ id: 'dashboard.createProject.title' })}>
        <form onSubmit={onSubmit} noValidate>
          {formError ? <FormError message={formError} /> : null}

          <div className="mb-[18px]">
            <FormLabel htmlFor={`${descriptionId}-name`}>
              {intl.formatMessage({ id: 'dashboard.createProject.name' })}
            </FormLabel>
            <Input
              id={`${descriptionId}-name`}
              autoFocus
              aria-invalid={errors.name ? true : undefined}
              aria-describedby={errors.name ? `${descriptionId}-name-error` : undefined}
              {...register('name')}
            />
            {errors.name ? (
              <p
                id={`${descriptionId}-name-error`}
                className="mt-1.5 text-[13px] text-semantic-error"
              >
                {errors.name.message}
              </p>
            ) : null}
          </div>

          <div className="mb-[18px]">
            <FormLabel htmlFor={descriptionId}>
              {intl.formatMessage({ id: 'dashboard.createProject.description' })}
            </FormLabel>
            <Textarea
              id={descriptionId}
              aria-invalid={errors.description ? true : undefined}
              aria-describedby={errors.description ? descriptionErrorId : undefined}
              {...register('description')}
            />
            {errors.description ? (
              <p id={descriptionErrorId} className="mt-1.5 text-[13px] text-semantic-error">
                {errors.description.message}
              </p>
            ) : null}
          </div>

          <div className="mt-2 flex justify-end gap-2">
            <DialogClose asChild>
              <Button type="button" variant="ghost">
                {intl.formatMessage({ id: 'dashboard.createProject.cancel' })}
              </Button>
            </DialogClose>
            <Button type="submit" disabled={mutation.isPending} aria-busy={mutation.isPending}>
              {intl.formatMessage({ id: 'dashboard.createProject.submit' })}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
