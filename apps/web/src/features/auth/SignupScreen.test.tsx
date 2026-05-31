import { waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { ApiError, apiClient } from '@/api/client';
import { axe } from '@/test/axe';
import { renderWithProviders } from '@/test/render';
import { SignupScreen } from './SignupScreen';

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
  id: 'u1',
  email: 'ada@example.com',
  display_name: 'Ada',
  initials: 'A',
  avatar_color: 'indigo',
  role: 'owner',
  workspace_id: 'w1',
};

async function fillValidForm(getByLabelText: (t: string) => HTMLElement) {
  await userEvent.type(getByLabelText('Display name'), 'Ada Lovelace');
  await userEvent.type(getByLabelText('Email'), 'ada@example.com');
  await userEvent.type(getByLabelText('Password'), 'hunter2pw');
  await userEvent.type(getByLabelText('Workspace name'), 'Analytical Engine');
}

afterEach(() => vi.restoreAllMocks());

describe('SignupScreen', () => {
  it('renders with no axe violations', async () => {
    const { container } = renderWithProviders(<SignupScreen />);
    expect(await axe(container)).toHaveNoViolations();
  });

  it('validates the password length client-side', async () => {
    const post = vi.spyOn(apiClient, 'post');
    const { getByLabelText, getByRole, findByText } = renderWithProviders(<SignupScreen />);
    await userEvent.type(getByLabelText('Password'), 'short');
    await userEvent.click(getByRole('button', { name: 'Create workspace' }));
    expect(await findByText('Password must be at least 8 characters')).toBeInTheDocument();
    expect(post).not.toHaveBeenCalled();
  });

  it('submits the snake_case payload and navigates on success', async () => {
    const post = vi.spyOn(apiClient, 'post').mockResolvedValue({ user });
    const { getByLabelText, getByRole } = renderWithProviders(<SignupScreen />);
    await fillValidForm(getByLabelText);
    await userEvent.click(getByRole('button', { name: 'Create workspace' }));
    await waitFor(() =>
      expect(post).toHaveBeenCalledWith('/auth/signup', {
        display_name: 'Ada Lovelace',
        email: 'ada@example.com',
        password: 'hunter2pw', // pragma: allowlist secret
        workspace_name: 'Analytical Engine',
      }),
    );
    expect(mockNavigate).toHaveBeenCalledWith({ to: '/dashboard', replace: true });
  });

  it('maps a 409 EMAIL_TAKEN to a field error on email', async () => {
    vi.spyOn(apiClient, 'post').mockRejectedValue(new ApiError(409, 'EMAIL_TAKEN', 'taken'));
    const { getByLabelText, getByRole, findByText } = renderWithProviders(<SignupScreen />);
    await fillValidForm(getByLabelText);
    await userEvent.click(getByRole('button', { name: 'Create workspace' }));
    expect(await findByText('That email is already registered.')).toBeInTheDocument();
    expect(mockNavigate).not.toHaveBeenCalled();
  });
});
