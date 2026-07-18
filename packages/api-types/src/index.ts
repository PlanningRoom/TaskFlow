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
export type AcceptInvitationRequest = Schemas['AcceptInvitationRequest'];
export type AcceptInvitationResponse = Schemas['AcceptInvitationResponse'];
export type ActivityEvent = Schemas['ActivityEventDTO'];
export type ChangePasswordRequest = Schemas['ChangePasswordRequest'];
export type ChangeRoleRequest = Schemas['ChangeRoleRequest'];
export type Comment = Schemas['CommentDTO'];
export type CreateCommentRequest = Schemas['CreateCommentRequest'];
export type CreateLabelRequest = Schemas['CreateLabelRequest'];
export type CreateProjectRequest = Schemas['CreateProjectRequest'];
export type CreateTaskRequest = Schemas['CreateTaskRequest'];
export type CurrentUser = Schemas['CurrentUser'];
export type DashboardProject = Schemas['DashboardProjectDTO'];
export type DashboardProjectsResponse = Schemas['DashboardProjectsResponse'];
export type DeleteAccountRequest = Schemas['DeleteAccountRequest'];
export type GrantProjectAccessRequest = Schemas['GrantProjectAccessRequest'];
export type GrantProjectAccessResponse = Schemas['GrantProjectAccessResponse'];
export type Invitation = Schemas['InvitationDTO'];
export type InvitationPreview = Schemas['InvitationPreviewResponse'];
export type Label = Schemas['LabelDTO'];
export type ListActivityResponse = Schemas['ListActivityResponse'];
export type ListCommentsResponse = Schemas['ListCommentsResponse'];
export type ListInvitationsResponse = Schemas['ListInvitationsResponse'];
export type ListLabelsResponse = Schemas['ListLabelsResponse'];
export type ListMembersResponse = Schemas['ListMembersResponse'];
export type ListNotificationsResponse = Schemas['ListNotificationsResponse'];
export type ListProjectAccessResponse = Schemas['ListProjectAccessResponse'];
export type ListProjectsResponse = Schemas['ListProjectsResponse'];
export type ListTasksResponse = Schemas['ListTasksResponse'];
export type LoginRequest = Schemas['LoginRequest'];
export type LoginResponse = Schemas['LoginResponse'];
export type Member = Schemas['MemberDTO'];
export type MyTaskGroup = Schemas['MyTaskGroup'];
export type MyTasksResponse = Schemas['MyTasksResponse'];
export type Notification = Schemas['NotificationDTO'];
export type NotificationTaskRef = Schemas['NotificationTaskRefDTO'];
export type OkResponse = Schemas['OkResponse'];
export type PasswordResetConfirm = Schemas['PasswordResetConfirm'];
export type PasswordResetRequest = Schemas['PasswordResetRequest'];
export type Project = Schemas['ProjectDTO'];
export type ProjectMember = Schemas['ProjectMemberDTO'];
export type ProjectRef = Schemas['ProjectRefDTO'];
export type ResendInvitationResponse = Schemas['ResendInvitationResponse'];
export type SearchResponse = Schemas['SearchResponse'];
export type SearchResult = Schemas['SearchResult'];
export type SendInvitationRequest = Schemas['SendInvitationRequest'];
export type SendInvitationResponse = Schemas['SendInvitationResponse'];
export type SignupRequest = Schemas['SignupRequest'];
export type SignupResponse = Schemas['SignupResponse'];
export type TaskCounts = Schemas['TaskCounts'];
export type TaskDetail = Schemas['TaskDetail'];
export type TaskSummary = Schemas['TaskSummary'];
export type UnreadCountResponse = Schemas['UnreadCountResponse'];
export type UpdateCommentRequest = Schemas['UpdateCommentRequest'];
export type UpdateLabelRequest = Schemas['UpdateLabelRequest'];
export type UpdateProfileRequest = Schemas['UpdateProfileRequest'];
export type UpdateProjectRequest = Schemas['UpdateProjectRequest'];
export type UpdateStatusRequest = Schemas['UpdateStatusRequest'];
export type UpdateTaskRequest = Schemas['UpdateTaskRequest'];
export type UpdateWorkspaceRequest = Schemas['UpdateWorkspaceRequest'];
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
