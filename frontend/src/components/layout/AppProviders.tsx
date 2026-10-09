import '@/index.css';

import type { ReactNode } from 'react';

/**
 * UI-library providers, shared by `main.tsx` and the test harness. shadcn/ui
 * needs none; importing the stylesheet here is what puts Tailwind on the page.
 */
export function AppProviders({ children }: { children: ReactNode }) {
  return <>{children}</>;
}
