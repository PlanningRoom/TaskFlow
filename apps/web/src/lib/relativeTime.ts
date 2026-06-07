/**
 * Format an ISO timestamp as a short relative string for activity feeds
 * ("just now", "5m ago", "2h ago", "3d ago"). Beyond a week it falls back to an
 * absolute date ("Apr 15" / "Apr 15, 2025"), matching {@link formatDueDate}'s
 * year handling. `now` is injectable for deterministic tests.
 */
const MINUTE = 60_000;
const HOUR = 60 * MINUTE;
const DAY = 24 * HOUR;
const WEEK = 7 * DAY;

export function formatRelativeTime(iso: string, now: Date = new Date()): string {
  const then = new Date(iso);
  const diff = now.getTime() - then.getTime();

  // Future or near-now timestamps read as "just now" rather than a negative age.
  if (diff < MINUTE) return 'just now';
  if (diff < HOUR) return `${Math.floor(diff / MINUTE)}m ago`;
  if (diff < DAY) return `${Math.floor(diff / HOUR)}h ago`;
  if (diff < WEEK) return `${Math.floor(diff / DAY)}d ago`;

  const opts: Intl.DateTimeFormatOptions =
    then.getFullYear() === now.getFullYear()
      ? { month: 'short', day: 'numeric' }
      : { month: 'short', day: 'numeric', year: 'numeric' };
  return new Intl.DateTimeFormat('en-US', opts).format(then);
}
