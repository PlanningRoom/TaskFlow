import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { apiClient } from '@/api/client';
import type { Label } from '@/api/types';
import { Button } from '@/components/ui';
import { renderWithProviders } from '@/test/render';
import { LabelModal } from './LabelModal';

afterEach(() => vi.restoreAllMocks());

describe('LabelModal', () => {
  it('creates a label with a chosen name and color', async () => {
    const post = vi
      .spyOn(apiClient, 'post')
      .mockResolvedValue({ id: 'l9', name: 'Blocked', color: 'red' } as Label);
    vi.spyOn(apiClient, 'get').mockResolvedValue({ labels: [] });
    const user = userEvent.setup({ pointerEventsCheck: 0 });

    const { getByRole, findByLabelText, findByText, getByText } = renderWithProviders(
      <LabelModal trigger={<Button>New label</Button>} />,
    );
    await user.click(getByRole('button', { name: 'New label' }));
    await user.type(await findByLabelText('Label name'), 'Blocked');
    // Live preview chip reflects the typed name while the modal is open.
    expect(getByText('Blocked')).toBeInTheDocument();
    await user.click(getByRole('button', { name: 'red' }));
    await user.click(getByRole('button', { name: 'Create label' }));

    expect(post).toHaveBeenCalledWith('/labels', { name: 'Blocked', color: 'red' });
    expect(await findByText('Label saved.')).toBeInTheDocument();
  });

  it('opens in edit mode prefilled from the label', async () => {
    vi.spyOn(apiClient, 'get').mockResolvedValue({ labels: [] });
    const user = userEvent.setup({ pointerEventsCheck: 0 });
    const label: Label = { id: 'l1', name: 'Bug', color: 'red' };

    const { getByRole, findByDisplayValue } = renderWithProviders(
      <LabelModal trigger={<Button>Edit</Button>} label={label} />,
    );
    await user.click(getByRole('button', { name: 'Edit' }));
    expect(await findByDisplayValue('Bug')).toBeInTheDocument();
    // Editing shows the "Edit label" dialog title and a "Save" submit button.
    expect(getByRole('heading', { name: 'Edit label' })).toBeInTheDocument();
    expect(getByRole('button', { name: 'Save' })).toBeInTheDocument();
  });
});
