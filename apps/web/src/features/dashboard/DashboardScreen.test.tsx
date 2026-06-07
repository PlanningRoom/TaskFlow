import { waitFor } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { apiClient } from '@/api/client';
import { axe } from '@/test/axe';
import { renderWithProviders } from '@/test/render';
import { DashboardScreen } from './DashboardScreen';

vi.mock('@tanstack/react-router', () => ({
  Link: ({ to, children, ...props }: { to: string; children: React.ReactNode }) => (
    <a href={to} {...props}>
      {children}
    </a>
  ),
  useNavigate: () => vi.fn(),
}));

const owner = {
  id: 'u1',
  email: 'owner@aurora.example.com',
  display_name: 'Olivia Owner',
  initials: 'OO',
  avatar_color: 'indigo',
  role: 'owner',
  workspace_id: 'w1',
};

const recently = new Date(Date.now() - 5 * 60_000).toISOString();

const populated = {
  '/dashboard/my-tasks': {
    groups: [
      {
        project: { id: 'p1', name: 'Website Redesign' },
        tasks: [
          {
            id: 't1',
            title: 'Fix the login bug',
            status: 'in_progress',
            priority: 'high',
            due_date: '2020-01-01', // overdue
            assignee: null,
            labels: [],
            comment_count: 0,
            project: { id: 'p1', name: 'Website Redesign' },
          },
        ],
      },
    ],
  },
  '/dashboard/projects': {
    projects: [
      {
        id: 'p1',
        name: 'Website Redesign',
        color: '#0d9488',
        task_counts: {
          backlog: 1,
          todo: 2,
          in_progress: 3,
          in_review: 0,
          done: 4,
          cancelled: 0,
        },
      },
    ],
  },
  '/activity': {
    events: [
      {
        id: 'a1',
        event_type: 'task.created',
        actor: {
          id: 'u2',
          display_name: 'Bob Builder',
          initials: 'BB',
          avatar_color: 'sky',
          deleted: false,
        },
        subject_type: 'task',
        subject_id: 't1',
        project: { id: 'p1', name: 'Website Redesign' },
        detail: 'Design the homepage',
        metadata: {},
        created_at: recently,
      },
    ],
    next_cursor: null,
  },
};

const empty = {
  '/dashboard/my-tasks': { groups: [] },
  '/dashboard/projects': { projects: [] },
  '/activity': { events: [], next_cursor: null },
};

function mockApi(user: typeof owner, data: Record<string, unknown>) {
  vi.spyOn(apiClient, 'get').mockImplementation(((path: string) => {
    if (path === '/auth/me') return Promise.resolve(user);
    if (path in data) return Promise.resolve(data[path]);
    return Promise.reject(new Error(`unexpected GET ${path}`));
  }) as typeof apiClient.get);
}

afterEach(() => vi.restoreAllMocks());

describe('DashboardScreen', () => {
  it('renders the populated dashboard with no axe violations', async () => {
    mockApi(owner, populated);
    const { container, findByText } = renderWithProviders(<DashboardScreen />);
    await findByText('Fix the login bug');
    expect(await axe(container)).toHaveNoViolations();
  });

  it('shows my tasks grouped by project with overdue dates highlighted', async () => {
    mockApi(owner, populated);
    const { findByText, getByText } = renderWithProviders(<DashboardScreen />);
    await findByText('Fix the login bug');
    expect(getByText('Website Redesign', { selector: 'h3' })).toBeInTheDocument();
    expect(getByText('Jan 1, 2020')).toHaveClass('text-semantic-error');
  });

  it('renders an activity sentence with actor and task title', async () => {
    mockApi(owner, populated);
    const { findByText, getByText } = renderWithProviders(<DashboardScreen />);
    expect(await findByText('Bob Builder')).toBeInTheDocument();
    expect(getByText('Design the homepage')).toBeInTheDocument();
  });

  it('renders projects with a status-count summary', async () => {
    mockApi(owner, populated);
    const { findByText } = renderWithProviders(<DashboardScreen />);
    expect(await findByText('10 tasks · 4 done')).toBeInTheDocument();
  });

  it('shows role-aware empty states and the Owner first-run create prompt', async () => {
    mockApi(owner, empty);
    const { findByText, getByRole } = renderWithProviders(<DashboardScreen />);
    expect(await findByText('No tasks assigned to you yet.')).toBeInTheDocument();
    expect(await findByText('No recent activity.')).toBeInTheDocument();
    expect(await findByText('No projects yet.')).toBeInTheDocument();
    expect(getByRole('button', { name: 'Create your first project' })).toBeInTheDocument();
  });

  it('hides the create prompt from Viewers', async () => {
    mockApi({ ...owner, role: 'viewer' }, empty);
    const { findByText, queryByRole } = renderWithProviders(<DashboardScreen />);
    await findByText('No projects yet.');
    expect(queryByRole('button', { name: 'Create your first project' })).toBeNull();
  });

  it('welcomes an invited user with no tasks or activity yet', async () => {
    mockApi({ ...owner, role: 'member' }, empty);
    const { findByText } = renderWithProviders(<DashboardScreen />);
    expect(await findByText('Welcome to your workspace.')).toBeInTheDocument();
  });

  it('does not show the welcome banner to the Owner', async () => {
    mockApi(owner, empty);
    const { findByText, queryByText } = renderWithProviders(<DashboardScreen />);
    await findByText('No projects yet.');
    await waitFor(() => expect(apiClient.get).toHaveBeenCalledWith('/activity'));
    expect(queryByText('Welcome to your workspace.')).toBeNull();
  });
});
