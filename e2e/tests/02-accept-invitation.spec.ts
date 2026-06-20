import { expect, test } from '@playwright/test';
import { login } from '../helpers/auth';
import { expectNoA11yViolations } from '../helpers/axe';
import { SEED_PASSWORD, SEED_USERS, uniqueEmail, WORKSPACE_NAME } from '../helpers/data';
import { waitForInvitationToken } from '../helpers/mailhog';

/**
 * Journey 2 (plan §I1): a new user accepts an emailed invitation. The Owner
 * sends the invite from Settings → Members; the token is recovered from MailHog;
 * a clean session accepts it and lands in the Aurora Studio workspace.
 */
test('Journey 2 — a new user accepts an emailed invitation', async ({ page, request }) => {
  const inviteEmail = uniqueEmail('invitee');

  await login(page, SEED_USERS.owner);
  await page.goto('/settings/members');
  await page.getByRole('button', { name: 'Invite member' }).click();

  const invite = page.getByRole('dialog');
  await invite.getByLabel('Email').fill(inviteEmail);
  await invite.getByRole('button', { name: 'Send invitation' }).click();
  await expect(invite).toBeHidden();

  const token = await waitForInvitationToken(request, inviteEmail);

  // Accept as a brand-new user in a logged-out session.
  await page.context().clearCookies();
  await page.goto(`/invitations/${token}`);
  await expectNoA11yViolations(page);

  await page.getByLabel('Display name').fill('Invited Newcomer');
  await page.getByLabel('Password').fill(SEED_PASSWORD);
  await page.getByRole('button', { name: 'Create account & join' }).click();

  await expect(page).toHaveURL(/\/dashboard$/);
  // They are now inside Aurora Studio (the invited-user welcome names the workspace).
  await expect(page.getByText(`Welcome to ${WORKSPACE_NAME}.`)).toBeVisible();
});
