import {
  createRootRoute,
  createRoute,
  createRouter,
  Outlet,
  redirect,
  useRouterState,
} from '@tanstack/react-router';
import { ApiError, apiClient } from '@/api/client';
import type { CurrentUser } from '@/api/types';
import { AppShell } from '@/components/shell/AppShell';
import { AcceptInvitationScreen } from '@/features/auth/AcceptInvitationScreen';
import { LoginScreen } from '@/features/auth/LoginScreen';
import { PasswordResetConfirmScreen } from '@/features/auth/PasswordResetConfirmScreen';
import { PasswordResetRequestScreen } from '@/features/auth/PasswordResetRequestScreen';
import { SignupScreen } from '@/features/auth/SignupScreen';
import { DashboardScreen } from '@/features/dashboard/DashboardScreen';
import { NotificationsScreen } from '@/features/notifications/NotificationsScreen';
import { LabelsTab } from '@/features/settings/LabelsTab';
import { MembersTab } from '@/features/settings/MembersTab';
import { ProfileTab } from '@/features/settings/ProfileTab';
import { SettingsLayout } from '@/features/settings/SettingsLayout';
import { WorkspaceTab } from '@/features/settings/WorkspaceTab';
import { ProjectView } from '@/features/tasks/ProjectView';
import { validateTaskSearch } from '@/features/tasks/taskQueryState';
import { CURRENT_USER_KEY } from '@/hooks/useCurrentUser';
import { getLastView } from '@/lib/projectView';
import { queryClient } from './query-client';

/**
 * Application route tree (ADR 055, screen inventory §3), code-based on TanStack
 * Router v1. Two branches hang off the root:
 *
 *  - Unauthenticated screens (`/login`, `/signup`, `/invitations/$token`,
 *    `/forgot-password`, `/reset-password`) render OUTSIDE the shell.
 *  - Everything else renders INSIDE {@link AppShell} via a pathless layout
 *    route (`shellRoute`), which supplies the sidebar + header and guards
 *    access by checking the session (Phase G1).
 */
const rootRoute = createRootRoute({ component: () => <Outlet /> });

/**
 * Resolve the signed-in user, caching it under {@link CURRENT_USER_KEY} so the
 * guard and the {@link useCurrentUser} hook share one fetch. Throws an
 * {@link ApiError} (status 401 when unauthenticated).
 */
function loadCurrentUser() {
  return queryClient.ensureQueryData<CurrentUser>({
    queryKey: CURRENT_USER_KEY,
    queryFn: () => apiClient.get<CurrentUser>('/auth/me'),
    staleTime: 5 * 60_000,
  });
}

/** Guard for auth screens that make no sense while signed in (login/signup). */
async function redirectIfAuthenticated() {
  let user: CurrentUser | undefined;
  try {
    user = await loadCurrentUser();
  } catch {
    return; // 401 (or transient) → let the auth screen render.
  }
  if (user) throw redirect({ to: '/dashboard' });
}

// --- Unauthenticated branch (no shell) ------------------------------------
const loginRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/login',
  beforeLoad: redirectIfAuthenticated,
  component: LoginScreen,
});

const signupRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/signup',
  beforeLoad: redirectIfAuthenticated,
  component: SignupScreen,
});

// Token arrives in the path (`/invitations/{token}` per the invitation email).
const acceptInvitationRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/invitations/$token',
  component: function AcceptInvitationRouteComponent() {
    const { token } = acceptInvitationRoute.useParams();
    return <AcceptInvitationScreen token={token} />;
  },
});

const forgotPasswordRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/forgot-password',
  component: PasswordResetRequestScreen,
});

// Token arrives in the query string (`/reset-password?token=…` per the email).
const resetPasswordRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/reset-password',
  validateSearch: (search: Record<string, unknown>): { token?: string } => ({
    token: typeof search.token === 'string' ? search.token : undefined,
  }),
  component: function ResetPasswordRouteComponent() {
    const { token } = resetPasswordRoute.useSearch();
    return <PasswordResetConfirmScreen token={token} />;
  },
});

// --- Authenticated branch (inside the shell) ------------------------------
/** Pathless layout route: wraps all app screens in the persistent shell. */
const shellRoute = createRoute({
  getParentRoute: () => rootRoute,
  id: 'shell',
  beforeLoad: async () => {
    try {
      await loadCurrentUser();
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) {
        throw redirect({ to: '/login' });
      }
      throw error;
    }
  },
  component: ShellLayout,
});

const indexRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/',
  beforeLoad: () => {
    throw redirect({ to: '/dashboard' });
  },
});

const dashboardRoute = createRoute({
  getParentRoute: () => shellRoute,
  path: '/dashboard',
  component: DashboardScreen,
});

const notificationsRoute = createRoute({
  getParentRoute: () => shellRoute,
  path: '/notifications',
  component: NotificationsScreen,
});

// Bare /projects/$projectId redirects to the board (default view).
const projectIndexRoute = createRoute({
  getParentRoute: () => shellRoute,
  path: '/projects/$projectId',
  beforeLoad: ({ params }) => {
    throw redirect({ to: '/projects/$projectId/board', params });
  },
});

const projectBoardRoute = createRoute({
  getParentRoute: () => shellRoute,
  path: '/projects/$projectId/board',
  validateSearch: validateTaskSearch,
  component: function BoardRouteComponent() {
    const { projectId } = projectBoardRoute.useParams();
    const search = projectBoardRoute.useSearch();
    return <ProjectView projectId={projectId} view="board" search={search} />;
  },
});

const projectListRoute = createRoute({
  getParentRoute: () => shellRoute,
  path: '/projects/$projectId/list',
  validateSearch: validateTaskSearch,
  component: function ListRouteComponent() {
    const { projectId } = projectListRoute.useParams();
    const search = projectListRoute.useSearch();
    return <ProjectView projectId={projectId} view="list" search={search} />;
  },
});

// Task detail renders as a panel over the project's last-used view (DRD §9).
const taskDetailRoute = createRoute({
  getParentRoute: () => shellRoute,
  path: '/projects/$projectId/tasks/$taskId',
  validateSearch: validateTaskSearch,
  component: function TaskDetailRouteComponent() {
    const { projectId, taskId } = taskDetailRoute.useParams();
    const search = taskDetailRoute.useSearch();
    return (
      <ProjectView
        projectId={projectId}
        view={getLastView(projectId)}
        search={search}
        taskId={taskId}
      />
    );
  },
});

const settingsIndexRoute = createRoute({
  getParentRoute: () => shellRoute,
  path: '/settings',
  beforeLoad: () => {
    throw redirect({ to: '/settings/workspace' });
  },
});

type SettingsTabKey = 'workspace' | 'members' | 'labels' | 'profile';

const settingsTab = (
  tab: SettingsTabKey,
  requiresManage: boolean,
  Content: () => React.ReactNode,
) =>
  createRoute({
    getParentRoute: () => shellRoute,
    path: `/settings/${tab}`,
    component: () => (
      <SettingsLayout tab={tab} requiresManage={requiresManage}>
        <Content />
      </SettingsLayout>
    ),
  });

const settingsWorkspaceRoute = settingsTab('workspace', true, WorkspaceTab);
const settingsMembersRoute = settingsTab('members', true, MembersTab);
const settingsLabelsRoute = settingsTab('labels', true, LabelsTab);
const settingsProfileRoute = settingsTab('profile', false, ProfileTab);

const routeTree = rootRoute.addChildren([
  loginRoute,
  signupRoute,
  acceptInvitationRoute,
  forgotPasswordRoute,
  resetPasswordRoute,
  indexRoute,
  shellRoute.addChildren([
    dashboardRoute,
    notificationsRoute,
    projectIndexRoute,
    projectBoardRoute,
    projectListRoute,
    taskDetailRoute,
    settingsIndexRoute,
    settingsWorkspaceRoute,
    settingsMembersRoute,
    settingsLabelsRoute,
    settingsProfileRoute,
  ]),
]);

export const router = createRouter({ routeTree, defaultPreload: 'intent' });

declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router;
  }
}

/** Shell layout: derives a breadcrumb from the active path and renders AppShell. */
function ShellLayout() {
  return (
    <AppShell breadcrumb={useBreadcrumb()}>
      <Outlet />
    </AppShell>
  );
}

/** Map the current pathname to human breadcrumb segments (DRD §6.4). */
function useBreadcrumb(): string[] {
  const pathname = useRouterState({ select: (s) => s.location.pathname });
  const parts = pathname.split('/').filter(Boolean);
  if (parts[0] === 'dashboard') return ['Dashboard'];
  if (parts[0] === 'notifications') return ['Notifications'];
  if (parts[0] === 'settings') {
    const tab = parts[1] ?? 'workspace';
    return ['Settings', tab.charAt(0).toUpperCase() + tab.slice(1)];
  }
  if (parts[0] === 'projects') {
    const view = parts[2] === 'list' ? 'List' : 'Board';
    return ['Projects', view];
  }
  return ['TaskFlow'];
}
