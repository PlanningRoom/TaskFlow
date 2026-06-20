import { expect, test } from '@playwright/test';
import { login } from '../helpers/auth';
import { expectNoA11yViolations } from '../helpers/axe';
import { openProjectBoard } from '../helpers/board';
import { SEED_NAMES, SEED_TASK_TITLE, SEED_USERS } from '../helpers/data';

/**
 * Journey 6 (plan §I1): global search, filtering, and the filtered-empty state.
 * The empty case filters by the Viewer as assignee — no seeded broad-project task
 * is assigned to them, and the journeys that create tasks never assign the
 * Viewer, so the result is deterministically zero.
 */
test('Journey 6 — search, filter, and empty states', async ({ page }) => {
  await login(page, SEED_USERS.owner);
  await openProjectBoard(page);

  // Global ⌘K search surfaces a seeded task.
  await page.keyboard.press('ControlOrMeta+KeyK');
  const search = page.getByRole('combobox', { name: 'Search tasks' });
  await expect(search).toBeFocused();
  await search.fill('Sprint');
  await expect(
    page.getByRole('listbox').getByRole('option', { name: new RegExp(SEED_TASK_TITLE) }),
  ).toBeVisible();
  await page.keyboard.press('Escape');

  // Filter by an assignee with no tasks → the filtered-empty state.
  await page.getByRole('button', { name: 'Filter' }).click();
  await page.getByRole('menuitem', { name: SEED_NAMES.viewer }).click();
  await page.keyboard.press('Escape'); // close the filter popover
  await expect(page).toHaveURL(/assignee=/);
  await expect(page.getByText('No tasks match these filters.')).toBeVisible();
  await expectNoA11yViolations(page);

  // Clearing filters restores the populated board.
  await page.getByRole('button', { name: 'Clear filters' }).click();
  await expect(page.getByRole('button', { name: SEED_TASK_TITLE })).toBeVisible();
});
