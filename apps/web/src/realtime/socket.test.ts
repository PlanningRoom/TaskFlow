import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { RealtimeClient, type RealtimeClientOptions } from './socket';
import type { RealtimeEnvelope } from './types';

/** Minimal stand-in for the browser WebSocket, driven manually by the test. */
class FakeSocket {
  static instances: FakeSocket[] = [];
  readyState = 0; // CONNECTING
  sent: string[] = [];
  onopen: (() => void) | null = null;
  onmessage: ((e: { data: string }) => void) | null = null;
  onclose: ((e: { code: number }) => void) | null = null;
  onerror: (() => void) | null = null;

  constructor(public url: string) {
    FakeSocket.instances.push(this);
  }
  send(data: string) {
    this.sent.push(data);
  }
  close() {
    this.readyState = 3;
  }
  // Test drivers:
  open() {
    this.readyState = 1;
    this.onopen?.();
  }
  emit(envelope: unknown) {
    this.onmessage?.({ data: JSON.stringify(envelope) });
  }
  drop(code = 1006) {
    this.readyState = 3;
    this.onclose?.({ code });
  }
}

function makeClient(overrides: Partial<RealtimeClientOptions> = {}) {
  const onEnvelope = vi.fn();
  const onStatusChange = vi.fn();
  const onReconnect = vi.fn();
  const onAuthFailure = vi.fn();
  const client = new RealtimeClient({
    csrfToken: 'tok',
    onEnvelope,
    onStatusChange,
    onReconnect,
    onAuthFailure,
    socketFactory: (url) => new FakeSocket(url) as unknown as WebSocket,
    random: () => 1, // deterministic: delay == full exponential value
    ...overrides,
  });
  return { client, onEnvelope, onStatusChange, onReconnect, onAuthFailure };
}

function latest(): FakeSocket {
  const socket = FakeSocket.instances.at(-1);
  if (!socket) throw new Error('no socket created yet');
  return socket;
}

beforeEach(() => {
  vi.useFakeTimers();
  FakeSocket.instances = [];
  // The default URL builder reads window.location; jsdom provides it.
});

afterEach(() => {
  vi.useRealTimers();
});

describe('RealtimeClient', () => {
  it('reports connecting then open and parses envelopes', () => {
    const { client, onEnvelope, onStatusChange } = makeClient();
    client.connect();
    expect(onStatusChange).toHaveBeenLastCalledWith('connecting');
    latest().open();
    expect(onStatusChange).toHaveBeenLastCalledWith('open');

    const env: RealtimeEnvelope = {
      type: 'task.updated',
      workspace_id: 'w',
      project_id: 'p',
      payload: { task_id: 't' },
      emitted_at: 'now',
    };
    latest().emit(env);
    expect(onEnvelope).toHaveBeenCalledWith(env);
  });

  it('ignores pong heartbeat acks and non-JSON frames', () => {
    const { client, onEnvelope } = makeClient();
    client.connect();
    latest().open();
    latest().emit({ type: 'pong' });
    latest().onmessage?.({ data: 'not-json' });
    expect(onEnvelope).not.toHaveBeenCalled();
  });

  it('sends periodic ping heartbeats while open', () => {
    const { client } = makeClient();
    client.connect();
    latest().open();
    vi.advanceTimersByTime(25_000);
    expect(latest().sent).toContain(JSON.stringify({ type: 'ping' }));
  });

  it('reconnects with backoff after an unexpected drop and resyncs', () => {
    const { client, onReconnect, onStatusChange } = makeClient();
    client.connect();
    latest().open();
    expect(FakeSocket.instances).toHaveLength(1);

    latest().drop(1006);
    expect(onStatusChange).toHaveBeenLastCalledWith('reconnecting');

    vi.advanceTimersByTime(1_000); // first backoff = base·2⁰ with jitter=1
    expect(FakeSocket.instances).toHaveLength(2);

    latest().open();
    expect(onReconnect).toHaveBeenCalledOnce(); // resync after re-open
  });

  it('caps backoff at 30s across repeated failures', () => {
    const delays: number[] = [];
    const setTimeoutSpy = vi.spyOn(globalThis, 'setTimeout');
    const { client } = makeClient();
    client.connect();
    latest().open();

    for (let i = 0; i < 8; i++) {
      latest().drop(1006);
      const lastDelay = setTimeoutSpy.mock.calls.at(-1)?.[1] ?? 0;
      delays.push(lastDelay);
      vi.advanceTimersByTime(lastDelay);
    }
    expect(Math.max(...delays)).toBeLessThanOrEqual(30_000);
    expect(delays.at(-1)).toBe(30_000); // saturated
  });

  it('treats 4401/4403 closes as terminal (no reconnect, auth failure fired)', () => {
    const { client, onAuthFailure, onStatusChange } = makeClient();
    client.connect();
    latest().open();
    latest().drop(4401);
    expect(onAuthFailure).toHaveBeenCalledOnce();
    expect(onStatusChange).toHaveBeenLastCalledWith('closed');
    vi.advanceTimersByTime(60_000);
    expect(FakeSocket.instances).toHaveLength(1); // no reconnect attempt
  });

  it('disconnect() closes the socket and stops reconnecting', () => {
    const { client } = makeClient();
    client.connect();
    latest().open();
    client.disconnect();
    expect(latest().readyState).toBe(3);
    vi.advanceTimersByTime(60_000);
    expect(FakeSocket.instances).toHaveLength(1);
  });
});
