# TaskFlow — Information Architecture & Navigation

**Version:** 1.0
**Date:** 2026-04-05
**Status:** Draft

---

## 1. Overview

This document defines the page structure, navigation model, and URL routing for TaskFlow. It maps every screen a user can reach, how screens relate to each other, and how users move between them.

---

## 2. Site Map

```
Authentication
├── Sign Up
├── Log In
└── Accept Invitation

Workspace (authenticated)
├── Dashboard
│   ├── My Tasks
│   ├── Recent Activity
│   └── Projects List
│
├── Project
│   ├── Board View
│   │   └── Task Detail (panel)
│   ├── List View
│   │   └── Task Detail (panel)
│   └── Project Settings (Admin/Owner)
│
├── Notifications
│
└── Settings
    ├── Profile
    ├── Workspace (Owner/Admin)
    └── Members (Owner/Admin)
```

---

## 3. Page Inventory

### 3.1 Authentication Pages

These pages are accessible without authentication.

| Page | Purpose | Access |
|------|---------|--------|
| **Sign Up** | New user creates an account and workspace | Unauthenticated |
| **Log In** | Existing user authenticates | Unauthenticated |
| **Accept Invitation** | Invited user creates an account or links an existing one to the workspace | Unauthenticated (via invitation link) |

### 3.2 Dashboard

The default landing page after login.

| Section | Content | Notes |
|---------|---------|-------|
| **My Tasks** | User's assigned tasks grouped by project, overdue tasks highlighted | Links to task detail within the parent project |
| **Recent Activity** | Workspace-wide activity feed showing recent changes | Chronological, scoped to projects the user can access |
| **Projects** | List of accessible projects with task status summaries | Each project links to its board view |

### 3.3 Project Pages

| Page | Purpose | Access |
|------|---------|--------|
| **Board View** | Kanban-style board with tasks organized by status columns | All roles with project access |
| **List View** | Table of tasks with sortable columns (title, status, assignee, priority, due date, labels) | All roles with project access |
| **Project Settings** | Project name, description, and member access management | Owner, Admin |

### 3.4 Task Detail

Task detail opens as a **side panel** overlaying the current view (board or list) rather than navigating to a separate page. This keeps the user's position in the project view and supports quick task-to-task browsing.

| Section | Content |
|---------|---------|
| **Header** | Title (editable), status dropdown, close button |
| **Properties** | Assignee, priority, due date, labels |
| **Description** | Markdown-formatted description (editable) |
| **Comments** | Threaded comment list with @mention support and new comment input |

### 3.5 Notifications

| Page | Purpose | Access |
|------|---------|--------|
| **Notifications** | List of in-app notifications (mentions, assignments, status changes, comments on assigned tasks) | All authenticated users |

Notifications are accessible from a persistent icon in the global header. Selecting a notification navigates to the relevant task within its project.

### 3.6 Settings Pages

| Page | Purpose | Access |
|------|---------|--------|
| **Profile** | User's display name, email, password change, account deletion | All authenticated users |
| **Workspace** | Workspace name and general settings | Owner, Admin |
| **Members** | Member list, role management, invitation sending and status | Owner, Admin |

---

## 4. Navigation Model

### 4.1 Global Header

Present on every authenticated page. Contains:

| Element | Behavior |
|---------|----------|
| **Logo / Home** | Navigates to dashboard |
| **Search** | Global task search — results link to task detail within the parent project |
| **Notifications** | Opens notifications page; badge shows unread count |
| **User Menu** | Dropdown with links to profile settings and log out |

### 4.2 Sidebar

A persistent left sidebar provides primary navigation.

| Element | Destination |
|---------|-------------|
| **Dashboard** | Dashboard page |
| **Projects** | Expandable list of accessible projects; selecting a project opens its board view |
| **Settings** | Settings pages (visible to all users; workspace and members sections restricted by role) |

On mobile viewports, the sidebar collapses into a hamburger menu accessible from the global header.

### 4.3 Project-Level Navigation

When viewing a project, a secondary navigation bar appears below the global header.

| Element | Behavior |
|---------|----------|
| **Project Name** | Displays current project; not a link |
| **Board / List Toggle** | Switches between board view and list view; preserves any active filters |
| **Filter Controls** | Filter tasks by status, assignee, priority, label, and due date |
| **Project Settings** | Gear icon linking to project settings (Owner/Admin only) |

### 4.4 Navigation Flows

**Login → Dashboard → Project → Task:**
```
Log In → Dashboard → Select Project (sidebar) → Board View → Select Task → Task Detail Panel
```

**Notification → Task:**
```
Notification Badge → Notifications Page → Select Notification → Project Board with Task Detail Panel open
```

**Search → Task:**
```
Search (header) → Results Dropdown → Select Result → Project Board with Task Detail Panel open
```

**Cross-Project Movement:**
```
Any Page → Sidebar → Select Different Project → Board View
```

---

## 5. URL Structure

All authenticated routes are nested under the workspace context.

| Route | Page |
|-------|------|
| `/signup` | Sign up |
| `/login` | Log in |
| `/invite/:token` | Accept invitation |
| `/dashboard` | Dashboard |
| `/projects/:projectId` | Project board view (default) |
| `/projects/:projectId/board` | Project board view (explicit) |
| `/projects/:projectId/list` | Project list view |
| `/projects/:projectId/tasks/:taskId` | Project view with task detail panel open |
| `/projects/:projectId/settings` | Project settings |
| `/notifications` | Notifications |
| `/settings/profile` | Profile settings |
| `/settings/workspace` | Workspace settings |
| `/settings/members` | Member management |

### 5.1 URL Behavior

- `/projects/:projectId` redirects to `/projects/:projectId/board` (board is the default view)
- `/projects/:projectId/tasks/:taskId` opens the task detail panel over whichever view (board or list) the user last used for that project
- Direct links to a task (e.g., from a notification or shared URL) open the project board view with the task panel open
- Unauthenticated users accessing any authenticated route are redirected to `/login` with a return URL preserved

---

## 6. Responsive Behavior

| Viewport | Adaptation |
|----------|------------|
| **Desktop** (1024px+) | Full layout with persistent sidebar, board view shows all status columns |
| **Tablet** (768–1023px) | Sidebar collapses to icons; board view horizontally scrollable |
| **Mobile** (<768px) | Sidebar becomes a hamburger menu; board view switches to a single-column stack grouped by status; task detail panel opens full-screen |

---

## 7. Role-Based Visibility

Navigation elements adapt based on the user's role. Hidden elements are not shown — they are not shown as disabled.

| Element | Owner | Admin | Member | Viewer |
|---------|-------|-------|--------|--------|
| Dashboard | Yes | Yes | Yes | Yes |
| Projects (sidebar) | Yes | Yes | Yes | Yes |
| Project Settings | Yes | Yes | No | No |
| Workspace Settings | Yes | Yes | No | No |
| Members Settings | Yes | Yes | No | No |
| Search | Yes | Yes | Yes | Yes |
| Notifications | Yes | Yes | Yes | Yes |
| Create Project | Yes | Yes | Yes | No |
| Create Task (within project) | Yes | Yes | Yes | No |

---

## 8. Reference Documents

| Document | Location |
|----------|----------|
| Business Requirements Document | [docs/business/business-requirements-document.md](../business/business-requirements-document.md) |
| Dashboard Layout Decision | [docs/product/decisions/020-dashboard-layout.md](decisions/020-dashboard-layout.md) |
| Board Interaction Decision | [docs/product/decisions/015-board-interaction.md](decisions/015-board-interaction.md) |
| Alternative Views Decision | [docs/product/decisions/017-alternative-views.md](decisions/017-alternative-views.md) |
| Task Card Content Decision | [docs/product/decisions/016-task-card-content.md](decisions/016-task-card-content.md) |
| Notification Triggers Decision | [docs/product/decisions/018-notification-triggers.md](decisions/018-notification-triggers.md) |
