import { createRouter } from '@tanstack/react-router';

import { routeTree } from './routeTree.gen';

/**
 * The router options the app runs on, shared with the test harness so a test
 * drives the same router the browser does.
 */
export const routerOptions = {
  routeTree,
  scrollRestoration: true,
} as const;

export const router = createRouter(routerOptions);

declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router;
  }
}
