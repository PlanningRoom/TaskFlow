import { waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { apiClient } from '@/api/client';
import { axe } from '@/test/axe';
import { renderWithProviders } from '@/test/render';
import { PasswordResetRequestScreen } from './PasswordResetRequestScreen';

vi.mock('@tanstack/react-router', () => ({
  Link: ({ to, children, ...props }: { to: string; children: React.ReactNode }) => (
    <a href={to} {...props}>
      {children}
    </a>
  ),
  useNavigate: () => vi.fn(),
}));

afterEach(() => vi.restoreAllMocks());

describe('PasswordResetRequestScreen', () => {
  it('renders with no axe violations', async () => {
    const { container } = renderWithProviders(<PasswordResetRequestScreen />);
    expect(await axe(container)).toHaveNoViolations();
  });

  it('posts the email and shows the neutral no-enumeration confirmation', async () => {
    const post = vi.spyOn(apiClient, 'post').mockResolvedValue({ ok: true });
    const { getByLabelText, getByRole, findByText, queryByLabelText } = renderWithProviders(
      <PasswordResetRequestScreen />,
    );
    await userEvent.type(getByLabelText('Email'), 'ada@example.com');
    await userEvent.click(getByRole('button', { name: 'Reset password' }));
    await waitFor(() =>
      expect(post).toHaveBeenCalledWith('/auth/password-reset/request', {
        email: 'ada@example.com',
      }),
    );
    expect(
      await findByText(
        "If an account exists for that email, we've sent password reset instructions.",
      ),
    ).toBeInTheDocument();
    // The form is replaced by the confirmation panel.
    expect(queryByLabelText('Email')).not.toBeInTheDocument();
  });
});
