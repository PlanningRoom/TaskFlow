import { Logo } from '@/components/shell/Logo';

/**
 * Placeholder for the unauthenticated screens (login / signup / accept
 * invitation), rendered OUTSIDE the app shell on the login background (DRD
 * §8.1). Part G1 replaces these with the real forms.
 */
export function AuthPlaceholder({ title }: { title: string }) {
  return (
    <div className="grid min-h-dvh place-items-center bg-bg-login px-4">
      <div className="w-full max-w-sm rounded-lg bg-bg-card p-8 shadow-modal">
        <div className="mb-6 flex justify-center">
          <Logo size="login" />
        </div>
        <h1 className="text-center text-xl font-semibold text-text-primary">{title}</h1>
        <p className="mt-2 text-center text-sm text-text-secondary">This screen is coming soon.</p>
      </div>
    </div>
  );
}
