import { useEffect, useState } from 'react';

/**
 * Reactive CSS media query (DRD §15 responsive behavior that CSS alone can't
 * express — e.g. choosing the collapsed sidebar rail, disabling board DnD).
 *
 * `fallback` is returned where `window.matchMedia` is unavailable (jsdom), so
 * component tests keep the desktop behavior they were written against unless
 * they shim matchMedia themselves.
 */
export function useMediaQuery(query: string, fallback = false): boolean {
  const supported = typeof window !== 'undefined' && typeof window.matchMedia === 'function';
  const [matches, setMatches] = useState(() =>
    supported ? window.matchMedia(query).matches : fallback,
  );

  useEffect(() => {
    if (!supported) return;
    const mql = window.matchMedia(query);
    const onChange = () => setMatches(mql.matches);
    onChange();
    mql.addEventListener('change', onChange);
    return () => mql.removeEventListener('change', onChange);
  }, [query, supported]);

  return matches;
}
