import type { Locator, Page } from '@playwright/test';

/**
 * Drag a dnd-kit draggable onto a droppable. dnd-kit's PointerSensor has a 5px
 * activation constraint and does not respond to Playwright's high-level
 * `dragTo`, so we drive the pointer by hand: press, nudge past the threshold,
 * glide to the target in steps, settle, release.
 */
export async function dragTo(page: Page, source: Locator, target: Locator): Promise<void> {
  const from = await source.boundingBox();
  const to = await target.boundingBox();
  if (!from || !to) throw new Error('drag source or target is not visible');

  const sx = from.x + from.width / 2;
  const sy = from.y + from.height / 2;
  const tx = to.x + to.width / 2;
  const ty = to.y + Math.min(to.height / 2, 80);

  await page.mouse.move(sx, sy);
  await page.mouse.down();
  await page.mouse.move(sx + 8, sy + 8, { steps: 6 }); // exceed the 5px activation distance
  await page.waitForTimeout(150); // let dnd-kit activate the drag and measure droppables
  await page.mouse.move(tx, ty, { steps: 12 });
  await page.mouse.move(tx, ty + 4, { steps: 4 }); // settle over the droppable
  await page.waitForTimeout(150); // let collision detection register the drop target
  await page.mouse.up();
}
