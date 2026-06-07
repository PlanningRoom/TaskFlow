import { waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { apiClient } from '@/api/client';
import { axe } from '@/test/axe';
import { renderWithProviders } from '@/test/render';
import { WorkspaceTab } from './WorkspaceTab';

function mockGet() {
  vi.spyOn(apiClient, 'get').mockImplementation(((path: string) => {
    if (path === '/workspaces/me')
      return Promise.resolve({
        id: 'w1',
        name: 'Aurora Studio',
        created_at: '2026-01-01T00:00:00Z',
      });
    return Promise.reject(new Error(`unexpected GET ${path}`));
  }) as typeof apiClient.get);
}

afterEach(() => vi.restoreAllMocks());

describe('WorkspaceTab', () => {
  it('prefills the name and has no axe violations', async () => {
    mockGet();
    const { container, findByDisplayValue } = renderWithProviders(<WorkspaceTab />);
    await findByDisplayValue('Aurora Studio');
    expect(await axe(container)).toHaveNoViolations();
  });

  it('saves the renamed workspace', async () => {
    mockGet();
    const patch = vi.spyOn(apiClient, 'patch').mockResolvedValue({
      id: 'w1',
      name: 'Aurora',
      created_at: '2026-01-01T00:00:00Z',
    });
    const { findByDisplayValue, getByRole } = renderWithProviders(<WorkspaceTab />);
    const input = await findByDisplayValue('Aurora Studio');
    await userEvent.clear(input);
    await userEvent.type(input, 'Aurora');
    await userEvent.click(getByRole('button', { name: 'Save' }));
    await waitFor(() => expect(patch).toHaveBeenCalledWith('/workspaces/me', { name: 'Aurora' }));
  });
});
