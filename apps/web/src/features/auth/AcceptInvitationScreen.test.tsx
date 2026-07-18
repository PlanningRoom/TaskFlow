import { waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { ApiError, apiClient } from '@/api/client';
import type { InvitationPreview } from '@/api/types';
import { axe } from '@/test/axe';
import { renderWithProviders } from '@/test/render';
import { AcceptInvitationScreen } from './AcceptInvitationScreen';

const { mockNavigate } = vi.hoisted(() => ({ mockNavigate: vi.fn() }));
vi.mock('@tanstack/react-router', () => ({
  Link: ({ to, children, ...props }: { to: string; children: React.ReactNode }) => (
    <a href={to} {...props}>
      {children}
    </a>
  ),
  useNavigate: () => mockNavigate,
}));

const user = {
  id: 'u2',
  email: 'grace@example.com',
  display_name: 'Grace',
  initials: 'G',
  avatar_color: 'emerald',
  role: 'member',
  workspace_id: 'w1',
};

const preview: InvitationPreview = {
  workspace_name: 'Aurora Studio',
  email: 'grace@example.com',
  role: 'member',
  invited_by: {
    id: 'u1',
    display_name: 'Aurora Owner',
    initials: 'AO',
    avatar_color: 'indigo',
    deleted: false,
  },
  status: 'pending',
  existing_user: false,
};

afterEach(() => vi.restoreAllMocks());

describe('AcceptInvitationScreen', () => {
  it('shows the workspace, inviter, and role from the preview, with no axe violations', async () => {
    vi.spyOn(apiClient, 'get').mockResolvedValue(preview);
    const { container, findByText } = renderWithProviders(
      <AcceptInvitationScreen token="tok-abc-12345678" />,
    );
    expect(await findByText('Aurora Owner invited you to join Aurora Studio.')).toBeInTheDocument();
    expect(await findByText("You'll join as Member, using grace@example.com.")).toBeInTheDocument();
    expect(await axe(container)).toHaveNoViolations();
  });

  it('submits token + account fields for a new user and navigates on success', async () => {
    vi.spyOn(apiClient, 'get').mockResolvedValue(preview);
    const post = vi.spyOn(apiClient, 'post').mockResolvedValue({ user });
    const { findByLabelText, getByRole } = renderWithProviders(
      <AcceptInvitationScreen token="tok-abc-12345678" />,
    );
    await userEvent.type(await findByLabelText('Display name'), 'Grace Hopper');
    await userEvent.type(await findByLabelText('Password'), 'hunter2pw');
    await userEvent.click(getByRole('button', { name: 'Create account & join' }));
    await waitFor(() =>
      expect(post).toHaveBeenCalledWith('/auth/accept-invitation', {
        token: 'tok-abc-12345678',
        display_name: 'Grace Hopper',
        password: 'hunter2pw', // pragma: allowlist secret
      }),
    );
    expect(mockNavigate).toHaveBeenCalledWith({ to: '/dashboard', replace: true });
  });

  it('offers a fields-free join for an existing account', async () => {
    vi.spyOn(apiClient, 'get').mockResolvedValue({ ...preview, existing_user: true });
    const post = vi.spyOn(apiClient, 'post').mockResolvedValue({ user });
    const { findByRole, queryByLabelText } = renderWithProviders(
      <AcceptInvitationScreen token="tok-abc-12345678" />,
    );
    const join = await findByRole('button', { name: 'Join Aurora Studio' });
    expect(queryByLabelText('Password')).not.toBeInTheDocument();
    await userEvent.click(join);
    await waitFor(() =>
      expect(post).toHaveBeenCalledWith('/auth/accept-invitation', {
        token: 'tok-abc-12345678',
      }),
    );
    expect(mockNavigate).toHaveBeenCalledWith({ to: '/dashboard', replace: true });
  });

  it('shows a dead-end message when no token is present', () => {
    const get = vi.spyOn(apiClient, 'get');
    const { getByRole, queryByLabelText } = renderWithProviders(<AcceptInvitationScreen />);
    expect(getByRole('alert')).toHaveTextContent('This invitation link is invalid.');
    expect(queryByLabelText('Password')).not.toBeInTheDocument();
    expect(get).not.toHaveBeenCalled();
  });

  it('renders the invalid state when the preview rejects the token', async () => {
    vi.spyOn(apiClient, 'get').mockRejectedValue(new ApiError(400, 'INVALID_TOKEN', 'bad'));
    const { findByText } = renderWithProviders(<AcceptInvitationScreen token="tok-abc-12345678" />);
    expect(
      await findByText('This invitation link is invalid or has already been used.'),
    ).toBeInTheDocument();
  });

  it('renders the expired state when the preview reports expired', async () => {
    vi.spyOn(apiClient, 'get').mockResolvedValue({ ...preview, status: 'expired' });
    const { findByText, queryByLabelText } = renderWithProviders(
      <AcceptInvitationScreen token="tok-abc-12345678" />,
    );
    expect(
      await findByText('This invitation has expired. Ask an admin to resend it.'),
    ).toBeInTheDocument();
    expect(queryByLabelText('Password')).not.toBeInTheDocument();
  });

  it('surfaces an accept-time expiry as a form error', async () => {
    vi.spyOn(apiClient, 'get').mockResolvedValue(preview);
    vi.spyOn(apiClient, 'post').mockRejectedValue(
      new ApiError(400, 'INVITATION_EXPIRED', 'expired'),
    );
    const { findByLabelText, getByRole, findByText } = renderWithProviders(
      <AcceptInvitationScreen token="tok-abc-12345678" />,
    );
    await userEvent.type(await findByLabelText('Display name'), 'Grace Hopper');
    await userEvent.type(await findByLabelText('Password'), 'hunter2pw');
    await userEvent.click(getByRole('button', { name: 'Create account & join' }));
    expect(
      await findByText('This invitation has expired. Ask an admin to resend it.'),
    ).toBeInTheDocument();
  });
});
