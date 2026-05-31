import { cn } from '@/lib/cn';

/**
 * PriorityIcon (DRD §7.6) — a colored arrow glyph. `none` renders nothing.
 * Glyphs: urgent ↑↑, high ↑, medium —, low ↓.
 */
export type Priority = 'urgent' | 'high' | 'medium' | 'low' | 'none';

const META: Record<
  Exclude<Priority, 'none'>,
  { glyph: string; className: string; label: string }
> = {
  urgent: { glyph: '↑↑', className: 'text-priority-urgent', label: 'Urgent priority' },
  high: { glyph: '↑', className: 'text-priority-high', label: 'High priority' },
  medium: { glyph: '—', className: 'text-priority-medium', label: 'Medium priority' },
  low: { glyph: '↓', className: 'text-priority-low', label: 'Low priority' },
};

export interface PriorityIconProps {
  priority: Priority;
  className?: string;
}

export function PriorityIcon({ priority, className }: PriorityIconProps) {
  if (priority === 'none') return null;
  const meta = META[priority];
  return (
    <span
      className={cn('shrink-0 text-[13px] font-bold leading-none', meta.className, className)}
      role="img"
      aria-label={meta.label}
    >
      <span aria-hidden>{meta.glyph}</span>
    </span>
  );
}
