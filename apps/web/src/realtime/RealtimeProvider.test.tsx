import { cleanup } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { axe } from 'vitest-axe';
import type { CurrentUser } from '@/api/types';
import { renderWithProviders } from '@/test/render';
import { RealtimeStatusContext } from './context';
import { RealtimeStatusIndicator } from './RealtimeStatusIndicator';

// --- Mocks for the provider's connect-gating ----------------------------------
const connect = vi.fn();
const disconnect = vi.fn();
vi.mock('./socket', () => ({
  RealtimeClient: vi.fn().mockImplementation(() => ({ connect, disconnect, send: vi.fn() })),
}));

let mockUser: CurrentUser | undefined;
vi.mock('@/hooks/useCurrentUser', () => ({
  CURRENT_USER_KEY: ['auth', 'me'],
  useCurrentUser: () => ({ data: mockUser }),
}));

vi.mock('@/lib/cookies', () => ({ CSRF_COOKIE: 'taskflow_csrf', readCookie: () => 'tok' }));

import { RealtimeProvider } from './RealtimeProvider';

const fakeUser = { id: 'u1', display_name: 'A', role: 'owner' } as unknown as CurrentUser;

afterEach(() => {
  cleanup();
  connect.mockClear();
  disconnect.mockClear();
  mockUser = undefined;
});

describe('RealtimeProvider', () => {
  it('does not connect when unauthenticated', () => {
    mockUser = undefined;
    renderWithProviders(<RealtimeProvider>child</RealtimeProvider>);
    expect(connect).not.toHaveBeenCalled();
  });

  it('connects when authenticated and disconnects on unmount', () => {
    mockUser = fakeUser;
    const { unmount } = renderWithProviders(<RealtimeProvider>child</RealtimeProvider>);
    expect(connect).toHaveBeenCalled();
    unmount();
    expect(disconnect).toHaveBeenCalled();
  });

  it('exposes a polite aria-live region', () => {
    mockUser = fakeUser;
    const { getByTestId } = renderWithProviders(<RealtimeProvider>child</RealtimeProvider>);
    expect(getByTestId('realtime-live-region')).toHaveAttribute('aria-live', 'polite');
  });
});

describe('RealtimeStatusIndicator', () => {
  function renderWithStatus(status: 'open' | 'reconnecting') {
    return renderWithProviders(
      <RealtimeStatusContext.Provider value={status}>
        <RealtimeStatusIndicator />
      </RealtimeStatusContext.Provider>,
    );
  }

  it('shows the reconnecting pill only while reconnecting', () => {
    const { queryByText, rerender } = renderWithStatus('reconnecting');
    expect(queryByText('Reconnecting…')).toBeInTheDocument();
    rerender(
      <RealtimeStatusContext.Provider value="open">
        <RealtimeStatusIndicator />
      </RealtimeStatusContext.Provider>,
    );
    expect(queryByText('Reconnecting…')).not.toBeInTheDocument();
  });

  it('has no axe violations', async () => {
    const { container } = renderWithStatus('reconnecting');
    expect(await axe(container)).toHaveNoViolations();
  });
});
