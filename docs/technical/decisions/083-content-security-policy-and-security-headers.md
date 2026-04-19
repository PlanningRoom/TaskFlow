# Decision 083: Content Security Policy & Security Headers

**Status:** Decided

**Category:** Security Hardening

**Question:** Which security headers are served, and what is the CSP?

**Options considered:**
- Strict CSP with nonces
- Moderate CSP with `'unsafe-inline'` for styles
- Report-only then enforce

**Decision:** Strict CSP, enforced from launch. Headers set by nginx on every response.

**Content-Security-Policy:**
```
default-src 'self';
script-src 'self';
style-src 'self' https://fonts.googleapis.com;
font-src https://fonts.gstatic.com;
img-src 'self' data:;
connect-src 'self' wss://{host};
frame-ancestors 'none';
base-uri 'self';
form-action 'self';
object-src 'none';
```

No `'unsafe-inline'`, no `'unsafe-eval'`. Tailwind compiles to class-based styles (no inline `style=""`), so `'unsafe-inline'` in `style-src` is unnecessary. Google Fonts (Decision 023) is allowed specifically.

**Other security headers:**
- `Strict-Transport-Security: max-age=63072000; includeSubDomains; preload`
- `X-Content-Type-Options: nosniff`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=()`
- `X-Frame-Options: DENY`

**Rationale:** CSP is the backstop if Markdown sanitization (Decision 060) ever fails. Strict from launch avoids the "we'll tighten it later" trap. `frame-ancestors 'none'` prevents clickjacking.
