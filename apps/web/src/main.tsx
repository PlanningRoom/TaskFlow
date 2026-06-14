import { QueryClientProvider } from '@tanstack/react-query';
import { RouterProvider } from '@tanstack/react-router';
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { IntlProvider } from 'react-intl';
import { queryClient } from '@/app/query-client';
import { router } from '@/app/router';
import { ToastProvider } from '@/components/ui/Toast';
import { TooltipProvider } from '@/components/ui/Tooltip';
import { DEFAULT_LOCALE, messagesByLocale } from '@/i18n';
import { RealtimeProvider } from '@/realtime/RealtimeProvider';
import './styles/global.css';

const rootElement = document.getElementById('root');
if (!rootElement) throw new Error('Missing #root element');

createRoot(rootElement).render(
  <StrictMode>
    <IntlProvider
      locale={DEFAULT_LOCALE}
      defaultLocale={DEFAULT_LOCALE}
      messages={messagesByLocale[DEFAULT_LOCALE]}
    >
      <QueryClientProvider client={queryClient}>
        <TooltipProvider delayDuration={200}>
          <ToastProvider>
            <RealtimeProvider>
              <RouterProvider router={router} />
            </RealtimeProvider>
          </ToastProvider>
        </TooltipProvider>
      </QueryClientProvider>
    </IntlProvider>
  </StrictMode>,
);
