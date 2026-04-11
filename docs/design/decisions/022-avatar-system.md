# Decision 022: Avatar System

**Status:** Decided

**Category:** User Identity

**Question:** How should user avatars be displayed? Options include initials on a colored background, Gravatar integration, user-uploaded photos, or abstract identicons. This has both a scope component (upload support requires storage infrastructure) and a design component (visual treatment).

**Decision:** Initials-based avatars on a deterministically assigned colored background. Each user is assigned a color from a fixed palette of 8–10 muted colors based on a hash of their user ID, ensuring the color is stable across sessions. The avatar displays the user's first and last initials (or first initial if no last name is provided) in white text on the colored circle.

Sizes: 32px for inline use (task cards, activity feed), 24px for compact contexts (list view rows), 40px for profile/header areas.

**Rationale:** Initials-based avatars work immediately with no setup required by the user — every new account gets a recognizable avatar automatically. This avoids the infrastructure of file uploads (storage, resizing, CDN) and the dependency on Gravatar (external service, requires user to have configured it). The deterministic color assignment means users become recognizable by their color+initials combination, which aids scanning on boards and activity feeds. The muted color palette matches the soft modern personality.
