import { useIntl } from 'react-intl';
import { useRealtimeStatus } from './context';

/**
 * Discreet "Reconnecting…" pill (Phase H1). Shown only while the realtime
 * connection is re-establishing; it auto-clears once the socket reopens. The
 * accompanying screen-reader announcement is handled by {@link RealtimeProvider}
 * so this stays purely visual (`aria-hidden`).
 */
export function RealtimeStatusIndicator() {
  const intl = useIntl();
  const status = useRealtimeStatus();
  if (status !== 'reconnecting') return null;

  return (
    <div
      aria-hidden
      className="fixed bottom-6 start-6 z-[998] flex items-center gap-2 rounded-full bg-text-primary px-3 py-1.5 text-[12px] font-medium text-white shadow-modal"
    >
      <span className="h-2 w-2 animate-pulse rounded-full bg-semantic-warning" />
      {intl.formatMessage({ id: 'realtime.reconnecting' })}
    </div>
  );
}
