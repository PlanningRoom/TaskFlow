# Decision 004: Typography

**Status:** Decided

**Category:** Visual Identity & Brand

**Question:** What font family should TaskFlow use (system fonts, or a web font like Inter, Geist, etc.), and what is the type scale and heading hierarchy?

**Decision:** Inter as the primary typeface, with the system font stack as fallback. The type scale uses a base size of 14px for body text with a modular scale for headings:

- **Body:** 14px / 1.5 line height
- **Small / caption:** 12px
- **H1:** 24px, semibold
- **H2:** 20px, semibold
- **H3:** 16px, semibold
- **UI labels / buttons:** 14px, medium weight
- **Monospace (code blocks):** System monospace stack

**Rationale:** Inter is the de facto standard for modern SaaS interfaces — it was designed specifically for screens, has excellent legibility at small sizes, supports a wide range of weights, and is free via Google Fonts. It pairs perfectly with a minimal & soft modern aesthetic. The 14px base balances readability with density for a task management tool where users scan lists and boards. The modular scale provides clear hierarchy without dramatic size jumps.
