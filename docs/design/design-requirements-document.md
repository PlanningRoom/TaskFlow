# TaskFlow — Design Requirements Document

**Version:** 1.0
**Date:** 2026-04-11
**Status:** Draft

---

## 1. Introduction

### 1.1 Purpose

This document defines the complete visual and interaction design specification for TaskFlow. It translates the product requirements, design decisions, and tone and voice guide into a concrete, implementable design system. Every color, spacing value, component style, and interaction pattern needed to build TaskFlow is documented here.

### 1.2 Design Direction

TaskFlow uses the **Warm Neutral** design option with the **Ocean Teal** color palette.

- **Warm Neutral** — Off-white and warm gray backgrounds with slightly prominent card shadows and warm undertones. The UI feels grounded and approachable, like a well-designed workspace. Not cold or clinical, but not playful either.
- **Ocean Teal** — A teal primary accent that is professional, calming, and distinct from the semantic colors used for statuses and priorities.

Together these produce an interface that is **minimal and soft modern** — clean without being sterile, warm without being casual.

### 1.3 Reference Documents

| Document | Location |
|----------|----------|
| Product Requirements Document | [docs/product/product-requirements-document.md](../product/product-requirements-document.md) |
| Business Requirements Document | [docs/business/business-requirements-document.md](../business/business-requirements-document.md) |
| Design Decisions | [docs/design/decisions/INDEX.md](decisions/INDEX.md) |
| Tone & Voice Guide | [docs/design/tone-and-voice-guide.md](tone-and-voice-guide.md) |
| Screen Inventory & Data Contracts | [docs/design/screen-inventory.md](screen-inventory.md) |
| Design Mockup | [docs/design/mockup.html](mockup.html) |

---

## 2. Design Tokens

All visual values are defined as CSS custom properties (design tokens). This enables future theming (e.g., dark mode) by swapping token values without changing component styles.

### 2.1 Color — Primary (Ocean Teal)

| Token | Value | Usage |
|-------|-------|-------|
| `--primary` | `#0d9488` | Buttons, links, active states, focus rings, selected navigation |
| `--primary-hover` | `#0f766e` | Button hover, link hover |
| `--primary-light` | `#f0fdfa` | Active sidebar item background, light tint for highlights |
| `--primary-lighter` | `#ccfbf1` | Subtle backgrounds, selected states |
| `--primary-text` | `#115e59` | Text on primary-light backgrounds, filter chips |
| `--primary-ring` | `rgba(13, 148, 136, 0.3)` | Focus ring glow on inputs and buttons |
| `--logo-color` | `#0d9488` | Logo icon mark fill |

### 2.2 Color — Backgrounds (Warm Neutral)

| Token | Value | Usage |
|-------|-------|-------|
| `--bg-app` | `#faf9f7` | Main application background |
| `--bg-sidebar` | `#f5f3ef` | Sidebar background |
| `--bg-card` | `#ffffff` | Cards, panels, modals, header, input fields |
| `--bg-surface` | `#f5f3ef` | Secondary surfaces, search input resting state |
| `--bg-hover` | `#f0ede8` | Hover state for interactive elements (sidebar links, ghost buttons) |
| `--bg-input` | `#ffffff` | Form input background |
| `--bg-column` | `#f5f3ef` | Board column card area background |
| `--login-bg` | `#f0ede8` | Login/sign-up page background |

### 2.3 Color — Text (Warm Neutral)

| Token | Value | Usage |
|-------|-------|-------|
| `--text-primary` | `#2c2418` | Headings, task titles, primary content |
| `--text-secondary` | `#75695a` | Body text, descriptions, secondary labels |
| `--text-tertiary` | `#a39888` | Placeholder text, timestamps, muted labels |
| `--text-on-surface` | `#4a3f33` | Text on surface backgrounds (descriptions, comments) |
| `--sidebar-text` | `#5c5244` | Sidebar navigation link text |

### 2.4 Color — Borders & Dividers

| Token | Value | Usage |
|-------|-------|-------|
| `--border-color` | `#e8e4dd` | Card borders, column separators, sub-nav dividers |
| `--border-input` | `#d4cfc7` | Form input borders (resting state) |
| `--border-sidebar` | `#e8e4dd` | Sidebar right border |
| `--divider` | `#ece8e1` | Section dividers, comment separators |

### 2.5 Color — Shadows

| Token | Value | Usage |
|-------|-------|-------|
| `--shadow-card` | `0 1px 3px rgba(120,100,70,0.06), 0 2px 8px rgba(120,100,70,0.03)` | Task cards, dashboard items |
| `--shadow-card-hover` | `0 3px 10px rgba(120,100,70,0.09)` | Card hover state |
| `--shadow-panel` | `0 4px 16px rgba(120,100,70,0.08)` | Task detail side panel |
| `--shadow-modal` | `0 8px 30px rgba(120,100,70,0.12)` | Modal dialogs, login card |
| `--shadow-dropdown` | `0 4px 12px rgba(120,100,70,0.08)` | Search results dropdown, user menu |

Note: Shadows use warm-tinted rgba values (`120,100,70`) rather than pure black to match the warm neutral aesthetic.

### 2.6 Color — Status

| Status | Foreground | Background | Usage |
|--------|-----------|------------|-------|
| Backlog | `#94a3b8` | `#f1f5f9` | Column header, status badge, status dot |
| To Do | `#3b82f6` | `#eff6ff` | Column header, status badge, status dot |
| In Progress | `#f59e0b` | `#fffbeb` | Column header, status badge, status dot |
| In Review | `#8b5cf6` | `#f5f3ff` | Column header, status badge, status dot |
| Done | `#22c55e` | `#f0fdf4` | Column header, status badge, status dot |
| Cancelled | `#e879a0` | `#fff1f2` | Column header, status badge (hidden by default) |

### 2.7 Color — Priority

| Priority | Color | Icon |
|----------|-------|------|
| Urgent | `#ef4444` (red) | Double up arrow |
| High | `#f97316` (orange) | Single up arrow |
| Medium | `#eab308` (yellow) | Horizontal bar |
| Low | `#3b82f6` (blue) | Single down arrow |
| None | — | No icon displayed |

### 2.8 Color — Semantic

| Token | Value | Usage |
|-------|-------|-------|
| `--semantic-error` | `#ef4444` | Error text, destructive buttons, overdue dates |
| `--semantic-error-bg` | `#fef2f2` | Error background tint |
| `--semantic-success` | `#22c55e` | Success toast icon, done status |
| `--semantic-warning` | `#f59e0b` | Approaching due date indicator |

### 2.9 Color — Label Palette

A fixed set of 8 muted colors for workspace labels. Labels display as colored chips with white text.

| Label Color | Value | Example Usage |
|-------------|-------|---------------|
| Blue | `#3b82f6` | "Design" |
| Green | `#22c55e` | "Content" |
| Red | `#ef4444` | "Bug" |
| Purple | `#8b5cf6` | "Feature" |
| Amber | `#f59e0b` | "Research" |
| Pink | `#ec4899` | "Marketing" |
| Cyan | `#06b6d4` | "Infra" |
| Orange | `#f97316` | "Docs" |

All label colors meet WCAG AA contrast requirements for white text on the colored background.

### 2.10 Color — Avatar Palette

A fixed set of 6 muted colors for initials-based avatars. Color is deterministically assigned based on a hash of the user's ID.

| Color | Value |
|-------|-------|
| Purple | `#8b5cf6` |
| Blue | `#3b82f6` |
| Green | `#059669` |
| Amber | `#d97706` |
| Rose | `#e11d48` |
| Cyan | `#0891b2` |

### 2.11 Spacing

Base unit: **4px**. All spacing values are multiples of 4.

| Token | Value | Usage |
|-------|-------|-------|
| `4px` | 4px | Tight gaps (between label chips, inline elements) |
| `6px` | 6px | Small gaps (between filter chips, icon + text) |
| `8px` | 8px | Standard gap (list item spacing, card meta gaps) |
| `10px` | 10px | Sidebar link padding, compact component padding |
| `12px` | 12px | Card internal padding, form group spacing |
| `16px` | 16px | Section padding, generous card padding |
| `20px` | 20px | Panel body padding, modal body padding |
| `24px` | 24px | Page-level padding, section spacing, dashboard grid gap |
| `32px` | 32px | Large section separation |

### 2.12 Border Radius

| Token | Value | Usage |
|-------|-------|-------|
| `--radius-sm` | `6px` | Buttons, form inputs, small cards, avatar-based containers |
| `--radius` | `8px` | Task cards, board column backgrounds, standard containers |
| `--radius-lg` | `12px` | Modals, login card, large panels |
| `10px` | 10px | Status badges (pill shape) |
| `12px` | 12px | Label chips, filter chips (pill shape) |
| `50%` | 50% | Avatars (circle) |

---

## 3. Typography

### 3.1 Font Family

- **Primary:** Inter (loaded via Google Fonts)
- **Fallback:** `-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif`
- **Monospace** (code blocks in descriptions): system monospace stack

### 3.2 Type Scale

| Element | Size | Weight | Line Height | Color |
|---------|------|--------|-------------|-------|
| Page heading (H1) | 24px | 600 (semibold) | 1.3 | `--text-primary` |
| Section heading (H2) | 17–20px | 600 | 1.3 | `--text-primary` |
| Sub-heading (H3) | 15–16px | 600 | 1.4 | `--text-primary` |
| Body text | 14px | 400 (regular) | 1.5 | `--text-on-surface` |
| UI labels / buttons | 14px | 500 (medium) | 1 | Varies |
| Small body / captions | 13px | 400–500 | 1.5 | `--text-secondary` |
| Tiny / meta text | 11–12px | 500 | 1.3 | `--text-tertiary` |
| Section labels (sidebar, settings) | 11px | 600, uppercase, 0.05em tracking | 1 | `--text-tertiary` |

### 3.3 Heading Weight

The Warm Neutral design uses `font-weight: 600` (semibold) for headings — bold enough to establish hierarchy without the heaviness of 700.

---

## 4. Iconography

### 4.1 Icon Library

**Lucide** — open source, outlined style.

### 4.2 Icon Sizing

| Context | Size | Stroke Width |
|---------|------|-------------|
| Standard UI (sidebar, header, buttons) | 18–20px | 1.75px |
| Compact (task cards, table rows) | 13–16px | 2px |
| Search icon in input | 15px | 2px |

### 4.3 Icon Color

Icons inherit the color of their parent text element. They do not have independent color treatments except when representing status or priority (where they use the semantic color).

---

## 5. Logo & Brand Mark

### 5.1 Logo Treatment

- **Icon mark:** A 28×32px rounded square (`border-radius: 7–8px`) filled with `--logo-color` (`#0d9488`), containing a white check-in-box SVG icon.
- **Wordmark:** "TaskFlow" in Inter, `font-weight: 700`, `font-size: 16–22px` depending on context, color `--text-primary`.
- **Sidebar:** Icon mark (28px) + wordmark (16px) side by side. On tablet (collapsed sidebar), icon mark only.
- **Login/sign-up:** Icon mark (32px) + wordmark (22px), centered above the form.

---

## 6. Layout

### 6.1 Application Shell

The authenticated application uses a fixed three-zone layout:

```
┌──────────────────────────────────────────────────┐
│                  Global Header (52px)             │
├──────────┬───────────────────────────────────────┤
│          │                                       │
│ Sidebar  │          Content Area                 │
│ (240px)  │          (flex: 1)                    │
│          │                                       │
│          │                                       │
└──────────┴───────────────────────────────────────┘
```

- **Sidebar:** 240px fixed width, `--bg-sidebar` background, right border `--border-sidebar`.
- **Global Header:** 52px fixed height, `--bg-card` background, bottom border `--border-color`.
- **Content Area:** Fills remaining space, `--bg-app` background. Scrolls independently.

### 6.2 Responsive Breakpoints

| Viewport | Width | Behavior |
|----------|-------|----------|
| **Desktop** | 1024px+ | Full layout — persistent sidebar (240px), all board columns visible |
| **Tablet** | 768–1023px | Sidebar collapses to icon-only width (~60px). Board scrolls horizontally. Task detail panel takes ~60% width. |
| **Mobile** | <768px | Sidebar hidden, accessible via hamburger menu (slide-out overlay). Board columns stack vertically. Task detail panel opens full-screen. |

### 6.3 Sidebar Content & Hierarchy

Top to bottom:

1. **Logo/wordmark** — 16px padding, 12px bottom padding
2. **Primary navigation** (8px horizontal padding)
   - Dashboard (layout grid icon)
   - Notifications (bell icon + unread count badge)
3. **Projects section** (16px top padding)
   - Section header: "Projects" label + "+" new project action
   - Project list: Each item has a colored dot (8px, 2px radius) + project name
4. **Bottom section** (pinned to bottom, top border)
   - Settings link (gear icon)
   - User identity: avatar (32px) + display name + role

**Sidebar link styling:**
- Padding: 8px vertical, 10px horizontal
- Border radius: `--radius-sm`
- Default: `--sidebar-text` color
- Hover: `--bg-hover` background, `--text-primary` color
- Active: `--primary-light` background, `--primary` color

### 6.4 Global Header Content

Left to right:

- **Breadcrumb / page title** — "Dashboard" or "Projects / Marketing Campaign" with `/` separators in `--text-tertiary`. Current page segment in `--text-primary`, `font-weight: 500`.
- **Search input** (pushed right via `margin-left: auto`) — 260px wide, `--bg-surface` resting background, teal focus ring. Includes search icon (left) and keyboard shortcut hint "⌘K" (right).
- **Notification bell** — icon button (34px square) with red badge (16px circle, 9px white text) showing unread count.
- **User avatar** — 28px avatar circle, opens user menu dropdown on click.

---

## 7. Components

### 7.1 Buttons

| Variant | Background | Text | Border | Usage |
|---------|-----------|------|--------|-------|
| **Primary** | `--primary` → `--primary-hover` on hover | White | None | Main actions: Create Project, Create Task, Log in, Save, Comment |
| **Secondary** | Transparent → `--primary-light` on hover | `--primary` | 1px `--primary` | Supporting actions |
| **Ghost** | Transparent → `--bg-hover` on hover | `--text-secondary` → `--text-primary` on hover | None | Toolbar actions, icon buttons, Cancel |
| **Destructive** | `#ef4444` → `#dc2626` on hover | White | None | Remove Member, Delete Account, Delete Label |

**All buttons:**
- Border radius: `--radius-sm` (6px)
- Padding: 9px 16px (standard), 6px 10px (small)
- Font: 14px / 500 weight (standard), 12px (small)
- Transition: 150ms all properties
- Cursor: pointer

### 7.2 Form Inputs

- **Border:** 1px `--border-input` (resting), 1px `--primary` (focused)
- **Focus ring:** `0 0 0 3px var(--primary-ring)`
- **Background:** `--bg-input` (white)
- **Border radius:** `--radius-sm` (6px)
- **Padding:** 9px 12px
- **Font:** 14px, `--text-primary`
- **Placeholder:** `--text-tertiary`
- **Labels:** Positioned above input, 13px, `font-weight: 500`, `--text-on-surface`, 6px bottom margin

**Select dropdowns** use the same styling with a chevron-down icon on the right via `background-image`.

**Textareas** share input styling with `resize: vertical` and `min-height: 80px`.

### 7.3 Avatars

Initials-based circles with deterministically assigned background color.

| Context | Size | Font Size |
|---------|------|-----------|
| Inline (task cards, activity feed, comments) | 32px | 12px |
| Compact (list rows, small references) | 24px | 10px |
| Profile / header | 40px | 14px |
| Header icon area | 28px | 10px |

- Shape: Circle (`border-radius: 50%`)
- Text: White, `font-weight: 600`, centered
- No border or shadow

### 7.4 Status Badges

Pill-shaped badges displaying the status name.

- Border radius: 10px
- Padding: 2px 8px
- Font: 11px, `font-weight: 500`
- Background: status background color (e.g., `#fffbeb` for In Progress)
- Text: status foreground color (e.g., `#f59e0b` for In Progress)

### 7.5 Label Chips

Small colored pills displaying the label name.

- Border radius: 10px
- Padding: 1px 8px
- Font: 11px, `font-weight: 500`
- Background: label color (from the fixed palette)
- Text: white

On task cards, show up to 3 labels. If more exist, show "+N" overflow indicator.

### 7.6 Priority Icons

Displayed as a text character (arrow) in the priority's color, `font-weight: 700`, `font-size: 13px`.

| Priority | Character | Color |
|----------|-----------|-------|
| Urgent | `↑↑` (double up arrow) | `#ef4444` |
| High | `↑` (single up arrow) | `#f97316` |
| Medium | `—` (horizontal bar) | `#eab308` |
| Low | `↓` (single down arrow) | `#3b82f6` |
| None | Not displayed | — |

### 7.7 Due Dates

- Font: 12px, `--text-secondary`
- Format: "Apr 15" (current year) or "Apr 15, 2025" (different year)
- **Overdue:** `--semantic-error` color, `font-weight: 500`
- **Approaching:** `--semantic-warning` color

### 7.8 Toast Notifications

- Position: Fixed, bottom-right, 24px from edges
- Background: `--text-primary` (dark)
- Text: White, 13px, `font-weight: 500`
- Border radius: `--radius` (8px)
- Shadow: `0 4px 20px rgba(0,0,0,0.15)`
- Includes a green checkmark icon for success
- Auto-dismisses after 5 seconds
- Animation: Fade up (200ms ease-out)
- Respects `prefers-reduced-motion` (instant display, no animation)

---

## 8. Page Specifications

### 8.1 Login / Sign Up

**Layout:** Centered card on `--login-bg` background.

- **Card:** 400px max width, `--bg-card` background, `--radius-lg` border radius, `--shadow-modal` shadow, 40px padding
- **Logo:** Centered above form, icon mark (32px) + wordmark (22px)
- **Heading:** "Welcome back" (login) / "Create your workspace" (sign up), 20px, semibold, centered
- **Subtext:** 13px, `--text-secondary`, centered, 28px bottom margin
- **Form fields:** Standard form inputs (see 7.2), 18px spacing between groups
- **Primary button:** Full width, 6px top margin
- **Footer link:** Centered, 13px, `--text-secondary`, with teal link to alternate page

### 8.2 Accept Invitation

**Layout:** Same centered card as login.

- Displays workspace name, inviter name, and assigned role
- For new users: account creation form (display name, email pre-filled, password)
- For existing users: confirmation message with "Join workspace" button
- Expired invitation: error state with message directing user to ask an admin to resend

### 8.3 Dashboard

**Layout:** Two-column grid within the content area, 24px padding, 24px gap.

- **Left column (60%):** My Tasks section
- **Right column (40%):** Recent Activity (top) + Projects (bottom)

#### My Tasks

- **Section title:** "My tasks", 15px, semibold
- **Task groups:** Grouped by project name. Group title: 12px, `font-weight: 600`, `--text-secondary`, 8px bottom margin
- **Task rows:** White card with `--shadow-card`, `--border-color` border, `--radius-sm` border radius, 10px vertical / 12px horizontal padding, 6px gap between rows
- Each row contains: priority icon, task title (13px, medium weight, truncated), status badge, due date
- Hover: `--shadow-card-hover`
- Click: navigates to task in project view with detail panel open
- **Empty state:** "No tasks assigned to you yet." + link to browse projects
- **First-run (Owner):** Contextual prompt to create first project (disappears after first project created)

#### Recent Activity

- **Section title:** "Recent activity", 15px, semibold
- **Activity entries:** Avatar (24px) + sentence-style content, separated by `--divider` borders
- Format: **[Actor name]** [action] **[task name]** — with project name and relative timestamp below in 11px `--text-tertiary`
- Task names are teal (`--primary`) and clickable
- **Empty state:** "No recent activity."

#### Projects

- **Section title:** "Projects", 15px, semibold
- **Project rows:** White card with shadow/border, colored dot (10px, 3px radius) + project name (13px, medium) + task count summary (11px, `--text-tertiary` with colored status dots)
- Click: navigates to project board view
- **Empty state:** "No projects yet." + Create Project button (role-aware)

### 8.4 Board View

**Layout:** Full-height flex column within the content area.

#### Project Sub-Navigation Bar

- Background: `--bg-card`, bottom border `--border-color`, 10px vertical / 24px horizontal padding
- **View toggle:** Two-button toggle (Board / List), `--border-color` border, `--radius-sm` radius. Active button: `--primary` background, white text. Inactive: transparent, `--text-secondary`.
- **Separator:** 1px × 20px vertical line in `--border-color`
- **Filter button:** "Filter" with funnel icon, outlined style matching `--border-color`
- **Sort dropdown:** "Newest first" with down-arrow icon
- **Right side:** "+ Create task" primary button (small variant), shown for Owner/Admin/Member

#### Filter Chips Bar

Shown only when filters are active. Same background and border as sub-nav.

- **Chips:** `--primary-light` background, `--primary-text` color, 12px pill radius, 11px font, × dismiss button
- **Clear all:** Underlined text link, 11px, `--text-secondary`

#### Board Columns

- Horizontal flex layout, 16px gap, 20px vertical / 24px horizontal padding
- **Column width:** 280px fixed, horizontal scroll when columns exceed viewport
- **Column header:** Status color indicator (10px square, 3px radius) + title (13px, 600 weight) + task count (12px, `--text-tertiary`), 12px bottom padding
- **Column card area:** `--bg-column` background, `--radius` border radius, 8px padding, vertical scroll per column
- **Columns shown:** Backlog, To Do, In Progress, In Review, Done (Cancelled hidden by default)

#### Task Cards

- Background: `--bg-card`, `--radius` border radius, `--border-color` border, `--shadow-card` shadow
- Padding: 12px
- Hover: `--shadow-card-hover`, `translateY(-1px)` lift
- Transition: 150ms shadow, 100ms transform
- Click: opens task detail panel

**Card layout (top to bottom):**
1. **Title:** 13px, `font-weight: 500`, `--text-primary`, max 2 lines with ellipsis overflow
2. **Labels:** Flex row of label chips (4px gap), max 3 visible + "+N" overflow, 10px bottom margin from title, 10px bottom margin to meta
3. **Meta row:** Priority icon (left), due date (left), comment count with chat icon (left), assignee avatar 24px (right-aligned)

**Drag-and-drop (desktop):**
- Drag a card between columns to change status
- Drop target column highlights with `--primary-light` background
- No reordering within columns

### 8.5 List View

**Layout:** Table within the content area, same sub-nav as board view with List toggle active.

- **Columns:** Title, Status (dropdown), Assignee (avatar + name), Priority (icon + label), Due date, Labels (chips)
- **All columns sortable** except Labels — click header to toggle ascending/descending
- **Row height:** ~48px (comfortable touch target)
- **Row click:** Opens task detail panel
- **Status change:** Inline dropdown on the status cell (Owner/Admin/Member)
- Filter state is shared with board view and preserved when switching

### 8.6 Notifications

**Layout:** Standard page within the content area, 24px padding.

- **Page title:** "Notifications" in header breadcrumb
- **Notification items:** Reverse chronological, each with unread indicator (teal dot), event description, task name (clickable), project name, relative timestamp
- **Unread styling:** `--primary-light` background tint. Read items: no background.
- Click: marks as read, navigates to task
- "Mark all as read" action at top
- **Empty state:** "You're all caught up."

### 8.7 Settings — Workspace

**Layout:** Settings area with sub-navigation (Workspace, Members, Labels, Profile) as either sidebar tabs or horizontal tabs.

- Workspace name input with Save button
- Accessible to Owner and Admin only (others redirected to dashboard)

### 8.8 Settings — Members

**Layout:** Two sections — member list and invitation list.

- **Member table:** Avatar, name, email, role dropdown (editable by Owner/Admin), remove button (Owner only)
- **Invitation table:** Email, role, status badge (pending/accepted/expired), sent date, resend button
- **Invite member button:** Opens Invite Member modal

### 8.9 Settings — Labels

**Layout:** List of workspace labels with management actions.

- Each row: color swatch, label name, edit button, delete button
- Create label button at top
- Accessible to Owner and Admin only
- **Empty state:** "No labels yet. Create your first label."

### 8.10 Settings — Profile

**Layout:** Profile form + password change + danger zone.

- Avatar preview (read-only), display name input, email (read-only), Save button
- Change password section: current password, new password, Update password button
- Danger zone: Delete account button (destructive)

---

## 9. Panel Specification

### 9.1 Task Detail Panel

**Type:** Side panel, slides in from right
**Trigger:** Click any task (card, row, dashboard item, activity link, or direct URL)
**Route:** Updates to `/projects/:projectId/tasks/:taskId`

**Dimensions:**
- Desktop: 480px width
- Tablet: ~60% viewport width
- Mobile: Full screen

**Overlay behavior:** Dimmed backdrop (`rgba(0, 0, 0, 0.25)`) over the board/list. Board content remains visible but not interactive. Click backdrop to close.

**Animation:** Slide in from right, 200ms ease-out. Respects `prefers-reduced-motion`.

**Panel layout (top to bottom):**

1. **Header** (20px top / 24px horizontal padding, bottom border)
   - Task title: 18px, semibold, `--text-primary`, editable inline (Owner/Admin/Member)
   - Status dropdown: Current status as badge, opens dropdown to change
   - Close button: × character, 30px square, `--text-tertiary`, hover `--bg-hover`

2. **Properties** (20px padding, grid layout: 100px label column + value column, 14px row gap)
   - Status: Status badge
   - Assignee: Avatar (24px) + name, dropdown selector
   - Priority: Priority icon + level name, dropdown selector
   - Due date: Date value with overdue/approaching styling, date picker
   - Labels: Label chips, multi-select from workspace labels
   - Viewers see all properties as read-only (no dropdowns or pickers)

3. **Description** (section title "Description", 13px semibold `--text-secondary`, bottom border)
   - Rendered Markdown view by default
   - Click to toggle to edit mode (Markdown textarea)
   - Supports: bold, italic, lists, links, code blocks, headers
   - 13px, `--text-on-surface`, 1.6 line height

4. **Comments** (section title "Comments")
   - Chronological (oldest first)
   - Each comment: Avatar (24px) + author name (13px, medium, `--text-primary`) + timestamp (11px, `--text-tertiary`) + body (13px, `--text-on-surface`, rendered Markdown)
   - @mentions styled with `--primary` color, `--primary-light` background, 3px radius
   - Comments separated by `--divider` borders
   - New comment input (Owner/Admin/Member): Avatar + text input + "Comment" primary button (small)

---

## 10. Modal Specifications

All modals share common styling:

- **Backdrop:** `rgba(0, 0, 0, 0.35)`, click to close
- **Container:** 480px width, `--bg-card` background, `--radius-lg` border radius, `--shadow-modal` shadow, max-height 85vh with internal scroll
- **Animation:** Fade in + slight scale-up (from 97% to 100%) + translateY (from 8px to 0), 150ms ease-out. Respects `prefers-reduced-motion`.
- **Header:** Modal title (17px, semibold) + close button (×), 20px top / 24px horizontal padding
- **Body:** 20px vertical / 24px horizontal padding, 18px spacing between form groups
- **Footer:** Right-aligned buttons (Cancel ghost + action primary), 24px horizontal / 20px bottom padding

### 10.1 Create Project

- Fields: Project name (required), Description (optional, textarea)
- Action: "Create project" primary button

### 10.2 Project Settings

- Two sections or tabs: Details (name, description, save) and Access (member list with add/remove)
- Action: "Save" primary button (details), inline add/remove (access)

### 10.3 Create Task

- Fields: Title (required), Description (optional, Markdown textarea), Assignee (dropdown), Priority (dropdown, default None), Due date (date picker), Labels (multi-select from fixed palette — clickable chips that toggle selected state)
- Two-column layout for Assignee + Priority row
- Action: "Create task" primary button. Shows success toast on completion.

### 10.4 Invite Member

- Fields: Email (required), Role dropdown (Admin, Member, Viewer — Owner not assignable)
- Action: "Send invitation" primary button

### 10.5 Remove Member (Confirmation)

- Message: "Remove [name] from this workspace? They'll lose access immediately, and their assigned tasks will become unassigned."
- Action: "Remove member" destructive button

### 10.6 Create / Edit Label

- Fields: Label name (required), Color (selection from fixed palette swatches — clickable grid)
- Preview: Shows the label chip as it will appear
- Action: "Create label" / "Save" primary button

### 10.7 Delete Label (Confirmation)

- Message: "Delete the label \"[name]\"? It will be removed from all tasks."
- Action: "Delete label" destructive button

### 10.8 Delete Account (Confirmation)

- Message: "Delete your account? Your personal data will be removed. Tasks and comments you created will be kept but anonymized."
- Fields: Current password (required, to confirm identity)
- Action: "Delete account" destructive button

---

## 11. Overlays & Dropdowns

### 11.1 Search Results Dropdown

- **Trigger:** Focus or type in the global search input, or press ⌘K / Ctrl+K
- **Position:** Below the search input, aligned to input width or wider
- **Shadow:** `--shadow-dropdown`
- **Max visible results:** ~8
- **Each result:** Task title (with matched text highlighted), project name, status badge
- **Keyboard navigation:** Arrow keys to select, Enter to navigate, Escape to close
- **No results:** "No tasks match your search."

### 11.2 User Menu Dropdown

- **Trigger:** Click user avatar in header
- **Position:** Below avatar, right-aligned
- **Content:** User display name, email, role badge, "Settings" link, "Sign out" action

### 11.3 Filter Dropdowns

- **Trigger:** Click "Filter" button in project sub-nav
- **Filters:** Status (checkboxes), Assignee (checkboxes + "Unassigned"), Priority (checkboxes), Label (checkboxes), Due date (radio: Overdue, Due today, Due this week, No due date)
- Selections apply immediately and appear as removable chips

### 11.4 @Mention Autocomplete

- **Trigger:** Type `@` in comment input or description editor
- **Position:** Inline below cursor
- **Each suggestion:** Avatar (24px) + display name
- **Source:** Workspace members list, filtered as user types

---

## 12. Interaction Patterns

### 12.1 Drag-and-Drop (Board View)

- **Desktop only.** Mobile users change status via the dropdown.
- Dragging a card shows visual feedback: drop target column highlights with `--primary-light` background.
- Cards move between columns only (status change). No reordering within columns.
- Keyboard alternative: status dropdown on the task card or in the task detail panel.

### 12.2 View Switching

- Board and List views share the same filter and sort state.
- Switching preserves active filters and is toggled via the view toggle in the project sub-nav.
- The application remembers the user's last-used view per project.

### 12.3 Real-Time Updates

- Task changes, new comments, and new notifications update in real time without page refresh.
- The notification badge count updates in real time.
- Screen reader users are informed of real-time changes via ARIA live regions.

### 12.4 Panel and Modal Dismissal

- **Escape key:** Closes the topmost overlay (modal first, then panel).
- **Backdrop click:** Closes the overlay.
- **Close button (×):** Closes the overlay.

---

## 13. Animation & Motion

### 13.1 Transitions

| Element | Property | Duration | Easing |
|---------|----------|----------|--------|
| Button hover | background, color | 150ms | ease |
| Card hover | box-shadow, transform | 150ms | ease |
| Input focus | border-color, box-shadow | 150ms | ease |
| Sidebar link hover | background, color | 120ms | ease |
| Side panel open | transform (translateX) | 200ms | ease-out |
| Modal open | opacity, transform (scale + translateY) | 150ms | ease-out |
| Toast appear | opacity, transform (translateY) | 200ms | ease-out |

### 13.2 Reduced Motion

When `prefers-reduced-motion: reduce` is active, all transitions are replaced with instant state changes (0ms duration). No element should animate. This is required for WCAG 2.1 AA compliance.

---

## 14. Accessibility

### 14.1 Color Contrast

- All text meets WCAG 2.1 AA minimum contrast ratios: 4.5:1 for normal text, 3:1 for large text.
- Information is never conveyed by color alone — status badges include text labels, priority has directional icons alongside color, overdue dates have both red color and contextual styling.
- The fixed label palette is designed for white text on colored backgrounds meeting AA contrast.

### 14.2 Keyboard Navigation

- All interactive elements are reachable and operable via keyboard.
- Visible focus indicators: `--primary` border + `--primary-ring` glow on all focusable elements.
- Logical tab order throughout the application.
- Board drag-and-drop has a keyboard alternative: status dropdown.

### 14.3 Screen Reader Support

- Semantic HTML elements throughout (nav, main, aside, header, section, button, table).
- ARIA attributes where semantic HTML is insufficient:
  - `aria-live` regions for real-time updates (new notifications, status changes)
  - `aria-label` for icon-only buttons (close, notification bell, settings)
  - `role="dialog"` and `aria-modal="true"` for modals
  - `aria-expanded` for dropdown triggers
- Status changes and new notifications are announced to screen readers.

### 14.4 Alternative Views

The list view serves as an accessible alternative to the board view. It is a general-purpose view available to all users, not hidden behind an accessibility setting.

---

## 15. Responsive Behavior

### 15.1 Desktop (1024px+)

- Sidebar: 240px, persistent, full content
- Board: All 5 status columns visible (may require horizontal scroll on smaller desktops)
- Dashboard: Two-column grid (60/40)
- Task detail panel: 480px overlay
- Search: Full 260px input visible

### 15.2 Tablet (768–1023px)

- Sidebar: Collapsed to icon-only (~60px), tooltip on hover for labels
- Board: Fixed-width columns, horizontal scroll
- Dashboard: Two-column grid (~55/45)
- Task detail panel: ~60% viewport width overlay
- Search: May be reduced width or behind icon

### 15.3 Mobile (<768px)

- Sidebar: Hidden, hamburger menu (slide-out from left with dimmed backdrop, same content as desktop sidebar)
- Board: Columns stack vertically (each column is full width, scroll vertically)
- Dashboard: Single column stacked (My Tasks → Projects → Recent Activity)
- Task detail panel: Full screen
- Search: Full width, may collapse behind icon in header
- List view: Horizontal scroll for table columns, or stacked card layout

---

## 16. Empty States & First-Run

All empty states follow the tone and voice guide — calm, directional, role-aware.

| Area | Message | Call to Action | Viewer Alternative |
|------|---------|---------------|-------------------|
| Dashboard — My Tasks | "No tasks assigned to you yet." | Link to browse projects | Same |
| Dashboard — Recent Activity | "No recent activity." | — | Same |
| Dashboard — Projects | "No projects yet." | "Create your first project" button | "No projects yet." (no button) |
| Board (no tasks) | "This project has no tasks yet." | "Create a task" button | "This project has no tasks yet." (no button) |
| Empty status column | Subtle "No tasks" hint text | — | Same |
| Search — no results | "No tasks match your search." | Suggest broadening the query | Same |
| Filter — no results | "No tasks match these filters." | "Clear filters" link | Same |
| Notifications (empty) | "You're all caught up." | — | Same |

**First-run prompts:**
- **Owner (new workspace):** Contextual prompts integrated into the standard UI (not a wizard): "Create your first project" on the dashboard, "Invite team members" in sidebar/settings. Prompts disappear once the action is completed.
- **Invited user:** Brief welcome message on the dashboard: "Welcome to [Workspace Name]." Disappears once the user has assignments and activity.

---

## 17. Internationalization

- All user-facing text is externalized to translation files using an i18n framework.
- CSS uses logical properties (`margin-inline-start`, `padding-inline-end`) to support future RTL languages.
- Dates, times, and numbers are formatted using the browser's locale via the JavaScript `Intl` API.
- Timestamps are stored in UTC and displayed in the user's local time zone.
- The application launches in English only. The architecture supports adding languages without code changes.

---

## 18. Error & Confirmation Patterns

### 18.1 Inline Validation

- For form fields (sign up, create project, create task)
- Error messages appear directly below the invalid field
- Styling: `--semantic-error` color text, small error icon
- Validation trigger: on blur and on submit

### 18.2 Toast Notifications

- For async feedback and non-blocking confirmations
- Position: fixed, bottom-right corner
- Auto-dismiss: 5 seconds
- Can be manually dismissed
- Examples: "Task created.", "Invitation sent.", "Changes saved.", "Couldn't save your changes. Please try again."

### 18.3 Destructive Confirmation Modals

- For irreversible actions: Remove Member, Delete Account, Delete Label
- Clear description of the action and its consequences
- Cancel button (ghost) + destructive action button (red)
- Specific button labels: "Remove member", "Delete account", "Delete label" — never generic "OK" or "Yes"

---

## 19. Reference — Screen Count

| Type | Count | Items |
|------|-------|-------|
| Pages | 11 | Login, Sign Up, Accept Invitation, Dashboard, Board View, List View, Notifications, Settings (Workspace, Members, Labels, Profile) |
| Panels | 1 | Task Detail |
| Modals | 9 | Create Project, Project Settings, Create Task, Invite Member, Remove Member, Create Label, Edit Label, Delete Label, Delete Account |
| Overlays | 4 | Search Results, User Menu, Filter Dropdowns, @Mention Autocomplete |
| Persistent Shell | 2 | Sidebar, Global Header |
| **Total** | **27** | |

Full data contracts for each screen are documented in the [Screen Inventory](screen-inventory.md).
