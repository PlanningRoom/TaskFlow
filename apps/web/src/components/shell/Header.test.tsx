import { waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { apiClient } from '@/api/client';
import { axe } from '@/test/axe';
import { renderWithProviders } from '@/test/render';
import { Header } from './Header';

const navigate = vi.fn();
vi.mock('@tanstack/react-router', () => ({
  Link: ({ to, children, ...props }: { to: string; children: React.ReactNode }) => (
    <a href={to} {...props}>
      {children}
    </a>
  ),
  useNavigate: () => navigate,
}));

const user = {
  id: 'u1',
  email: 'olivia@aurora.example.com',
  display_name: 'Olivia Owner',
  initials: 'OO',
  avatar_color: 'indigo',
  role: 'owner',
  workspace_id: 'w1',
};

function mockApi(unread: number) {
  vi.spyOn(apiClient, 'get').mockImplementation(((path: string) => {
    if (path === '/auth/me') return Promise.resolve(user);
    if (path === '/notifications/unread-count') return Promise.resolve({ count: unread });
    return Promise.reject(new Error(`unexpected GET ${path}`));
  }) as typeof apiClient.get);
}

afterEach(() => {
  vi.restoreAllMocks();
  navigate.mockClear();
});

describe('Header', () => {
  it('renders breadcrumb segments with the last marked current', () => {
    mockApi(0);
    const { getByText } = renderWithProviders(
      <Header breadcrumb={['Website Redesign', 'Board']} />,
    );
    expect(getByText('Website Redesign')).toBeInTheDocument();
    expect(getByText('Board')).toHaveAttribute('aria-current', 'page');
  });

  it('shows the unread count in the bell label and badge', async () => {
    mockApi(3);
    const { findByLabelText, getByText } = renderWithProviders(
      <Header breadcrumb={['Dashboard']} />,
    );
    expect(await findByLabelText('Notifications (3 unread)')).toBeInTheDocument();
    expect(getByText('3')).toBeInTheDocument();
  });

  it('labels the bell without a count when there are no unread notifications', async () => {
    mockApi(0);
    const { findByLabelText } = renderWithProviders(<Header breadcrumb={['Dashboard']} />);
    expect(await findByLabelText('Notifications')).toBeInTheDocument();
  });

  it('has no axe violations', async () => {
    mockApi(2);
    const { container, findByLabelText } = renderWithProviders(
      <Header breadcrumb={['Dashboard']} />,
    );
    await findByLabelText('User menu');
    expect(await axe(container)).toHaveNoViolations();
  });

  it('opens the user menu showing identity, and signs out (DRD §11.2)', async () => {
    mockApi(0);
    const post = vi.spyOn(apiClient, 'post').mockResolvedValue({ ok: true });
    const u = userEvent.setup({ pointerEventsCheck: 0 });
    const { findByLabelText, getByRole, getByText } = renderWithProviders(
      <Header breadcrumb={['Dashboard']} />,
    );
    await u.click(await findByLabelText('User menu'));
    // Identity block: name, email, role badge.
    expect(getByText('olivia@aurora.example.com')).toBeInTheDocument();
    expect(getByText('Owner')).toBeInTheDocument();

    await u.click(getByRole('menuitem', { name: 'Sign out' }));
    expect(post).toHaveBeenCalledWith('/auth/logout');
    await waitFor(() => expect(navigate).toHaveBeenCalledWith({ to: '/login' }));
  });

  it('navigates to settings from the user menu', async () => {
    mockApi(0);
    const u = userEvent.setup({ pointerEventsCheck: 0 });
    const { findByLabelText, getByRole } = renderWithProviders(
      <Header breadcrumb={['Dashboard']} />,
    );
    await u.click(await findByLabelText('User menu'));
    await u.click(getByRole('menuitem', { name: 'Settings' }));
    expect(navigate).toHaveBeenCalledWith({ to: '/settings/profile' });
  });
});
