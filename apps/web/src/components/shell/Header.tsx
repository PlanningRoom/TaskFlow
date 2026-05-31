import { Avatar } from '@/components/ui/Avatar';
import { Bell, Search } from '@/components/ui/icons';
import { useCurrentUser } from '@/hooks/useCurrentUser';

/**
 * Global header (DRD §6.4). 52px bar: breadcrumb (left), 260px search input
 * with ⌘K hint (pushed right), notification bell with unread badge, and the
 * user avatar. Search + dropdowns are non-functional placeholders here; the
 * search overlay is Phase G7 and the user menu is wired with the shell screens.
 */
export interface HeaderProps {
  /** Breadcrumb segments; the last is the current page (rendered emphasized). */
  breadcrumb: string[];
  unreadCount?: number;
}

export function Header({ breadcrumb, unreadCount = 0 }: HeaderProps) {
  const { data: user } = useCurrentUser();

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

      <div className="relative ms-auto w-[260px]">
        <Search
          size={15}
          strokeWidth={2}
          className="pointer-events-none absolute inset-y-0 start-2.5 my-auto text-text-tertiary"
        />
        <input
          type="text"
          placeholder="Search tasks..."
          aria-label="Search tasks"
          className="w-full rounded-sm border border-border bg-bg-surface py-[7px] ps-8 pe-10 text-[13px] text-text-primary placeholder:text-text-tertiary focus-visible:border-primary focus-visible:bg-bg-card focus-visible:outline-none focus-visible:ring-[3px] focus-visible:ring-primary"
        />
        <kbd className="pointer-events-none absolute inset-y-0 end-2 my-auto h-fit text-[11px] text-text-tertiary">
          ⌘K
        </kbd>
      </div>

      <div className="flex items-center gap-1.5">
        <button
          type="button"
          className="relative grid h-[34px] w-[34px] place-items-center rounded-sm text-text-secondary hover:bg-bg-hover hover:text-text-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
          aria-label={`Notifications${unreadCount ? ` (${unreadCount} unread)` : ''}`}
        >
          <Bell size={19} strokeWidth={1.75} />
          {unreadCount > 0 && (
            <span className="absolute -end-0.5 -top-0.5 grid h-4 min-w-4 place-items-center rounded-full bg-semantic-error px-1 text-[9px] font-bold text-white">
              {unreadCount}
            </span>
          )}
        </button>
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
