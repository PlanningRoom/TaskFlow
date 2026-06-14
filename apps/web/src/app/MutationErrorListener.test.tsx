import { QueryClientProvider, useMutation } from '@tanstack/react-query';
import { render } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import type { ReactNode } from 'react';
import { IntlProvider } from 'react-intl';
import { describe, expect, it } from 'vitest';
import { Button, ToastProvider } from '@/components/ui';
import { DEFAULT_LOCALE, messagesByLocale } from '@/i18n';
import { MutationErrorListener } from './MutationErrorListener';
import { queryClient } from './query-client';

/**
 * Exercises the real app `queryClient` (with its MutationCache) so the global
 * error-toast wiring is covered end to end: a failing opted-in mutation should
 * surface the standardized toast; an opted-out one should not.
 */
function Harness({ meta }: { meta?: Record<string, unknown> }) {
  const mutation = useMutation({
    mutationFn: () => Promise.reject(new Error('boom')),
    meta,
  });
  return <Button onClick={() => mutation.mutate()}>go</Button>;
}

function renderWithRealClient(node: ReactNode) {
  function Wrapper({ children }: { children: ReactNode }) {
    return (
      <IntlProvider
        locale={DEFAULT_LOCALE}
        defaultLocale={DEFAULT_LOCALE}
        messages={messagesByLocale[DEFAULT_LOCALE]}
      >
        <QueryClientProvider client={queryClient}>
          <ToastProvider>
            <MutationErrorListener />
            {children}
          </ToastProvider>
        </QueryClientProvider>
      </IntlProvider>
    );
  }
  return render(<Wrapper>{node}</Wrapper>);
}

describe('MutationErrorListener', () => {
  it('shows the standardized toast when an opted-in mutation fails', async () => {
    const user = userEvent.setup();
    const { getByRole, findByText } = renderWithRealClient(<Harness meta={{ errorToast: true }} />);
    await user.click(getByRole('button', { name: 'go' }));
    expect(await findByText("Couldn't save your changes. Please try again.")).toBeInTheDocument();
  });

  it('stays silent when the failing mutation has not opted in', async () => {
    const user = userEvent.setup();
    const { getByRole, queryByText } = renderWithRealClient(<Harness />);
    await user.click(getByRole('button', { name: 'go' }));
    // Give the rejected mutation a tick to settle.
    await new Promise((r) => setTimeout(r, 20));
    expect(queryByText("Couldn't save your changes. Please try again.")).toBeNull();
  });
});
