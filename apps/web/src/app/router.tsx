import { createRootRoute, createRoute, createRouter, Outlet } from '@tanstack/react-router';
import { Placeholder } from '@/components/Placeholder';

/**
 * Minimal TanStack Router v1 tree (ADR 055). Phase F1 wires the router with a
 * root route (renders an `<Outlet />`) and a single placeholder index route so
 * the provider is verifiable. The full authenticated/unauthenticated route tree
 * (shell, auth screens, project routes) is built in Phase F4 against screen
 * inventory §3.
 */
const rootRoute = createRootRoute({
  component: () => <Outlet />,
});

const indexRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/',
  component: Placeholder,
});

const routeTree = rootRoute.addChildren([indexRoute]);

export const router = createRouter({
  routeTree,
  defaultPreload: 'intent',
});

// Type-safe router registration (TanStack Router v1).
declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router;
  }
}
