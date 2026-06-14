/**
 * Real-time event contract (Phase H1). Mirrors the backend envelope built in
 * `apps/api/taskflow/realtime/publish.py` (TDD §10.2). Payloads carry IDs only —
 * not full DTOs — so the dispatcher invalidates queries to refetch rather than
 * patching the cache (TDD §10.4 reconcile-from-DB semantics).
 */

/** Wire envelope every WebSocket message arrives in. */
export interface RealtimeEnvelope {
  type: string;
  workspace_id: string | null;
  project_id: string | null;
  payload: Record<string, unknown>;
  emitted_at: string;
}

/** Connection lifecycle state surfaced to the UI indicator. */
export type RealtimeStatus = 'connecting' | 'open' | 'reconnecting' | 'closed';

/** Control frames the client sends to the server (ws.py `_reader_loop`). */
export type ControlMessage = { type: 'ping' } | { type: 'refresh_subscriptions' };
