import { waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { ApiError, apiClient } from '@/api/client';
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

afterEach(() => vi.restoreAllMocks());

describe('AcceptInvitationScreen', () => {
  it('renders with no axe violations', async () => {
    const { container } = renderWithProviders(<AcceptInvitationScreen token="tok-abc-12345678" />);
    expect(await axe(container)).toHaveNoViolations();
  });

  it('submits token + account fields and navigates on success', async () => {
    const post = vi.spyOn(apiClient, 'post').mockResolvedValue({ user });
    const { getByLabelText, getByRole } = renderWithProviders(
      <AcceptInvitationScreen token="tok-abc-12345678" />,
    );
    await userEvent.type(getByLabelText('Display name'), 'Grace Hopper');
    await userEvent.type(getByLabelText('Password'), 'hunter2pw');
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

  it('shows a dead-end message when no token is present', () => {
    const { getByRole, queryByLabelText } = renderWithProviders(<AcceptInvitationScreen />);
    expect(getByRole('alert')).toHaveTextContent('This invitation link is invalid.');
    expect(queryByLabelText('Password')).not.toBeInTheDocument();
  });

  it('renders the expired state on INVITATION_EXPIRED', async () => {
    vi.spyOn(apiClient, 'post').mockRejectedValue(
      new ApiError(400, 'INVITATION_EXPIRED', 'expired'),
    );
    const { getByLabelText, getByRole, findByText } = renderWithProviders(
      <AcceptInvitationScreen token="tok-abc-12345678" />,
    );
    await userEvent.type(getByLabelText('Display name'), 'Grace Hopper');
    await userEvent.type(getByLabelText('Password'), 'hunter2pw');
    await userEvent.click(getByRole('button', { name: 'Create account & join' }));
    expect(
      await findByText('This invitation has expired. Ask an admin to resend it.'),
    ).toBeInTheDocument();
  });

  it('renders the invalid state on INVALID_TOKEN', async () => {
    vi.spyOn(apiClient, 'post').mockRejectedValue(new ApiError(400, 'INVALID_TOKEN', 'bad'));
    const { getByLabelText, getByRole, findByText } = renderWithProviders(
      <AcceptInvitationScreen token="tok-abc-12345678" />,
    );
    await userEvent.type(getByLabelText('Display name'), 'Grace Hopper');
    await userEvent.type(getByLabelText('Password'), 'hunter2pw');
    await userEvent.click(getByRole('button', { name: 'Create account & join' }));
    expect(
      await findByText('This invitation link is invalid or has already been used.'),
    ).toBeInTheDocument();
  });
});
