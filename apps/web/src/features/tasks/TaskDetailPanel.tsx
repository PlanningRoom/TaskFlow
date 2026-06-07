import { useEffect, useMemo, useState } from 'react';
import { useIntl } from 'react-intl';
import type { Comment, CurrentUser, TaskDetail, UserSummary } from '@/api/types';
import { Markdown } from '@/components/Markdown';
import { Avatar, Button } from '@/components/ui';
import { X } from '@/components/ui/icons';
import { useProjectAccess } from '@/features/projects/useProject';
import { useLabels } from '@/features/settings/useLabels';
import { useCurrentUser } from '@/hooks/useCurrentUser';
import { cn } from '@/lib/cn';
import { formatRelativeTime } from '@/lib/relativeTime';
import { MentionTextarea } from './MentionTextarea';
import {
  AssigneeSelect,
  DueDatePicker,
  LabelMultiSelect,
  PrioritySelect,
  StatusSelect,
} from './TaskFields';
import { useComments, useCreateComment } from './useComments';
import { useTask, useUpdateTask, useUpdateTaskStatus } from './useTasks';

/**
 * Task Detail panel (DRD §9 / PRD §10). Route-driven right-hand overlay over the
 * board/list: backdrop + Esc + × close, slide-in (reduced-motion respected).
 * Inline-editable title, status + property editors, Markdown description, and a
 * comments thread with @mention autocomplete. Viewers see everything read-only.
 */
export function TaskDetailPanel({
  projectId,
  taskId,
  role,
  onClose,
}: {
  projectId: string;
  taskId: string;
  role: CurrentUser['role'];
  onClose: () => void;
}) {
  const intl = useIntl();
  const { data: task, isPending, isError } = useTask(taskId);
  const updateTask = useUpdateTask(taskId, projectId);
  const updateStatus = useUpdateTaskStatus(projectId);
  const { data: access } = useProjectAccess(projectId);
  const { data: labelData } = useLabels();
  const { data: currentUser } = useCurrentUser();
  const canEdit = role !== 'viewer';

  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === 'Escape' && onClose();
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [onClose]);

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

  return (
    <div className="fixed inset-0 z-40 flex justify-end">
      <button
        type="button"
        aria-label={intl.formatMessage({ id: 'task.panel.closeBackdrop' })}
        className="absolute inset-0 bg-black/25"
        onClick={onClose}
      />
      <div
        role="dialog"
        aria-modal="true"
        aria-label={intl.formatMessage({ id: 'task.panel.label' })}
        className={cn(
          'relative flex h-full w-full max-w-[480px] flex-col bg-bg-card shadow-modal transition-transform duration-200 ease-out motion-reduce:transition-none',
          mounted ? 'translate-x-0' : 'translate-x-full',
        )}
      >
        {isPending ? (
          <p className="p-6 text-[13px] text-text-tertiary">
            {intl.formatMessage({ id: 'app.loading' })}
          </p>
        ) : isError || !task ? (
          <div className="flex items-center justify-between p-6">
            <p className="text-[13px] text-text-secondary">
              {intl.formatMessage({ id: 'task.panel.error' })}
            </p>
            <CloseButton onClose={onClose} label={intl.formatMessage({ id: 'task.panel.close' })} />
          </div>
        ) : (
          <PanelBody
            task={task}
            canEdit={canEdit}
            members={members}
            labels={labelData?.labels ?? []}
            onClose={onClose}
            onTitle={(title) => updateTask.mutate({ title })}
            onStatus={(status) => updateStatus.mutate({ taskId, status })}
            onAssignee={(assignee_id) => updateTask.mutate({ assignee_id })}
            onPriority={(priority) => updateTask.mutate({ priority })}
            onDue={(due_date) => updateTask.mutate({ due_date })}
            onLabels={(label_ids) => updateTask.mutate({ label_ids })}
            onDescription={(description) => updateTask.mutate({ description })}
          />
        )}
      </div>
    </div>
  );
}

function CloseButton({ onClose, label }: { onClose: () => void; label: string }) {
  return (
    <button
      type="button"
      onClick={onClose}
      aria-label={label}
      className="rounded-sm p-1.5 text-text-tertiary hover:bg-bg-hover hover:text-text-primary"
    >
      <X size={18} />
    </button>
  );
}

interface PanelBodyProps {
  task: TaskDetail;
  canEdit: boolean;
  members: UserSummary[];
  labels: import('@/api/types').Label[];
  onClose: () => void;
  onTitle: (title: string) => void;
  onStatus: (status: TaskDetail['status']) => void;
  onAssignee: (userId: string | null) => void;
  onPriority: (priority: TaskDetail['priority']) => void;
  onDue: (date: string | null) => void;
  onLabels: (labelIds: string[]) => void;
  onDescription: (description: string) => void;
}

function PanelBody(props: PanelBodyProps) {
  const { task, canEdit, members, labels, onClose } = props;
  const intl = useIntl();
  const [titleDraft, setTitleDraft] = useState(task.title);
  const [editingTitle, setEditingTitle] = useState(false);
  const [descDraft, setDescDraft] = useState(task.description ?? '');
  const [editingDesc, setEditingDesc] = useState(false);

  function commitTitle() {
    setEditingTitle(false);
    const next = titleDraft.trim();
    if (next && next !== task.title) props.onTitle(next);
    else setTitleDraft(task.title);
  }
  function commitDesc() {
    setEditingDesc(false);
    if (descDraft !== (task.description ?? '')) props.onDescription(descDraft);
  }

  const label = (id: string) => intl.formatMessage({ id });
  const row = (text: string, control: React.ReactNode) => (
    <div className="grid grid-cols-[96px_1fr] items-center gap-2 py-1.5">
      <span className="text-[13px] text-text-tertiary">{text}</span>
      <div>{control}</div>
    </div>
  );

  return (
    <>
      <header className="flex items-start gap-2 border-b border-border px-6 py-4">
        <div className="min-w-0 flex-1">
          {editingTitle && canEdit ? (
            <input
              // biome-ignore lint/a11y/noAutofocus: focusing the title is the point of entering edit mode
              autoFocus
              value={titleDraft}
              onChange={(e) => setTitleDraft(e.target.value)}
              onBlur={commitTitle}
              onKeyDown={(e) => {
                if (e.key === 'Enter') commitTitle();
                if (e.key === 'Escape') {
                  setTitleDraft(task.title);
                  setEditingTitle(false);
                }
              }}
              className="w-full rounded-sm border border-border-input px-2 py-1 text-[18px] font-semibold text-text-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
              aria-label={label('task.field.title')}
            />
          ) : (
            <button
              type="button"
              onClick={() => canEdit && setEditingTitle(true)}
              className={cn(
                'text-start text-[18px] font-semibold text-text-primary',
                canEdit && 'hover:bg-bg-hover rounded-sm',
              )}
              disabled={!canEdit}
            >
              {task.title}
            </button>
          )}
        </div>
        <CloseButton onClose={onClose} label={label('task.panel.close')} />
      </header>

      <div className="min-h-0 flex-1 overflow-y-auto px-6 py-4">
        <section className="border-b border-divider pb-4">
          {row(
            label('task.field.status'),
            <StatusSelect value={task.status} onChange={props.onStatus} disabled={!canEdit} />,
          )}
          {row(
            label('task.field.assignee'),
            <AssigneeSelect
              value={task.assignee}
              members={members}
              onChange={props.onAssignee}
              disabled={!canEdit}
            />,
          )}
          {row(
            label('task.field.priority'),
            <PrioritySelect
              value={task.priority}
              onChange={props.onPriority}
              disabled={!canEdit}
            />,
          )}
          {row(
            label('task.field.dueDate'),
            <DueDatePicker value={task.due_date} onChange={props.onDue} disabled={!canEdit} />,
          )}
          {row(
            label('task.field.labels'),
            <LabelMultiSelect
              value={task.labels.map((l) => l.id)}
              labels={labels}
              onChange={props.onLabels}
              disabled={!canEdit}
            />,
          )}
        </section>

        <section className="border-b border-divider py-4">
          <h3 className="mb-2 text-[13px] font-semibold text-text-secondary">
            {label('task.section.description')}
          </h3>
          {editingDesc && canEdit ? (
            <textarea
              // biome-ignore lint/a11y/noAutofocus: entering edit mode should focus the editor
              autoFocus
              value={descDraft}
              onChange={(e) => setDescDraft(e.target.value)}
              onBlur={commitDesc}
              className="min-h-24 w-full rounded-sm border border-border-input bg-bg-input p-2 text-[13px] text-text-on-surface focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
              aria-label={label('task.section.description')}
            />
          ) : (
            <button
              type="button"
              onClick={() => canEdit && setEditingDesc(true)}
              className={cn('block w-full text-start', canEdit && 'rounded-sm hover:bg-bg-hover')}
              disabled={!canEdit}
            >
              {task.description ? (
                <Markdown>{task.description}</Markdown>
              ) : (
                <span className="text-[13px] text-text-tertiary">
                  {label(canEdit ? 'task.description.empty' : 'task.description.none')}
                </span>
              )}
            </button>
          )}
        </section>

        <CommentsSection taskId={task.id} members={members} canEdit={canEdit} />
      </div>
    </>
  );
}

function CommentsSection({
  taskId,
  members,
  canEdit,
}: {
  taskId: string;
  members: UserSummary[];
  canEdit: boolean;
}) {
  const intl = useIntl();
  const { data } = useComments(taskId);
  const createComment = useCreateComment(taskId);
  const [body, setBody] = useState('');
  const comments = data?.comments ?? [];

  function submit() {
    const trimmed = body.trim();
    if (!trimmed) return;
    createComment.mutate({ body: trimmed }, { onSuccess: () => setBody('') });
  }

  return (
    <section className="py-4">
      <h3 className="mb-3 text-[13px] font-semibold text-text-secondary">
        {intl.formatMessage({ id: 'task.section.comments' })}
      </h3>
      <ul className="flex flex-col gap-4">
        {comments.map((comment) => (
          <CommentItem key={comment.id} comment={comment} />
        ))}
      </ul>
      {comments.length === 0 ? (
        <p className="text-[13px] text-text-tertiary">
          {intl.formatMessage({ id: 'task.comments.empty' })}
        </p>
      ) : null}
      {canEdit ? (
        <div className="mt-4">
          <MentionTextarea
            id="new-comment"
            value={body}
            onChange={setBody}
            members={members}
            placeholder={intl.formatMessage({ id: 'task.comments.placeholder' })}
          />
          <div className="mt-2 flex justify-end">
            <Button
              type="button"
              size="sm"
              onClick={submit}
              disabled={createComment.isPending || body.trim().length === 0}
            >
              {intl.formatMessage({ id: 'task.comments.submit' })}
            </Button>
          </div>
        </div>
      ) : null}
    </section>
  );
}

function CommentItem({ comment }: { comment: Comment }) {
  return (
    <li className="flex gap-2.5">
      <Avatar
        size="sm"
        initials={comment.author?.initials ?? '?'}
        color={comment.author?.avatar_color}
        id={comment.author?.id}
      />
      <div className="min-w-0 flex-1">
        <div className="flex items-baseline gap-2">
          <span className="text-[13px] font-medium text-text-primary">
            {comment.author?.display_name ?? 'Unknown'}
          </span>
          <span className="text-[11px] text-text-tertiary">
            {formatRelativeTime(comment.created_at)}
          </span>
        </div>
        <Markdown className="mt-0.5">{comment.body}</Markdown>
      </div>
    </li>
  );
}
