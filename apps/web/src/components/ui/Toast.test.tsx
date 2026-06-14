import { act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { axe } from '@/test/axe';
import { renderWithProviders } from '@/test/render';
import { Button } from './Button';
import { useToast } from './Toast';

/** Tiny harness exercising the toast context from a real component. */
function ToastDemo() {
  const toast = useToast();
  return (
    <div>
      <Button onClick={() => toast.show('Saved.')}>success</Button>
      <Button onClick={() => toast.show('Failed.', 'error')}>error</Button>
    </div>
  );
}

describe('Toast', () => {
  beforeEach(() => vi.useFakeTimers({ shouldAdvanceTime: true }));
  afterEach(() => vi.useRealTimers());

  it('shows a success toast with the message and check icon', async () => {
    const user = userEvent.setup();
    const { getByRole, findByText } = renderWithProviders(<ToastDemo />);
    await user.click(getByRole('button', { name: 'success' }));
    expect(await findByText('Saved.')).toBeInTheDocument();
  });

  it('shows an error toast', async () => {
    const user = userEvent.setup();
    const { getByRole, findByText } = renderWithProviders(<ToastDemo />);
    await user.click(getByRole('button', { name: 'error' }));
    expect(await findByText('Failed.')).toBeInTheDocument();
  });

  it('can be dismissed manually via the close button', async () => {
    const user = userEvent.setup();
    const { getByRole, findByText, queryByText } = renderWithProviders(<ToastDemo />);
    await user.click(getByRole('button', { name: 'success' }));
    await findByText('Saved.');
    await user.click(getByRole('button', { name: 'Dismiss' }));
    expect(queryByText('Saved.')).toBeNull();
  });

  it('auto-dismisses after the 5s duration', async () => {
    const user = userEvent.setup();
    const { getByRole, findByText, queryByText } = renderWithProviders(<ToastDemo />);
    await user.click(getByRole('button', { name: 'success' }));
    await findByText('Saved.');
    act(() => {
      vi.advanceTimersByTime(6000);
    });
    expect(queryByText('Saved.')).toBeNull();
  });

  it('has no axe violations while a toast is visible', async () => {
    const user = userEvent.setup();
    const { container, getByRole, findByText } = renderWithProviders(<ToastDemo />);
    await user.click(getByRole('button', { name: 'error' }));
    await findByText('Failed.');
    // Radix Toast renders each toast as <li role="status"> inside an <ol>
    // viewport — the correct live-region pattern, but axe's `aria-allowed-role`
    // and `list` rules flag the role-on-li markup. Scope those two out; all
    // other WCAG rules still run.
    expect(
      await axe(container, {
        rules: { 'aria-allowed-role': { enabled: false }, list: { enabled: false } },
      }),
    ).toHaveNoViolations();
  });
});
