import { within } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { apiClient } from '@/api/client';
import { axe } from '@/test/axe';
import { renderWithProviders } from '@/test/render';
import { AppShell } from './AppShell';

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
  email: 'o@aurora.example.com',
  display_name: 'Olivia',
  initials: 'O',
  avatar_color: 'indigo',
  role: 'owner',
  workspace_id: 'w1',
};

function mockApi() {
  vi.spyOn(apiClient, 'get').mockImplementation(((path: string) => {
    if (path === '/auth/me') return Promise.resolve(owner);
    if (path === '/notifications/unread-count') return Promise.resolve({ count: 0 });
    if (path === '/projects') return Promise.resolve({ projects: [] });
    if (path === '/workspaces/me/invitations')
      return Promise.resolve({ invitations: [{ id: 'i1' }] });
    return Promise.reject(new Error(`unexpected GET ${path}`));
  }) as typeof apiClient.get);
}

afterEach(() => vi.restoreAllMocks());

describe('AppShell', () => {
  it('renders the breadcrumb, a main landmark and the page content', async () => {
    mockApi();
    const { getByRole, getByText } = renderWithProviders(
      <AppShell breadcrumb={['Dashboard']}>
        <p>Page body</p>
      </AppShell>,
    );
    expect(getByRole('main')).toContainElement(getByText('Page body'));
    // "Dashboard" appears in both the sidebar nav and the breadcrumb; assert the
    // breadcrumb one carries aria-current.
    const breadcrumb = getByRole('navigation', { name: 'Breadcrumb' });
    expect(within(breadcrumb).getByText('Dashboard')).toHaveAttribute('aria-current', 'page');
  });

  it('has no axe violations', async () => {
    mockApi();
    const { container, findByLabelText } = renderWithProviders(
      <AppShell breadcrumb={['Dashboard']}>
        <p>Page body</p>
      </AppShell>,
    );
    await findByLabelText('User menu');
    expect(await axe(container)).toHaveNoViolations();
  });
});
