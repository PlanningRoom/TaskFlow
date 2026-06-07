import { waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { apiClient } from '@/api/client';
import type { Notification } from '@/api/types';
import { axe } from '@/test/axe';
import { renderWithProviders } from '@/test/render';
import { NotificationsScreen } from './NotificationsScreen';

vi.mock('@tanstack/react-router', () => ({
  Link: ({ to, children, ...props }: { to: string; children: React.ReactNode }) => (
    <a href={to} {...props}>
      {children}
    </a>
  ),
  useNavigate: () => vi.fn(),
}));

const notification: Notification = {
  id: 'n1',
  event_type: 'mention',
  actor: { id: 'u2', display_name: 'Bob', initials: 'B', avatar_color: 'sky', deleted: false },
  task: { id: 't1', title: 'Fix the login bug' },
  project: { id: 'p1', name: 'Website' },
  detail: 'mentioned you',
  read: false,
  created_at: '2026-06-06T10:00:00Z',
  read_at: null,
  metadata: {},
};

function mockGet(notifications: Notification[]) {
  vi.spyOn(apiClient, 'get').mockImplementation(((path: string) => {
    if (path === '/notifications') return Promise.resolve({ notifications, next_cursor: null });
    if (path === '/notifications/unread-count') return Promise.resolve({ count: 0 });
    return Promise.reject(new Error(`unexpected GET ${path}`));
  }) as typeof apiClient.get);
}

afterEach(() => vi.restoreAllMocks());

describe('NotificationsScreen', () => {
  it('renders notifications with no axe violations', async () => {
    mockGet([notification]);
    const { container, findByText, getByText } = renderWithProviders(<NotificationsScreen />);
    expect(await findByText(/mentioned you in a comment/)).toBeInTheDocument();
    expect(getByText('Fix the login bug')).toBeInTheDocument();
    expect(await axe(container)).toHaveNoViolations();
  });

  it('marks all as read', async () => {
    mockGet([notification]);
    const post = vi.spyOn(apiClient, 'post').mockResolvedValue({ ok: true });
    const { findByRole } = renderWithProviders(<NotificationsScreen />);
    await userEvent.click(await findByRole('button', { name: 'Mark all as read' }));
    await waitFor(() => expect(post).toHaveBeenCalledWith('/notifications/mark-all-read'));
  });

  it('shows the empty state when there are no notifications', async () => {
    mockGet([]);
    const { findByText } = renderWithProviders(<NotificationsScreen />);
    expect(await findByText("You're all caught up.")).toBeInTheDocument();
  });
});
