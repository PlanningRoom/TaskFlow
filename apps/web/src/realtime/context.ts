import { createContext, useContext } from 'react';
import type { RealtimeStatus } from './types';

/**
 * Connection status published by {@link RealtimeProvider}. Defaults to `closed`
 * so consumers rendered outside the provider (e.g. isolated tests) degrade
 * gracefully instead of throwing.
 */
export const RealtimeStatusContext = createContext<RealtimeStatus>('closed');

/** Read the live WebSocket connection status (Phase H1). */
export function useRealtimeStatus(): RealtimeStatus {
  return useContext(RealtimeStatusContext);
}
