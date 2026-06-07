import { Link } from '@tanstack/react-router';
import { Avatar } from '@/components/ui/Avatar';
import { Bell } from '@/components/ui/icons';
import { useUnreadCount } from '@/features/notifications/useNotifications';
import { SearchOverlay } from '@/features/search/SearchOverlay';
import { useCurrentUser } from '@/hooks/useCurrentUser';

/**
 * Global header (DRD §6.4). 52px bar: breadcrumb (left), the global search
 * overlay (Phase G7), the notification bell with live unread badge (Phase G6),
 * and the user avatar.
 */
export interface HeaderProps {
  /** Breadcrumb segments; the last is the current page (rendered emphasized). */
  breadcrumb: string[];
}

export function Header({ breadcrumb }: HeaderProps) {
  const { data: user } = useCurrentUser();
  const { data: unread } = useUnreadCount();
  const unreadCount = unread?.count ?? 0;

  return (
    <header className="flex h-[52px] shrink-0 items-center gap-4 border-b border-border bg-bg-card px-6">
      <nav aria-label="Breadcrumb" className="flex items-center gap-1.5 text-[13px]">
        {breadcrumb.map((seg, i) => {
          const last = i === breadcrumb.length - 1;
          return (
            <span key={seg} className="flex items-center gap-1.5">
              {i > 0 && <span className="text-text-tertiary">/</span>}
              <span
                className={last ? 'font-medium text-text-primary' : 'text-text-secondary'}
                aria-current={last ? 'page' : undefined}
              >
                {seg}
              </span>
            </span>
          );
        })}
      </nav>

      <div className="ms-auto">
        <SearchOverlay />
      </div>

      <div className="flex items-center gap-1.5">
        <Link
          to="/notifications"
          className="relative grid h-[34px] w-[34px] place-items-center rounded-sm text-text-secondary hover:bg-bg-hover hover:text-text-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
          aria-label={`Notifications${unreadCount ? ` (${unreadCount} unread)` : ''}`}
        >
          <Bell size={19} strokeWidth={1.75} />
          {unreadCount > 0 && (
            <span className="absolute -end-0.5 -top-0.5 grid h-4 min-w-4 place-items-center rounded-full bg-semantic-error px-1 text-[9px] font-bold text-white">
              {unreadCount}
            </span>
          )}
        </Link>
        {user && (
          <button
            type="button"
            className="rounded-full focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
            aria-label="User menu"
          >
            <Avatar size="header" initials={user.initials} color={user.avatar_color} id={user.id} />
          </button>
        )}
      </div>
    </header>
  );
}
