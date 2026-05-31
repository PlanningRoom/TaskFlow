import type { ReactNode } from 'react';
import { Logo } from '@/components/shell/Logo';

/**
 * Centered card shell for the unauthenticated screens (DRD §8.1): logo above a
 * heading + optional subtext, rendered on the login background OUTSIDE the app
 * shell. Shared by login / signup / accept-invitation / password-reset so the
 * layout, spacing, and max width stay identical across the auth journey.
 */
export function AuthCard({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle?: string;
  children: ReactNode;
}) {
  return (
    <div className="grid min-h-dvh place-items-center bg-bg-login px-4">
      <div className="w-full max-w-sm rounded-lg bg-bg-card p-8 shadow-modal">
        <div className="mb-6 flex justify-center">
          <Logo size="login" />
        </div>
        <h1 className="text-center text-xl font-semibold text-text-primary">{title}</h1>
        {subtitle ? (
          <p className="mt-2 mb-7 text-center text-sm text-text-secondary">{subtitle}</p>
        ) : null}
        {children}
      </div>
    </div>
  );
}
