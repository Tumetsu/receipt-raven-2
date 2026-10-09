import { QueryClientProvider } from '@tanstack/react-query';
import { RouterProvider } from '@tanstack/react-router';
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';

import { AppProviders } from '@/components/layout/AppProviders';
import { queryClient } from '@/lib/queryClient';
import { router } from '@/router';

const root = document.getElementById('root');
if (!root) {
  throw new Error('index.html has no #root element');
}

// The service worker receives files shared from other apps (see public/sw.js).
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker
      .register('/sw.js', { scope: '/' })
      .catch((error: unknown) => console.error('Service worker registration failed', error));
  });
}

createRoot(root).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <AppProviders>
        <RouterProvider router={router} />
      </AppProviders>
    </QueryClientProvider>
  </StrictMode>
);
