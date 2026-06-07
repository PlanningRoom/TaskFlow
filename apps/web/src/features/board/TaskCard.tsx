import { useDraggable } from '@dnd-kit/core';
import { CSS } from '@dnd-kit/utilities';
import type { TaskSummary } from '@/api/types';
import { Avatar, DueDate, LabelChip, LabelOverflow, PriorityIcon } from '@/components/ui';
import { MessageSquare } from '@/components/ui/icons';
import { cn } from '@/lib/cn';

/**
 * Board task card (DRD §8.4): title (2-line clamp), up to 3 labels + overflow,
 * and a meta row (priority / due / comment count / assignee). Draggable for
 * edit roles; a plain click (no drag movement) opens the detail panel.
 */
const MAX_LABELS = 3;

export function TaskCard({
  task,
  canDrag,
  onOpen,
}: {
  task: TaskSummary;
  canDrag: boolean;
  onOpen: () => void;
}) {
  const { attributes, listeners, setNodeRef, transform, isDragging } = useDraggable({
    id: task.id,
    data: { status: task.status },
    disabled: !canDrag,
  });

  const labels = task.labels.slice(0, MAX_LABELS);
  const overflow = task.labels.length - labels.length;

  return (
    <button
      type="button"
      ref={setNodeRef}
      onClick={onOpen}
      style={{ transform: CSS.Translate.toString(transform) }}
      className={cn(
        'flex flex-col gap-2 rounded-md border border-border bg-bg-card p-3 text-start shadow-card transition-shadow hover:shadow-card-hover',
        isDragging && 'opacity-50',
      )}
      {...listeners}
      {...attributes}
    >
      <span className="line-clamp-2 text-[13px] font-medium text-text-primary">{task.title}</span>
      {task.labels.length > 0 ? (
        <span className="flex flex-wrap items-center gap-1">
          {labels.map((label) => (
            <LabelChip key={label.id} name={label.name} color={label.color} />
          ))}
          {overflow > 0 ? <LabelOverflow count={overflow} /> : null}
        </span>
      ) : null}
      <span className="flex items-center gap-2.5 text-text-secondary">
        <PriorityIcon priority={task.priority} />
        <DueDate date={task.due_date} />
        {task.comment_count > 0 ? (
          <span className="inline-flex items-center gap-1 text-xs">
            <MessageSquare size={13} strokeWidth={1.75} />
            {task.comment_count}
          </span>
        ) : null}
        {task.assignee ? (
          <Avatar
            size="sm"
            initials={task.assignee.initials}
            color={task.assignee.avatar_color}
            id={task.assignee.id}
            className="ms-auto"
          />
        ) : null}
      </span>
    </button>
  );
}
