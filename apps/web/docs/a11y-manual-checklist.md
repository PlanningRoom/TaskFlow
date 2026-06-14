# TaskFlow Frontend — Manual Accessibility Checklist (Phase H4)

WCAG 2.1 AA (DRD §14) is verified by two complementary passes:

1. **Automated** — every component test runs `vitest-axe` (`src/test/axe.ts`). This
   covers ARIA roles/names, label associations, and structural rules on rendered
   markup. The `color-contrast` rule is disabled there because jsdom has no layout
   engine, so contrast is checked manually below.
2. **Manual** — the items in this file. They require a real browser, a screen
   reader, or a second client and therefore cannot run in CI. Run them against a
   seeded local stack (`make seed`, backend in Docker + `pnpm dev`) before launch
   (Part I) and after any change to navigation, modals, or the realtime layer.

Status: **deferred** — automated coverage is green; the manual passes below are the
standing pre-launch checklist (same runtime-verification caveat as prior frontend
phases). Tick each item during the Part I acceptance sweep.

## Keyboard navigation (DRD §14.2)
- [ ] Every interactive element is reachable with Tab and operable with Enter/Space.
- [ ] Focus order is logical on: login, signup, dashboard, board, list, task panel,
      settings tabs, search overlay.
- [ ] Focus ring (`--primary` border + `--primary-ring` glow) is visible on all
      focusable elements.
- [ ] Board drag-and-drop has a working keyboard alternative: the per-row/per-card
      status dropdown changes status without a pointer (DRD §14.2 / §14.4).
- [ ] Modals trap focus; Esc closes; focus returns to the trigger on close
      (Create Project, Create Task, Invite Member, Project Settings, all confirm
      dialogs, Delete Account).
- [ ] Search overlay: ⌘K/Ctrl+K opens; arrows move the active option; Enter
      navigates; Esc closes and restores focus to the trigger.

## Screen reader (VoiceOver / NVDA) (DRD §14.3)
- [ ] Landmarks announce correctly: header, sidebar (`aside`/`nav`), main.
- [ ] Icon-only buttons announce a name (notification bell with count, settings,
      close ×, new project, invite team members, filter-chip remove).
- [ ] Dropdown triggers announce expanded/collapsed state (Radix-provided).
- [ ] Modals announce as dialogs with their title and description (the confirm
      dialogs read their consequence sentence via `aria-describedby`).
- [ ] Live region announces: incoming @mention, "Reconnecting…", "Back online"
      (`RealtimeProvider` polite region); new-notification badge updates silently.
- [ ] Status badges, priority, and overdue state are conveyed by text/icon, not
      color alone (DRD §14.1).

## Color contrast (DRD §14.1) — spot-check against DRD §2 tokens
- [ ] Body text on `--bg-app` / `--bg-card` ≥ 4.5:1.
- [ ] Secondary/tertiary text ≥ 4.5:1 (or ≥ 3:1 if large).
- [ ] White text on each fixed label color and on `--primary` ≥ 4.5:1.
- [ ] Status badge text on its tint ≥ 4.5:1.
- [ ] Focus ring is distinguishable against adjacent backgrounds.

## Reduced motion (DRD §13.2)
- [ ] With `prefers-reduced-motion: reduce`, no element animates: task panel slide,
      toast fade, modal transitions all become instant (global rule in
      `styles/global.css`).

## Realtime two-client check (carried over from H1)
- [ ] Two browser contexts, same workspace: user A moves a task on the board →
      user B sees the move within ~1s without reloading.
- [ ] User A @mentions user B in a comment → B's notification badge increments and
      the polite live region announces the mention.
