import { z } from 'zod';

/**
 * Shared form-schema primitives (ADR 056). Feature forms (auth in Phase G1,
 * settings in G8, etc.) compose these with React Hook Form via
 * `@hookform/resolvers/zod` so validation rules stay consistent and mirror the
 * backend's Pydantic constraints (e.g. password min length 8 per Phase B4).
 */

export const emailSchema = z
  .string()
  .trim()
  .min(1, 'Email is required')
  .email('Enter a valid email');

export const passwordSchema = z.string().min(8, 'Password must be at least 8 characters');

export const displayNameSchema = z
  .string()
  .trim()
  .min(1, 'Display name is required')
  .max(120, 'Display name is too long');

export const workspaceNameSchema = z
  .string()
  .trim()
  .min(1, 'Workspace name is required')
  .max(120, 'Workspace name is too long');

// --- Auth form schemas (Phase G1) -----------------------------------------
// Each mirrors the backend Pydantic constraints in apps/api/taskflow/schemas/auth.py.

/**
 * Login does NOT pre-validate password length: the backend deliberately leaves
 * `LoginRequest.password` unconstrained so a wrong password returns 401, not
 * 422. We only require non-empty so the field can't be submitted blank.
 */
export const loginSchema = z.object({
  email: emailSchema,
  password: z.string().min(1, 'Password is required'),
});

export const signupSchema = z.object({
  displayName: displayNameSchema,
  email: emailSchema,
  password: passwordSchema,
  workspaceName: workspaceNameSchema,
});

export const acceptInvitationSchema = z.object({
  displayName: displayNameSchema,
  password: passwordSchema,
});

export const passwordResetRequestSchema = z.object({
  email: emailSchema,
});

export const passwordResetConfirmSchema = z
  .object({
    newPassword: passwordSchema,
    confirmPassword: z.string().min(1, 'Please confirm your password'),
  })
  .refine((values) => values.newPassword === values.confirmPassword, {
    message: "Passwords don't match",
    path: ['confirmPassword'],
  });

// --- Project form schemas (Phase G2) --------------------------------------
// Mirrors CreateProjectRequest in apps/api/taskflow/schemas/projects.py.

export const createProjectSchema = z.object({
  name: z.string().trim().min(1, 'Project name is required').max(120, 'Project name is too long'),
  description: z.string().trim().max(2000, 'Description is too long').optional(),
});

// --- Task / settings form schemas (Phases G3–G8) --------------------------

export const createTaskSchema = z.object({
  title: z.string().trim().min(1, 'Title is required').max(400, 'Title is too long'),
  description: z.string().trim().max(20000, 'Description is too long').optional(),
});

export const inviteMemberSchema = z.object({
  email: emailSchema,
  role: z.enum(['admin', 'member', 'viewer']),
});

export const labelSchema = z.object({
  name: z.string().trim().min(1, 'Label name is required').max(64, 'Label name is too long'),
  color: z.enum(['blue', 'green', 'red', 'purple', 'amber', 'pink', 'cyan', 'orange']),
});

export const changePasswordSchema = z.object({
  currentPassword: z.string().min(1, 'Enter your current password'),
  newPassword: passwordSchema,
});

export const deleteAccountSchema = z.object({
  password: z.string().min(1, 'Enter your password to confirm'),
});

export type LoginValues = z.infer<typeof loginSchema>;
export type SignupValues = z.infer<typeof signupSchema>;
export type AcceptInvitationValues = z.infer<typeof acceptInvitationSchema>;
export type PasswordResetRequestValues = z.infer<typeof passwordResetRequestSchema>;
export type PasswordResetConfirmValues = z.infer<typeof passwordResetConfirmSchema>;
export type CreateProjectValues = z.infer<typeof createProjectSchema>;
export type CreateTaskValues = z.infer<typeof createTaskSchema>;
export type InviteMemberValues = z.infer<typeof inviteMemberSchema>;
export type LabelValues = z.infer<typeof labelSchema>;
export type ChangePasswordValues = z.infer<typeof changePasswordSchema>;
export type DeleteAccountValues = z.infer<typeof deleteAccountSchema>;
