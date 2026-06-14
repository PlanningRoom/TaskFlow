import { useQueryClient } from '@tanstack/react-query';
import { useEffect, useRef, useState } from 'react';
import { useIntl } from 'react-intl';
import { CURRENT_USER_KEY, useCurrentUser } from '@/hooks/useCurrentUser';
import { CSRF_COOKIE, readCookie } from '@/lib/cookies';
import { RealtimeStatusContext } from './context';
import { createRealtimeDispatcher } from './dispatcher';
import { RealtimeClient } from './socket';
import type { RealtimeStatus } from './types';

/**
 * RealtimeProvider (Phase H1) — opens the `/ws` connection once the user is
 * authenticated, routes inbound envelopes into query-cache invalidations, and
 * publishes connection status to the shell indicator. Also hosts a polite
 * `aria-live` region for cross-page announcements (PRD §16.2 / DRD §14.3).
 *
 * Connection is gated on `useCurrentUser`: it shares the cached `['auth','me']`
 * query (no extra fetch) and the socket only opens when a user is present, so
 * unauthenticated routes never connect.
 */
export function RealtimeProvider({ children }: { children: React.ReactNode }) {
  const intl = useIntl();
  const queryClient = useQueryClient();
  const { data: user } = useCurrentUser();
  const userId = user?.id;

  const [status, setStatus] = useState<RealtimeStatus>('closed');
  const [announcement, setAnnouncement] = useState('');
  const clientRef = useRef<RealtimeClient | null>(null);
  const prevStatusRef = useRef<RealtimeStatus>('closed');

  useEffect(() => {
    if (!userId) return;
    const csrfToken = readCookie(CSRF_COOKIE);
    if (!csrfToken) return;

    const dispatch = createRealtimeDispatcher({
      queryClient,
      requestRefresh: () => clientRef.current?.send({ type: 'refresh_subscriptions' }),
      announce: () => setAnnouncement(intl.formatMessage({ id: 'realtime.mentioned' })),
    });

    const client = new RealtimeClient({
      csrfToken,
      onEnvelope: dispatch,
      onStatusChange: setStatus,
      // A reconnect after a prior open means we may have missed events: resync.
      onReconnect: () => void queryClient.invalidateQueries(),
      onAuthFailure: () => void queryClient.invalidateQueries({ queryKey: CURRENT_USER_KEY }),
    });
    clientRef.current = client;
    client.connect();

    return () => {
      client.disconnect();
      clientRef.current = null;
    };
  }, [userId, queryClient, intl]);

  // Announce reconnection transitions for screen-reader users. "Back online" is
  // only meaningful coming out of a drop, so it's gated on the previous status.
  useEffect(() => {
    const prev = prevStatusRef.current;
    if (status === 'reconnecting') {
      setAnnouncement(intl.formatMessage({ id: 'realtime.reconnecting' }));
    } else if (status === 'open' && prev === 'reconnecting') {
      setAnnouncement(intl.formatMessage({ id: 'realtime.online' }));
    }
    prevStatusRef.current = status;
  }, [status, intl]);

  return (
    <RealtimeStatusContext.Provider value={status}>
      {children}
      <div aria-live="polite" className="sr-only" data-testid="realtime-live-region">
        {announcement}
      </div>
    </RealtimeStatusContext.Provider>
  );
}
