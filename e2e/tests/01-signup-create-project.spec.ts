import { expect, test } from '@playwright/test';
import { expectNoA11yViolations } from '../helpers/axe';
import { SEED_PASSWORD, uniqueEmail } from '../helpers/data';

/**
 * Journey 1 (plan §I1): sign up → create a workspace → create the first project,
 * as a brand-new Owner. Uses a unique email so it is idempotent across reruns.
 */
test('Journey 1 — signup creates a workspace, then the first project', async ({ page }) => {
  const email = uniqueEmail('owner');
  const workspaceName = `E2E Studio ${Date.now()}`;

  await page.goto('/signup');
  await expectNoA11yViolations(page);

  await page.getByLabel('Display name').fill('E2E Owner');
  await page.getByLabel('Email').fill(email);
  await page.getByLabel('Password').fill(SEED_PASSWORD);
  await page.getByLabel('Workspace name').fill(workspaceName);
  await page.getByRole('button', { name: 'Create workspace' }).click();

  await expect(page).toHaveURL(/\/dashboard$/);
  // A fresh Owner sees the first-run "create a project" prompt.
  const firstProject = page.getByRole('button', { name: 'Create your first project' });
  await expect(firstProject).toBeVisible();
  await expectNoA11yViolations(page);

  await firstProject.click();
  const dialog = page.getByRole('dialog');
  await dialog.getByLabel('Project name').fill('Launch Plan');
  await dialog.getByRole('button', { name: 'Create project' }).click();

  // Creating a project routes straight to its board.
  await expect(page).toHaveURL(/\/projects\/[0-9a-f-]+\/board$/);
});
