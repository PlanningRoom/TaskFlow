import { waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { ApiError, apiClient } from '@/api/client';
import { axe } from '@/test/axe';
import { renderWithProviders } from '@/test/render';
import { PasswordResetConfirmScreen } from './PasswordResetConfirmScreen';

vi.mock('@tanstack/react-router', () => ({
  Link: ({ to, children, ...props }: { to: string; children: React.ReactNode }) => (
    <a href={to} {...props}>
      {children}
    </a>
  ),
  useNavigate: () => vi.fn(),
}));

afterEach(() => vi.restoreAllMocks());

describe('PasswordResetConfirmScreen', () => {
  it('renders with no axe violations', async () => {
    const { container } = renderWithProviders(<PasswordResetConfirmScreen token="tok-12345678" />);
    expect(await axe(container)).toHaveNoViolations();
  });

  it('shows the invalid state when no token is present', () => {
    const { getByRole } = renderWithProviders(<PasswordResetConfirmScreen />);
    expect(getByRole('alert')).toHaveTextContent('This reset link is invalid.');
  });

  it('blocks submit when the two passwords differ', async () => {
    const post = vi.spyOn(apiClient, 'post');
    const { getByLabelText, getByRole, findByText } = renderWithProviders(
      <PasswordResetConfirmScreen token="tok-12345678" />,
    );
    await userEvent.type(getByLabelText('New password'), 'hunter2pw');
    await userEvent.type(getByLabelText('Confirm new password'), 'different1');
    await userEvent.click(getByRole('button', { name: 'Update password' }));
    expect(await findByText("Passwords don't match")).toBeInTheDocument();
    expect(post).not.toHaveBeenCalled();
  });

  it('posts token + new_password and shows the done panel on success', async () => {
    const post = vi.spyOn(apiClient, 'post').mockResolvedValue({ ok: true });
    const { getByLabelText, getByRole, findByText } = renderWithProviders(
      <PasswordResetConfirmScreen token="tok-12345678" />,
    );
    await userEvent.type(getByLabelText('New password'), 'hunter2pw');
    await userEvent.type(getByLabelText('Confirm new password'), 'hunter2pw');
    await userEvent.click(getByRole('button', { name: 'Update password' }));
    await waitFor(() =>
      expect(post).toHaveBeenCalledWith('/auth/password-reset/confirm', {
        token: 'tok-12345678',
        new_password: 'hunter2pw', // pragma: allowlist secret
      }),
    );
    expect(await findByText('Password updated')).toBeInTheDocument();
  });

  it('renders the invalid-token state on INVALID_TOKEN', async () => {
    vi.spyOn(apiClient, 'post').mockRejectedValue(new ApiError(400, 'INVALID_TOKEN', 'bad'));
    const { getByLabelText, getByRole, findByText } = renderWithProviders(
      <PasswordResetConfirmScreen token="tok-12345678" />,
    );
    await userEvent.type(getByLabelText('New password'), 'hunter2pw');
    await userEvent.type(getByLabelText('Confirm new password'), 'hunter2pw');
    await userEvent.click(getByRole('button', { name: 'Update password' }));
    expect(await findByText('This reset link is invalid or has expired.')).toBeInTheDocument();
  });
});
