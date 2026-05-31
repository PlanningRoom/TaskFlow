import { cn } from '@/lib/cn';

/**
 * Logo & brand mark (DRD §5): a rounded teal square holding a white
 * check-in-box glyph, plus the "TaskFlow" wordmark. `size` switches between the
 * sidebar treatment (28px mark / 16px wordmark) and the login treatment
 * (32px mark / 22px wordmark). `markOnly` is used by the collapsed sidebar.
 */
export interface LogoProps {
  size?: 'sidebar' | 'login';
  markOnly?: boolean;
  className?: string;
}

export function Logo({ size = 'sidebar', markOnly = false, className }: LogoProps) {
  const isLogin = size === 'login';
  const markPx = isLogin ? 32 : 28;
  return (
    <span className={cn('inline-flex items-center gap-2.5', className)}>
      <span
        className="inline-flex items-center justify-center rounded-[7px] bg-logo text-white"
        style={{ width: markPx, height: markPx }}
        aria-hidden
      >
        <svg
          width={markPx * 0.6}
          height={markPx * 0.6}
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth={2.5}
          strokeLinecap="round"
          strokeLinejoin="round"
          role="img"
          aria-label="TaskFlow"
        >
          <title>TaskFlow</title>
          <polyline points="9 11 12 14 22 4" />
          <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11" />
        </svg>
      </span>
      {!markOnly && (
        <span className={cn('font-bold text-text-primary', isLogin ? 'text-[22px]' : 'text-base')}>
          TaskFlow
        </span>
      )}
    </span>
  );
}
