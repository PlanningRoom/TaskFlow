# TaskFlow — Product Requirements Document

**Version:** 1.0
**Date:** 2026-04-05
**Status:** Draft

---

## 1. Introduction

### 1.1 Purpose

This document defines the product requirements for TaskFlow — what the application does, how users interact with it, and the expected behavior of every feature. It translates business requirements and product decisions into a specification that can guide design and implementation.

### 1.2 Scope

TaskFlow is a collaborative task management web application for teams of 10–50 users. It is a demonstration project with no revenue model. This PRD covers the initial release.

### 1.3 Reference Documents

| Document | Location |
|----------|----------|
| Business Overview | [docs/business/business-overview.md](../business/business-overview.md) |
| Business Requirements Document | [docs/business/business-requirements-document.md](../business/business-requirements-document.md) |
| User Journeys & Use Cases | [docs/business/user-journeys.md](../business/user-journeys.md) |
| Business Decision Records | [docs/business/decisions/INDEX.md](../business/decisions/INDEX.md) |
| Product Decision Records | [docs/product/decisions/INDEX.md](decisions/INDEX.md) |
| Information Architecture | [docs/product/information-architecture.md](information-architecture.md) |

---

## 2. User Roles

TaskFlow has four roles. A user's role determines what they can see and do across the entire application.

| Role | Description |
|------|-------------|
| **Owner** | Workspace creator. Full control over workspace settings, members, and all content. One per workspace. |
| **Admin** | Day-to-day management. Invites users, manages roles, configures projects and labels. |
| **Member** | Working contributor. Creates and manages tasks, projects, comments. |
| **Viewer** | Read-only participant. Can view all content they have access to but cannot create or modify anything. |

### 2.1 Permission Summary

| Action | Owner | Admin | Member | Viewer |
|--------|-------|-------|--------|--------|
| Create workspace | Yes | — | — | — |
| Update workspace settings | Yes | Yes | No | No |
| Invite users | Yes | Yes | No | No |
| Remove users | Yes | No | No | No |
| Change user roles | Yes | Yes | No | No |
| Create project | Yes | Yes | Yes | No |
| Manage project settings | Yes | Yes | No | No |
| Manage project access | Yes | Yes | No | No |
| Create task | Yes | Yes | Yes | No |
| Edit task | Yes | Yes | Yes | No |
| Change task status | Yes | Yes | Yes | No |
| Add comment | Yes | Yes | Yes | No |
| Create/edit/delete labels | Yes | Yes | No | No |
| View content (with project access) | Yes | Yes | Yes | Yes |
| Search and filter | Yes | Yes | Yes | Yes |
| Receive notifications | Yes | Yes | Yes | Yes |

Permissions operate on two layers:

- **Workspace-level:** The user's role sets their baseline capabilities.
- **Project-level:** Access controls determine which projects a user can see. A user with project access can perform any action their role allows within that project.

---

## 3. Authentication & Onboarding

### 3.1 Sign Up

- Users create an account with an email address and password.
- No social login (Google, GitHub) or magic links.
- Upon sign up, the user creates a new workspace and becomes its Owner.
- Only one sign-up path exists — there is no public registration for joining an existing workspace. Users join existing workspaces through invitations.

### 3.2 Log In

- Users log in with email and password.
- After login, users land on the dashboard.

### 3.3 Invitations

- Owners and Admins invite users by entering an email address and selecting a role.
- The invitee receives an invitation (delivery mechanism is an implementation detail).
- Invitations expire after **7 days**.
- Expired or missed invitations can be **resent** by Owners and Admins.
- Invitation revocation is not supported.
- Owners and Admins can view invitation status: **pending**, **accepted**, or **expired**.
- If the invited email belongs to an existing TaskFlow user, accepting the invitation adds them to the workspace with the assigned role — no new account is created.
- If the invited email does not have an account, accepting the invitation prompts account creation, after which the user joins the workspace.

### 3.4 First-Run Experience

**New workspace (Owner):**
- The workspace loads normally with contextual prompts guiding the Owner to:
  1. Create their first project.
  2. Invite team members.
- Prompts are integrated into the standard UI (not a separate wizard or modal tour).
- Prompts disappear once the corresponding action is completed.

**Joining a workspace (Invited user):**
- The user lands on the dashboard with a brief welcome message orienting them to the workspace.
- The welcome message disappears once the user has assignments and activity.

### 3.5 Empty States

Every area that can be empty displays a contextual message with a call to action guiding the user to the next step.

| Area | Message Example | Call to Action |
|------|----------------|----------------|
| Dashboard — My Tasks | "No tasks assigned to you yet" | Link to browse projects |
| Dashboard — Recent Activity | "No recent activity" | — |
| Dashboard — Projects | "No projects yet" | "Create your first project" button |
| Project board (no tasks) | "This project has no tasks yet" | "Create a task" button |
| Empty status column | Subtle hint text (e.g., "No tasks") | — |
| Search — no results | "No tasks match your search" | Suggest broadening the query |
| Filter — no results | "No tasks match these filters" | "Clear filters" link |
| Notifications (empty) | "You're all caught up" | — |

Empty states are **role-aware**: Viewers see informational messages without action prompts for things they cannot do (e.g., "No tasks yet" without a "Create a task" button).

---

## 4. Workspace Management

### 4.1 Workspace Settings

- **Workspace name:** Editable by Owner and Admin.
- Each user belongs to one workspace (multi-workspace support is not provided).

### 4.2 Member Management

- Owners and Admins can view the full member list including each member's role and status.
- Owners and Admins can change a user's role at any time. Changes take effect immediately.
- Owners can remove users from the workspace:
  - The removed user loses all access immediately.
  - Tasks assigned to the removed user become **unassigned**.
  - Content created by the removed user (tasks, comments) is retained.

---

## 5. Projects

### 5.1 Creating a Project

- Owners, Admins, and Members can create projects.
- Required field: **project name**.
- Optional field: **description**.
- New projects are visible to the creator. Access for other users is managed through project-level access controls.

### 5.2 Project Access

- Admins and Owners manage which users can access each project.
- Users without access to a project cannot see it in the sidebar, dashboard, search results, or activity feeds.
- Granting access gives the user visibility and interaction rights consistent with their workspace role.

### 5.3 Project Settings

- Available to Owners and Admins.
- Editable fields: project name, description.
- Project access management (add/remove users).

### 5.4 Task Workflow

All projects share a fixed set of task statuses:

| Status | Meaning |
|--------|---------|
| **Backlog** | Captured but not yet planned |
| **To Do** | Planned and ready to be picked up |
| **In Progress** | Actively being worked on |
| **In Review** | Awaiting review, approval, or quality check |
| **Done** | Completed |
| **Cancelled** | Abandoned (can be applied from any active status) |

- Tasks can move freely between Backlog, To Do, In Progress, In Review, and Done.
- Any active task can be moved to Cancelled.
- Custom workflows and user-defined statuses are not supported.

---

## 6. Tasks

### 6.1 Creating a Task

- Owners, Admins, and Members can create tasks within a project.
- New tasks default to **Backlog** status.

| Field | Required | Default | Details |
|-------|----------|---------|---------|
| **Title** | Yes | — | Short summary of the task |
| **Description** | No | Empty | Supports Markdown formatting |
| **Assignee** | No | Unassigned | One user from the workspace who has access to the project |
| **Priority** | No | None | One of: None, Low, Medium, High, Urgent |
| **Due date** | No | None | Date only (no time component) |
| **Labels** | No | None | One or more labels from the workspace label set |

### 6.2 Editing a Task

- Owners, Admins, and Members can edit all task fields.
- Viewers can view task details but cannot edit.
- All task fields are editable after creation.
- Changes are reflected in real time for all users viewing the task or project.

### 6.3 Task Status Changes

Users can change a task's status through:

- **Drag-and-drop** on the board view (desktop) — drag a task card from one status column to another.
- **Status dropdown** on the task detail panel — select a new status from the dropdown.
- **Status dropdown** on the list view — change status inline.

### 6.4 Due Dates

- Due dates represent end-of-day in the user's local time zone.
- Tasks are visually marked when:
  - **Overdue** — the due date has passed.
  - **Approaching** — the due date is near (visual indicator on cards and dashboard).
- No due-date-specific notifications are generated.

### 6.5 Priority

- Priority is a dedicated task field, separate from labels.
- Levels are fixed and cannot be configured: **None**, **Low**, **Medium**, **High**, **Urgent**.
- "None" is the default — priority is optional.
- Priority is displayed as a visual indicator on task cards.
- Tasks can be sorted and filtered by priority.

### 6.6 Task Ordering

- Within a status column on the board view, tasks are sorted by **creation date (newest first)** by default.
- Users can change the sort to: **priority**, **due date**, or **assignee**.
- Manual drag-and-drop reordering within a column is not supported.

### 6.7 Task Relationships

- All tasks are standalone. No subtasks, dependencies, or blocker relationships.
- Users can reference related tasks informally in comments.

### 6.8 File Attachments

- Not supported. Tasks and comments are text-only.
- Users can share links to external files in comments or descriptions.

### 6.9 Cancelled Tasks

- Any active task can be moved to Cancelled.
- Cancelled tasks are **hidden from active views by default** (board and list views).
- A filter option allows users to include cancelled tasks in the view.
- Cancelled tasks retain all their data and comments.

---

## 7. Labels

### 7.1 Label Management

- Labels are **workspace-wide** — a single set shared across all projects.
- Only **Owners and Admins** can create, edit, and delete labels.
- Members and Viewers select from the existing label set when viewing or filtering.

### 7.2 Label Properties

| Property | Details |
|----------|---------|
| **Name** | Text name for the label |
| **Color** | Selected from a fixed color palette |

- The fixed palette ensures consistent contrast and accessibility.
- Labels display as **colored chips** (colored background with label text) on task cards and in filters.

### 7.3 Applying Labels

- Owners, Admins, and Members can add or remove labels on tasks.
- A task can have **multiple labels**.
- Labels are applied from the task detail panel.

---

## 8. Board View

The board view is the primary project view, displaying tasks as cards organized in columns by status.

### 8.1 Layout

- One column per status: Backlog, To Do, In Progress, In Review, Done.
- Cancelled tasks are hidden by default.
- Each column displays a count of tasks in that status.

### 8.2 Task Cards

Each card displays:

| Element | Details |
|---------|---------|
| **Title** | Task title (truncated if long) |
| **Assignee** | Avatar of the assigned user (or empty if unassigned) |
| **Labels** | Colored label chips |
| **Due date** | Date value with overdue visual indicator if past due |
| **Priority** | Visual indicator (icon or badge) |
| **Comment count** | Number of comments on the task |

Task descriptions are not shown on cards — users open the task detail panel for the full description.

### 8.3 Interactions

- **Click a card** → opens the task detail panel (side panel overlay).
- **Drag a card to another column** → changes the task's status (desktop only).
- **Sort control** → changes task ordering within columns (creation date, priority, due date, assignee).
- **Filter controls** → filter visible tasks by status, assignee, priority, label, or due date.

### 8.4 Drag-and-Drop

- Primary interaction for status changes on desktop.
- Visual feedback during drag: drop target column highlights.
- Not available on mobile — users use the status dropdown instead.
- Drag-and-drop moves tasks between columns (status change) only. Reordering within a column is not supported.

---

## 9. List View

An alternative tabular view of project tasks, available to all users.

### 9.1 Layout

- Tasks displayed as rows in a table.
- Columns: title, status, assignee, priority, due date, labels.
- All columns are **sortable** (click column header to sort ascending/descending).

### 9.2 Interactions

- **Click a row** → opens the task detail panel.
- **Status dropdown** → change task status inline (no drag-and-drop).
- **Filter controls** → same filters as board view, shared state between views.

### 9.3 View Switching

- Users toggle between board and list view via the project-level navigation.
- Active filters are preserved when switching views.
- The application remembers the user's last-used view per project.

---

## 10. Task Detail Panel

The task detail panel opens as a **side panel overlaying the current view** (board or list). It does not navigate away from the project view.

### 10.1 Layout

| Section | Content |
|---------|---------|
| **Header** | Task title (editable inline), status dropdown, close button |
| **Properties** | Assignee selector, priority selector, due date picker, label selector |
| **Description** | Markdown-rendered description with edit mode |
| **Comments** | Chronological list of comments with a new comment input at the bottom |

### 10.2 Editing

- Editable fields update on save/blur — no separate "edit mode" for the entire panel.
- Markdown description toggles between rendered view and edit mode.
- All changes are saved immediately and reflected in real time for other users.

### 10.3 Deep Links

- Each task has a unique URL (`/projects/:projectId/tasks/:taskId`).
- Opening a task URL loads the project view with the task detail panel open.
- Task URLs can be shared and used in notifications to link directly to a task.

---

## 11. Comments

### 11.1 Adding Comments

- Owners, Admins, and Members can add comments on tasks.
- Viewers cannot comment.
- Comments support **Markdown formatting** (bold, italic, lists, links, code blocks, headers).
- Comments support **@mentions** — typing `@` followed by a user's name shows a suggestion list of workspace members.

### 11.2 Comment Display

- Comments are displayed in **chronological order** (oldest first).
- Each comment shows: author name, author avatar, timestamp, and rendered Markdown content.
- @mentions are visually distinct within the comment text (e.g., highlighted or styled differently).

### 11.3 Comment Editing and Deletion

- Comment editing and deletion behavior is an implementation detail to be determined during design.

---

## 12. Search and Filtering

### 12.1 Global Search

- Accessible from the global header on every page.
- Searches tasks by keyword across all projects the user has access to.
- Results appear in a **dropdown below the search input** as the user types.
- Each result shows: task title, project name, and status.
- Selecting a result navigates to the project view with the task detail panel open.
- Search queries match against task titles and descriptions.

### 12.2 Project Filters

- Available on both board and list views via filter controls in the project-level navigation.
- Filter dimensions:

| Filter | Options |
|--------|---------|
| **Status** | Any combination of the six statuses (cancelled excluded by default) |
| **Assignee** | One or more workspace members, or "Unassigned" |
| **Priority** | One or more priority levels |
| **Label** | One or more labels |
| **Due date** | Overdue, due today, due this week, no due date |

- Multiple filters can be applied simultaneously (AND logic between dimensions).
- Active filters are visually indicated and can be individually cleared or cleared all at once.
- Filter state is preserved when switching between board and list views.

---

## 13. Dashboard

The dashboard is the default landing page after login. It provides a personal overview of the user's work and workspace activity.

### 13.1 My Tasks

- Displays all tasks assigned to the current user across all accessible projects.
- Tasks are **grouped by project**.
- Each task shows: title, status, priority, and due date.
- **Overdue tasks are visually highlighted** (e.g., red text or icon on the due date).
- Clicking a task navigates to the project view with the task detail panel open.

### 13.2 Recent Activity

- A chronological feed of recent changes across all projects the user has access to.
- Activity types: status changes, new comments, new tasks, assignments, and reassignments.
- Each entry shows: what changed, who made the change, which task, which project, and when.
- Clicking an activity entry navigates to the relevant task.

### 13.3 Projects

- A list of all projects the user has access to.
- Each project shows: project name and a summary of task counts by status.
- Clicking a project navigates to its board view.

---

## 14. Activity Feed

Activity feeds provide a chronological record of changes. They exist at two levels:

### 14.1 Dashboard Activity Feed

- Workspace-wide — aggregates activity from all projects the user can access.
- Displayed in the "Recent Activity" section of the dashboard (see Section 13.2).

### 14.2 Project Activity Feed

- Scoped to a single project — shows only changes within that project.
- Accessible from the project view.
- Same entry format as the dashboard feed: what changed, who, which task, when.

### 14.3 Task-Level History

- Individual tasks do not have a dedicated activity or history log.
- Comments on the task serve as the task-level record of discussion and decisions.

---

## 15. Notifications

### 15.1 Notification Triggers

Four events generate in-app notifications:

| Event | Recipient | Condition |
|-------|-----------|-----------|
| **@mentioned in a comment** | The mentioned user | Another user mentions you in a comment |
| **Task assigned to you** | The assignee | A task is newly assigned or reassigned to you |
| **Status change on your task** | The assignee | Someone else moves a task you are assigned to |
| **Comment on your task** | The assignee | Someone else comments on a task you are assigned to |

- **Self-triggered actions do not generate notifications.** If you move your own task, comment on your own task, or assign a task to yourself, no notification is created.

### 15.2 Notification Display

- Notifications are accessed via a **bell icon in the global header**.
- A **badge on the icon** shows the count of unread notifications.
- The notifications page shows a list of all notifications in reverse chronological order.
- Each notification shows: event description, the task involved, the project, and the timestamp.
- Unread notifications are visually distinct from read notifications.
- Clicking a notification navigates to the relevant task within its project.

### 15.3 Notification Preferences

- The notification set is **fixed for all users**. There are no user-configurable notification preferences.
- No email notifications — all notifications are in-app only.

### 15.4 Real-Time Delivery

- Notifications appear in real time without requiring a page refresh.
- The unread badge count updates in real time.

---

## 16. Accessibility

TaskFlow targets **WCAG 2.1 Level AA** compliance.

### 16.1 Keyboard Navigation

- All interactive elements are reachable and operable via keyboard.
- Visible focus indicators on all focusable elements.
- Logical tab order throughout the application.
- The board view's drag-and-drop has a keyboard-accessible alternative: the status dropdown on task cards and in the task detail panel.

### 16.2 Screen Reader Support

- Semantic HTML elements used throughout.
- ARIA attributes applied where semantic HTML alone is insufficient (e.g., live regions for real-time updates, labels for icon-only buttons).
- Status changes, new notifications, and real-time updates are announced to screen readers.

### 16.3 Visual Accessibility

- Color contrast meets WCAG 2.1 AA minimum ratios (4.5:1 for normal text, 3:1 for large text).
- Information is never conveyed by color alone — text labels, icons, or patterns accompany color indicators (e.g., overdue dates have both red color and an icon).
- The fixed label color palette is designed to meet contrast requirements.

### 16.4 Alternative Views

- The **list view** serves as an accessible alternative to the board view.
- It is a general-purpose view available to all users, not hidden behind an accessibility setting.

---

## 17. Responsive Design

TaskFlow is a web application accessed through the browser on any device.

| Viewport | Behavior |
|----------|----------|
| **Desktop** (1024px+) | Full layout with persistent sidebar. Board view shows all status columns. |
| **Tablet** (768–1023px) | Sidebar collapses to icons. Board view scrolls horizontally. |
| **Mobile** (<768px) | Sidebar becomes a hamburger menu. Board view stacks columns vertically. Task detail panel opens full-screen. |

- No native mobile or desktop applications.
- An active internet connection is required.

---

## 18. Internationalization

- The application launches in **English only**.
- All user-facing text is externalized to translation files, enabling future language additions without code changes.
- Dates, times, and numbers are formatted according to the **user's browser locale** using the JavaScript `Intl` API.
- Timestamps are stored in UTC and displayed in the user's local time zone.
- CSS uses logical properties (e.g., `margin-inline-start`) to support future right-to-left language additions.

---

## 19. Real-Time Updates

All collaborative data updates in real time without requiring a manual page refresh:

| Update | Where Visible |
|--------|---------------|
| Task status change | Board view, list view, dashboard, activity feed |
| Task field edit (title, assignee, priority, due date, labels) | Board view card, list view row, task detail panel, dashboard |
| New comment | Task detail panel, activity feed |
| New task created | Board view, list view, activity feed |
| New notification | Notification badge count, notifications page |
| Task assignment/reassignment | Board view card, task detail panel, dashboard |

- If two users are editing the same task simultaneously, the last write wins. Conflict resolution beyond this is not provided.

---

## 20. Account & Data Management

### 20.1 Profile Settings

- Users can update their display name and password.
- Email address is displayed but changing it is an implementation detail.

### 20.2 Account Deletion

- Any user can request deletion of their own account.
- Deletion requires confirmation.
- Upon deletion:
  - Personal data (name, email, password) is removed.
  - Workspace content (tasks, comments) created by the user is **retained but anonymized**.
  - Tasks assigned to the deleted user become **unassigned**.

---

## 21. Out of Scope

The following are explicitly excluded from this release. These boundaries are documented to prevent scope creep, not to suggest future priority.

- File attachments on tasks or comments
- Subtasks, dependencies, or blocker relationships between tasks
- Bulk operations (multi-select and batch actions)
- Custom workflows or user-defined statuses
- Email notifications
- Notification preferences
- Calendar view
- Project planning, time tracking, or reporting
- External tool integrations (Slack, GitHub, email, calendars)
- Public API
- Native mobile or desktop applications
- Offline access
- Self-hosted deployment option
- Invitation revocation
- Task-level activity history log
