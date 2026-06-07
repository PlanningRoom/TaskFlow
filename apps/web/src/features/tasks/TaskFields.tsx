import type { Label, UserSummary } from '@/api/types';
import {
  Avatar,
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  LabelChip,
  PriorityIcon,
  STATUS_LABELS,
  StatusBadge,
} from '@/components/ui';
import { Calendar, Check, ChevronDown } from '@/components/ui/icons';
import { cn } from '@/lib/cn';
import type { TaskPriority, TaskStatus } from './useTasks';

/**
 * Inline property editors shared by the Create Task modal (G3) and the Task
 * Detail panel (G5). Each is controlled and accepts `disabled` so the panel can
 * render Viewers a read-only value. Data (members, labels) is supplied by the
 * parent so these stay pure and testable.
 */

const TRIGGER =
  'inline-flex items-center gap-1.5 rounded-sm px-2 py-1 text-[13px] text-text-primary hover:bg-bg-hover disabled:cursor-default disabled:hover:bg-transparent';

export const PRIORITY_LABELS: Record<TaskPriority, string> = {
  none: 'None',
  low: 'Low',
  medium: 'Medium',
  high: 'High',
  urgent: 'Urgent',
};

const STATUS_ORDER: TaskStatus[] = [
  'backlog',
  'todo',
  'in_progress',
  'in_review',
  'done',
  'cancelled',
];
const PRIORITY_ORDER: TaskPriority[] = ['none', 'low', 'medium', 'high', 'urgent'];

export function StatusSelect({
  value,
  onChange,
  disabled,
}: {
  value: TaskStatus;
  onChange: (status: TaskStatus) => void;
  disabled?: boolean;
}) {
  if (disabled) return <StatusBadge status={value} />;
  return (
    <DropdownMenu>
      <DropdownMenuTrigger
        className="rounded-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
        aria-label="Change status"
      >
        <StatusBadge status={value} />
      </DropdownMenuTrigger>
      <DropdownMenuContent align="start">
        {STATUS_ORDER.map((status) => (
          <DropdownMenuItem key={status} onSelect={() => onChange(status)}>
            <StatusBadge status={status} />
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

export function PrioritySelect({
  value,
  onChange,
  disabled,
}: {
  value: TaskPriority;
  onChange: (priority: TaskPriority) => void;
  disabled?: boolean;
}) {
  const label = (
    <span className="inline-flex items-center gap-1.5">
      <PriorityIcon priority={value} />
      {PRIORITY_LABELS[value]}
    </span>
  );
  if (disabled) return <span className="text-[13px] text-text-primary">{label}</span>;
  return (
    <DropdownMenu>
      <DropdownMenuTrigger className={TRIGGER} aria-label="Change priority">
        {label}
        <ChevronDown size={14} className="text-text-tertiary" />
      </DropdownMenuTrigger>
      <DropdownMenuContent align="start">
        {PRIORITY_ORDER.map((priority) => (
          <DropdownMenuItem key={priority} onSelect={() => onChange(priority)}>
            <PriorityIcon priority={priority} />
            <span className="ms-1.5">{PRIORITY_LABELS[priority]}</span>
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

export function AssigneeSelect({
  value,
  members,
  onChange,
  disabled,
}: {
  value: UserSummary | null;
  members: UserSummary[];
  onChange: (userId: string | null) => void;
  disabled?: boolean;
}) {
  const display = value ? (
    <span className="inline-flex items-center gap-1.5">
      <Avatar size="sm" initials={value.initials} color={value.avatar_color} id={value.id} />
      {value.display_name ?? 'Unknown'}
    </span>
  ) : (
    <span className="text-text-tertiary">Unassigned</span>
  );
  if (disabled) return <span className="text-[13px] text-text-primary">{display}</span>;
  return (
    <DropdownMenu>
      <DropdownMenuTrigger className={TRIGGER} aria-label="Change assignee">
        {display}
        <ChevronDown size={14} className="text-text-tertiary" />
      </DropdownMenuTrigger>
      <DropdownMenuContent align="start">
        <DropdownMenuItem onSelect={() => onChange(null)}>
          <span className="text-text-tertiary">Unassigned</span>
        </DropdownMenuItem>
        {members.map((member) => (
          <DropdownMenuItem key={member.id} onSelect={() => onChange(member.id)}>
            <Avatar
              size="sm"
              initials={member.initials}
              color={member.avatar_color}
              id={member.id}
            />
            <span className="ms-1.5">{member.display_name ?? 'Unknown'}</span>
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

export function LabelMultiSelect({
  value,
  labels,
  onChange,
  disabled,
}: {
  value: string[];
  labels: Label[];
  onChange: (labelIds: string[]) => void;
  disabled?: boolean;
}) {
  const selected = labels.filter((l) => value.includes(l.id));
  const chips =
    selected.length > 0 ? (
      <span className="flex flex-wrap gap-1">
        {selected.map((l) => (
          <LabelChip key={l.id} name={l.name} color={l.color} />
        ))}
      </span>
    ) : (
      <span className="text-text-tertiary">None</span>
    );
  if (disabled) return chips;

  function toggle(id: string) {
    onChange(value.includes(id) ? value.filter((v) => v !== id) : [...value, id]);
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger className={cn(TRIGGER, 'flex-wrap')} aria-label="Edit labels">
        {chips}
        <ChevronDown size={14} className="text-text-tertiary" />
      </DropdownMenuTrigger>
      <DropdownMenuContent align="start">
        {labels.length === 0 ? (
          <DropdownMenuItem disabled>No labels yet</DropdownMenuItem>
        ) : (
          labels.map((label) => (
            <DropdownMenuItem
              key={label.id}
              onSelect={(e) => {
                e.preventDefault();
                toggle(label.id);
              }}
            >
              <span className="flex w-4 justify-center">
                {value.includes(label.id) ? <Check size={14} className="text-primary" /> : null}
              </span>
              <LabelChip name={label.name} color={label.color} />
            </DropdownMenuItem>
          ))
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

export function DueDatePicker({
  value,
  onChange,
  disabled,
}: {
  value: string | null;
  onChange: (date: string | null) => void;
  disabled?: boolean;
}) {
  if (disabled) {
    return (
      <span className="text-[13px] text-text-primary">
        {value ?? <span className="text-text-tertiary">No due date</span>}
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1.5">
      <Calendar size={14} className="text-text-tertiary" />
      <input
        type="date"
        value={value ?? ''}
        onChange={(e) => onChange(e.target.value || null)}
        className="rounded-sm border border-border-input bg-bg-input px-2 py-1 text-[13px] text-text-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
        aria-label="Due date"
      />
    </span>
  );
}

export { STATUS_LABELS, STATUS_ORDER };
