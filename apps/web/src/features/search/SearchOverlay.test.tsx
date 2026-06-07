import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';
import type { RequestOptions } from '@/api/client';
import { apiClient } from '@/api/client';
import { axe } from '@/test/axe';
import { renderWithProviders } from '@/test/render';
import { SearchOverlay } from './SearchOverlay';

const { mockNavigate } = vi.hoisted(() => ({ mockNavigate: vi.fn() }));
vi.mock('@tanstack/react-router', () => ({ useNavigate: () => mockNavigate }));

const result = {
  task_id: 't1',
  title: 'Login flow',
  status: 'todo' as const,
  project: { id: 'p1', name: 'Website' },
};

function mockSearch() {
  vi.spyOn(apiClient, 'get').mockImplementation(((path: string, options?: RequestOptions) => {
    if (path === '/search') {
      const q = String(options?.query?.q ?? '');
      return Promise.resolve({ results: q === 'zzz' ? [] : [result] });
    }
    return Promise.reject(new Error(`unexpected GET ${path}`));
  }) as typeof apiClient.get);
}

afterEach(() => vi.restoreAllMocks());

describe('SearchOverlay', () => {
  it('shows results after typing, with no axe violations', async () => {
    mockSearch();
    const { container, getByRole, findByText } = renderWithProviders(<SearchOverlay />);
    await userEvent.type(getByRole('combobox'), 'log');
    expect(await findByText('Website')).toBeInTheDocument();
    expect(await axe(container)).toHaveNoViolations();
  });

  it('navigates to the task on Enter', async () => {
    mockSearch();
    const { getByRole, findByText } = renderWithProviders(<SearchOverlay />);
    await userEvent.type(getByRole('combobox'), 'log');
    await findByText('Website');
    await userEvent.keyboard('{Enter}');
    expect(mockNavigate).toHaveBeenCalledWith({
      to: '/projects/$projectId/tasks/$taskId',
      params: { projectId: 'p1', taskId: 't1' },
    });
  });

  it('shows an empty message when nothing matches', async () => {
    mockSearch();
    const { getByRole, findByText } = renderWithProviders(<SearchOverlay />);
    await userEvent.type(getByRole('combobox'), 'zzz');
    expect(await findByText('No tasks match your search.')).toBeInTheDocument();
  });
});
