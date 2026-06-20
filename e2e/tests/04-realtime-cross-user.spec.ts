import { expect, test } from '@playwright/test';
import { login } from '../helpers/auth';
import { columnDropZone, openProjectBoard, taskCard } from '../helpers/board';
import { SEED_USERS } from '../helpers/data';
import { dragTo } from '../helpers/dnd';

/**
 * Journey 4 (plan §I1 / TDD §10): two browser contexts on the same board. User A
 * creates and moves a task; user B sees both changes without reloading, proving
 * the `/ws` fan-out → cache-invalidate → refetch bridge (H1). The spec target is
 * <1s; we assert with a generous ceiling to stay non-flaky in CI.
 */
test('Journey 4 — a task move propagates to another user in real time', async ({ browser }) => {
  const title = `E2E realtime ${Date.now()}`;
  const ctxA = await browser.newContext();
  const ctxB = await browser.newContext();
  const a = await ctxA.newPage();
  const b = await ctxB.newPage();

  try {
    await login(a, SEED_USERS.owner);
    await login(b, SEED_USERS.dev1);
    await openProjectBoard(a);
    await openProjectBoard(b);

    // A creates a task; B sees it arrive in Backlog via real-time (no reload).
    await a.getByRole('button', { name: 'Create task' }).click();
    const dialog = a.getByRole('dialog');
    await dialog.getByLabel('Title').fill(title);
    await dialog.getByRole('button', { name: 'Create task' }).click();
    await expect(taskCard(a, title, 'Backlog')).toBeVisible();
    await expect(taskCard(b, title, 'Backlog')).toBeVisible({ timeout: 15_000 });

    // A drags it to In Progress; B sees the move propagate.
    await dragTo(a, taskCard(a, title), columnDropZone(a, 'In Progress'));
    await expect(taskCard(a, title, 'In Progress')).toBeVisible();
    await expect(taskCard(b, title, 'In Progress')).toBeVisible({ timeout: 15_000 });
  } finally {
    await ctxA.close();
    await ctxB.close();
  }
});
