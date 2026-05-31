import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render } from '@testing-library/react';
import type { ReactElement, ReactNode } from 'react';
import { IntlProvider } from 'react-intl';
import { DEFAULT_LOCALE, messagesByLocale } from '@/i18n';

/**
 * Render a component with the providers screens depend on: a fresh TanStack
 * Query client (isolated per test) and react-intl loaded with the real English
 * catalog so assertions can match on shipped copy. Router hooks (`useNavigate`,
 * `Link`, `useParams`, `useSearch`) are NOT provided here — tests that need
 * them mock `@tanstack/react-router` directly.
 */
export function renderWithProviders(ui: ReactElement) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  function Wrapper({ children }: { children: ReactNode }) {
    return (
      <IntlProvider
        locale={DEFAULT_LOCALE}
        defaultLocale={DEFAULT_LOCALE}
        messages={messagesByLocale[DEFAULT_LOCALE]}
      >
        <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
      </IntlProvider>
    );
  }
  return { ...render(ui, { wrapper: Wrapper }), queryClient };
}
