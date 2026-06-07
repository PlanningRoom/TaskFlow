import { zodResolver } from '@hookform/resolvers/zod';
import { type ReactNode, useState } from 'react';
import { useForm } from 'react-hook-form';
import { useIntl } from 'react-intl';
import {
  Avatar,
  Button,
  Dialog,
  DialogContent,
  DialogTrigger,
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  FormLabel,
  Input,
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
  Textarea,
  useToast,
} from '@/components/ui';
import { Plus, X } from '@/components/ui/icons';
import { FormError } from '@/features/auth/FormField';
import { useMembers } from '@/features/settings/useMembers';
import { type CreateProjectValues, createProjectSchema } from '@/forms/schemas';
import {
  useGrantProjectAccess,
  useProject,
  useProjectAccess,
  useRevokeProjectAccess,
  useUpdateProject,
} from './useProject';

/**
 * Project Settings modal (DRD §10.2 / screen inventory §5.2). Details tab edits
 * name + description; Access tab manages explicit project membership (Owner/
 * Admin have implicit access and aren't listed). Triggered from the board/list
 * sub-nav settings icon.
 */
export function ProjectSettingsModal({
  projectId,
  trigger,
}: {
  projectId: string;
  trigger: ReactNode;
}) {
  const intl = useIntl();
  const [open, setOpen] = useState(false);

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>{trigger}</DialogTrigger>
      <DialogContent title={intl.formatMessage({ id: 'project.settings.title' })}>
        <Tabs defaultValue="details">
          <TabsList>
            <TabsTrigger value="details">
              {intl.formatMessage({ id: 'project.settings.details' })}
            </TabsTrigger>
            <TabsTrigger value="access">
              {intl.formatMessage({ id: 'project.settings.access' })}
            </TabsTrigger>
          </TabsList>
          <TabsContent value="details">
            <DetailsTab projectId={projectId} />
          </TabsContent>
          <TabsContent value="access">
            <AccessTab projectId={projectId} />
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
}

function DetailsTab({ projectId }: { projectId: string }) {
  const intl = useIntl();
  const toast = useToast();
  const { data: project } = useProject(projectId);
  const mutation = useUpdateProject(projectId);
  const [formError, setFormError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<CreateProjectValues>({
    resolver: zodResolver(createProjectSchema),
    values: { name: project?.name ?? '', description: project?.description ?? '' },
  });

  const onSubmit = handleSubmit((values) => {
    setFormError(null);
    mutation.mutate(
      { name: values.name, description: values.description?.trim() || null },
      {
        onSuccess: () => toast.show(intl.formatMessage({ id: 'project.settings.saved' })),
        onError: () => setFormError(intl.formatMessage({ id: 'auth.error.generic' })),
      },
    );
  });

  return (
    <form onSubmit={onSubmit} noValidate className="pt-4">
      {formError ? <FormError message={formError} /> : null}
      <div className="mb-[18px]">
        <FormLabel htmlFor="project-name">
          {intl.formatMessage({ id: 'project.field.name' })}
        </FormLabel>
        <Input
          id="project-name"
          aria-invalid={errors.name ? true : undefined}
          {...register('name')}
        />
        {errors.name ? (
          <p className="mt-1.5 text-[13px] text-semantic-error">{errors.name.message}</p>
        ) : null}
      </div>
      <div className="mb-[18px]">
        <FormLabel htmlFor="project-description">
          {intl.formatMessage({ id: 'project.field.description' })}
        </FormLabel>
        <Textarea id="project-description" {...register('description')} />
      </div>
      <div className="flex justify-end">
        <Button type="submit" disabled={mutation.isPending} aria-busy={mutation.isPending}>
          {intl.formatMessage({ id: 'project.settings.save' })}
        </Button>
      </div>
    </form>
  );
}

function AccessTab({ projectId }: { projectId: string }) {
  const intl = useIntl();
  const { data: access } = useProjectAccess(projectId);
  const { data: memberData } = useMembers();
  const grant = useGrantProjectAccess(projectId);
  const revoke = useRevokeProjectAccess(projectId);

  const accessMembers = access?.members ?? [];
  const accessIds = new Set(accessMembers.map((m) => m.user.id));
  // Candidates to add: workspace Members/Viewers not already granted (Owner/
  // Admin have implicit access and don't need an explicit grant).
  const candidates = (memberData?.members ?? []).filter(
    (m) => !accessIds.has(m.id) && (m.role === 'member' || m.role === 'viewer'),
  );

  return (
    <div className="pt-4">
      <ul className="flex flex-col gap-1">
        {accessMembers.map(({ user }) => (
          <li key={user.id} className="flex items-center gap-2.5 py-1.5">
            <Avatar size="sm" initials={user.initials} color={user.avatar_color} id={user.id} />
            <span className="flex-1 text-[13px] text-text-primary">
              {user.display_name ?? 'Unknown'}
            </span>
            <button
              type="button"
              onClick={() => revoke.mutate(user.id)}
              className="rounded-sm p-1 text-text-tertiary hover:bg-bg-hover hover:text-semantic-error"
              aria-label={intl.formatMessage({ id: 'project.access.remove' })}
            >
              <X size={16} />
            </button>
          </li>
        ))}
        {accessMembers.length === 0 ? (
          <li className="py-1.5 text-[13px] text-text-tertiary">
            {intl.formatMessage({ id: 'project.access.empty' })}
          </li>
        ) : null}
      </ul>

      <div className="mt-3">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button type="button" variant="secondary" size="sm" disabled={candidates.length === 0}>
              <Plus size={16} strokeWidth={1.75} />
              {intl.formatMessage({ id: 'project.access.add' })}
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="start">
            {candidates.map((member) => (
              <DropdownMenuItem key={member.id} onSelect={() => grant.mutate(member.id)}>
                <Avatar
                  size="sm"
                  initials={member.initials}
                  color={member.avatar_color}
                  id={member.id}
                />
                <span className="ms-1.5">{member.display_name ?? member.email}</span>
              </DropdownMenuItem>
            ))}
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </div>
  );
}
