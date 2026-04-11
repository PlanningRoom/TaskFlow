# Decision 025: Error & Confirmation Patterns

**Status:** Decided

**Category:** Error & Edge Case Handling

**Question:** How should errors and confirmations be displayed? For validation errors: inline messages, toast notifications, or banner alerts? For destructive actions (delete account, remove user): modal dialog, inline confirmation, or another pattern? What tone should error messages use?

**Decision:** A layered approach using three patterns:

- **Inline validation:** For form fields (sign up, create project, create task). Error messages appear directly below the invalid field in red text with an error icon. Validation occurs on blur and on submit.
- **Toast notifications:** For async feedback and non-blocking confirmations. Toasts appear in the bottom-right corner, auto-dismiss after 5 seconds, and can be manually dismissed. Used for: "Task created", "Invitation sent", "Changes saved", and transient errors like "Failed to save — please try again."
- **Modal dialog:** For destructive confirmations. A centered modal with a clear description of the action and its consequences, a cancel button, and a red destructive action button. Used for: Remove User, Delete Account.

Error tone is neutral and helpful — describe what went wrong and what to do, never blame the user.

**Rationale:** Each pattern matches the urgency and context of the interaction. Inline validation catches errors at the source before submission. Toasts provide lightweight feedback that doesn't interrupt workflow — important for a real-time collaborative tool where actions happen frequently. Modals force a deliberate pause for irreversible actions, preventing accidental data loss. The layered approach avoids using modals for everything (which creates fatigue) or toasts for everything (which misses critical confirmations).
