import { Outlet } from '@tanstack/react-router';

import { APP_NAME } from '@/lib/appInfo';

/** Page chrome around every route. */
export function AppLayout() {
  return (
    <div className="min-h-screen">
      <header className="border-b">
        <div className="mx-auto flex h-14 max-w-3xl items-center px-4">
          <span className="text-lg font-semibold">{APP_NAME}</span>
        </div>
      </header>
      <main className="mx-auto max-w-3xl px-4 py-8">
        <Outlet />
      </main>
    </div>
  );
}
