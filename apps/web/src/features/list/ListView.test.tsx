import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { apiClient } from '@/api/client';
import type { TaskSummary } from '@/api/types';
import { axe } from '@/test/axe';
import { renderWithProviders } from '@/test/render';
import { ListView } from './ListView';

// `role` is a ListView prop (user role), not an ARIA attribute — bind via consts.
const OWNER = 'owner' as const;
const VIEWER = 'viewer' as const;

function task(overrides: Partial<TaskSummary> = {}): TaskSummary {
  return {
    id: 't1',
    title: 'Fix the login bug',
    status: 'todo',
    priority: 'high',
    due_date: null,
    assignee: { id: 'u2', display_name: 'Bob', initials: 'B', avatar_color: 'sky', deleted: false },
    labels: [],
    comment_count: 0,
    project: { id: 'p1', name: 'Website' },
    ...overrides,
  };
}

function mockApi(tasks: TaskSummary[]) {
  vi.spyOn(apiClient, 'get').mockImplementation(((path: string) => {
    if (path === '/projects/p1/tasks') return Promise.resolve({ tasks, next_cursor: null });
    return Promise.reject(new Error(`unexpected GET ${path}`));
  }) as typeof apiClient.get);
}

const noop = () => {};
const baseProps = {
  projectId: 'p1',
  params: {},
  search: {},
  onOpenTask: noop,
  onClearFilters: noop,
  onSortChange: noop,
};

afterEach(() => vi.restoreAllMocks());

describe('ListView', () => {
  it('renders rows with no axe violations', async () => {
    mockApi([task()]);
    const { container, findByText, getByText } = renderWithProviders(
      <ListView {...baseProps} role={OWNER} />,
    );
    await findByText('Fix the login bug');
    expect(getByText('Bob')).toBeInTheDocument();
    expect(await axe(container)).toHaveNoViolations();
  });

  it('calls onSortChange when a sortable header is clicked', async () => {
    mockApi([task()]);
    const onSortChange = vi.fn();
    const { findByText, getByRole } = renderWithProviders(
      <ListView {...baseProps} role={OWNER} onSortChange={onSortChange} />,
    );
    await findByText('Fix the login bug');
    await userEvent.click(getByRole('button', { name: /Priority/ }));
    expect(onSortChange).toHaveBeenCalledWith('priority');
  });

  it('lets editors change status inline but not viewers', async () => {
    mockApi([task()]);
    const { findByText, queryByRole, getByRole, rerender } = renderWithProviders(
      <ListView {...baseProps} role={OWNER} />,
    );
    await findByText('Fix the login bug');
    expect(getByRole('button', { name: 'Change status' })).toBeInTheDocument();

    rerender(<ListView {...baseProps} role={VIEWER} />);
    expect(queryByRole('button', { name: 'Change status' })).toBeNull();
  });

  it('shows a filtered-empty state', async () => {
    mockApi([]);
    const onClearFilters = vi.fn();
    const { findByText, getByRole } = renderWithProviders(
      <ListView
        {...baseProps}
        role={OWNER}
        params={{ priority: ['high'] }}
        onClearFilters={onClearFilters}
      />,
    );
    expect(await findByText('No tasks match these filters.')).toBeInTheDocument();
    await userEvent.click(getByRole('button', { name: 'Clear filters' }));
    expect(onClearFilters).toHaveBeenCalled();
  });
});
