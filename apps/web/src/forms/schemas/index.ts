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

export type LoginValues = z.infer<typeof loginSchema>;
export type SignupValues = z.infer<typeof signupSchema>;
export type AcceptInvitationValues = z.infer<typeof acceptInvitationSchema>;
export type PasswordResetRequestValues = z.infer<typeof passwordResetRequestSchema>;
export type PasswordResetConfirmValues = z.infer<typeof passwordResetConfirmSchema>;
