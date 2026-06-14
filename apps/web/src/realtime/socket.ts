import type { ControlMessage, RealtimeEnvelope, RealtimeStatus } from './types';

/**
 * RealtimeClient (Phase H1) — a framework-agnostic wrapper around the browser
 * `WebSocket` that connects to `/ws`, parses inbound envelopes, sends heartbeat
 * pings, and reconnects with jittered exponential backoff (TDD §10.4).
 *
 * It is deliberately free of React so it can be unit-tested with a fake socket
 * and fake timers. The {@link RealtimeProvider} owns one instance.
 */

const PING_INTERVAL_MS = 25_000;
const BACKOFF_BASE_MS = 1_000;
const BACKOFF_CAP_MS = 30_000;

// Standardized `WebSocket.readyState` values. Referenced as literals so the
// module doesn't depend on a global `WebSocket` existing (jsdom omits it).
const WS_OPEN = 1;

/** Application close codes (TDD §10.1) that must NOT trigger a reconnect. */
const TERMINAL_CLOSE_CODES = new Set([4401, 4403]);

export interface RealtimeClientOptions {
  /** CSRF token from the `taskflow_csrf` cookie, sent as the `?csrf=` param. */
  csrfToken: string;
  onEnvelope: (envelope: RealtimeEnvelope) => void;
  onStatusChange: (status: RealtimeStatus) => void;
  /** Fired after a reconnect that follows a prior successful open — resync. */
  onReconnect: () => void;
  /** Fired on a 4401/4403 close — caller should re-auth (redirect to login). */
  onAuthFailure: () => void;
  /** Injectable factory for tests; defaults to the global `WebSocket`. */
  socketFactory?: (url: string) => WebSocket;
  /** Injectable jitter [0,1) for deterministic tests; defaults to Math.random. */
  random?: () => number;
}

export class RealtimeClient {
  private readonly opts: RealtimeClientOptions;
  private socket: WebSocket | null = null;
  private status: RealtimeStatus = 'closed';
  private attempt = 0;
  private wasConnected = false;
  /** Set once `disconnect()` is called so async callbacks become no-ops. */
  private stopped = false;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private pingTimer: ReturnType<typeof setInterval> | null = null;

  constructor(opts: RealtimeClientOptions) {
    this.opts = opts;
  }

  private buildUrl(): string {
    const scheme = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const csrf = encodeURIComponent(this.opts.csrfToken);
    return `${scheme}//${window.location.host}/ws?csrf=${csrf}`;
  }

  private setStatus(status: RealtimeStatus): void {
    if (this.status === status) return;
    this.status = status;
    this.opts.onStatusChange(status);
  }

  /** Open the connection. Idempotent: ignored if a socket is already live. */
  connect(): void {
    if (this.stopped) return;
    if (this.socket && this.socket.readyState <= WS_OPEN) return;

    this.setStatus(this.wasConnected ? 'reconnecting' : 'connecting');
    const factory = this.opts.socketFactory ?? ((url) => new WebSocket(url));
    const socket = factory(this.buildUrl());
    this.socket = socket;

    socket.onopen = () => {
      if (this.stopped) return;
      this.attempt = 0;
      this.setStatus('open');
      this.startHeartbeat();
      if (this.wasConnected) this.opts.onReconnect();
      this.wasConnected = true;
    };

    socket.onmessage = (event: MessageEvent) => {
      if (this.stopped) return;
      let parsed: unknown;
      try {
        parsed = JSON.parse(typeof event.data === 'string' ? event.data : '');
      } catch {
        return; // ignore non-JSON frames
      }
      if (!parsed || typeof parsed !== 'object') return;
      const msg = parsed as { type?: unknown };
      if (msg.type === 'pong') return; // heartbeat ack
      if (typeof msg.type !== 'string') return;
      this.opts.onEnvelope(parsed as RealtimeEnvelope);
    };

    socket.onclose = (event: CloseEvent) => {
      this.stopHeartbeat();
      this.socket = null;
      if (this.stopped) return;
      if (TERMINAL_CLOSE_CODES.has(event.code)) {
        this.setStatus('closed');
        this.opts.onAuthFailure();
        return;
      }
      this.scheduleReconnect();
    };

    // `onerror` precedes `onclose`; the close handler drives reconnection so we
    // only need to keep the socket from throwing uncaught.
    socket.onerror = () => {};
  }

  /** Close the connection for good (logout / unmount). Stops all timers. */
  disconnect(): void {
    this.stopped = true;
    this.clearReconnect();
    this.stopHeartbeat();
    if (this.socket) {
      this.socket.onclose = null;
      this.socket.onerror = null;
      this.socket.onmessage = null;
      this.socket.onopen = null;
      try {
        this.socket.close();
      } catch {
        // ignore
      }
      this.socket = null;
    }
    this.setStatus('closed');
  }

  /** Send a control frame (ping / refresh_subscriptions) when open. */
  send(message: ControlMessage): void {
    if (this.socket && this.socket.readyState === WS_OPEN) {
      this.socket.send(JSON.stringify(message));
    }
  }

  /** Backoff delay for the current attempt: min(cap, base·2ⁿ) with full jitter. */
  private backoffDelay(): number {
    const exp = Math.min(BACKOFF_CAP_MS, BACKOFF_BASE_MS * 2 ** this.attempt);
    const rand = this.opts.random ?? Math.random;
    return Math.round(exp * rand());
  }

  private scheduleReconnect(): void {
    this.setStatus('reconnecting');
    const delay = this.backoffDelay();
    this.attempt += 1;
    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null;
      this.connect();
    }, delay);
  }

  private clearReconnect(): void {
    if (this.reconnectTimer !== null) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
  }

  private startHeartbeat(): void {
    this.stopHeartbeat();
    this.pingTimer = setInterval(() => this.send({ type: 'ping' }), PING_INTERVAL_MS);
  }

  private stopHeartbeat(): void {
    if (this.pingTimer !== null) {
      clearInterval(this.pingTimer);
      this.pingTimer = null;
    }
  }
}
