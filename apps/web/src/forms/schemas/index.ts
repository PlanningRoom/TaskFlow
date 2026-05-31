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
