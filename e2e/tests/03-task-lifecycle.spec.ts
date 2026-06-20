import { expect, test } from '@playwright/test';
import { login } from '../helpers/auth';
import { expectNoA11yViolations } from '../helpers/axe';
import { columnDropZone, openProjectBoard, taskCard } from '../helpers/board';
import { SEED_NAMES, SEED_USERS } from '../helpers/data';
import { dragTo } from '../helpers/dnd';

/**
 * Journey 3 (plan §I1): create a task → drag Backlog → In Progress → comment with
 * an @mention → mark Done. Creates its own task so it never depends on seeded
 * task state being pristine.
 */
test('Journey 3 — task lifecycle: create, drag, comment, complete', async ({ page }) => {
  const title = `E2E lifecycle ${Date.now()}`;

  await login(page, SEED_USERS.owner);
  await openProjectBoard(page);
  await expectNoA11yViolations(page);

  // Create the task — lands in Backlog by default.
  await page.getByRole('button', { name: 'Create task' }).click();
  const create = page.getByRole('dialog');
  await create.getByLabel('Title').fill(title);
  await create.getByRole('button', { name: 'Create task' }).click();
  await expect(create).toBeHidden();
  await expect(taskCard(page, title, 'Backlog')).toBeVisible();

  // Drag it to In Progress.
  await dragTo(page, taskCard(page, title), columnDropZone(page, 'In Progress'));
  await expect(taskCard(page, title, 'In Progress')).toBeVisible();

  // Open the detail panel and comment with an @mention of another member.
  await taskCard(page, title).click();
  const panel = page.getByRole('dialog', { name: 'Task details' });
  const comment = panel.getByPlaceholder('Write a comment… use @ to mention');
  await comment.click();
  await comment.pressSequentially('Nice — @mason');
  await panel.getByRole('button', { name: SEED_NAMES.dev2 }).click(); // pick from the @mention menu
  await comment.pressSequentially(' please review');
  await panel.getByRole('button', { name: 'Comment' }).click();
  await expect(panel.getByText('please review')).toBeVisible();

  // Mark it Done via the status dropdown.
  await panel.getByRole('button', { name: 'Change status' }).click();
  await page.getByRole('menuitem', { name: 'Done' }).click();
  await expect(
    panel.getByRole('button', { name: 'Change status' }).getByText('Done'),
  ).toBeVisible();
});
