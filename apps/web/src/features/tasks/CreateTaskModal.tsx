import { zodResolver } from '@hookform/resolvers/zod';
import { type ReactNode, useMemo, useState } from 'react';
import { useForm } from 'react-hook-form';
import { useIntl } from 'react-intl';
import type { Label, UserSummary } from '@/api/types';
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
import { useProjectAccess } from '@/features/projects/useProject';
import { useLabels } from '@/features/settings/useLabels';
import { type CreateTaskValues, createTaskSchema } from '@/forms/schemas';
import { useCurrentUser } from '@/hooks/useCurrentUser';
import { AssigneeSelect, DueDatePicker, LabelMultiSelect, PrioritySelect } from './TaskFields';
import type { TaskPriority } from './useTasks';
import { useCreateTask } from './useTasks';

/**
 * Create Task modal (DRD §10.3). Title + description via React Hook Form; the
 * assignee/priority/due/labels are controlled selects (local state). New tasks
 * default to Backlog/None on the backend. Reused by the board + list "+ Create
 * task" buttons.
 */
export function CreateTaskModal({ projectId, trigger }: { projectId: string; trigger: ReactNode }) {
  const intl = useIntl();
  const toast = useToast();
  const { data: currentUser } = useCurrentUser();
  const { data: access } = useProjectAccess(projectId);
  const { data: labelData } = useLabels();
  const labels: Label[] = labelData?.labels ?? [];

  const [open, setOpen] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const [assigneeId, setAssigneeId] = useState<string | null>(null);
  const [priority, setPriority] = useState<TaskPriority>('none');
  const [dueDate, setDueDate] = useState<string | null>(null);
  const [labelIds, setLabelIds] = useState<string[]>([]);

  // Assignable members = project-access members, plus the current Owner/Admin
  // (who have implicit access but may not be in the explicit access list).
  const members = useMemo<UserSummary[]>(() => {
    const list = (access?.members ?? []).map((m) => m.user);
    if (
      currentUser &&
      (currentUser.role === 'owner' || currentUser.role === 'admin') &&
      !list.some((u) => u.id === currentUser.id)
    ) {
      list.unshift({
        id: currentUser.id,
        display_name: currentUser.display_name,
        initials: currentUser.initials,
        avatar_color: currentUser.avatar_color,
        deleted: false,
      });
    }
    return list;
  }, [access, currentUser]);

  const assignee = members.find((m) => m.id === assigneeId) ?? null;

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<CreateTaskValues>({ resolver: zodResolver(createTaskSchema) });

  const mutation = useCreateTask(projectId);

  function resetAll() {
    reset();
    setFormError(null);
    setAssigneeId(null);
    setPriority('none');
    setDueDate(null);
    setLabelIds([]);
  }

  const onSubmit = handleSubmit((values) => {
    setFormError(null);
    mutation.mutate(
      {
        title: values.title,
        description: values.description?.trim() || null,
        assignee_id: assigneeId,
        priority,
        due_date: dueDate,
        label_ids: labelIds,
      },
      {
        onSuccess: () => {
          setOpen(false);
          resetAll();
          toast.show(intl.formatMessage({ id: 'task.create.success' }));
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
        if (!next) resetAll();
      }}
    >
      <DialogTrigger asChild>{trigger}</DialogTrigger>
      <DialogContent title={intl.formatMessage({ id: 'task.create.title' })}>
        <form onSubmit={onSubmit} noValidate>
          {formError ? <FormError message={formError} /> : null}

          <div className="mb-[18px]">
            <FormLabel htmlFor="create-task-title">
              {intl.formatMessage({ id: 'task.field.title' })}
            </FormLabel>
            <Input
              id="create-task-title"
              autoFocus
              aria-invalid={errors.title ? true : undefined}
              {...register('title')}
            />
            {errors.title ? (
              <p className="mt-1.5 text-[13px] text-semantic-error">{errors.title.message}</p>
            ) : null}
          </div>

          <div className="mb-[18px]">
            <FormLabel htmlFor="create-task-description">
              {intl.formatMessage({ id: 'task.field.description' })}
            </FormLabel>
            <Textarea id="create-task-description" {...register('description')} />
          </div>

          <div className="mb-[18px] grid grid-cols-2 gap-3">
            <div>
              <FormLabel>{intl.formatMessage({ id: 'task.field.assignee' })}</FormLabel>
              <AssigneeSelect value={assignee} members={members} onChange={setAssigneeId} />
            </div>
            <div>
              <FormLabel>{intl.formatMessage({ id: 'task.field.priority' })}</FormLabel>
              <PrioritySelect value={priority} onChange={setPriority} />
            </div>
          </div>

          <div className="mb-[18px] grid grid-cols-2 gap-3">
            <div>
              <FormLabel>{intl.formatMessage({ id: 'task.field.dueDate' })}</FormLabel>
              <DueDatePicker value={dueDate} onChange={setDueDate} />
            </div>
            <div>
              <FormLabel>{intl.formatMessage({ id: 'task.field.labels' })}</FormLabel>
              <LabelMultiSelect value={labelIds} labels={labels} onChange={setLabelIds} />
            </div>
          </div>

          <div className="mt-2 flex justify-end gap-2">
            <DialogClose asChild>
              <Button type="button" variant="ghost">
                {intl.formatMessage({ id: 'task.create.cancel' })}
              </Button>
            </DialogClose>
            <Button type="submit" disabled={mutation.isPending} aria-busy={mutation.isPending}>
              {intl.formatMessage({ id: 'task.create.submit' })}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
