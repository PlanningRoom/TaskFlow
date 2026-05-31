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
import { CURRENT_USER_KEY } from '@/hooks/useCurrentUser';
import { PlaceholderPage } from '@/routes/PlaceholderPage';
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
  component: () => <PlaceholderPage title="Dashboard" />,
});

const notificationsRoute = createRoute({
  getParentRoute: () => shellRoute,
  path: '/notifications',
  component: () => <PlaceholderPage title="Notifications" />,
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
  component: () => <PlaceholderPage title="Board" />,
});

const projectListRoute = createRoute({
  getParentRoute: () => shellRoute,
  path: '/projects/$projectId/list',
  component: () => <PlaceholderPage title="List" />,
});

// Task detail is a panel over the board (screen inventory §9.1); placeholder page for now.
const taskDetailRoute = createRoute({
  getParentRoute: () => shellRoute,
  path: '/projects/$projectId/tasks/$taskId',
  component: () => <PlaceholderPage title="Task detail" />,
});

const settingsIndexRoute = createRoute({
  getParentRoute: () => shellRoute,
  path: '/settings',
  beforeLoad: () => {
    throw redirect({ to: '/settings/workspace' });
  },
});

const settingsTab = (tab: string, title: string) =>
  createRoute({
    getParentRoute: () => shellRoute,
    path: `/settings/${tab}`,
    component: () => <PlaceholderPage title={`Settings — ${title}`} />,
  });

const settingsWorkspaceRoute = settingsTab('workspace', 'Workspace');
const settingsMembersRoute = settingsTab('members', 'Members');
const settingsLabelsRoute = settingsTab('labels', 'Labels');
const settingsProfileRoute = settingsTab('profile', 'Profile');

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
