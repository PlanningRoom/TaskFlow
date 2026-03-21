# TaskFlow User Journeys & Use Cases

## User Journeys

### Journey 1: New Workspace Setup

**Actor:** Owner

1. Owner signs up and creates a new TaskFlow workspace
2. Owner creates their first project (e.g., "Website Redesign")
3. Owner invites team members via email, assigning roles (Admin, Member, Viewer)
4. Invited users receive invitations, create accounts, and land in the workspace
5. Owner creates initial tasks and assigns them to team members
6. Team members receive notifications and begin working

### Journey 2: Daily Task Management

**Actor:** Member

1. Member logs in and views their dashboard showing assigned tasks across projects
2. Member reviews notifications for new assignments, comments, and status changes
3. Member opens a task, reads the description and comments, then moves it to "In Progress"
4. Member adds a comment with a question, @mentioning a teammate for input
5. Teammate receives a notification, reads the comment, and replies
6. Member completes the work and moves the task to "In Review"
7. After approval, the task is moved to "Done"

### Journey 3: Project Oversight

**Actor:** Admin

1. Admin opens a project board and reviews task distribution across statuses
2. Admin notices several tasks stuck in "In Progress" and checks comments for blockers
3. Admin creates new tasks for unplanned work that has come up
4. Admin reassigns tasks to balance workload across team members
5. Admin uses filters to view only high-priority or overdue items
6. Admin checks the activity feed to understand recent progress

### Journey 4: Stakeholder Review

**Actor:** Viewer

1. Viewer receives an invitation to join a project as a read-only participant
2. Viewer opens the project board and browses tasks by status
3. Viewer uses search to find a specific task they were told about
4. Viewer reads task details and comment threads to understand progress
5. Viewer filters by label/tag to see tasks related to their area of interest

### Journey 5: Task Lifecycle

**Actor:** Member, then Admin

1. Member creates a new task, adding a title, description, labels, and an assignee
2. Task starts in "Backlog" and is later moved to "To Do" during planning
3. Assignee picks up the task and moves it to "In Progress"
4. Assignee adds comments documenting decisions and progress
5. Assignee moves the task to "In Review" and @mentions the Admin
6. Admin reviews the task, adds a comment with feedback
7. Task is moved back to "In Progress" for revisions, then back to "In Review"
8. Admin approves and moves the task to "Done"

### Journey 6: Workspace Administration

**Actor:** Owner / Admin

1. Admin invites a new team member who has joined the organization
2. Admin adjusts a user's role from Viewer to Member as their involvement grows
3. Admin manages project-level access, granting a new member access to specific projects
4. Owner removes a departed team member from the workspace
5. Owner reviews workspace settings and updates the workspace name

---

## Use Cases

### UC-01: Create Account and Workspace

- **Actor:** Owner
- **Precondition:** User has no existing account
- **Flow:** User signs up → creates workspace → becomes Owner
- **Postcondition:** Workspace exists with one Owner

### UC-02: Invite User

- **Actor:** Owner / Admin
- **Precondition:** Workspace exists
- **Flow:** Actor selects "Invite" → enters email and role → invitation is sent
- **Postcondition:** Invitee receives invitation; upon acceptance, they join with the assigned role

### UC-03: Create Project

- **Actor:** Owner / Admin / Member
- **Precondition:** User is logged in and has permission to create projects
- **Flow:** User creates project → enters name and description → project appears in workspace
- **Postcondition:** Project exists with default task statuses (Backlog → To Do → In Progress → In Review → Done)

### UC-04: Create Task

- **Actor:** Owner / Admin / Member
- **Precondition:** Project exists and user has Member-level access or above
- **Flow:** User creates task → enters title, description, labels, and assignee → task is added to "Backlog"
- **Postcondition:** Task exists in project; assignee is notified

### UC-05: Update Task Status

- **Actor:** Owner / Admin / Member
- **Precondition:** Task exists and user has permission
- **Flow:** User moves task to a new status (e.g., "To Do" → "In Progress")
- **Postcondition:** Task status is updated; change appears in activity feed; relevant users are notified in real time

### UC-06: Comment on Task

- **Actor:** Owner / Admin / Member
- **Precondition:** Task exists and user has permission
- **Flow:** User writes a comment, optionally @mentioning teammates → submits
- **Postcondition:** Comment is visible on the task; @mentioned users receive notifications

### UC-07: Search and Filter Tasks

- **Actor:** Any role
- **Precondition:** User has access to at least one project
- **Flow:** User enters a search term or applies filters (status, label, assignee) → matching tasks are displayed
- **Postcondition:** Filtered task list is shown

### UC-08: View Activity Feed

- **Actor:** Any role
- **Precondition:** User has access to at least one project
- **Flow:** User opens the activity feed → sees a chronological list of recent changes (status updates, comments, new tasks, assignments)
- **Postcondition:** User is informed of recent project activity

### UC-09: Manage User Roles

- **Actor:** Owner / Admin
- **Precondition:** Target user is a workspace member
- **Flow:** Actor selects a user → changes their role (e.g., Viewer → Member)
- **Postcondition:** User's permissions are updated immediately

### UC-10: Cancel Task

- **Actor:** Owner / Admin / Member
- **Precondition:** Task exists and is not already "Done" or "Cancelled"
- **Flow:** User moves task to "Cancelled" → optionally adds a comment explaining why
- **Postcondition:** Task is marked as Cancelled and no longer appears in active views by default

### UC-11: Remove User from Workspace

- **Actor:** Owner
- **Precondition:** Target user is a workspace member and is not the Owner
- **Flow:** Owner selects user → confirms removal → user loses access
- **Postcondition:** User can no longer access the workspace; their tasks remain but are unassigned

### UC-12: View Dashboard

- **Actor:** Any role
- **Precondition:** User is logged in
- **Flow:** User opens dashboard → sees summary of their assigned tasks, recent activity, and project statuses
- **Postcondition:** User has an at-a-glance overview of their work

### UC-13: Delete Account and Data

- **Actor:** Any role (for their own account)
- **Precondition:** User has an account
- **Flow:** User requests account deletion → confirms → account and personal data are removed
- **Postcondition:** User's personal data is deleted per GDPR-aware practices; workspace data (tasks, comments) is retained but anonymized
