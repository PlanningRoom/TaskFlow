import type { ApiErrorEnvelope } from '@taskflow/api-types';

/**
 * Typed, cookie-based fetch client for the TaskFlow API (ADR 042/043/051).
 *
 * - Session auth rides on the `taskflow_session` cookie; every request sends
 *   credentials so the browser attaches it.
 * - State-changing methods carry the CSRF double-submit header: the value is
 *   read from the JS-readable `csrf_token` cookie and echoed as `X-CSRF-Token`.
 * - Non-2xx responses are parsed into a typed `ApiError` and thrown.
 *
 * The base path is relative (`/api/v1`); nginx proxies it in production and the
 * Vite dev server proxies it to the API (see vite.config.ts).
 */

const API_BASE = '/api/v1';
const CSRF_COOKIE = 'csrf_token';
const CSRF_HEADER = 'X-CSRF-Token';
const UNSAFE_METHODS = new Set(['POST', 'PUT', 'PATCH', 'DELETE']);

/** Error thrown for any non-2xx response, carrying the ADR 043 envelope. */
export class ApiError extends Error {
  readonly status: number;
  readonly code: string;
  readonly fields?: Record<string, string[]>;

  constructor(status: number, code: string, message: string, fields?: Record<string, string[]>) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.code = code;
    this.fields = fields;
  }
}

function readCookie(name: string): string | undefined {
  // document is undefined under SSR/tests without jsdom; guard defensively.
  if (typeof document === 'undefined') return undefined;
  for (const part of document.cookie.split(';')) {
    const [key, ...rest] = part.trim().split('=');
    if (key === name) return decodeURIComponent(rest.join('='));
  }
  return undefined;
}

export interface RequestOptions {
  method?: string;
  /** JSON-serializable request body. Sent as `application/json`. */
  body?: unknown;
  /** Query parameters; `undefined`/`null` values are dropped. */
  query?: Record<string, string | number | boolean | undefined | null>;
  signal?: AbortSignal;
}

function buildUrl(path: string, query?: RequestOptions['query']): string {
  const url = `${API_BASE}${path}`;
  if (!query) return url;
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(query)) {
    if (value !== undefined && value !== null) params.append(key, String(value));
  }
  const qs = params.toString();
  return qs ? `${url}?${qs}` : url;
}

async function toApiError(response: Response): Promise<ApiError> {
  let code = 'UNKNOWN';
  let message = response.statusText || 'Request failed';
  let fields: Record<string, string[]> | undefined;
  try {
    const data = (await response.json()) as Partial<ApiErrorEnvelope>;
    if (data.error) {
      code = data.error.code ?? code;
      message = data.error.message ?? message;
      fields = data.error.fields;
    }
  } catch {
    // Non-JSON error body (e.g. a proxy 502); keep the status-derived defaults.
  }
  return new ApiError(response.status, code, message, fields);
}

/**
 * Perform a typed request. `T` is the expected success payload; callers pass
 * the generated DTO type. 204/empty responses resolve to `undefined as T`.
 */
export async function apiFetch<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const method = (options.method ?? 'GET').toUpperCase();
  const headers: Record<string, string> = { Accept: 'application/json' };

  if (options.body !== undefined) headers['Content-Type'] = 'application/json';

  if (UNSAFE_METHODS.has(method)) {
    const csrf = readCookie(CSRF_COOKIE);
    if (csrf) headers[CSRF_HEADER] = csrf;
  }

  const response = await fetch(buildUrl(path, options.query), {
    method,
    headers,
    credentials: 'include',
    body: options.body !== undefined ? JSON.stringify(options.body) : undefined,
    signal: options.signal,
  });

  if (!response.ok) throw await toApiError(response);

  if (response.status === 204 || response.headers.get('Content-Length') === '0') {
    return undefined as T;
  }
  const text = await response.text();
  return (text ? JSON.parse(text) : undefined) as T;
}

/** Convenience verbs over {@link apiFetch}. */
export const apiClient = {
  get: <T>(path: string, options?: Omit<RequestOptions, 'method' | 'body'>) =>
    apiFetch<T>(path, { ...options, method: 'GET' }),
  post: <T>(path: string, body?: unknown, options?: Omit<RequestOptions, 'method'>) =>
    apiFetch<T>(path, { ...options, method: 'POST', body }),
  patch: <T>(path: string, body?: unknown, options?: Omit<RequestOptions, 'method'>) =>
    apiFetch<T>(path, { ...options, method: 'PATCH', body }),
  put: <T>(path: string, body?: unknown, options?: Omit<RequestOptions, 'method'>) =>
    apiFetch<T>(path, { ...options, method: 'PUT', body }),
  delete: <T>(path: string, body?: unknown, options?: Omit<RequestOptions, 'method'>) =>
    apiFetch<T>(path, { ...options, method: 'DELETE', body }),
};
