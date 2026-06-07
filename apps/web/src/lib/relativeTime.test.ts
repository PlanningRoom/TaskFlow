import { describe, expect, it } from 'vitest';
import { formatRelativeTime } from './relativeTime';

const now = new Date('2026-06-07T12:00:00Z');
const ago = (ms: number) => new Date(now.getTime() - ms).toISOString();

describe('formatRelativeTime', () => {
  it('reads sub-minute and future timestamps as "just now"', () => {
    expect(formatRelativeTime(ago(0), now)).toBe('just now');
    expect(formatRelativeTime(ago(30_000), now)).toBe('just now');
    expect(formatRelativeTime(new Date(now.getTime() + 60_000).toISOString(), now)).toBe(
      'just now',
    );
  });

  it('formats minutes, hours, and days', () => {
    expect(formatRelativeTime(ago(5 * 60_000), now)).toBe('5m ago');
    expect(formatRelativeTime(ago(2 * 60 * 60_000), now)).toBe('2h ago');
    expect(formatRelativeTime(ago(3 * 24 * 60 * 60_000), now)).toBe('3d ago');
  });

  it('falls back to an absolute date beyond a week (no relative suffix)', () => {
    const iso = ago(10 * 24 * 60 * 60_000);
    const expected = new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric' }).format(
      new Date(iso),
    );
    expect(formatRelativeTime(iso, now)).toBe(expected);
  });

  it('includes the year for dates in a different year', () => {
    const iso = '2025-01-15T12:00:00Z';
    const expected = new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    }).format(new Date(iso));
    expect(formatRelativeTime(iso, now)).toBe(expected);
    expect(expected).toContain('2025');
  });
});
