import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { createMemoryHistory, createRouter, RouterProvider } from '@tanstack/react-router';
import { render } from 'vitest-browser-react';

import { AppProviders } from '@/components/layout/AppProviders';
import { routerOptions } from '@/router';

/**
 * Renders the whole app at `path`: the real route tree and the same providers
 * `src/main.tsx` mounts, over a fresh QueryClient that never retries.
 */
export async function renderApp({ path }: { path: string }) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  const router = createRouter({
    ...routerOptions,
    history: createMemoryHistory({ initialEntries: [path] }),
  });

  const screen = await render(
    <QueryClientProvider client={queryClient}>
      <AppProviders>
        <RouterProvider router={router} />
      </AppProviders>
    </QueryClientProvider>
  );
  return { screen, router, queryClient };
}
