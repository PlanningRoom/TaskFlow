import { useEffect, useState } from 'react';
import { useMediaQuery } from '@/hooks/useMediaQuery';
import { RealtimeStatusIndicator } from '@/realtime/RealtimeStatusIndicator';
import { Header } from './Header';
import { Sidebar } from './Sidebar';

/**
 * AppShell (DRD §6.1) — the persistent three-zone layout for authenticated
 * routes. Header (52px) spans the top; sidebar (240px, or a 60px rail on
 * tablet) and the scrolling content area sit below it.
 *
 * Responsive (DRD §6.2 / §15): full sidebar ≥1024px, icon-only rail on tablet
 * (768–1023px), and below 768px the sidebar is hidden behind a hamburger in
 * the header that opens it as an overlay (backdrop / Esc / link-click close).
 */
export interface AppShellProps {
  breadcrumb: string[];
  children: React.ReactNode;
}

export function AppShell({ breadcrumb, children }: AppShellProps) {
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  // Tablet rail; jsdom (no matchMedia) falls back to the full sidebar.
  const isTablet = useMediaQuery('(min-width: 768px) and (max-width: 1023px)');

  useEffect(() => {
    if (!mobileNavOpen) return;
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') setMobileNavOpen(false);
    };
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, [mobileNavOpen]);

  return (
    <div className="flex h-dvh flex-col">
      <Header breadcrumb={breadcrumb} onMenuClick={() => setMobileNavOpen(true)} />
      <div className="flex min-h-0 flex-1">
        {/* Docked sidebar (hidden below md, where the overlay takes over). */}
        {!mobileNavOpen && (
          <div className="hidden md:block">
            <Sidebar collapsed={isTablet} />
          </div>
        )}
        <main className="min-w-0 flex-1 overflow-y-auto bg-bg-app">{children}</main>
      </div>
      {mobileNavOpen ? (
        <div
          className="fixed inset-0 z-50 md:hidden"
          role="dialog"
          aria-modal="true"
          aria-label="Navigation"
        >
          <button
            type="button"
            className="absolute inset-0 w-full bg-black/40"
            aria-label="Close navigation"
            onClick={() => setMobileNavOpen(false)}
          />
          <div
            className="absolute inset-y-0 start-0 shadow-card-hover"
            // Following any sidebar link is a navigation — dismiss the overlay.
            onClickCapture={(event) => {
              if ((event.target as HTMLElement).closest('a')) setMobileNavOpen(false);
            }}
          >
            <Sidebar />
          </div>
        </div>
      ) : null}
      <RealtimeStatusIndicator />
    </div>
  );
}
