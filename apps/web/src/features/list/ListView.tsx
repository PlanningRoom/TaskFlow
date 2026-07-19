import { useIntl } from 'react-intl';
import type { CurrentUser, TaskSummary } from '@/api/types';
import { Avatar, DueDate, LabelChip, LabelOverflow, PriorityIcon } from '@/components/ui';
import { PRIORITY_LABELS, StatusSelect } from '@/features/tasks/TaskFields';
import type { TaskSearch } from '@/features/tasks/taskQueryState';
import type { TaskQueryParams, TaskSort } from '@/features/tasks/useTasks';
import { useProjectTasks, useUpdateTaskStatus } from '@/features/tasks/useTasks';
import { cn } from '@/lib/cn';

/**
 * List view (DRD §8.5 / PRD §9). Tabular alternative to the board sharing the
 * same filter/sort URL state. Priority/Due/Assignee headers drive the backend
 * sort; the Status cell has an inline role-gated dropdown; a row opens the panel.
 */
const MAX_LABELS = 3;

interface ListProps {
  projectId: string;
  params: TaskQueryParams;
  search: TaskSearch;
  role: CurrentUser['role'];
  onOpenTask: (taskId: string) => void;
  onClearFilters: () => void;
  onSortChange: (sort: TaskSort) => void;
}

export function ListView({
  projectId,
  params,
  search,
  role,
  onOpenTask,
  onClearFilters,
  onSortChange,
}: ListProps) {
  const intl = useIntl();
  const { data, isPending, isError } = useProjectTasks(projectId, params);
  const updateStatus = useUpdateTaskStatus(projectId);
  const canEdit = role !== 'viewer';
  const activeSort = search.sort ?? 'created_at';

  if (isPending)
    return (
      <p className="p-6 text-[13px] text-text-tertiary">
        {intl.formatMessage({ id: 'app.loading' })}
      </p>
    );
  if (isError)
    return (
      <p className="p-6 text-[13px] text-text-secondary">
        {intl.formatMessage({ id: 'board.error' })}
      </p>
    );

  const tasks = data?.tasks ?? [];
  if (tasks.length === 0) {
    const filtered =
      params.status || params.assignee || params.priority || params.label || params.due;
    return (
      <div className="flex flex-col items-center gap-3 p-12 text-center">
        <p className="text-[13px] text-text-secondary">
          {filtered
            ? intl.formatMessage({ id: 'board.empty.filtered' })
            : intl.formatMessage({ id: 'board.empty' })}
        </p>
        {filtered ? (
          <button
            type="button"
            onClick={onClearFilters}
            className="text-[13px] text-primary underline"
          >
            {intl.formatMessage({ id: 'board.clearFilters' })}
          </button>
        ) : null}
      </div>
    );
  }

  const sortHeader = (label: string, sort: TaskSort) => (
    <button
      type="button"
      onClick={() => onSortChange(sort)}
      className={cn(
        'inline-flex items-center gap-1 hover:text-text-primary',
        activeSort === sort && 'text-text-primary',
      )}
    >
      {label}
      {activeSort === sort ? <span aria-hidden>↓</span> : null}
    </button>
  );

  return (
    // Mobile (DRD §15.3): the table keeps its column layout and scrolls
    // horizontally inside this wrapper rather than crushing the cells.
    <div className="overflow-x-auto">
      <table className="w-full min-w-[640px] border-collapse text-[13px]">
        <thead>
          <tr className="border-b border-border text-start text-[11px] font-semibold uppercase tracking-[0.03em] text-text-tertiary">
            <th className="px-6 py-2 text-start font-semibold">Title</th>
            <th className="px-3 py-2 text-start font-semibold">Status</th>
            <th className="px-3 py-2 text-start font-semibold">
              {sortHeader('Assignee', 'assignee')}
            </th>
            <th className="px-3 py-2 text-start font-semibold">
              {sortHeader('Priority', 'priority')}
            </th>
            <th className="px-3 py-2 text-start font-semibold">{sortHeader('Due', 'due_date')}</th>
            <th className="px-3 py-2 text-start font-semibold">Labels</th>
          </tr>
        </thead>
        <tbody>
          {tasks.map((task) => (
            <ListRow
              key={task.id}
              task={task}
              canEdit={canEdit}
              onOpen={() => onOpenTask(task.id)}
              onStatusChange={(status) => updateStatus.mutate({ taskId: task.id, status })}
            />
          ))}
        </tbody>
      </table>
    </div>
  );
}

function ListRow({
  task,
  canEdit,
  onOpen,
  onStatusChange,
}: {
  task: TaskSummary;
  canEdit: boolean;
  onOpen: () => void;
  onStatusChange: (status: TaskSummary['status']) => void;
}) {
  const labels = task.labels.slice(0, MAX_LABELS);
  const overflow = task.labels.length - labels.length;
  return (
    <tr className="border-b border-divider hover:bg-bg-hover">
      <td className="px-6 py-2.5">
        <button
          type="button"
          onClick={onOpen}
          className="text-start font-medium text-text-primary hover:underline"
        >
          {task.title}
        </button>
      </td>
      <td className="px-3 py-2.5">
        <StatusSelect value={task.status} onChange={onStatusChange} disabled={!canEdit} />
      </td>
      <td className="px-3 py-2.5">
        {task.assignee ? (
          <span className="inline-flex items-center gap-1.5 text-text-secondary">
            <Avatar
              size="sm"
              initials={task.assignee.initials}
              color={task.assignee.avatar_color}
              id={task.assignee.id}
            />
            {task.assignee.display_name ?? 'Unknown'}
          </span>
        ) : (
          <span className="text-text-tertiary">—</span>
        )}
      </td>
      <td className="px-3 py-2.5 text-text-secondary">
        <span className="inline-flex items-center gap-1.5">
          <PriorityIcon priority={task.priority} />
          {PRIORITY_LABELS[task.priority]}
        </span>
      </td>
      <td className="px-3 py-2.5">
        <DueDate date={task.due_date} />
      </td>
      <td className="px-3 py-2.5">
        <span className="flex flex-wrap items-center gap-1">
          {labels.map((label) => (
            <LabelChip key={label.id} name={label.name} color={label.color} />
          ))}
          {overflow > 0 ? <LabelOverflow count={overflow} /> : null}
        </span>
      </td>
    </tr>
  );
}
