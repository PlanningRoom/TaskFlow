import { waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { ApiError, apiClient } from '@/api/client';
import { CURRENT_USER_KEY } from '@/hooks/useCurrentUser';
import { axe } from '@/test/axe';
import { renderWithProviders } from '@/test/render';
import { LoginScreen } from './LoginScreen';

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

afterEach(() => vi.restoreAllMocks());

describe('LoginScreen', () => {
  it('renders with no axe violations', async () => {
    const { container } = renderWithProviders(<LoginScreen />);
    expect(await axe(container)).toHaveNoViolations();
  });

  it('shows validation errors on empty submit', async () => {
    const post = vi.spyOn(apiClient, 'post');
    const { getByRole, findByText } = renderWithProviders(<LoginScreen />);
    await userEvent.click(getByRole('button', { name: 'Log in' }));
    expect(await findByText('Email is required')).toBeInTheDocument();
    expect(await findByText('Password is required')).toBeInTheDocument();
    expect(post).not.toHaveBeenCalled();
  });

  it('submits credentials, seeds the user cache, and navigates to the dashboard', async () => {
    const post = vi.spyOn(apiClient, 'post').mockResolvedValue({ user });
    const { getByLabelText, getByRole, queryClient } = renderWithProviders(<LoginScreen />);
    await userEvent.type(getByLabelText('Email'), 'ada@example.com');
    await userEvent.type(getByLabelText('Password'), 'hunter2pw');
    await userEvent.click(getByRole('button', { name: 'Log in' }));
    await waitFor(() =>
      expect(post).toHaveBeenCalledWith('/auth/login', {
        email: 'ada@example.com',
        password: 'hunter2pw', // pragma: allowlist secret
      }),
    );
    expect(mockNavigate).toHaveBeenCalledWith({ to: '/dashboard', replace: true });
    expect(queryClient.getQueryData(CURRENT_USER_KEY)).toEqual(user);
  });

  it('shows a generic message on 401 without enumerating', async () => {
    vi.spyOn(apiClient, 'post').mockRejectedValue(new ApiError(401, 'INVALID_CREDENTIALS', 'nope'));
    const { getByLabelText, getByRole, findByRole } = renderWithProviders(<LoginScreen />);
    await userEvent.type(getByLabelText('Email'), 'ada@example.com');
    await userEvent.type(getByLabelText('Password'), 'wrongpass');
    await userEvent.click(getByRole('button', { name: 'Log in' }));
    expect(await findByRole('alert')).toHaveTextContent('Invalid email or password.');
    expect(mockNavigate).not.toHaveBeenCalled();
  });
});
