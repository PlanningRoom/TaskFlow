import { cn } from '@/lib/cn';

/**
 * LabelChip (DRD §7.5 / §2.9) — a colored pill with white text. `color` is one
 * of the eight fixed palette names. On dense surfaces, render up to 3 and use
 * {@link LabelOverflow} for the "+N" remainder.
 */
export type LabelColor = 'blue' | 'green' | 'red' | 'purple' | 'amber' | 'pink' | 'cyan' | 'orange';

const COLOR_CLASS: Record<LabelColor, string> = {
  blue: 'bg-label-blue',
  green: 'bg-label-green',
  red: 'bg-label-red',
  purple: 'bg-label-purple',
  amber: 'bg-label-amber',
  pink: 'bg-label-pink',
  cyan: 'bg-label-cyan',
  orange: 'bg-label-orange',
};

export interface LabelChipProps {
  name: string;
  color: LabelColor;
  className?: string;
}

export function LabelChip({ name, color, className }: LabelChipProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-badge px-2 py-px text-[11px] font-medium text-white',
        COLOR_CLASS[color],
        className,
      )}
    >
      {name}
    </span>
  );
}

export function LabelOverflow({ count }: { count: number }) {
  if (count <= 0) return null;
  return (
    <span className="inline-flex items-center rounded-badge px-2 py-px text-[11px] font-medium text-text-tertiary">
      +{count}
    </span>
  );
}
