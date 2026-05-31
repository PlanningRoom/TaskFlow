import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/cn';

/**
 * Avatar (DRD §7.3 / §2.10) — an initials circle whose background is one of the
 * six fixed palette colors, deterministically chosen from the user id.
 *
 * Palette-name reconciliation: the backend returns `avatar_color` as one of
 * `indigo|violet|amber|emerald|rose|sky` (taskflow/schemas/users.py), but the
 * DRD §2.10 tokens are named `purple|blue|green|amber|rose|cyan`. The two lists
 * are position-aligned, so this record maps API name -> DRD token utility,
 * preserving the deterministic distribution. (Tracked divergence; see the F3
 * status note. If the backend palette strings are renamed to the DRD names
 * later, drop the alias rows.)
 */
const API_COLOR_TO_TOKEN: Record<string, string> = {
  indigo: 'bg-avatar-purple',
  violet: 'bg-avatar-blue',
  amber: 'bg-avatar-amber',
  emerald: 'bg-avatar-green',
  rose: 'bg-avatar-rose',
  sky: 'bg-avatar-cyan',
  // Accept DRD names too, in case a caller passes a token name directly.
  purple: 'bg-avatar-purple',
  blue: 'bg-avatar-blue',
  green: 'bg-avatar-green',
  cyan: 'bg-avatar-cyan',
};

const DRD_PALETTE = [
  'bg-avatar-purple',
  'bg-avatar-blue',
  'bg-avatar-green',
  'bg-avatar-amber',
  'bg-avatar-rose',
  'bg-avatar-cyan',
] as const;

/**
 * Client-side fallback when only an id is known (no server `avatar_color`).
 * Uses a simple stable string hash — NOT the backend's SHA-256, so prefer the
 * server-provided `color` whenever available to stay in sync.
 */
export function colorClassForId(id: string): string {
  let hash = 0;
  for (let i = 0; i < id.length; i++) hash = (hash * 31 + id.charCodeAt(i)) >>> 0;
  // Non-null: modulo by a non-empty tuple length always yields a valid index.
  return DRD_PALETTE[hash % DRD_PALETTE.length] as string;
}

const avatar = cva(
  'inline-flex shrink-0 items-center justify-center rounded-full font-semibold text-white',
  {
    variants: {
      size: {
        sm: 'h-6 w-6 text-[10px]', // 24px — list rows
        header: 'h-7 w-7 text-[10px]', // 28px — header icon area
        md: 'h-8 w-8 text-xs', // 32px — cards, comments
        lg: 'h-10 w-10 text-sm', // 40px — profile
      },
    },
    defaultVariants: { size: 'md' },
  },
);

export interface AvatarProps extends VariantProps<typeof avatar> {
  initials: string;
  /** Server `avatar_color` (preferred) or a DRD token name. */
  color?: string;
  /** Fallback id used to derive a color when `color` is absent. */
  id?: string;
  /** Accessible label; defaults to the initials. */
  label?: string;
  className?: string;
}

export function Avatar({ initials, color, id, size, label, className }: AvatarProps) {
  const colorClass =
    (color ? API_COLOR_TO_TOKEN[color] : undefined) ??
    (id ? colorClassForId(id) : undefined) ??
    'bg-avatar-blue';
  return (
    <span
      className={cn(avatar({ size }), colorClass, className)}
      role="img"
      aria-label={label ?? initials}
    >
      <span aria-hidden>{initials}</span>
    </span>
  );
}
