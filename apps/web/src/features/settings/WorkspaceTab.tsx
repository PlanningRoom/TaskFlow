import { zodResolver } from '@hookform/resolvers/zod';
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useIntl } from 'react-intl';
import { z } from 'zod';
import { Button, FormLabel, Input, useToast } from '@/components/ui';
import { FormError } from '@/features/auth/FormField';
import { workspaceNameSchema } from '@/forms/schemas';
import { useUpdateWorkspace, useWorkspace } from './useWorkspace';

const schema = z.object({ name: workspaceNameSchema });
type Values = z.infer<typeof schema>;

/** Workspace settings tab (DRD §8.7): rename the workspace (Owner/Admin). */
export function WorkspaceTab() {
  const intl = useIntl();
  const toast = useToast();
  const { data: workspace } = useWorkspace();
  const mutation = useUpdateWorkspace();
  const [formError, setFormError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<Values>({
    resolver: zodResolver(schema),
    values: { name: workspace?.name ?? '' },
  });

  const onSubmit = handleSubmit((values) => {
    setFormError(null);
    mutation.mutate(values, {
      onSuccess: () => toast.show(intl.formatMessage({ id: 'settings.workspace.saved' })),
      onError: () => setFormError(intl.formatMessage({ id: 'auth.error.generic' })),
    });
  });

  return (
    <form onSubmit={onSubmit} noValidate className="max-w-md">
      {formError ? <FormError message={formError} /> : null}
      <div className="mb-[18px]">
        <FormLabel htmlFor="workspace-name">
          {intl.formatMessage({ id: 'settings.workspace.name' })}
        </FormLabel>
        <Input
          id="workspace-name"
          aria-invalid={errors.name ? true : undefined}
          {...register('name')}
        />
        {errors.name ? (
          <p className="mt-1.5 text-[13px] text-semantic-error">{errors.name.message}</p>
        ) : null}
      </div>
      <Button type="submit" disabled={mutation.isPending} aria-busy={mutation.isPending}>
        {intl.formatMessage({ id: 'settings.save' })}
      </Button>
    </form>
  );
}
