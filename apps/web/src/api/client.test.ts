import { afterEach, describe, expect, it, vi } from 'vitest';
import { ApiError, apiClient, apiFetch } from './client';

function mockResponse(body: unknown, init: ResponseInit): Response {
  return new Response(body === undefined ? null : JSON.stringify(body), {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  });
}

afterEach(() => {
  vi.restoreAllMocks();
  // Reset cookies between tests.
  // biome-ignore lint/suspicious/noDocumentCookie: test fixture sets the CSRF cookie directly
  document.cookie = 'taskflow_csrf=; expires=Thu, 01 Jan 1970 00:00:00 GMT';
});

describe('apiFetch', () => {
  it('parses the ADR 043 error envelope into a typed ApiError', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      mockResponse(
        { error: { code: 'UNAUTHENTICATED', message: 'Not signed in.' } },
        { status: 401 },
      ),
    );

    const err = (await apiClient.get('/auth/me').catch((e) => e)) as ApiError;
    expect(err).toBeInstanceOf(ApiError);
    expect(err.status).toBe(401);
    expect(err.code).toBe('UNAUTHENTICATED');
    expect(err.message).toBe('Not signed in.');
  });

  it('surfaces 422 validation fields', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      mockResponse(
        {
          error: {
            code: 'VALIDATION_ERROR',
            message: 'Validation failed.',
            fields: { email: ['REQUIRED'] },
          },
        },
        { status: 422 },
      ),
    );

    const err = (await apiFetch('/auth/signup', { method: 'POST', body: {} }).catch(
      (e) => e,
    )) as ApiError;
    expect(err.code).toBe('VALIDATION_ERROR');
    expect(err.fields).toEqual({ email: ['REQUIRED'] });
  });

  it('returns the parsed JSON payload on success', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      mockResponse({ id: 'u1', role: 'owner' }, { status: 200 }),
    );
    const me = await apiClient.get<{ id: string; role: string }>('/auth/me');
    expect(me).toEqual({ id: 'u1', role: 'owner' });
  });

  it('attaches the CSRF header from the cookie on unsafe methods', async () => {
    // biome-ignore lint/suspicious/noDocumentCookie: test fixture sets the CSRF cookie directly
    document.cookie = 'taskflow_csrf=tok-123';
    const fetchSpy = vi
      .spyOn(globalThis, 'fetch')
      .mockResolvedValue(mockResponse({ ok: true }, { status: 200 }));

    await apiClient.post('/labels', { name: 'Bug' });

    const [, init] = fetchSpy.mock.calls[0] as [string, RequestInit];
    expect((init.headers as Record<string, string>)['X-CSRF-Token']).toBe('tok-123');
    expect(init.credentials).toBe('include');
  });

  it('does not attach the CSRF header on GET', async () => {
    // biome-ignore lint/suspicious/noDocumentCookie: test fixture sets the CSRF cookie directly
    document.cookie = 'taskflow_csrf=tok-123';
    const fetchSpy = vi
      .spyOn(globalThis, 'fetch')
      .mockResolvedValue(mockResponse({ ok: true }, { status: 200 }));

    await apiClient.get('/auth/me');

    const [, init] = fetchSpy.mock.calls[0] as [string, RequestInit];
    expect((init.headers as Record<string, string>)['X-CSRF-Token']).toBeUndefined();
  });
});
