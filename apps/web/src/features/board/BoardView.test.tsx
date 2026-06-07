import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { apiClient } from '@/api/client';
import type { TaskSummary } from '@/api/types';
import { axe } from '@/test/axe';
import { renderWithProviders } from '@/test/render';
import { BoardView } from './BoardView';

vi.mock('@tanstack/react-router', () => ({ useNavigate: () => vi.fn() }));

// `role` here is a BoardView prop (the user role), not an ARIA attribute — bind
// it via consts so biome's a11y lint doesn't read the literal as a DOM role.
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

function task(overrides: Partial<TaskSummary> = {}): TaskSummary {
  return {
    id: 't1',
    title: 'Fix the login bug',
    status: 'todo',
    priority: 'high',
    due_date: null,
    assignee: null,
    labels: [],
    comment_count: 0,
    project: { id: 'p1', name: 'Website' },
    ...overrides,
  };
}

function mockApi(tasks: TaskSummary[], role = 'owner') {
  vi.spyOn(apiClient, 'get').mockImplementation(((path: string) => {
    if (path === '/projects/p1/tasks') return Promise.resolve({ tasks, next_cursor: null });
    if (path === '/auth/me') return Promise.resolve({ ...owner, role });
    if (path === '/projects/p1/access') return Promise.resolve({ members: [] });
    if (path === '/labels') return Promise.resolve({ labels: [] });
    return Promise.reject(new Error(`unexpected GET ${path}`));
  }) as typeof apiClient.get);
}

const noop = () => {};

afterEach(() => vi.restoreAllMocks());

describe('BoardView', () => {
  it('renders columns and a task with no axe violations', async () => {
    mockApi([task()]);
    const { container, findByText, getByText } = renderWithProviders(
      <BoardView
        projectId="p1"
        params={{}}
        search={{}}
        role={OWNER}
        onOpenTask={noop}
        onClearFilters={noop}
      />,
    );
    await findByText('Fix the login bug');
    expect(getByText('To Do')).toBeInTheDocument();
    expect(getByText('Backlog')).toBeInTheDocument();
    expect(await axe(container)).toHaveNoViolations();
  });

  it('shows the empty state with a create button for editors', async () => {
    mockApi([]);
    const { findByText, getByRole } = renderWithProviders(
      <BoardView
        projectId="p1"
        params={{}}
        search={{}}
        role={OWNER}
        onOpenTask={noop}
        onClearFilters={noop}
      />,
    );
    expect(await findByText('This project has no tasks yet.')).toBeInTheDocument();
    expect(getByRole('button', { name: 'Create a task' })).toBeInTheDocument();
  });

  it('hides the create button from viewers', async () => {
    mockApi([], 'viewer');
    const { findByText, queryByRole } = renderWithProviders(
      <BoardView
        projectId="p1"
        params={{}}
        search={{}}
        role={VIEWER}
        onOpenTask={noop}
        onClearFilters={noop}
      />,
    );
    await findByText('This project has no tasks yet.');
    expect(queryByRole('button', { name: 'Create a task' })).toBeNull();
  });

  it('shows a filtered-empty state that clears filters', async () => {
    mockApi([]);
    const onClearFilters = vi.fn();
    const { findByText, getByRole } = renderWithProviders(
      <BoardView
        projectId="p1"
        params={{ status: ['todo'] }}
        search={{ status: ['todo'] }}
        role={OWNER}
        onOpenTask={noop}
        onClearFilters={onClearFilters}
      />,
    );
    expect(await findByText('No tasks match these filters.')).toBeInTheDocument();
    await userEvent.click(getByRole('button', { name: 'Clear filters' }));
    expect(onClearFilters).toHaveBeenCalled();
  });
});
