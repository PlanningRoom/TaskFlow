/**
 * Constants for the seeded "Aurora Studio" workspace (apps/api/taskflow/scripts/seed.py).
 * Every user shares one password; display names drive @mention autocomplete and
 * assignee filters.
 */
export const SEED_PASSWORD = 'correct-horse-battery-staple'; // pragma: allowlist secret

export const SEED_USERS = {
  owner: 'owner@aurora.example.com',
  admin: 'admin@aurora.example.com',
  dev1: 'dev1@aurora.example.com',
  dev2: 'dev2@aurora.example.com',
  viewer: 'viewer@aurora.example.com',
} as const;

export const SEED_NAMES = {
  owner: 'Aurora Owens',
  admin: 'Adam Min',
  dev1: 'Dana Engineer',
  dev2: 'Mason Code',
  viewer: 'Vivian Watch',
} as const;

export const WORKSPACE_NAME = 'Aurora Studio';

/** The project with the broadest access (owner/admin implicit + dev1/dev2/viewer granted). */
export const BROAD_PROJECT = 'Mobile App Redesign';

/** A task seeded into {@link BROAD_PROJECT}, assigned to dev1 — handy for search/comment journeys. */
export const SEED_TASK_TITLE = 'Sprint planning review';

let seq = 0;
/** A unique, collision-proof email so signup/invite journeys survive local reruns against a persisted DB. */
export function uniqueEmail(prefix = 'e2e'): string {
  seq += 1;
  return `${prefix}.${Date.now()}.${seq}@example.com`;
}
