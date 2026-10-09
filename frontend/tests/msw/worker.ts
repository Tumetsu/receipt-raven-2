import { setupWorker } from 'msw/browser';

import { notesHandlers } from './notesApi';

/** The MSW worker every browser test runs against. Add each API's handlers here. */
export const worker = setupWorker(...notesHandlers);
