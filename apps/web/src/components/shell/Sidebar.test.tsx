import { waitFor } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { apiClient } from '@/api/client';
import { axe } from '@/test/axe';
import { renderWithProviders } from '@/test/render';
import { Sidebar } from './Sidebar';

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

function mockApi(user: typeof owner, invitations: unknown[]) {
  vi.spyOn(apiClient, 'get').mockImplementation(((path: string) => {
    if (path === '/auth/me') return Promise.resolve(user);
    if (path === '/projects') return Promise.resolve({ projects: [] });
    if (path === '/workspaces/me/invitations') return Promise.resolve({ invitations });
    return Promise.reject(new Error(`unexpected GET ${path}`));
  }) as typeof apiClient.get);
}

afterEach(() => vi.restoreAllMocks());

describe('Sidebar — invite-team first-run prompt', () => {
  it('shows the prompt to an Owner with no invitations sent', async () => {
    mockApi(owner, []);
    const { findByRole } = renderWithProviders(<Sidebar />);
    expect(await findByRole('button', { name: 'Invite team members' })).toBeInTheDocument();
  });

  it('hides the prompt once at least one invitation exists', async () => {
    mockApi(owner, [{ id: 'i1', email: 'a@b.com', role: 'member', status: 'pending' }]);
    const { findByText, queryByRole } = renderWithProviders(<Sidebar />);
    await findByText('Olivia Owner');
    await waitFor(() => expect(apiClient.get).toHaveBeenCalledWith('/workspaces/me/invitations'));
    expect(queryByRole('button', { name: 'Invite team members' })).toBeNull();
  });

  it('does not show the prompt to a Member', async () => {
    mockApi({ ...owner, role: 'member' }, []);
    const { findByText, queryByRole } = renderWithProviders(<Sidebar />);
    await findByText('Olivia Owner');
    expect(queryByRole('button', { name: 'Invite team members' })).toBeNull();
  });

  it('has no axe violations', async () => {
    mockApi(owner, []);
    const { container, findByRole } = renderWithProviders(<Sidebar />);
    await findByRole('button', { name: 'Invite team members' });
    expect(await axe(container)).toHaveNoViolations();
  });
});
