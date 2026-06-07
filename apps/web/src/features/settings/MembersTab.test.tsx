import { afterEach, describe, expect, it, vi } from 'vitest';
import { apiClient } from '@/api/client';
import type { Invitation, Member } from '@/api/types';
import { axe } from '@/test/axe';
import { renderWithProviders } from '@/test/render';
import { MembersTab } from './MembersTab';

const owner = {
  id: 'u1',
  email: 'o@aurora.example.com',
  display_name: 'Olivia',
  initials: 'O',
  avatar_color: 'indigo',
  role: 'owner',
  workspace_id: 'w1',
};

const members: Member[] = [
  {
    id: 'u1',
    display_name: 'Olivia',
    email: 'o@aurora.example.com',
    initials: 'O',
    avatar_color: 'indigo',
    role: 'owner',
    joined_at: '2026-01-01T00:00:00Z',
  },
  {
    id: 'u2',
    display_name: 'Bob',
    email: 'bob@aurora.example.com',
    initials: 'B',
    avatar_color: 'sky',
    role: 'member',
    joined_at: '2026-02-01T00:00:00Z',
  },
];

const invitations: Invitation[] = [
  {
    id: 'i1',
    email: 'new@aurora.example.com',
    role: 'member',
    status: 'pending',
    invited_by: null,
    sent_at: '2026-06-01T00:00:00Z',
    expires_at: '2026-06-08T00:00:00Z',
    accepted_at: null,
  },
];

function mockGet() {
  vi.spyOn(apiClient, 'get').mockImplementation(((path: string) => {
    if (path === '/workspaces/me/members') return Promise.resolve({ members });
    if (path === '/workspaces/me/invitations') return Promise.resolve({ invitations });
    if (path === '/auth/me') return Promise.resolve(owner);
    return Promise.reject(new Error(`unexpected GET ${path}`));
  }) as typeof apiClient.get);
}

afterEach(() => vi.restoreAllMocks());

describe('MembersTab', () => {
  it('lists members and invitations with no axe violations', async () => {
    mockGet();
    const { container, findByText, getByText } = renderWithProviders(<MembersTab />);
    expect(await findByText('Bob')).toBeInTheDocument();
    expect(getByText('new@aurora.example.com')).toBeInTheDocument();
    expect(getByText('Resend')).toBeInTheDocument();
    expect(await axe(container)).toHaveNoViolations();
  });

  it('lets the Owner remove a non-owner member', async () => {
    mockGet();
    const { findByText, getByRole } = renderWithProviders(<MembersTab />);
    await findByText('Bob');
    expect(getByRole('button', { name: 'Remove' })).toBeInTheDocument();
  });
});
