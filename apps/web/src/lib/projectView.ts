/**
 * Per-project "last-used view" (board vs list) persisted to localStorage
 * (PRD §9.3) so reopening a project lands on the view you left it on. All
 * access is guarded — localStorage throws in private mode / SSR / some tests.
 */
export type ProjectViewKind = 'board' | 'list';

const storageKey = (projectId: string) => `taskflow:lastView:${projectId}`;

export function getLastView(projectId: string): ProjectViewKind {
  try {
    return localStorage.getItem(storageKey(projectId)) === 'list' ? 'list' : 'board';
  } catch {
    return 'board';
  }
}

export function setLastView(projectId: string, view: ProjectViewKind): void {
  try {
    localStorage.setItem(storageKey(projectId), view);
  } catch {
    // Ignore — persistence is a convenience, not a requirement.
  }
}
