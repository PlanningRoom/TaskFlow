import { expect, test } from '@playwright/test';
import { login } from '../helpers/auth';
import { openProjectBoard } from '../helpers/board';
import { SEED_NAMES, SEED_TASK_TITLE, SEED_USERS } from '../helpers/data';
import { unreadCount } from '../helpers/notifications';

/**
 * Journey 5 (plan §I1 / TDD §10.3): user A @mentions user B in a comment; B's
 * header notification badge increments in real time. Asserts an increase over
 * B's baseline so it is robust to any seed-delivered notifications.
 */
test('Journey 5 — an @mention raises a real-time notification badge', async ({ browser }) => {
  const ctxA = await browser.newContext();
  const ctxB = await browser.newContext();
  const a = await ctxA.newPage();
  const b = await ctxB.newPage();

  try {
    await login(a, SEED_USERS.owner);
    await login(b, SEED_USERS.dev1); // Dana Engineer
    await b.goto('/dashboard');
    const before = await unreadCount(b);

    // A opens a seeded task and mentions dev1 in a comment.
    await openProjectBoard(a);
    await a.getByRole('button', { name: SEED_TASK_TITLE }).first().click();
    const panel = a.getByRole('dialog', { name: 'Task details' });
    const comment = panel.getByPlaceholder('Write a comment… use @ to mention');
    await comment.click();
    await comment.pressSequentially('Heads up @dana');
    await panel.getByRole('button', { name: SEED_NAMES.dev1 }).click();
    await comment.pressSequentially(' please take a look');
    await panel.getByRole('button', { name: 'Comment' }).click();

    // B's badge increments without a reload.
    await expect.poll(() => unreadCount(b), { timeout: 15_000 }).toBeGreaterThan(before);

    // And the notification is listed on B's notifications page.
    await b.goto('/notifications');
    await expect(b.getByText(/mentioned you/).first()).toBeVisible();
  } finally {
    await ctxA.close();
    await ctxB.close();
  }
});
