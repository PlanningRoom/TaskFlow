import {
  createRootRoute,
  createRoute,
  createRouter,
  Outlet,
  redirect,
  useRouterState,
} from '@tanstack/react-router';
import { AppShell } from '@/components/shell/AppShell';
import { AuthPlaceholder } from '@/routes/AuthPlaceholder';
import { PlaceholderPage } from '@/routes/PlaceholderPage';

/**
 * Application route tree (ADR 055, screen inventory §3), code-based on TanStack
 * Router v1. Two branches hang off the root:
 *
 *  - Unauthenticated screens (`/login`, `/signup`, `/invitations/$token`) render
 *    OUTSIDE the shell via {@link AuthPlaceholder}.
 *  - Everything else renders INSIDE {@link AppShell} via a pathless layout
 *    route (`shellRoute`), which supplies the sidebar + header.
 *
 * Every leaf renders a placeholder for now; Part G fills in the real screens.
 * Auth redirect guards are added in G1 — F4 only structures the tree.
 */
const rootRoute = createRootRoute({ component: () => <Outlet /> });

// --- Unauthenticated branch (no shell) ------------------------------------
const loginRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/login',
  component: () => <AuthPlaceholder title="Log in" />,
});

const signupRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/signup',
  component: () => <AuthPlaceholder title="Create your workspace" />,
});

const acceptInvitationRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/invitations/$token',
  component: () => <AuthPlaceholder title="Accept invitation" />,
});

// --- Authenticated branch (inside the shell) ------------------------------
/** Pathless layout route: wraps all app screens in the persistent shell. */
const shellRoute = createRoute({
  getParentRoute: () => rootRoute,
  id: 'shell',
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
