/**
 * Read a single cookie value by name. Returns `undefined` when absent or when
 * `document` is unavailable (SSR / tests without jsdom). Shared by the API
 * client (CSRF double-submit header) and the realtime bridge (CSRF query param).
 */
export function readCookie(name: string): string | undefined {
  if (typeof document === 'undefined') return undefined;
  for (const part of document.cookie.split(';')) {
    const [key, ...rest] = part.trim().split('=');
    if (key === name) return decodeURIComponent(rest.join('='));
  }
  return undefined;
}

/** Name of the JS-readable CSRF cookie issued by the backend on login. */
export const CSRF_COOKIE = 'taskflow_csrf';
