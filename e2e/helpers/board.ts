import { expect, type Locator, type Page } from '@playwright/test';
import { BROAD_PROJECT } from './data';

/**
 * Navigate to a project's board via the sidebar (scoped to the `<aside>` so the
 * dashboard's project cards don't create an ambiguous match).
 */
export async function openProjectBoard(page: Page, projectName = BROAD_PROJECT): Promise<void> {
  await page.goto('/dashboard');
  await page.locator('aside').getByRole('link', { name: projectName }).click();
  await expect(page).toHaveURL(/\/projects\/[0-9a-f-]+\/board$/);
}

/**
 * A board column container, located from its header status label. Coupled to the
 * column's `w-[280px]` wrapper (BoardView) — the most stable hook available
 * without test ids.
 */
export function boardColumn(page: Page, statusLabel: string): Locator {
  return page.locator(
    `xpath=//span[normalize-space()=${xpathLiteral(statusLabel)}]/ancestor::div[contains(@class,'w-[280px]')][1]`,
  );
}

/** The droppable body of a board column (the `min-h-24` inner box). */
export function columnDropZone(page: Page, statusLabel: string): Locator {
  return boardColumn(page, statusLabel).locator("xpath=.//div[contains(@class,'min-h-24')]");
}

/** A task card (a `<button>`) located by its title, optionally scoped to a column. */
export function taskCard(page: Page, title: string, statusLabel?: string): Locator {
  const scope = statusLabel ? columnDropZone(page, statusLabel) : page;
  return scope.getByRole('button', { name: title });
}

/** Escape a string for safe embedding as an XPath string literal. */
function xpathLiteral(value: string): string {
  if (!value.includes("'")) return `'${value}'`;
  if (!value.includes('"')) return `"${value}"`;
  return `concat('${value.replace(/'/g, "',\"'\",'")}')`;
}
