import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { apiClient } from '@/api/client';
import { axe } from '@/test/axe';
import { renderWithProviders } from '@/test/render';
import { ProjectSubNav } from './ProjectSubNav';
import type { TaskSearch } from './taskQueryState';

vi.mock('@tanstack/react-router', () => ({
  Link: ({ to, children, ...props }: { to: string; children: React.ReactNode }) => (
    <a href={to} {...props}>
      {children}
    </a>
  ),
  useNavigate: () => vi.fn(),
}));

function mockApi() {
  vi.spyOn(apiClient, 'get').mockImplementation(((path: string) => {
    if (path === '/workspaces/me/members')
      return Promise.resolve({
        members: [
          {
            id: 'u2',
            display_name: 'Bob',
            email: 'bob@x.com',
            initials: 'B',
            avatar_color: 'sky',
            role: 'member',
            joined_at: '2026-01-01T00:00:00Z',
          },
        ],
      });
    if (path === '/labels')
      return Promise.resolve({ labels: [{ id: 'l1', name: 'Bug', color: 'red' }] });
    return Promise.reject(new Error(`unexpected GET ${path}`));
  }) as typeof apiClient.get);
}

function renderNav(search: TaskSearch, onSearchChange = vi.fn(), onViewChange = vi.fn()) {
  return {
    onSearchChange,
    onViewChange,
    ...renderWithProviders(
      <ProjectSubNav
        projectId="p1"
        view="board"
        search={search}
        // `role` is the user role prop, not an ARIA role.
        role={'owner' as const}
        onViewChange={onViewChange}
        onSearchChange={onSearchChange}
      />,
    ),
  };
}

afterEach(() => vi.restoreAllMocks());

describe('ProjectSubNav', () => {
  it('toggles the active view', async () => {
    mockApi();
    const user = userEvent.setup();
    const { onViewChange, getByRole } = renderNav({});
    await user.click(getByRole('button', { name: 'List' }));
    expect(onViewChange).toHaveBeenCalledWith('list');
  });

  it('renders active-filter chips and clears them', async () => {
    mockApi();
    const user = userEvent.setup();
    const { onSearchChange, getByRole } = renderNav({ status: ['todo'], sort: 'priority' });

    // A chip with a remove button is shown for the active status filter.
    await user.click(getByRole('button', { name: /Remove .* filter/ }));
    expect(onSearchChange).toHaveBeenCalled();

    // "Clear all" resets filters but preserves the sort.
    await user.click(getByRole('button', { name: 'Clear all' }));
    expect(onSearchChange).toHaveBeenLastCalledWith({ sort: 'priority' });
  });

  it('changes the sort from the dropdown', async () => {
    mockApi();
    const user = userEvent.setup();
    const { onSearchChange, getByRole } = renderNav({});
    await user.click(getByRole('button', { name: /Sort:/ }));
    await user.click(await getByRole('menuitem', { name: 'Priority' }));
    expect(onSearchChange).toHaveBeenCalledWith(expect.objectContaining({ sort: 'priority' }));
  });

  it('toggles a status filter from the Filter dropdown', async () => {
    mockApi();
    const user = userEvent.setup();
    const { onSearchChange, getByRole } = renderNav({});
    await user.click(getByRole('button', { name: 'Filter' }));
    await user.click(await getByRole('menuitem', { name: 'Backlog' }));
    expect(onSearchChange).toHaveBeenCalledWith(expect.objectContaining({ status: ['backlog'] }));
  });

  it('has no axe violations', async () => {
    mockApi();
    const { container } = renderNav({ status: ['todo'] });
    expect(await axe(container)).toHaveNoViolations();
  });
});
