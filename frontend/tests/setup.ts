import { afterAll, afterEach, beforeAll } from 'vitest';
import { cleanup } from 'vitest-browser-react';

import { API_BASE_URL } from '@/api/base-url';

import { resetNotesApi } from './msw/notesApi';
import { worker } from './msw/worker';

const unhandledRequests: string[] = [];

beforeAll(async () => {
  // Components build URLs from a constant compiled out of `import.meta.env`,
  // so a leaked env var can only be caught here, not corrected.
  if (API_BASE_URL !== '') {
    throw new Error(
      `API_BASE_URL is ${JSON.stringify(API_BASE_URL)}, not ''. An environment ` +
        'variable reached the test build; see envPrefix in vitest.config.ts.'
    );
  }

  await worker.start({
    quiet: true,
    // MSW's own 'error' strategy only fails the request, which a component can
    // swallow. Recording them and failing in afterEach means a test can never
    // pass while talking to an endpoint nobody mocked.
    onUnhandledRequest(request, print) {
      const url = new URL(request.url);
      if (!url.pathname.startsWith('/api/')) return;
      unhandledRequests.push(`${request.method} ${url.pathname}`);
      print.error();
    },
  });
});

afterEach(async () => {
  await cleanup();
  worker.resetHandlers();
  resetNotesApi();

  const unhandled = unhandledRequests.splice(0);
  if (unhandled.length > 0) {
    throw new Error(
      `Unmocked request(s): ${unhandled.join(', ')}. Add a handler under tests/msw/.`
    );
  }
});

afterAll(() => {
  worker.stop();
});
