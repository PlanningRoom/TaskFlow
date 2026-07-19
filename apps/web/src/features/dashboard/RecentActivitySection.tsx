import { Link } from '@tanstack/react-router';
import { type ReactNode, useMemo } from 'react';
import { useIntl } from 'react-intl';
import type { ActivityEvent } from '@/api/types';
import { Avatar } from '@/components/ui';
import { formatRelativeTime } from '@/lib/relativeTime';
import { DashboardNote, DashboardSection } from './DashboardSection';
import { useDashboardActivity } from './useDashboard';

/**
 * "Recent activity" panel (DRD §8.3 / PRD §13.2). A workspace-scoped feed
 * (first page) of task/comment events, each as an avatar + sentence with a
 * relative timestamp; the row links to the relevant task when resolvable.
 */
export function RecentActivitySection() {
  const intl = useIntl();
  const { data, isPending, isError } = useDashboardActivity();
  const events = data?.events ?? [];

  return (
    <DashboardSection title={intl.formatMessage({ id: 'dashboard.activity.title' })}>
      {isPending ? (
        <DashboardNote>{intl.formatMessage({ id: 'app.loading' })}</DashboardNote>
      ) : isError ? (
        <DashboardNote>{intl.formatMessage({ id: 'dashboard.error' })}</DashboardNote>
      ) : events.length > 0 ? (
        <ul className="flex flex-col">
          {events.map((event) => (
            <ActivityRow key={event.id} event={event} />
          ))}
        </ul>
      ) : (
        <DashboardNote>{intl.formatMessage({ id: 'dashboard.activity.empty' })}</DashboardNote>
      )}
    </DashboardSection>
  );
}

/** Resolve the task this event points at, if both project and task id are known. */
function taskTarget(event: ActivityEvent): { projectId: string; taskId: string } | null {
  if (!event.project) return null;
  const taskId =
    event.subject_type === 'task'
      ? event.subject_id
      : typeof event.metadata?.task_id === 'string'
        ? event.metadata.task_id
        : null;
  return taskId ? { projectId: event.project.id, taskId } : null;
}

/** One feed row (avatar + sentence + relative time). Shared with the project-scope panel. */
export function ActivityRow({ event }: { event: ActivityEvent }) {
  const intl = useIntl();
  const target = useMemo(() => taskTarget(event), [event]);
  const actorName =
    event.actor?.display_name ?? intl.formatMessage({ id: 'dashboard.activity.someone' });

  // Verb phrase + optional teal task label, keyed off the event type.
  let phrase: string;
  let taskLabel: string | null = null;
  switch (event.event_type) {
    case 'task.created':
      phrase = intl.formatMessage({ id: 'dashboard.activity.created' });
      taskLabel = event.detail; // the task title (backend `_detail_for`)
      break;
    case 'task.status_changed':
      phrase = intl.formatMessage(
        { id: 'dashboard.activity.statusChanged' },
        { detail: event.detail ?? '' },
      );
      break;
    case 'task.assigned':
      phrase = intl.formatMessage({ id: 'dashboard.activity.assigned' });
      break;
    case 'task.unassigned':
      phrase = intl.formatMessage({ id: 'dashboard.activity.unassigned' });
      break;
    case 'comment.created':
      phrase = intl.formatMessage({ id: 'dashboard.activity.commented' });
      break;
    default:
      phrase = event.detail ?? intl.formatMessage({ id: 'dashboard.activity.generic' });
  }

  const body = (
    <>
      <Avatar
        size="sm"
        initials={event.actor?.initials ?? '?'}
        color={event.actor?.avatar_color}
        id={event.actor?.id}
        label={actorName}
      />
      <div className="min-w-0 flex-1">
        <p className="text-[13px] text-text-secondary">
          <span className="font-medium text-text-primary">{actorName}</span> {phrase}
          {taskLabel ? <span className="font-medium text-primary"> {taskLabel}</span> : null}
        </p>
        <p className="mt-0.5 text-[11px] text-text-tertiary">
          {event.project ? `${event.project.name} · ` : ''}
          {formatRelativeTime(event.created_at)}
        </p>
      </div>
    </>
  );

  return (
    <li className="border-b border-divider last:border-b-0">
      {target ? (
        <Link
          to="/projects/$projectId/tasks/$taskId"
          params={target}
          className="flex items-start gap-2.5 py-2.5"
        >
          {body}
        </Link>
      ) : (
        <Row>{body}</Row>
      )}
    </li>
  );
}

function Row({ children }: { children: ReactNode }) {
  return <div className="flex items-start gap-2.5 py-2.5">{children}</div>;
}
