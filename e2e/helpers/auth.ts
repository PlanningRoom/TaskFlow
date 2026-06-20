import { expect, type Page } from '@playwright/test';
import { SEED_PASSWORD } from './data';

/**
 * Log in through the real UI and wait for the dashboard. Used as a precondition
 * for the journeys whose assertion is something other than login itself.
 */
export async function login(page: Page, email: string, password = SEED_PASSWORD): Promise<void> {
  await page.goto('/login');
  await page.getByLabel('Email').fill(email);
  await page.getByLabel('Password').fill(password);
  await page.getByRole('button', { name: 'Log in' }).click();
  await expect(page).toHaveURL(/\/dashboard$/);
}
