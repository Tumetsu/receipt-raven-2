import { setupWorker } from 'msw/browser';

import { fakeApiHandlers } from './fakeApi';

/** The MSW worker every browser test runs against. Add each API's handlers here. */
export const worker = setupWorker(...fakeApiHandlers);
