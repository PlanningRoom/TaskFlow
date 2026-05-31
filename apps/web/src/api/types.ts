/**
 * Re-export the generated API DTO aliases so app code imports domain types from
 * a single local module (`@/api/types`) rather than reaching into the
 * `@taskflow/api-types` package directly. Add aliases here as screens need them.
 */
export type {
  AcceptInvitationRequest,
  AcceptInvitationResponse,
  ActivityEvent,
  ApiErrorEnvelope,
  Comment,
  CurrentUser,
  DashboardProject,
  Invitation,
  Label,
  LoginRequest,
  LoginResponse,
  Member,
  Notification,
  OkResponse,
  PasswordResetConfirm,
  PasswordResetRequest,
  Project,
  SearchResult,
  SignupRequest,
  SignupResponse,
  TaskDetail,
  TaskSummary,
  UserSummary,
  Workspace,
} from '@taskflow/api-types';
