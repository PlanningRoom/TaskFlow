/**
 * @taskflow/api-types — the frontend's typed view of the backend contract.
 *
 * `schema.d.ts` is generated from the backend's OpenAPI document by
 * `pnpm gen:api` (see scripts/gen.mjs) and must not be edited by hand. This
 * module re-exports the raw `paths`/`components`/`operations` interfaces plus
 * hand-curated convenience aliases for the schemas screens reference most. Add
 * an alias here when a new DTO becomes widely used.
 */
import type { components, operations, paths } from './generated/schema';

export type { components, operations, paths };

/** Every named schema, keyed by its OpenAPI component name. */
export type Schemas = components['schemas'];

// --- Convenience aliases (alphabetical) -----------------------------------
export type ActivityEvent = Schemas['ActivityEventDTO'];
export type Comment = Schemas['CommentDTO'];
export type CurrentUser = Schemas['CurrentUser'];
export type DashboardProject = Schemas['DashboardProjectDTO'];
export type Invitation = Schemas['InvitationDTO'];
export type Label = Schemas['LabelDTO'];
export type Member = Schemas['MemberDTO'];
export type Notification = Schemas['NotificationDTO'];
export type Project = Schemas['ProjectDTO'];
export type SearchResult = Schemas['SearchResult'];
export type TaskDetail = Schemas['TaskDetail'];
export type TaskSummary = Schemas['TaskSummary'];
export type UserSummary = Schemas['UserSummary'];
export type Workspace = Schemas['WorkspaceDTO'];

/**
 * The ADR 043 error envelope returned on every non-2xx response.
 * Mirrors `taskflow/errors.py::_envelope`. Not an OpenAPI component (it's
 * produced by exception handlers), so it's declared by hand here.
 */
export interface ApiErrorEnvelope {
  error: {
    code: string;
    message: string;
    fields?: Record<string, string[]>;
  };
}
