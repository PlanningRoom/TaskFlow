# TaskFlow — Screen Inventory & Data Contracts

**Version:** 1.0
**Date:** 2026-04-11
**Status:** Draft

---

## 1. Purpose

This document catalogs every page, panel, modal, and overlay in TaskFlow along with the data each screen requires. It serves as a bridge between the product requirements, design decisions, and implementation — ensuring nothing is missed in design and development.

---

## 2. Conventions

**Data contract notation:**

- Fields marked with `*` are required.
- Fields in `[brackets]` are conditional (shown only to certain roles or in certain states).
- `→` indicates a navigation action (where clicking takes the user).
- `Role:` indicates which roles can access the screen or see specific elements.

---

## 3. Pages

### 3.1 Login

**Route:** `/login`
**Role:** Unauthenticated users
**Purpose:** Authenticate an existing user.

| Element | Data |
|---------|------|
| Logo & wordmark | Static |
| Email input | `email*` |
| Password input | `password*` |
| "Log in" button | Submits form |
| "Sign up" link | → Sign Up page |

**Data contract — request:**

```
LoginRequest {
  email: string
  password: string
}
```

**Data contract — response:**

```
LoginResponse {
  token: string
  user: CurrentUser
}
```

**States:** Default, validation error (inline per field), authentication error ("Invalid email or password").

---

### 3.2 Sign Up

**Route:** `/signup`
**Role:** Unauthenticated users
**Purpose:** Create a new account and workspace.

| Element | Data |
|---------|------|
| Logo & wordmark | Static |
| Display name input | `displayName*` |
| Email input | `email*` |
| Password input | `password*` |
| Workspace name input | `workspaceName*` |
| "Create workspace" button | Submits form |
| "Log in" link | → Login page |

**Data contract — request:**

```
SignUpRequest {
  displayName: string
  email: string
  password: string
  workspaceName: string
}
```

**Data contract — response:**

```
SignUpResponse {
  token: string
  user: CurrentUser
  workspace: Workspace
}
```

**States:** Default, validation errors (inline per field), duplicate email error.

---

### 3.3 Accept Invitation

**Route:** `/invitations/:token`
**Role:** Unauthenticated or authenticated users with a valid invitation token
**Purpose:** Accept a workspace invitation, creating an account if needed.

| Element | Data |
|---------|------|
| Logo & wordmark | Static |
| Workspace name | `invitation.workspaceName` |
| Invited role | `invitation.role` |
| Inviter name | `invitation.invitedBy.displayName` |
| **If no existing account:** | |
| Display name input | `displayName*` |
| Email (pre-filled, read-only) | `invitation.email` |
| Password input | `password*` |
| "Create account & join" button | Submits form |
| **If existing account (logged in):** | |
| Confirmation message | "Join [workspace] as [role]?" |
| "Join workspace" button | Accepts invitation |
| **If existing account (logged out):** | |
| "Log in to accept" link | → Login page (returns here after login) |

**Data contract — loaded:**

```
Invitation {
  id: string
  token: string
  email: string
  role: Role
  workspaceName: string
  invitedBy: { displayName: string }
  status: "pending" | "accepted" | "expired"
  expiresAt: datetime
}
```

**States:** Default (new user), default (existing user), invitation expired, invitation already accepted, invalid token.

---

### 3.4 Dashboard

**Route:** `/dashboard`
**Role:** All authenticated users
**Purpose:** Personal overview of assigned work, recent activity, and accessible projects.

**Layout:** Two-column on desktop (60/40), single-column stacked on mobile.

#### Left Column — My Tasks

| Element | Data |
|---------|------|
| Section heading | "My tasks" |
| Task groups | Grouped by `project.name` |
| Each task row: | |
| — Task title | `task.title` → opens task in project view |
| — Status badge | `task.status` with status color |
| — Priority icon | `task.priority` (hidden if None) |
| — Due date | `task.dueDate` with overdue styling |
| Empty state | "No tasks assigned to you yet." + link to browse projects |
| [First-run prompt — Owner] | "Create your first project." → Create Project modal |

**Data contract:**

```
DashboardTasks {
  groups: Array<{
    project: { id: string, name: string }
    tasks: Array<TaskSummary>
  }>
}

TaskSummary {
  id: string
  title: string
  status: Status
  priority: Priority
  dueDate: date | null
  project: { id: string, name: string }
}
```

#### Right Column — Recent Activity

| Element | Data |
|---------|------|
| Section heading | "Recent activity" |
| Activity entries | Chronological list (newest first) |
| Each entry: | |
| — Actor avatar | `entry.actor.initials`, `entry.actor.avatarColor` |
| — Sentence | "[Actor] [action] [target]" |
| — Project name | `entry.project.name` |
| — Relative timestamp | `entry.createdAt` formatted as relative |
| — Click target | → task in project view |
| Empty state | "No recent activity." |

**Data contract:**

```
ActivityEntry {
  id: string
  type: "status_change" | "comment" | "task_created" | "assignment" | "reassignment"
  actor: UserSummary
  task: { id: string, title: string }
  project: { id: string, name: string }
  detail: string | null       // e.g., "to In Review" for status changes
  createdAt: datetime
}
```

#### Right Column — Projects

| Element | Data |
|---------|------|
| Section heading | "Projects" |
| Each project row: | |
| — Project name | `project.name` → project board view |
| — Task count summary | Count per status (e.g., "3 to do · 5 in progress · 2 done") |
| Empty state | "No projects yet." + [Create Project button for Owner/Admin/Member] |

**Data contract:**

```
ProjectSummary {
  id: string
  name: string
  taskCounts: {
    backlog: number
    todo: number
    inProgress: number
    inReview: number
    done: number
    cancelled: number
  }
}
```

---

### 3.5 Project — Board View

**Route:** `/projects/:projectId/board`
**Role:** All users with project access
**Purpose:** Primary project view showing tasks as cards in status columns.

#### Project Sub-Navigation Bar

| Element | Data |
|---------|------|
| View toggle | Board (active) / List |
| Filter button | Opens filter dropdowns |
| Active filter chips | One chip per active filter, each with × dismiss |
| "Clear all" link | Shown when filters are active |
| Sort dropdown | Creation date (default), priority, due date, assignee |
| [Project settings icon] | → Project Settings modal (Owner/Admin only) |
| ["Create task" button] | Opens Create Task modal (Owner/Admin/Member only) |

#### Board Columns

One column per status: Backlog, To Do, In Progress, In Review, Done. Cancelled hidden by default (visible via status filter).

| Element | Data |
|---------|------|
| Column header | `status.label` with status color indicator |
| Task count | `column.tasks.length` |
| Task cards | Ordered by current sort |

#### Task Card

| Element | Data |
|---------|------|
| Title | `task.title` (1–2 lines, truncated) |
| Label chips | `task.labels[]` (up to 3 visible, "+N" overflow) |
| Priority icon | `task.priority` (hidden if None) |
| Due date | `task.dueDate` with overdue/approaching styling |
| Comment count | `task.commentCount` with icon |
| Assignee avatar | `task.assignee.initials`, `task.assignee.avatarColor` (empty if unassigned) |
| Click | → opens Task Detail Panel |
| Drag (desktop) | → changes task status to target column |

**Data contract:**

```
ProjectBoard {
  project: Project
  columns: Array<{
    status: Status
    tasks: Array<TaskCard>
  }>
  filters: FilterState
  sort: SortField
}

Project {
  id: string
  name: string
  description: string | null
}

TaskCard {
  id: string
  title: string
  status: Status
  priority: Priority
  dueDate: date | null
  assignee: UserSummary | null
  labels: Array<Label>
  commentCount: number
}

FilterState {
  statuses: Array<Status>        // default: all except Cancelled
  assignees: Array<string>       // user IDs, or "unassigned"
  priorities: Array<Priority>
  labels: Array<string>          // label IDs
  dueDateFilter: "overdue" | "today" | "this_week" | "no_due_date" | null
}

SortField: "created_at" | "priority" | "due_date" | "assignee"
```

**States:** Default (populated), empty project, empty column, filtered with no results, drag in progress (column highlight).

---

### 3.6 Project — List View

**Route:** `/projects/:projectId/list`
**Role:** All users with project access
**Purpose:** Tabular alternative to the board view.

#### Project Sub-Navigation Bar

Same as Board View (Section 3.5), with List toggle active.

#### Task Table

| Column | Data | Sortable |
|--------|------|----------|
| Title | `task.title` → opens Task Detail Panel | Yes |
| Status | `task.status` as badge with dropdown (Owner/Admin/Member) | Yes |
| Assignee | `task.assignee` avatar + name | Yes |
| Priority | `task.priority` icon + label | Yes |
| Due date | `task.dueDate` with overdue styling | Yes |
| Labels | `task.labels[]` as chips | No |

**Data contract:** Same `TaskCard` array as Board View, rendered as rows. Filter and sort state is shared between views.

**States:** Default (populated), empty project, filtered with no results.

---

### 3.7 Notifications

**Route:** `/notifications`
**Role:** All authenticated users
**Purpose:** View all notifications in reverse chronological order.

| Element | Data |
|---------|------|
| Page heading | "Notifications" |
| Each notification: | |
| — Unread indicator | `notification.read` (visual distinction) |
| — Event description | Based on `notification.type` |
| — Task name | `notification.task.title` → task in project view |
| — Project name | `notification.project.name` |
| — Timestamp | `notification.createdAt` formatted as relative |
| Click action | Marks as read, navigates to task |
| "Mark all as read" action | Marks all notifications as read |
| Empty state | "You're all caught up." |

**Data contract:**

```
Notification {
  id: string
  type: "mention" | "assignment" | "status_change" | "comment"
  read: boolean
  actor: UserSummary
  task: { id: string, title: string }
  project: { id: string, name: string }
  detail: string | null
  createdAt: datetime
}
```

---

### 3.8 Settings — Workspace

**Route:** `/settings/workspace`
**Role:** Owner, Admin (read-write); Member, Viewer (no access — redirect to dashboard)
**Purpose:** Edit workspace-level settings.

| Element | Data |
|---------|------|
| Settings sub-navigation | Workspace (active), Members, Labels, Profile |
| Workspace name input | `workspace.name*` |
| "Save" button | Saves changes |

**Data contract:**

```
WorkspaceSettings {
  name: string
}
```

---

### 3.9 Settings — Members

**Route:** `/settings/members`
**Role:** Owner, Admin (read-write); Member, Viewer (no access — redirect to dashboard)
**Purpose:** View and manage workspace members and invitations.

#### Member List

| Column | Data |
|--------|------|
| Avatar | `member.initials`, `member.avatarColor` |
| Name | `member.displayName` |
| Email | `member.email` |
| Role | `member.role` as dropdown (Owner/Admin can change) |
| [Remove button] | Owner only, → Remove Member confirmation modal |

#### Invitation List

| Column | Data |
|--------|------|
| Email | `invitation.email` |
| Role | `invitation.role` |
| Status | `invitation.status` ("pending", "accepted", "expired") |
| Sent date | `invitation.createdAt` |
| [Resend button] | Shown for pending/expired invitations |

| Action | Data |
|--------|------|
| "Invite member" button | → Invite Member modal |

**Data contract:**

```
MemberList {
  members: Array<{
    id: string
    displayName: string
    email: string
    initials: string
    avatarColor: string
    role: Role
  }>
  invitations: Array<{
    id: string
    email: string
    role: Role
    status: "pending" | "accepted" | "expired"
    createdAt: datetime
  }>
}
```

---

### 3.10 Settings — Labels

**Route:** `/settings/labels`
**Role:** Owner, Admin (read-write); Member, Viewer (no access — redirect to dashboard)
**Purpose:** Manage workspace-wide labels.

| Element | Data |
|---------|------|
| Settings sub-navigation | Workspace, Members, Labels (active), Profile |
| Label list | All workspace labels |
| Each label row: | |
| — Color swatch | `label.color` |
| — Label name | `label.name` |
| — Edit button | → Edit Label modal |
| — Delete button | → Delete Label confirmation modal |
| "Create label" button | → Create Label modal |
| Empty state | "No labels yet. Create your first label." |

**Data contract:**

```
Label {
  id: string
  name: string
  color: string    // hex value from the fixed palette
}
```

---

### 3.11 Settings — Profile

**Route:** `/settings/profile`
**Role:** All authenticated users
**Purpose:** Edit personal profile and account settings.

| Element | Data |
|---------|------|
| Settings sub-navigation | Workspace, Members, Labels, Profile (active) |
| Avatar preview | `user.initials`, `user.avatarColor` (read-only) |
| Display name input | `user.displayName*` |
| Email | `user.email` (read-only display) |
| "Save" button | Saves profile changes |
| **Change Password section** | |
| Current password input | `currentPassword*` |
| New password input | `newPassword*` |
| "Update password" button | Saves password change |
| **Danger Zone section** | |
| "Delete account" button | → Delete Account confirmation modal |

**Data contract:**

```
ProfileSettings {
  displayName: string
  email: string (read-only)
}

ChangePasswordRequest {
  currentPassword: string
  newPassword: string
}
```

---

## 4. Panels

### 4.1 Task Detail Panel

**Trigger:** Click a task card (board view), click a task row (list view), click a task in dashboard or activity feed, navigate to task URL
**Route updates to:** `/projects/:projectId/tasks/:taskId`
**Type:** Side panel, slides in from right, overlays current view with dimmed backdrop
**Width:** ~480px desktop, ~60% tablet, full-screen mobile
**Role:** All users with project access can view. Owner, Admin, Member can edit. Viewer is read-only.

#### Header

| Element | Data |
|---------|------|
| Task title | `task.title*` (editable inline for Owner/Admin/Member) |
| Status dropdown | `task.status` (editable for Owner/Admin/Member) |
| Close button | Closes panel, returns to board/list |

#### Properties

| Element | Data |
|---------|------|
| Assignee selector | `task.assignee` — dropdown of project members |
| Priority selector | `task.priority` — dropdown of priority levels |
| Due date picker | `task.dueDate` — date picker, date only |
| Label selector | `task.labels[]` — multi-select from workspace labels |

#### Description

| Element | Data |
|---------|------|
| Rendered Markdown | `task.description` (rendered view by default) |
| Edit mode | Toggles to Markdown text editor |

#### Comments

| Element | Data |
|---------|------|
| Comment list | Chronological (oldest first) |
| Each comment: | |
| — Author avatar | `comment.author.initials`, `comment.author.avatarColor` |
| — Author name | `comment.author.displayName` |
| — Timestamp | `comment.createdAt` formatted as relative |
| — Content | `comment.body` rendered as Markdown |
| — @mentions | Visually highlighted within rendered content |
| [New comment input] | Markdown editor with @mention autocomplete (Owner/Admin/Member) |
| [Submit button] | "Comment" |

**Data contract:**

```
TaskDetail {
  id: string
  title: string
  description: string | null      // raw Markdown
  status: Status
  priority: Priority
  dueDate: date | null
  assignee: UserSummary | null
  labels: Array<Label>
  comments: Array<Comment>
  project: { id: string, name: string }
  createdAt: datetime
}

Comment {
  id: string
  body: string                     // raw Markdown with @mention syntax
  author: UserSummary
  createdAt: datetime
}

UserSummary {
  id: string
  displayName: string
  initials: string
  avatarColor: string
}
```

**States:** Default (populated), empty description, no comments, Viewer read-only (no edit controls, no comment input).

---

## 5. Modals

### 5.1 Create Project

**Trigger:** "Create project" button (sidebar, dashboard empty state, first-run prompt)
**Role:** Owner, Admin, Member

| Element | Data |
|---------|------|
| Modal heading | "Create project" |
| Project name input | `name*` |
| Description input | `description` (optional, textarea) |
| "Cancel" button | Closes modal |
| "Create project" button | Submits form |

**Data contract — request:**

```
CreateProjectRequest {
  name: string
  description: string | null
}
```

**States:** Default, validation error (name required).

---

### 5.2 Project Settings

**Trigger:** Project settings icon in project sub-nav
**Role:** Owner, Admin

| Element | Data |
|---------|------|
| Modal heading | "Project settings" |
| **Details tab** | |
| Project name input | `project.name*` |
| Description input | `project.description` (textarea) |
| "Save" button | Saves changes |
| **Access tab** | |
| Member access list | Members with access, each with a remove (×) button |
| "Add member" dropdown | Workspace members not yet added |
| Each row: avatar, name, role badge, remove button |

**Data contract:**

```
ProjectSettings {
  name: string
  description: string | null
  members: Array<{
    id: string
    displayName: string
    initials: string
    avatarColor: string
    role: Role
  }>
}

UpdateProjectRequest {
  name: string
  description: string | null
}

UpdateProjectAccessRequest {
  addUserIds: Array<string>
  removeUserIds: Array<string>
}
```

**States:** Default, validation error (name required).

---

### 5.3 Create Task

**Trigger:** "Create task" button in project sub-nav or board empty state
**Role:** Owner, Admin, Member

| Element | Data |
|---------|------|
| Modal heading | "Create task" |
| Title input | `title*` |
| Description input | `description` (optional, Markdown textarea) |
| Assignee dropdown | `assigneeId` — project members or unassigned |
| Priority dropdown | `priority` — None (default), Low, Medium, High, Urgent |
| Due date picker | `dueDate` — date only |
| Label multi-select | `labelIds[]` — workspace labels |
| "Cancel" button | Closes modal |
| "Create task" button | Submits form, task defaults to Backlog status |

**Data contract — request:**

```
CreateTaskRequest {
  title: string
  description: string | null
  assigneeId: string | null
  priority: Priority              // default: "none"
  dueDate: date | null
  labelIds: Array<string>
}
```

**Data contract — supporting data (loaded into dropdowns):**

```
TaskFormOptions {
  members: Array<UserSummary>     // project members for assignee
  labels: Array<Label>            // workspace labels
}
```

**States:** Default, validation error (title required).

---

### 5.4 Invite Member

**Trigger:** "Invite member" button on Settings — Members page, or first-run "Invite team members" prompt
**Role:** Owner, Admin

| Element | Data |
|---------|------|
| Modal heading | "Invite member" |
| Email input | `email*` |
| Role dropdown | `role*` — Admin, Member, Viewer (Owner cannot be assigned) |
| "Cancel" button | Closes modal |
| "Send invitation" button | Submits form |

**Data contract — request:**

```
InviteMemberRequest {
  email: string
  role: "admin" | "member" | "viewer"
}
```

**States:** Default, validation error (email required, valid format), duplicate email error ("That email address is already in this workspace").

---

### 5.5 Remove Member Confirmation

**Trigger:** Remove button on member row in Settings — Members
**Role:** Owner

| Element | Data |
|---------|------|
| Modal heading | "Remove member" |
| Confirmation message | "Remove [displayName] from this workspace? They'll lose access immediately, and their assigned tasks will become unassigned." |
| "Cancel" button | Closes modal |
| "Remove member" button (destructive) | Executes removal |

**Data contract — request:**

```
RemoveMemberRequest {
  userId: string
}
```

---

### 5.6 Create Label

**Trigger:** "Create label" button on Settings — Labels page
**Role:** Owner, Admin

| Element | Data |
|---------|------|
| Modal heading | "Create label" |
| Name input | `name*` |
| Color palette selector | `color*` — select from fixed palette swatches |
| Preview | Shows label chip as it will appear |
| "Cancel" button | Closes modal |
| "Create label" button | Submits form |

**Data contract — request:**

```
CreateLabelRequest {
  name: string
  color: string                   // hex from fixed palette
}
```

**States:** Default, validation error (name required, color required).

---

### 5.7 Edit Label

**Trigger:** Edit button on label row in Settings — Labels
**Role:** Owner, Admin

| Element | Data |
|---------|------|
| Modal heading | "Edit label" |
| Name input | `label.name*` (pre-filled) |
| Color palette selector | `label.color*` (pre-selected) |
| Preview | Updated label chip |
| "Cancel" button | Closes modal |
| "Save" button | Submits form |

**Data contract — request:**

```
UpdateLabelRequest {
  name: string
  color: string
}
```

---

### 5.8 Delete Label Confirmation

**Trigger:** Delete button on label row in Settings — Labels
**Role:** Owner, Admin

| Element | Data |
|---------|------|
| Modal heading | "Delete label" |
| Confirmation message | "Delete the label \"[name]\"? It will be removed from all tasks." |
| "Cancel" button | Closes modal |
| "Delete label" button (destructive) | Executes deletion |

**Data contract — request:**

```
DeleteLabelRequest {
  labelId: string
}
```

---

### 5.9 Delete Account Confirmation

**Trigger:** "Delete account" button on Settings — Profile
**Role:** All authenticated users (own account only)

| Element | Data |
|---------|------|
| Modal heading | "Delete account" |
| Confirmation message | "Delete your account? Your personal data will be removed. Tasks and comments you created will be kept but anonymized." |
| Password input | `password*` (confirm identity) |
| "Cancel" button | Closes modal |
| "Delete account" button (destructive) | Executes deletion |

**Data contract — request:**

```
DeleteAccountRequest {
  password: string
}
```

---

## 6. Overlays & Dropdowns

### 6.1 Search Results Dropdown

**Trigger:** Focus on or type in the global search input (also Cmd+K / Ctrl+K)
**Location:** Below the header search input
**Role:** All authenticated users

| Element | Data |
|---------|------|
| Search input | `query` typed by user |
| Results list (max ~8 visible) | Filtered as user types |
| Each result: | |
| — Task title | `result.title` (matched text highlighted) |
| — Project name | `result.project.name` |
| — Status badge | `result.status` with color |
| Click action | → task in project view with detail panel open |
| No results state | "No tasks match your search." |
| Keyboard navigation | Arrow keys to select, Enter to navigate, Escape to close |

**Data contract:**

```
SearchResult {
  id: string
  title: string
  status: Status
  project: { id: string, name: string }
}
```

---

### 6.2 User Menu Dropdown

**Trigger:** Click user avatar in the global header
**Location:** Below the avatar, aligned right
**Role:** All authenticated users

| Element | Data |
|---------|------|
| User display name | `user.displayName` |
| User email | `user.email` |
| User role badge | `user.role` |
| "Settings" link | → Settings — Profile |
| "Sign out" action | Logs out, → Login page |

---

### 6.3 Filter Dropdowns

**Trigger:** Click "Filter" button in project sub-nav
**Location:** Below the filter button in the project sub-nav
**Role:** All users with project access

| Filter | Options | Data Source |
|--------|---------|-------------|
| Status | Checkboxes for each status | Fixed statuses |
| Assignee | Checkboxes for project members + "Unassigned" | `project.members` |
| Priority | Checkboxes for each level | Fixed priorities |
| Label | Checkboxes for each label | `workspace.labels` |
| Due date | Radio: Overdue, Due today, Due this week, No due date | Computed from `task.dueDate` |

Each filter applies immediately on selection. Active selections appear as removable chips below the toolbar.

---

### 6.4 @Mention Autocomplete

**Trigger:** Type `@` in the comment input or task description editor
**Location:** Inline below the cursor position
**Role:** Owner, Admin, Member (within comment/description editors)

| Element | Data |
|---------|------|
| Suggestion list | Filtered as user types after `@` |
| Each suggestion: | |
| — Avatar | `user.initials`, `user.avatarColor` |
| — Display name | `user.displayName` |
| Select action | Inserts @mention into text |

**Data contract:**

```
MentionSuggestion {
  id: string
  displayName: string
  initials: string
  avatarColor: string
}
```

Source: workspace members list.

---

## 7. Persistent Shell

The following elements are present on every authenticated page.

### 7.1 Sidebar

| Element | Data |
|---------|------|
| Logo / wordmark | Static (icon-only on tablet) |
| "Dashboard" link | → Dashboard |
| "Notifications" link | → Notifications (with unread count badge) |
| "Projects" heading | Static |
| Project list | `projects[]` — user's accessible projects |
| Each project: name | `project.name` → project board view |
| ["New project" action] | → Create Project modal (Owner/Admin/Member) |
| **Bottom section** | |
| "Settings" link | → Settings — Workspace |
| User avatar + name | `user.initials`, `user.avatarColor`, `user.displayName` |
| User role | `user.role` |

**Data contract:**

```
SidebarData {
  user: CurrentUser
  projects: Array<{ id: string, name: string }>
  unreadNotificationCount: number
}

CurrentUser {
  id: string
  displayName: string
  email: string
  initials: string
  avatarColor: string
  role: Role
}
```

### 7.2 Global Header

| Element | Data |
|---------|------|
| Hamburger icon (mobile only) | Opens sidebar |
| Breadcrumb / page title | Derived from current route |
| Search input | Always visible |
| Notifications bell | `unreadNotificationCount` as badge |
| User avatar | `user.initials`, `user.avatarColor` → User Menu Dropdown |

---

## 8. Shared Types

These types are referenced across multiple screens.

```
Role: "owner" | "admin" | "member" | "viewer"

Status: "backlog" | "todo" | "in_progress" | "in_review" | "done" | "cancelled"

Priority: "none" | "low" | "medium" | "high" | "urgent"

Label {
  id: string
  name: string
  color: string
}

UserSummary {
  id: string
  displayName: string
  initials: string
  avatarColor: string
}
```

---

## 9. Screen Count Summary

| Type | Count | Items |
|------|-------|-------|
| **Pages** | 11 | Login, Sign Up, Accept Invitation, Dashboard, Board View, List View, Notifications, Settings (Workspace, Members, Labels, Profile) |
| **Panels** | 1 | Task Detail |
| **Modals** | 9 | Create Project, Project Settings, Create Task, Invite Member, Remove Member, Create Label, Edit Label, Delete Label, Delete Account |
| **Overlays / Dropdowns** | 4 | Search Results, User Menu, Filter Dropdowns, @Mention Autocomplete |
| **Persistent Shell** | 2 | Sidebar, Global Header |
| **Total** | 27 | |

---

## 10. Reference Documents

| Document | Location |
|----------|----------|
| Product Requirements Document | [docs/product/product-requirements-document.md](../product/product-requirements-document.md) |
| Design Decisions | [docs/design/decisions/INDEX.md](decisions/INDEX.md) |
| Tone & Voice Guide | [docs/design/tone-and-voice-guide.md](tone-and-voice-guide.md) |
| Information Architecture | [docs/product/information-architecture.md](../product/information-architecture.md) |
