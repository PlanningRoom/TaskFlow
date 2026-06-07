import { afterEach, describe, expect, it, vi } from 'vitest';
import { apiClient } from '@/api/client';
import type { Label } from '@/api/types';
import { axe } from '@/test/axe';
import { renderWithProviders } from '@/test/render';
import { LabelsTab } from './LabelsTab';

function mockLabels(labels: Label[]) {
  vi.spyOn(apiClient, 'get').mockImplementation(((path: string) => {
    if (path === '/labels') return Promise.resolve({ labels });
    return Promise.reject(new Error(`unexpected GET ${path}`));
  }) as typeof apiClient.get);
}

afterEach(() => vi.restoreAllMocks());

describe('LabelsTab', () => {
  it('lists labels with no axe violations', async () => {
    mockLabels([{ id: 'l1', name: 'Bug', color: 'red' }]);
    const { container, findByText } = renderWithProviders(<LabelsTab />);
    expect(await findByText('Bug')).toBeInTheDocument();
    expect(await axe(container)).toHaveNoViolations();
  });

  it('shows the empty state when there are no labels', async () => {
    mockLabels([]);
    const { findByText } = renderWithProviders(<LabelsTab />);
    expect(await findByText('No labels yet. Create your first label.')).toBeInTheDocument();
  });
});
