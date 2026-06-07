import { waitFor } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { apiClient } from '@/api/client';
import { renderWithProviders } from '@/test/render';
import { SettingsLayout } from './SettingsLayout';

const { mockNavigate } = vi.hoisted(() => ({ mockNavigate: vi.fn() }));
vi.mock('@tanstack/react-router', () => ({
  Link: ({ to, children, ...props }: { to: string; children: React.ReactNode }) => (
    <a href={to} {...props}>
      {children}
    </a>
  ),
  useNavigate: () => mockNavigate,
}));

const user = (role: string) => ({
  id: 'u1',
  email: 'u@aurora.example.com',
  display_name: 'U',
  initials: 'U',
  avatar_color: 'indigo',
  role,
  workspace_id: 'w1',
});

function mockUser(role: string) {
  vi.spyOn(apiClient, 'get').mockImplementation(((path: string) => {
    if (path === '/auth/me') return Promise.resolve(user(role));
    return Promise.reject(new Error(`unexpected GET ${path}`));
  }) as typeof apiClient.get);
}

afterEach(() => vi.restoreAllMocks());

describe('SettingsLayout', () => {
  it('renders manage tabs and content for an Owner', async () => {
    mockUser('owner');
    const { findByText, getByRole } = renderWithProviders(
      <SettingsLayout tab="workspace" requiresManage>
        <div>SECRET CONTENT</div>
      </SettingsLayout>,
    );
    expect(await findByText('SECRET CONTENT')).toBeInTheDocument();
    expect(getByRole('link', { name: 'Members' })).toBeInTheDocument();
  });

  it('redirects non-managers away from a manage-only tab', async () => {
    mockUser('viewer');
    const { queryByText } = renderWithProviders(
      <SettingsLayout tab="members" requiresManage>
        <div>SECRET CONTENT</div>
      </SettingsLayout>,
    );
    await waitFor(() => expect(mockNavigate).toHaveBeenCalledWith({ to: '/dashboard' }));
    expect(queryByText('SECRET CONTENT')).toBeNull();
  });
});
