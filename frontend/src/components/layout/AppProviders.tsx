import '@/index.css';

import type { ReactNode } from 'react';

import { Toaster } from '@/components/ui/sonner';
import { TooltipProvider } from '@/components/ui/tooltip';

import { ThemeProvider } from './ThemeProvider';

const TOAST_TOP = 'calc(env(safe-area-inset-top) + 16px)';

/**
 * UI-library providers, shared by `main.tsx` and the test harness: the light
 * and dark theme (a `dark` class on <html>), tooltips and toast messages.
 */
export function AppProviders({ children }: { children: ReactNode }) {
  return (
    <ThemeProvider>
      <TooltipProvider delayDuration={300}>
        {children}
        <Toaster
          position="top-center"
          richColors
          closeButton
          // Below the iOS status bar and notch in the installed app.
          offset={{ top: TOAST_TOP }}
          mobileOffset={{ top: TOAST_TOP }}
        />
      </TooltipProvider>
    </ThemeProvider>
  );
}
