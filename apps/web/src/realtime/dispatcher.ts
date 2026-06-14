import type { QueryClient } from '@tanstack/react-query';
import type { RealtimeEnvelope } from './types';

/**
 * Realtime dispatcher (Phase H1, TDD §10.3). Translates an inbound envelope into
 * TanStack Query cache invalidations using the app's real query keys. Because
 * the backend envelopes carry IDs only (not full DTOs), we invalidate and let
 * the active query refetch rather than `setQueryData` — consistent with the
 * reconcile-from-DB semantics of TDD §10.4.
 *
 * Key prefixes do the heavy lifting: invalidating `['task', id]` also matches
 * `['task', id, 'comments']`; `['notifications']` covers `['notifications',
 * 'unread-count']`; `['tasks', projectId]` covers every filter/sort variant.
 */

export interface DispatcherDeps {
  queryClient: Pick<QueryClient, 'invalidateQueries'>;
  /** Ask the server to re-enumerate project subscriptions (access changed). */
  requestRefresh: () => void;
  /** Announce a cross-page event to the aria-live region (TDD §10.3 whitelist). */
  announce?: (kind: 'mention') => void;
}

function str(payload: Record<string, unknown>, key: string): string | undefined {
  const value = payload[key];
  return typeof value === 'string' ? value : undefined;
}

export function createRealtimeDispatcher(deps: DispatcherDeps) {
  const { queryClient, requestRefresh, announce } = deps;
  const invalidate = (queryKey: readonly unknown[]) => {
    void queryClient.invalidateQueries({ queryKey });
  };

  /** Extra invalidations driven by the inner event_type of an `activity` event. */
  function handleActivity(envelope: RealtimeEnvelope): void {
    invalidate(['activity']);
    const inner = str(envelope.payload, 'event_type') ?? '';
    const projectId = envelope.project_id ?? str(envelope.payload, 'project_id');

    if (inner.startsWith('project.')) {
      invalidate(['projects']);
      invalidate(['dashboard']);
      if (projectId) invalidate(['project', projectId]);
    } else if (inner.startsWith('workspace.label.')) {
      invalidate(['labels']);
    } else if (inner.startsWith('workspace.invitation.')) {
      invalidate(['invitations']);
      invalidate(['members']); // an accepted invitation adds a member
    } else if (inner.startsWith('workspace.user.')) {
      invalidate(['members']);
    } else if (inner === 'workspace.updated') {
      invalidate(['workspace']);
    }
    // task.* inner activity is already covered by the dedicated task.* events.
  }

  return function dispatch(envelope: RealtimeEnvelope): void {
    const { payload } = envelope;
    const projectId = envelope.project_id ?? str(payload, 'project_id');
    const taskId = str(payload, 'task_id');

    switch (envelope.type) {
      case 'task.created':
        if (projectId) invalidate(['tasks', projectId]);
        invalidate(['dashboard']);
        break;

      case 'task.updated':
      case 'task.status_changed':
        if (taskId) invalidate(['task', taskId]);
        if (projectId) invalidate(['tasks', projectId]);
        invalidate(['dashboard']);
        break;

      case 'comment.created':
        // Prefix invalidation refreshes both the comment list and the task
        // detail (comment count).
        if (taskId) invalidate(['task', taskId]);
        break;

      case 'notification.created':
        invalidate(['notifications']);
        // Per TDD §10.3 only @mentions are announced cross-page; other kinds
        // (assignment, status, comment) update the badge silently.
        if (str(payload, 'event_type') === 'mention') announce?.('mention');
        break;

      case 'activity':
        handleActivity(envelope);
        break;

      case 'control.access_changed':
        invalidate(['projects']);
        invalidate(['dashboard']);
        requestRefresh();
        break;

      default:
        // Forward-compatible: unknown event types are ignored.
        break;
    }
  };
}
