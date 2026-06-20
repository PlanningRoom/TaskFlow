import type { APIRequestContext } from '@playwright/test';

/**
 * MailHog HTTP API helpers. The dev email adapter delivers via SMTP→MailHog
 * (apps/api/taskflow/services/emails.py); these read the inbox so the
 * accept-invitation journey can recover the emailed token. Invitation emails are
 * multipart (text + html) with base64 transfer encoding, so we decode each MIME
 * part before scanning for the accept URL.
 */
const MAILHOG_URL = process.env.MAILHOG_URL ?? 'http://localhost:8025';

interface MailhogPart {
  Headers?: Record<string, string[]>;
  Body?: string;
}

interface MailhogMessage {
  Content?: { Body?: string };
  MIME?: { Parts?: MailhogPart[] };
}

function decodeQuotedPrintable(input: string): string {
  return input
    .replace(/=\r?\n/g, '')
    .replace(/=([0-9A-Fa-f]{2})/g, (_match, hex: string) => String.fromCharCode(parseInt(hex, 16)));
}

/** Plausible plaintext decodings of a transfer-encoded MIME part body. */
function decodeVariants(raw: string, encoding?: string): string[] {
  const variants = [raw, decodeQuotedPrintable(raw)];
  const looksBase64 =
    (encoding ?? '').toLowerCase().includes('base64') || /^[A-Za-z0-9+/=\s]+$/.test(raw);
  if (looksBase64) {
    try {
      variants.push(Buffer.from(raw, 'base64').toString('utf-8'));
    } catch {
      // not valid base64 — ignore
    }
  }
  return variants;
}

function findInvitationToken(message: MailhogMessage): string | null {
  const bodies: Array<{ raw: string; encoding?: string }> = [];
  if (message.Content?.Body) bodies.push({ raw: message.Content.Body });
  for (const part of message.MIME?.Parts ?? []) {
    if (part.Body) {
      bodies.push({ raw: part.Body, encoding: part.Headers?.['Content-Transfer-Encoding']?.[0] });
    }
  }
  for (const { raw, encoding } of bodies) {
    for (const text of decodeVariants(raw, encoding)) {
      const match = text.match(/\/invitations\/([^\s"'<>]+)/);
      if (match?.[1]) return match[1];
    }
  }
  return null;
}

/**
 * Poll until an invitation email addressed to `toEmail` arrives, then return its
 * raw token (the `/invitations/<token>` path segment from the accept URL).
 */
export async function waitForInvitationToken(
  request: APIRequestContext,
  toEmail: string,
  timeoutMs = 20_000,
): Promise<string> {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    const res = await request.get(
      `${MAILHOG_URL}/api/v2/search?kind=to&query=${encodeURIComponent(toEmail)}`,
    );
    if (res.ok()) {
      const body = (await res.json()) as { items?: MailhogMessage[] };
      for (const item of body.items ?? []) {
        const token = findInvitationToken(item);
        if (token) return token;
      }
    }
    await new Promise((resolve) => setTimeout(resolve, 500));
  }
  throw new Error(`No invitation email for ${toEmail} arrived within ${timeoutMs}ms`);
}
