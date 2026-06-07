import { zodResolver } from '@hookform/resolvers/zod';
import { type ReactNode, useState } from 'react';
import { useForm } from 'react-hook-form';
import { useIntl } from 'react-intl';
import type { Label } from '@/api/types';
import {
  Button,
  Dialog,
  DialogClose,
  DialogContent,
  DialogTrigger,
  FormLabel,
  Input,
  LabelChip,
  type LabelColor,
  useToast,
} from '@/components/ui';
import { FormError } from '@/features/auth/FormField';
import { type LabelValues, labelSchema } from '@/forms/schemas';
import { cn } from '@/lib/cn';
import { useCreateLabel, useUpdateLabel } from './useLabels';

const PALETTE: LabelColor[] = ['blue', 'green', 'red', 'purple', 'amber', 'pink', 'cyan', 'orange'];

/** Create/Edit Label modal (DRD §10.6/§10.7): name + palette swatch + live preview. */
export function LabelModal({ trigger, label }: { trigger: ReactNode; label?: Label }) {
  const intl = useIntl();
  const toast = useToast();
  const [open, setOpen] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const create = useCreateLabel();
  const update = useUpdateLabel();
  const editing = Boolean(label);

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    reset,
    formState: { errors },
  } = useForm<LabelValues>({
    resolver: zodResolver(labelSchema),
    defaultValues: { name: label?.name ?? '', color: label?.color ?? 'blue' },
  });

  const name = watch('name');
  const color = watch('color');

  function close() {
    setOpen(false);
    setFormError(null);
    reset({ name: label?.name ?? '', color: label?.color ?? 'blue' });
  }

  const onSubmit = handleSubmit((values) => {
    setFormError(null);
    const onSuccess = () => {
      close();
      toast.show(intl.formatMessage({ id: 'settings.labels.saved' }));
    };
    const onError = () => setFormError(intl.formatMessage({ id: 'auth.error.generic' }));
    if (label) update.mutate({ labelId: label.id, body: values }, { onSuccess, onError });
    else create.mutate(values, { onSuccess, onError });
  });

  const pending = create.isPending || update.isPending;

  return (
    <Dialog open={open} onOpenChange={(next) => (next ? setOpen(true) : close())}>
      <DialogTrigger asChild>{trigger}</DialogTrigger>
      <DialogContent
        title={intl.formatMessage({
          id: editing ? 'settings.labels.editTitle' : 'settings.labels.createTitle',
        })}
      >
        <form onSubmit={onSubmit} noValidate>
          {formError ? <FormError message={formError} /> : null}
          <div className="mb-[18px]">
            <FormLabel htmlFor="label-name">
              {intl.formatMessage({ id: 'settings.labels.name' })}
            </FormLabel>
            <Input
              id="label-name"
              autoFocus
              aria-invalid={errors.name ? true : undefined}
              {...register('name')}
            />
            {errors.name ? (
              <p className="mt-1.5 text-[13px] text-semantic-error">{errors.name.message}</p>
            ) : null}
          </div>
          <div className="mb-[18px]">
            <FormLabel>{intl.formatMessage({ id: 'settings.labels.color' })}</FormLabel>
            <div className="flex flex-wrap gap-2">
              {PALETTE.map((c) => (
                <button
                  key={c}
                  type="button"
                  aria-label={c}
                  aria-pressed={color === c}
                  onClick={() => setValue('color', c, { shouldDirty: true })}
                  className={cn(
                    'h-7 w-7 rounded-full',
                    `bg-label-${c}`,
                    color === c && 'ring-2 ring-offset-2 ring-text-primary',
                  )}
                />
              ))}
            </div>
          </div>
          <div className="mb-[18px]">
            <FormLabel>{intl.formatMessage({ id: 'settings.labels.preview' })}</FormLabel>
            <LabelChip
              name={name || intl.formatMessage({ id: 'settings.labels.name' })}
              color={color}
            />
          </div>
          <div className="mt-2 flex justify-end gap-2">
            <DialogClose asChild>
              <Button type="button" variant="ghost">
                {intl.formatMessage({ id: 'settings.cancel' })}
              </Button>
            </DialogClose>
            <Button type="submit" disabled={pending} aria-busy={pending}>
              {intl.formatMessage({ id: editing ? 'settings.save' : 'settings.labels.create' })}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
