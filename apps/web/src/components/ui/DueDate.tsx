import { cn } from '@/lib/cn';

/**
 * DueDate (DRD §7.7) — formats an ISO date as "Apr 15" (current year) or
 * "Apr 15, 2025" (other years). Overdue → error color + medium weight;
 * approaching (within `approachingDays`, default 3) → warning color.
 */
export interface DueDateProps {
  /** ISO date string (YYYY-MM-DD) or null. */
  date: string | null;
  /** Reference "now" for testability; defaults to the current date. */
  now?: Date;
  approachingDays?: number;
  className?: string;
}

const MS_PER_DAY = 86_400_000;

export function formatDueDate(date: Date, now: Date): string {
  const opts: Intl.DateTimeFormatOptions =
    date.getFullYear() === now.getFullYear()
      ? { month: 'short', day: 'numeric' }
      : { month: 'short', day: 'numeric', year: 'numeric' };
  return new Intl.DateTimeFormat('en-US', opts).format(date);
}

export function DueDate({ date, now = new Date(), approachingDays = 3, className }: DueDateProps) {
  if (!date) return null;
  const due = new Date(`${date}T00:00:00`);
  const startOfToday = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const daysUntil = Math.round((due.getTime() - startOfToday.getTime()) / MS_PER_DAY);

  const overdue = daysUntil < 0;
  const approaching = !overdue && daysUntil <= approachingDays;

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1 whitespace-nowrap text-xs text-text-secondary',
        overdue && 'font-medium text-semantic-error',
        approaching && 'text-semantic-warning',
        className,
      )}
    >
      {formatDueDate(due, now)}
    </span>
  );
}
