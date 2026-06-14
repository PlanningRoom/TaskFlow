import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { apiClient } from '@/api/client';
import { axe } from '@/test/axe';
import { renderWithProviders } from '@/test/render';
import { ProjectView } from './ProjectView';

const navigate = vi.fn();
vi.mock('@tanstack/react-router', () => ({
  Link: ({ to, children, ...props }: { to: string; children: React.ReactNode }) => (
    <a href={to} {...props}>
      {children}
    </a>
  ),
  useNavigate: () => navigate,
}));

const member = {
  id: 'u1',
  email: 'm@aurora.example.com',
  display_name: 'Mara Member',
  initials: 'MM',
  avatar_color: 'sky',
  role: 'member',
  workspace_id: 'w1',
};

const tasks = [
  {
    id: 't1',
    title: 'Fix the login bug',
    status: 'in_progress',
    priority: 'high',
    due_date: null,
    assignee: null,
    labels: [],
    comment_count: 0,
    project: { id: 'p1', name: 'Website Redesign' },
  },
];

function mockApi() {
  vi.spyOn(apiClient, 'get').mockImplementation(((path: string) => {
    if (path === '/auth/me') return Promise.resolve(member);
    if (path === '/workspaces/me/members') return Promise.resolve({ members: [] });
    if (path === '/labels') return Promise.resolve({ labels: [] });
    if (path === '/projects/p1/tasks') return Promise.resolve({ tasks, next_cursor: null });
    if (path === '/projects/p1/access') return Promise.resolve({ members: [] });
    if (path === '/tasks/t1')
      return Promise.resolve({ ...tasks[0], description: null, created_at: '', updated_at: '' });
    if (path === '/tasks/t1/comments') return Promise.resolve({ comments: [] });
    return Promise.reject(new Error(`unexpected GET ${path}`));
  }) as typeof apiClient.get);
}

afterEach(() => {
  vi.restoreAllMocks();
  navigate.mockClear();
});

describe('ProjectView', () => {
  it('renders the sub-nav and the board with tasks', async () => {
    mockApi();
    const { findByText, getByRole } = renderWithProviders(
      <ProjectView projectId="p1" view="board" search={{}} />,
    );
    expect(await findByText('Fix the login bug')).toBeInTheDocument();
    // Board/List view toggle from the sub-nav.
    expect(getByRole('button', { name: 'Board' })).toHaveAttribute('aria-pressed', 'true');
    expect(getByRole('button', { name: 'List' })).toHaveAttribute('aria-pressed', 'false');
  });

  it('navigates when switching to the list view', async () => {
    mockApi();
    const { findByText, getByRole } = renderWithProviders(
      <ProjectView projectId="p1" view="board" search={{}} />,
    );
    await findByText('Fix the login bug');
    getByRole('button', { name: 'List' }).click();
    expect(navigate).toHaveBeenCalledWith(
      expect.objectContaining({ to: '/projects/$projectId/list', params: { projectId: 'p1' } }),
    );
  });

  it('clears filters from the chip bar', async () => {
    mockApi();
    const { findByText, getByRole } = renderWithProviders(
      <ProjectView projectId="p1" view="board" search={{ status: ['todo'], sort: 'priority' }} />,
    );
    await findByText('Fix the login bug');
    getByRole('button', { name: 'Clear all' }).click();
    expect(navigate).toHaveBeenCalledWith(
      expect.objectContaining({ search: { sort: 'priority' } }),
    );
  });

  it('opens the task panel for a taskId and closes it on Escape', async () => {
    mockApi();
    const user = userEvent.setup();
    const { findByRole } = renderWithProviders(
      <ProjectView projectId="p1" view="board" search={{}} taskId="t1" />,
    );
    // The detail panel mounts as a dialog over the board.
    await findByRole('dialog', { name: 'Task details' });
    await user.keyboard('{Escape}');
    expect(navigate).toHaveBeenCalledWith(
      expect.objectContaining({ to: '/projects/$projectId/board', params: { projectId: 'p1' } }),
    );
  });

  it('has no axe violations', async () => {
    mockApi();
    const { container, findByText } = renderWithProviders(
      <ProjectView projectId="p1" view="board" search={{}} />,
    );
    await findByText('Fix the login bug');
    expect(await axe(container)).toHaveNoViolations();
  });
});
