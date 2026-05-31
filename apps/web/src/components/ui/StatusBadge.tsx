import { cn } from '@/lib/cn';

/**
 * StatusBadge (DRD §7.4 / §2.6) — a pill showing a task status in its fg/bg
 * color pair. `status` matches the backend task status values.
 */
export type TaskStatus = 'backlog' | 'todo' | 'in_progress' | 'in_review' | 'done' | 'cancelled';

const STATUS_META: Record<TaskStatus, { label: string; className: string }> = {
  backlog: { label: 'Backlog', className: 'bg-status-backlog-bg text-status-backlog' },
  todo: { label: 'To Do', className: 'bg-status-todo-bg text-status-todo' },
  in_progress: {
    label: 'In Progress',
    className: 'bg-status-progress-bg text-status-progress',
  },
  in_review: { label: 'In Review', className: 'bg-status-review-bg text-status-review' },
  done: { label: 'Done', className: 'bg-status-done-bg text-status-done' },
  cancelled: {
    label: 'Cancelled',
    className: 'bg-status-cancelled-bg text-status-cancelled',
  },
};

export interface StatusBadgeProps {
  status: TaskStatus;
  className?: string;
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const meta = STATUS_META[status];
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1 whitespace-nowrap rounded-badge px-2 py-0.5 text-[11px] font-medium',
        meta.className,
        className,
      )}
    >
      {meta.label}
    </span>
  );
}

export const STATUS_LABELS = Object.fromEntries(
  (Object.entries(STATUS_META) as [TaskStatus, { label: string }][]).map(([k, v]) => [k, v.label]),
) as Record<TaskStatus, string>;
