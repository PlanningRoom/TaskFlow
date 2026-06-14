import { describe, expect, it, vi } from 'vitest';
import { createRealtimeDispatcher } from './dispatcher';
import type { RealtimeEnvelope } from './types';

function envelope(type: string, payload: Record<string, unknown> = {}): RealtimeEnvelope {
  return {
    type,
    workspace_id: 'w1',
    project_id: null,
    payload,
    emitted_at: '2026-06-14T00:00:00Z',
  };
}

function setup() {
  const invalidateQueries = vi.fn();
  const requestRefresh = vi.fn();
  const announce = vi.fn();
  const dispatch = createRealtimeDispatcher({
    queryClient: { invalidateQueries },
    requestRefresh,
    announce,
  });
  // Collected list of invalidated keys for convenient assertions.
  const keys = () => invalidateQueries.mock.calls.map((c) => c[0].queryKey);
  return { dispatch, invalidateQueries, requestRefresh, announce, keys };
}

describe('createRealtimeDispatcher', () => {
  it('task.created invalidates the project task list and dashboard', () => {
    const { dispatch, keys } = setup();
    dispatch(envelope('task.created', { task_id: 't1', project_id: 'p1', status: 'backlog' }));
    expect(keys()).toContainEqual(['tasks', 'p1']);
    expect(keys()).toContainEqual(['dashboard']);
  });

  it('task.updated invalidates the single task, list, and dashboard', () => {
    const { dispatch, keys } = setup();
    dispatch(envelope('task.updated', { task_id: 't1', project_id: 'p1', status: 'done' }));
    expect(keys()).toContainEqual(['task', 't1']);
    expect(keys()).toContainEqual(['tasks', 'p1']);
    expect(keys()).toContainEqual(['dashboard']);
  });

  it('task.status_changed invalidates the single task and list', () => {
    const { dispatch, keys } = setup();
    dispatch(
      envelope('task.status_changed', { task_id: 't1', project_id: 'p1', from: 'a', to: 'b' }),
    );
    expect(keys()).toContainEqual(['task', 't1']);
    expect(keys()).toContainEqual(['tasks', 'p1']);
  });

  it('comment.created invalidates the task prefix (detail + comments)', () => {
    const { dispatch, keys } = setup();
    dispatch(envelope('comment.created', { comment_id: 'c1', task_id: 't1', project_id: 'p1' }));
    expect(keys()).toContainEqual(['task', 't1']);
  });

  it('notification.created invalidates notifications and announces only mentions', () => {
    const { dispatch, keys, announce } = setup();
    dispatch(
      envelope('notification.created', {
        notification_id: 'n1',
        recipient_id: 'u1',
        event_type: 'mention',
      }),
    );
    expect(keys()).toContainEqual(['notifications']);
    expect(announce).toHaveBeenCalledWith('mention');
  });

  it('notification.created updates the badge silently for non-mention kinds', () => {
    const { dispatch, keys, announce } = setup();
    dispatch(
      envelope('notification.created', {
        notification_id: 'n2',
        recipient_id: 'u1',
        event_type: 'task_assigned',
      }),
    );
    expect(keys()).toContainEqual(['notifications']);
    expect(announce).not.toHaveBeenCalled();
  });

  it('control.access_changed invalidates projects and requests a re-subscribe', () => {
    const { dispatch, keys, requestRefresh } = setup();
    dispatch(envelope('control.access_changed', { project_id: 'p1', change: 'granted' }));
    expect(keys()).toContainEqual(['projects']);
    expect(keys()).toContainEqual(['dashboard']);
    expect(requestRefresh).toHaveBeenCalledOnce();
  });

  it('activity always invalidates the activity feed', () => {
    const { dispatch, keys } = setup();
    dispatch(envelope('activity', { event_type: 'task.created', project_id: 'p1' }));
    expect(keys()).toContainEqual(['activity']);
  });

  it('activity maps project.* to projects + dashboard + project detail', () => {
    const { dispatch, keys } = setup();
    dispatch(envelope('activity', { event_type: 'project.updated', project_id: 'p1' }));
    expect(keys()).toContainEqual(['projects']);
    expect(keys()).toContainEqual(['project', 'p1']);
    expect(keys()).toContainEqual(['dashboard']);
  });

  it('activity maps workspace.label.* to labels, invitation.* to invitations+members', () => {
    const { dispatch, keys } = setup();
    dispatch(envelope('activity', { event_type: 'workspace.label.created' }));
    expect(keys()).toContainEqual(['labels']);
    dispatch(envelope('activity', { event_type: 'workspace.invitation.accepted' }));
    expect(keys()).toContainEqual(['invitations']);
    expect(keys()).toContainEqual(['members']);
  });

  it('ignores unknown event types without invalidating', () => {
    const { dispatch, invalidateQueries } = setup();
    dispatch(envelope('something.new', { foo: 'bar' }));
    expect(invalidateQueries).not.toHaveBeenCalled();
  });
});
