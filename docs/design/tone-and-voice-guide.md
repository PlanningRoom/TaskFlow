# TaskFlow — Tone & Voice Guide

**Version:** 1.0
**Date:** 2026-04-11
**Status:** Draft

---

## 1. Purpose

This guide defines how TaskFlow communicates with users through its interface. It covers the personality behind every label, message, empty state, error, and confirmation — ensuring the application speaks with a consistent voice across all touchpoints.

---

## 2. Brand Voice

TaskFlow's voice is **clear, calm, and helpful**. It reflects the minimal & soft modern personality established in the design decisions: clean without being cold, approachable without being casual.

### 2.1 Voice Attributes

| Attribute | What it means | What it doesn't mean |
|-----------|--------------|---------------------|
| **Clear** | Say exactly what happened or what to do next. Use plain language. Avoid jargon, abbreviations, and ambiguity. | Not blunt or robotic. Clarity doesn't mean stripping out all warmth. |
| **Calm** | Don't alarm the user unnecessarily. Even errors should feel manageable. The interface never shouts, rushes, or creates urgency where there is none. | Not passive or vague. Calm doesn't mean burying important information in soft language. |
| **Helpful** | Guide the user toward the next step. If something went wrong, say what they can do about it. If something is empty, point them in the right direction. | Not condescending or hand-holding. Assume the user is competent. Don't over-explain obvious things. |
| **Concise** | Use the fewest words that fully communicate the message. Every word should earn its place. | Not terse or cryptic. Brevity should never sacrifice clarity. |

### 2.2 Voice Spectrum

TaskFlow's voice sits in a specific range:

```
Formal ←——————●———————→ Casual
               ↑
          Slightly informal.
          Professional but not corporate.
```

- Use contractions naturally ("you're", "can't", "we'll") — they soften the tone without losing clarity.
- Avoid slang, humor that could fall flat across cultures, and overly playful language.
- Address the user as "you" — never "the user" or "one."
- Refer to TaskFlow as "TaskFlow" in formal contexts (privacy policy, onboarding) and avoid self-reference elsewhere (say "Your tasks" not "TaskFlow's task list").

---

## 3. Writing Principles

### 3.1 Lead with What Matters

Put the most important information first. Users scan — they don't read every word.

| Instead of | Write |
|-----------|-------|
| "The action you attempted could not be completed because the invitation has expired." | "This invitation has expired." |
| "In order to create a new task, you'll need to first select a project." | "Select a project to create a task." |

### 3.2 Use Active Voice

Active voice is clearer and more direct. Passive voice is acceptable when the actor is irrelevant or unknown.

| Instead of | Write |
|-----------|-------|
| "The task was moved to Done by Sarah." | "Sarah moved this task to Done." |
| "Your password has been updated." | "Password updated." (actor is obvious) |

### 3.3 Be Specific, Not Generic

Tell users exactly what happened or what to do. Avoid generic messages that apply to everything and help with nothing.

| Instead of | Write |
|-----------|-------|
| "Something went wrong." | "Couldn't save your changes. Please try again." |
| "Invalid input." | "Project name is required." |
| "Action completed successfully." | "Task created." |

### 3.4 Respect the User's Time

Don't state the obvious. Don't repeat what the interface already shows. Don't add filler words.

| Instead of | Write |
|-----------|-------|
| "You have successfully logged in to your account." | (No message needed — just show the dashboard.) |
| "Click the button below to create a new project." | "Create your first project." (next to the button) |

---

## 4. Tone by Context

The voice stays consistent, but the tone shifts based on context. Think of tone as volume and warmth — the voice is always the same person, but they adjust how they speak based on the situation.

### 4.1 Onboarding & First-Run

**Tone:** Warm and encouraging. This is the user's first impression.

- Welcome without being effusive. One line is enough.
- Guide without lecturing. Point to the next step, don't explain the whole product.
- Disappear gracefully. Prompts should feel natural to dismiss, not persistent.

| Example | Context |
|---------|---------|
| "Welcome to TaskFlow. Start by creating your first project." | Owner first-run prompt |
| "Welcome to [Workspace Name]." | Invited user's first dashboard visit |

### 4.2 Empty States

**Tone:** Calm and directional. Acknowledge the emptiness without making it feel like a problem.

- State what's empty in plain terms.
- If the user can take action, offer a clear next step.
- If the user can't take action (Viewers), keep it informational — no action prompts for things they can't do.

| Example | Context |
|---------|---------|
| "No tasks assigned to you yet." | Dashboard — My Tasks (empty) |
| "This project has no tasks yet." | Board view (empty, Viewer) |
| "No tasks match your search. Try broadening your query." | Search — no results |
| "You're all caught up." | Notifications (empty) |

### 4.3 Success Confirmations

**Tone:** Brief and confident. Confirm the action and get out of the way.

- Use toast notifications for non-blocking confirmations.
- State what happened in 2–4 words. No exclamation marks, no celebratory language.

| Example | Context |
|---------|---------|
| "Task created." | After creating a task |
| "Invitation sent." | After inviting a user |
| "Changes saved." | After editing task details |
| "Comment added." | After posting a comment |

### 4.4 Errors & Validation

**Tone:** Calm and constructive. Explain what went wrong and what to do about it. Never blame the user.

- Be specific about the problem.
- If there's a fix, say what it is.
- If retrying might help, suggest it.
- Don't use technical language (no error codes, stack traces, or HTTP status numbers in user-facing messages).

| Example | Context |
|---------|---------|
| "Project name is required." | Inline validation — empty name field |
| "That email address is already in this workspace." | Invitation form — duplicate invite |
| "Couldn't save your changes. Please try again." | Transient save failure |
| "This invitation has expired. Ask an admin to resend it." | Expired invitation link |

### 4.5 Destructive Confirmations

**Tone:** Direct and serious. Make the consequences clear without being dramatic.

- State exactly what will happen in plain terms.
- Name the irreversible consequence.
- Use a clear action label on the confirm button — not "OK" or "Yes."

| Example | Context |
|---------|---------|
| "Remove Sarah from this workspace? She'll lose access immediately, and her assigned tasks will become unassigned." / Button: **Remove Member** | Remove user confirmation |
| "Delete your account? Your personal data will be removed. Tasks and comments you created will be kept but anonymized." / Button: **Delete Account** | Account deletion confirmation |

### 4.6 Notifications

**Tone:** Neutral and informative. Just the facts — who did what, to which task, when.

- Use the sentence-style format from Decision 021.
- Keep entries scannable. No editorial commentary.

| Example | Context |
|---------|---------|
| "Sarah moved Design homepage to In Review." | Status change notification |
| "Alex commented on Fix login bug." | Comment notification |
| "Jordan assigned Update API docs to you." | Assignment notification |

### 4.7 Activity Feed

**Tone:** Same as notifications — neutral, factual, scannable. The activity feed is a record, not a conversation.

---

## 5. UI Label Conventions

### 5.1 Buttons

- Use verb phrases for action buttons: "Create Project", "Send Invitation", "Save Changes."
- Use specific labels over generic ones: "Remove Member" over "Delete", "Create Task" over "Submit."
- Cancel buttons say "Cancel." Not "Dismiss", "Never mind", or "Go back."

### 5.2 Form Labels

- Use sentence case: "Project name", not "Project Name" or "PROJECT NAME."
- Keep labels short — 1–3 words. Use helper text below the input for additional guidance.
- Placeholder text should be an example, not an instruction: "e.g., Marketing Campaign" not "Enter project name here."

### 5.3 Navigation & Headings

- Use sentence case for headings: "My tasks", "Recent activity."
- Use title case for proper nouns and product features that function as section names in navigation: "Dashboard", "Projects", "Settings."
- Breadcrumbs use the actual names: "Projects / Marketing / Board."

### 5.4 Timestamps

- Use relative time for recent activity: "2m ago", "1h ago", "3d ago."
- Switch to absolute dates after 7 days: "Apr 4, 2026."
- Dates on tasks use the short format: "Apr 11" (current year) or "Apr 11, 2025" (different year).

---

## 6. Internationalization Considerations

Although TaskFlow launches in English only, the tone and voice guide is written with future translation in mind:

- Avoid idioms, puns, and cultural references that don't translate ("knock it out of the park", "back to square one").
- Keep sentences simple and structurally straightforward — complex grammar is harder to translate accurately.
- Don't embed UI text in code. All strings referenced in this guide should be externalized to translation files.
- Don't concatenate strings to build sentences ("You have " + count + " tasks") — different languages have different word orders. Use parameterized templates instead.

---

## 7. Reference

| Document | Location |
|----------|----------|
| Design Decisions | [docs/design/decisions/INDEX.md](decisions/INDEX.md) |
| Product Requirements Document | [docs/product/product-requirements-document.md](../product/product-requirements-document.md) |
| Business Requirements Document | [docs/business/business-requirements-document.md](../business/business-requirements-document.md) |
