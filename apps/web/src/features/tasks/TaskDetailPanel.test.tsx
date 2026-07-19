import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { apiClient } from '@/api/client';
import type { Comment, TaskDetail } from '@/api/types';
import { axe } from '@/test/axe';
import { renderWithProviders } from '@/test/render';
import { TaskDetailPanel } from './TaskDetailPanel';

// `role` is a TaskDetailPanel prop (user role), not an ARIA attribute.
const OWNER = 'owner' as const;
const VIEWER = 'viewer' as const;

const owner = {
  id: 'u1',
  email: 'o@aurora.example.com',
  display_name: 'Olivia',
  initials: 'O',
  avatar_color: 'indigo',
  role: 'owner',
  workspace_id: 'w1',
};

const taskDetail: TaskDetail = {
  id: 't1',
  title: 'Fix the login bug',
  status: 'todo',
  priority: 'high',
  due_date: null,
  assignee: null,
  labels: [],
  comment_count: 1,
  project: { id: 'p1', name: 'Website' },
  description: 'Read the docs first',
  created_at: '2026-06-01T10:00:00Z',
  updated_at: '2026-06-01T10:00:00Z',
};

const comment: Comment = {
  id: 'c1',
  body: 'First comment for @bob',
  author: { id: 'u2', display_name: 'Bob', initials: 'B', avatar_color: 'sky', deleted: false },
  mentions: [{ id: 'u2', display_name: 'Bob', initials: 'B', avatar_color: 'sky', deleted: false }],
  created_at: '2026-06-02T10:00:00Z',
  updated_at: '2026-06-02T10:00:00Z',
};

function mockApi() {
  vi.spyOn(apiClient, 'get').mockImplementation(((path: string) => {
    if (path === '/tasks/t1') return Promise.resolve(taskDetail);
    if (path === '/tasks/t1/comments') return Promise.resolve({ comments: [comment] });
    if (path === '/projects/p1/access') return Promise.resolve({ members: [] });
    if (path === '/labels') return Promise.resolve({ labels: [] });
    if (path === '/auth/me') return Promise.resolve(owner);
    return Promise.reject(new Error(`unexpected GET ${path}`));
  }) as typeof apiClient.get);
}

afterEach(() => vi.restoreAllMocks());

describe('TaskDetailPanel', () => {
  it('renders the task, description and comments with no axe violations', async () => {
    mockApi();
    const { container, findByText, getByText } = renderWithProviders(
      <TaskDetailPanel projectId="p1" taskId="t1" role={OWNER} onClose={vi.fn()} />,
    );
    await findByText('Fix the login bug');
    expect(getByText('Read the docs first')).toBeInTheDocument();
    expect(getByText(/First comment for/)).toBeInTheDocument();
    // Resolved @mentions render as teal chips (spans, not links).
    const chip = getByText('@bob');
    expect(chip.tagName).toBe('SPAN');
    expect(chip.className).toContain('text-primary');
    expect(getByText('To Do')).toBeInTheDocument();
    expect(await axe(container)).toHaveNoViolations();
  });

  it('is read-only for viewers (no comment box)', async () => {
    mockApi();
    const { findByText, queryByRole } = renderWithProviders(
      <TaskDetailPanel projectId="p1" taskId="t1" role={VIEWER} onClose={vi.fn()} />,
    );
    await findByText('Fix the login bug');
    expect(queryByRole('button', { name: 'Comment' })).toBeNull();
  });

  it('closes on Escape and on backdrop click', async () => {
    mockApi();
    const onClose = vi.fn();
    const { findByText, getByLabelText } = renderWithProviders(
      <TaskDetailPanel projectId="p1" taskId="t1" role={OWNER} onClose={onClose} />,
    );
    await findByText('Fix the login bug');
    await userEvent.keyboard('{Escape}');
    expect(onClose).toHaveBeenCalledTimes(1);
    await userEvent.click(getByLabelText('Close task details'));
    expect(onClose).toHaveBeenCalledTimes(2);
  });

  it('commits an edited title', async () => {
    mockApi();
    const patch = vi
      .spyOn(apiClient, 'patch')
      .mockResolvedValue({ ...taskDetail, title: 'New title' });
    const user = userEvent.setup();
    const { findByText, getByRole, getByLabelText } = renderWithProviders(
      <TaskDetailPanel projectId="p1" taskId="t1" role={OWNER} onClose={vi.fn()} />,
    );
    await user.click(await findByText('Fix the login bug'));
    const input = getByLabelText('Title');
    await user.clear(input);
    await user.type(input, 'New title{Enter}');
    expect(patch).toHaveBeenCalledWith('/tasks/t1', { title: 'New title' });
    // Title button is back (edit mode exited).
    expect(getByRole('button', { name: 'New title' })).toBeInTheDocument();
  });

  it('commits an edited description on blur', async () => {
    mockApi();
    const patch = vi.spyOn(apiClient, 'patch').mockResolvedValue(taskDetail);
    const user = userEvent.setup();
    const { findByText, getByLabelText } = renderWithProviders(
      <TaskDetailPanel projectId="p1" taskId="t1" role={OWNER} onClose={vi.fn()} />,
    );
    await user.click(await findByText('Read the docs first'));
    const textarea = getByLabelText('Description');
    await user.clear(textarea);
    await user.type(textarea, 'Updated notes');
    await user.tab(); // blur commits
    expect(patch).toHaveBeenCalledWith('/tasks/t1', { description: 'Updated notes' });
  });

  it('changes status via the status select', async () => {
    mockApi();
    const patch = vi.spyOn(apiClient, 'patch').mockResolvedValue(taskDetail);
    const user = userEvent.setup({ pointerEventsCheck: 0 });
    const { findByText, getByLabelText, getByRole } = renderWithProviders(
      <TaskDetailPanel projectId="p1" taskId="t1" role={OWNER} onClose={vi.fn()} />,
    );
    await findByText('Fix the login bug');
    await user.click(getByLabelText('Change status'));
    await user.click(getByRole('menuitem', { name: 'In Progress' }));
    expect(patch).toHaveBeenCalledWith('/tasks/t1/status', { status: 'in_progress' });
  });

  it('posts a comment', async () => {
    mockApi();
    const post = vi
      .spyOn(apiClient, 'post')
      .mockResolvedValue({ ...comment, id: 'c2', body: 'Nice' });
    const user = userEvent.setup();
    const { findByText, getByPlaceholderText, getByRole } = renderWithProviders(
      <TaskDetailPanel projectId="p1" taskId="t1" role={OWNER} onClose={vi.fn()} />,
    );
    await findByText('Fix the login bug');
    await user.type(getByPlaceholderText('Write a comment… use @ to mention'), 'Nice');
    await user.click(getByRole('button', { name: 'Comment' }));
    expect(post).toHaveBeenCalledWith('/tasks/t1/comments', { body: 'Nice' });
  });
});
