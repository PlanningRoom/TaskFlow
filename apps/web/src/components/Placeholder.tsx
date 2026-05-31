import { FormattedMessage } from 'react-intl';

/**
 * Temporary landing page for Phase F1. Its only job is to prove the skeleton is
 * wired: design tokens render (warm-neutral palette, Inter, teal accent),
 * react-intl resolves messages, and the router mounts a route. Replaced by the
 * real app shell + routes in Phase F4.
 */
export function Placeholder() {
  return (
    <main className="grid min-h-dvh place-items-center bg-bg-app px-6 text-center">
      <div className="max-w-md rounded-lg bg-bg-card p-8 shadow-modal">
        <div className="mx-auto mb-4 grid h-8 w-8 place-items-center rounded-sm bg-logo text-bg-card">
          <span aria-hidden className="text-base font-bold">
            ✓
          </span>
        </div>
        <h1 className="mb-2 text-2xl font-semibold text-text-primary">
          <FormattedMessage id="app.name" />
        </h1>
        <p className="text-sm text-text-secondary">
          <FormattedMessage id="app.skeletonReady" />
        </p>
      </div>
    </main>
  );
}
