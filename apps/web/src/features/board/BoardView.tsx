import {
  DndContext,
  type DragEndEvent,
  KeyboardSensor,
  PointerSensor,
  useDroppable,
  useSensor,
  useSensors,
} from '@dnd-kit/core';
import { useIntl } from 'react-intl';
import type { CurrentUser, TaskSummary } from '@/api/types';
import { Button, STATUS_LABELS } from '@/components/ui';
import { Plus } from '@/components/ui/icons';
import { CreateTaskModal } from '@/features/tasks/CreateTaskModal';
import type { TaskSearch } from '@/features/tasks/taskQueryState';
import type { TaskQueryParams, TaskStatus } from '@/features/tasks/useTasks';
import { useProjectTasks, useUpdateTaskStatus } from '@/features/tasks/useTasks';
import { cn } from '@/lib/cn';
import { TaskCard } from './TaskCard';

/**
 * Board view (DRD §8.4 / PRD §8). Five status columns (Cancelled appears only
 * when filtered in); drag a card to another column to change status, with the
 * optimistic update from {@link useUpdateTaskStatus}. Desktop drag + keyboard
 * sensor; cards open the detail panel on click.
 */
const COLUMNS: TaskStatus[] = ['backlog', 'todo', 'in_progress', 'in_review', 'done'];

interface BoardProps {
  projectId: string;
  params: TaskQueryParams;
  search: TaskSearch;
  role: CurrentUser['role'];
  onOpenTask: (taskId: string) => void;
  onClearFilters: () => void;
}

export function BoardView({
  projectId,
  params,
  search,
  role,
  onOpenTask,
  onClearFilters,
}: BoardProps) {
  const intl = useIntl();
  const { data, isPending, isError } = useProjectTasks(projectId, params);
  const updateStatus = useUpdateTaskStatus(projectId);
  const canEdit = role !== 'viewer';

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 5 } }),
    useSensor(KeyboardSensor),
  );

  const columns = search.cancelled ? [...COLUMNS, 'cancelled' as TaskStatus] : COLUMNS;
  const tasks = data?.tasks ?? [];
  const byStatus = (status: TaskStatus) => tasks.filter((t) => t.status === status);

  function onDragEnd(event: DragEndEvent) {
    const overId = event.over?.id as TaskStatus | undefined;
    const current = event.active.data.current?.status as TaskStatus | undefined;
    const taskId = String(event.active.id);
    if (overId && current && overId !== current) {
      updateStatus.mutate({ taskId, status: overId });
    }
  }

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
        ) : canEdit ? (
          <CreateTaskModal
            projectId={projectId}
            trigger={
              <Button size="sm">
                <Plus size={16} strokeWidth={1.75} />
                {intl.formatMessage({ id: 'board.createTask' })}
              </Button>
            }
          />
        ) : null}
      </div>
    );
  }

  return (
    <DndContext sensors={sensors} onDragEnd={onDragEnd}>
      <div className="flex h-full gap-4 p-6">
        {columns.map((status) => (
          <BoardColumn
            key={status}
            status={status}
            tasks={byStatus(status)}
            canDrag={canEdit}
            onOpenTask={onOpenTask}
          />
        ))}
      </div>
    </DndContext>
  );
}

function BoardColumn({
  status,
  tasks,
  canDrag,
  onOpenTask,
}: {
  status: TaskStatus;
  tasks: TaskSummary[];
  canDrag: boolean;
  onOpenTask: (taskId: string) => void;
}) {
  const { setNodeRef, isOver } = useDroppable({ id: status });
  return (
    <div className="flex w-[280px] shrink-0 flex-col">
      <div className="flex items-center gap-2 pb-2">
        <span className={cn('h-2.5 w-2.5 rounded-[3px]', STATUS_DOT[status])} aria-hidden />
        <span className="text-[13px] font-semibold text-text-primary">{STATUS_LABELS[status]}</span>
        <span className="text-xs text-text-tertiary">{tasks.length}</span>
      </div>
      <div
        ref={setNodeRef}
        className={cn(
          'flex min-h-24 flex-1 flex-col gap-2 rounded-md bg-bg-column p-2 transition-colors',
          isOver && 'bg-primary-light',
        )}
      >
        {tasks.map((task) => (
          <TaskCard
            key={task.id}
            task={task}
            canDrag={canDrag}
            onOpen={() => onOpenTask(task.id)}
          />
        ))}
        {tasks.length === 0 ? (
          <p className="px-1 py-2 text-[11px] text-text-tertiary">No tasks</p>
        ) : null}
      </div>
    </div>
  );
}

/** Literal status→dot color classes (dynamic class names aren't scanned by Tailwind). */
const STATUS_DOT: Record<TaskStatus, string> = {
  backlog: 'bg-status-backlog',
  todo: 'bg-status-todo',
  in_progress: 'bg-status-progress',
  in_review: 'bg-status-review',
  done: 'bg-status-done',
  cancelled: 'bg-status-cancelled',
};
