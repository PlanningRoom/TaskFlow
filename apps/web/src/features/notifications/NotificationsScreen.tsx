import { Link } from '@tanstack/react-router';
import { useIntl } from 'react-intl';
import type { Notification } from '@/api/types';
import { Avatar, Button } from '@/components/ui';
import { cn } from '@/lib/cn';
import { formatRelativeTime } from '@/lib/relativeTime';
import { useMarkAllRead, useMarkRead, useNotifications } from './useNotifications';

/**
 * Notifications page (DRD §8.6 / PRD §15). Reverse-chronological list with an
 * unread tint + teal dot; a row marks itself read and navigates to the task.
 * "Mark all as read" clears the lot.
 */
export function NotificationsScreen() {
  const intl = useIntl();
  const { data, isPending, isError } = useNotifications();
  const markAll = useMarkAllRead();
  const notifications = data?.notifications ?? [];
  const hasUnread = notifications.some((n) => !n.read);

  return (
    <div className="mx-auto max-w-2xl p-6">
      <div className="mb-4 flex items-center justify-between">
        <h1 className="text-[17px] font-semibold text-text-primary">
          {intl.formatMessage({ id: 'notifications.title' })}
        </h1>
        {hasUnread ? (
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={() => markAll.mutate()}
            disabled={markAll.isPending}
          >
            {intl.formatMessage({ id: 'notifications.markAll' })}
          </Button>
        ) : null}
      </div>

      {isPending ? (
        <p className="text-[13px] text-text-tertiary">
          {intl.formatMessage({ id: 'app.loading' })}
        </p>
      ) : isError ? (
        <p className="text-[13px] text-text-secondary">
          {intl.formatMessage({ id: 'notifications.error' })}
        </p>
      ) : notifications.length === 0 ? (
        <p className="text-[13px] text-text-secondary">
          {intl.formatMessage({ id: 'notifications.empty' })}
        </p>
      ) : (
        <ul className="flex flex-col gap-px">
          {notifications.map((n) => (
            <NotificationRow key={n.id} notification={n} />
          ))}
        </ul>
      )}
    </div>
  );
}

function NotificationRow({ notification: n }: { notification: Notification }) {
  const intl = useIntl();
  const markRead = useMarkRead();
  const actor = n.actor?.display_name ?? intl.formatMessage({ id: 'notifications.someone' });
  const taskTitle = n.task?.title ?? intl.formatMessage({ id: 'notifications.aTask' });

  const lead = intl.formatMessage({ id: `notifications.${verbKey(n.event_type)}` }, { actor });

  const inner = (
    <>
      <span className="mt-1.5 flex w-2 justify-center" aria-hidden>
        {!n.read ? <span className="h-2 w-2 rounded-full bg-primary" /> : null}
      </span>
      <Avatar
        size="sm"
        initials={n.actor?.initials ?? '?'}
        color={n.actor?.avatar_color}
        id={n.actor?.id}
      />
      <span className="min-w-0 flex-1">
        <span className="text-[13px] text-text-secondary">
          {lead} <span className="font-medium text-primary">{taskTitle}</span>
        </span>
        <span className="mt-0.5 block text-[11px] text-text-tertiary">
          {n.project ? `${n.project.name} · ` : ''}
          {formatRelativeTime(n.created_at)}
        </span>
      </span>
    </>
  );

  const className = cn(
    'flex items-start gap-2.5 rounded-sm px-3 py-2.5',
    !n.read ? 'bg-primary-light' : 'hover:bg-bg-hover',
  );

  if (n.task && n.project) {
    return (
      <li>
        <Link
          to="/projects/$projectId/tasks/$taskId"
          params={{ projectId: n.project.id, taskId: n.task.id }}
          onClick={() => !n.read && markRead.mutate(n.id)}
          className={className}
        >
          {inner}
        </Link>
      </li>
    );
  }
  return (
    <li>
      <button
        type="button"
        onClick={() => !n.read && markRead.mutate(n.id)}
        className={cn(className, 'w-full text-start')}
      >
        {inner}
      </button>
    </li>
  );
}

function verbKey(eventType: Notification['event_type']): string {
  switch (eventType) {
    case 'mention':
      return 'mention';
    case 'task_assigned':
      return 'assigned';
    case 'task_status_changed':
      return 'status';
    default:
      return 'commented';
  }
}
