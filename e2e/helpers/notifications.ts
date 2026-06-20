import type { Locator, Page } from '@playwright/test';

/** The header notification bell link (its accessible name carries the unread count). */
export function notificationBell(page: Page): Locator {
  // Scope to <header>: the sidebar also has a "Notifications" link.
  return page.locator('header').getByRole('link', { name: /Notifications/ });
}

/** Parse the unread count from the bell's `aria-label` ("Notifications (N unread)" → N). */
export async function unreadCount(page: Page): Promise<number> {
  const label = (await notificationBell(page).getAttribute('aria-label')) ?? '';
  const match = label.match(/\((\d+) unread\)/);
  return match ? Number(match[1]) : 0;
}
