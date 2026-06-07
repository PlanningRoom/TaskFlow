import { waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { apiClient } from '@/api/client';
import { renderWithProviders } from '@/test/render';
import { ProfileTab } from './ProfileTab';

vi.mock('@tanstack/react-router', () => ({ useNavigate: () => vi.fn() }));

const user = {
  id: 'u1',
  email: 'olivia@aurora.example.com',
  display_name: 'Olivia',
  initials: 'O',
  avatar_color: 'indigo',
  role: 'owner',
  workspace_id: 'w1',
};

function mockGet() {
  vi.spyOn(apiClient, 'get').mockImplementation(((path: string) => {
    if (path === '/auth/me') return Promise.resolve(user);
    return Promise.reject(new Error(`unexpected GET ${path}`));
  }) as typeof apiClient.get);
}

afterEach(() => vi.restoreAllMocks());

describe('ProfileTab', () => {
  it('shows the email and prefilled display name', async () => {
    mockGet();
    const { findByText, findByDisplayValue } = renderWithProviders(<ProfileTab />);
    expect(await findByText('olivia@aurora.example.com')).toBeInTheDocument();
    await findByDisplayValue('Olivia');
  });

  it('saves the display name', async () => {
    mockGet();
    const patch = vi.spyOn(apiClient, 'patch').mockResolvedValue(user);
    const { findByDisplayValue, getByRole } = renderWithProviders(<ProfileTab />);
    const input = await findByDisplayValue('Olivia');
    await userEvent.clear(input);
    await userEvent.type(input, 'Olivia O');
    await userEvent.click(getByRole('button', { name: 'Save' }));
    await waitFor(() =>
      expect(patch).toHaveBeenCalledWith('/auth/me', { display_name: 'Olivia O' }),
    );
  });

  it('changes the password', async () => {
    mockGet();
    const post = vi.spyOn(apiClient, 'post').mockResolvedValue({ ok: true });
    const { getByLabelText, getByRole } = renderWithProviders(<ProfileTab />);
    await userEvent.type(getByLabelText('Current password'), 'oldpassword');
    await userEvent.type(getByLabelText('New password'), 'newpassword1');
    await userEvent.click(getByRole('button', { name: 'Update password' }));
    await waitFor(() =>
      expect(post).toHaveBeenCalledWith('/auth/change-password', {
        current_password: 'oldpassword', // pragma: allowlist secret
        new_password: 'newpassword1', // pragma: allowlist secret
      }),
    );
  });
});
