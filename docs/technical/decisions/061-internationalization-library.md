# Decision 061: Internationalization Library

**Status:** Decided

**Category:** Client Architecture

**Question:** Which i18n framework manages translation strings?

**Options considered:**
- `react-intl` (FormatJS)
- `i18next` / `react-i18next`
- Lingui

**Decision:** `react-intl` (FormatJS) with ICU MessageFormat.

- English strings live in `apps/web/src/locales/en.json`.
- Launch locales: English only — per Decision 018, but the plumbing is in place for more.
- Messages with plurals/selects use ICU syntax (`{count, plural, one {# task} other {# tasks}}`).
- `Intl.*` APIs (Decision 020) handle dates, times, numbers.
- Locale bundles will be lazy-loaded when a second locale is added.

**Rationale:** ICU MessageFormat is the most rigorous option for plural/select/gender rules, avoiding the bugs that simpler template approaches ship with. FormatJS aligns with the `Intl` API strategy. `i18next` would be simpler but less correct for real localization work; since we are building-in i18n-readiness now to avoid rework later, rigor wins.
