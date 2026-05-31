import { Header } from './Header';
import { Sidebar } from './Sidebar';

/**
 * AppShell (DRD §6.1) — the persistent three-zone layout for authenticated
 * routes. Header (52px) spans the top; sidebar (240px, or a 60px rail on
 * tablet) and the scrolling content area sit below it.
 *
 * Responsive (DRD §6.2): the sidebar is hidden below the `md` breakpoint
 * (<768px) where a hamburger overlay takes over; the icon-only tablet rail and
 * the mobile overlay are layered in with mobile-nav polish in a later phase.
 * The breakpoints render without breaking here.
 */
export interface AppShellProps {
  breadcrumb: string[];
  children: React.ReactNode;
}

export function AppShell({ breadcrumb, children }: AppShellProps) {
  return (
    <div className="flex h-dvh flex-col">
      <Header breadcrumb={breadcrumb} />
      <div className="flex min-h-0 flex-1">
        {/* Desktop sidebar; hidden on mobile (hamburger overlay TBD). */}
        <div className="hidden md:block">
          <Sidebar />
        </div>
        <main className="min-w-0 flex-1 overflow-y-auto bg-bg-app">{children}</main>
      </div>
    </div>
  );
}
