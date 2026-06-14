import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import { axe } from '@/test/axe';
import { renderWithProviders } from '@/test/render';
import { Button } from './Button';
import { ConfirmDialog } from './ConfirmDialog';

function renderDialog(onConfirm: () => unknown) {
  return renderWithProviders(
    <ConfirmDialog
      trigger={<Button>Open delete</Button>}
      title="Delete label"
      description='Delete the label "Bug"? It will be removed from all tasks.'
      confirmLabel="Delete label"
      onConfirm={onConfirm}
    />,
  );
}

describe('ConfirmDialog', () => {
  it('runs the action on confirm and closes', async () => {
    const user = userEvent.setup();
    const onConfirm = vi.fn();
    const { getByRole, findByText, queryByRole } = renderDialog(onConfirm);

    await user.click(getByRole('button', { name: 'Open delete' }));
    await findByText(/Delete the label/);
    await user.click(getByRole('button', { name: 'Delete label' }));

    expect(onConfirm).toHaveBeenCalledOnce();
    expect(queryByRole('dialog')).toBeNull();
  });

  it('does not run the action on cancel', async () => {
    const user = userEvent.setup();
    const onConfirm = vi.fn();
    const { getByRole, findByText } = renderDialog(onConfirm);

    await user.click(getByRole('button', { name: 'Open delete' }));
    await findByText(/Delete the label/);
    await user.click(getByRole('button', { name: 'Cancel' }));

    expect(onConfirm).not.toHaveBeenCalled();
  });

  it('has no axe violations when open', async () => {
    const user = userEvent.setup();
    const { getByRole, findByText, baseElement } = renderDialog(vi.fn());
    await user.click(getByRole('button', { name: 'Open delete' }));
    await findByText(/Delete the label/);
    expect(await axe(baseElement)).toHaveNoViolations();
  });
});
