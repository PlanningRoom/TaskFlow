import { useEffect } from 'react';
import { useIntl } from 'react-intl';
import { useToast } from '@/components/ui';
import { registerMutationErrorHandler } from '@/lib/mutationErrorToast';

/**
 * Wires the standardized mutation-error toast (DRD §18.2) to the global
 * MutationCache. Renders nothing; it just registers a handler that shows the
 * error toast so `app/query-client.ts` can trigger it without depending on
 * React context. Mount inside <IntlProvider> and <ToastProvider>.
 */
export function MutationErrorListener() {
  const intl = useIntl();
  const toast = useToast();

  useEffect(
    () =>
      registerMutationErrorHandler(() =>
        toast.show(intl.formatMessage({ id: 'errors.mutation' }), 'error'),
      ),
    [intl, toast],
  );

  return null;
}
