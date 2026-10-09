import { http, HttpResponse } from 'msw';

import type {
  Job,
  LedgerAccount,
  Receipt,
  ReceiptRequest,
  ReceiptSummary,
} from '@/api/generated/model';

/**
 * An in-memory Receipt Raven API, so a test can approve a receipt or retry a
 * job and see the pages change the way they would against the real backend.
 * `resetFakeApi` runs after every test.
 */
interface State {
  receipts: Receipt[];
  jobs: Job[];
  nextId: number;
  ledgerRejection: string | null;
  approvals: { receiptId: number; body: ReceiptRequest }[];
  uploads: { name: string; type: string; size: number }[];
}

const fresh = (): State => ({
  receipts: [],
  jobs: [],
  nextId: 1,
  ledgerRejection: null,
  approvals: [],
  uploads: [],
});

let state = fresh();

export function resetFakeApi() {
  state = fresh();
}

/** What the backend received, for assertions. */
export const recorded = {
  approvals: () => state.approvals,
  uploads: () => state.uploads,
  receipts: () => state.receipts,
};

/** Make the next approvals fail the way a ledger rejection does. */
export function rejectApprovals(reason: string) {
  state.ledgerRejection = reason;
}

const ACCOUNTS: LedgerAccount[] = [
  { name: 'Assets:Checking', type: 'Assets' },
  { name: 'Liabilities:CreditCard', type: 'Liabilities' },
  { name: 'Expenses:Groceries', type: 'Expenses' },
  { name: 'Expenses:Office', type: 'Expenses' },
  { name: 'Expenses:Clothes', type: 'Expenses' },
];

type ItemSeed = [name: string, account: string, price: number];

export function seedReceipt(
  overrides: Partial<Receipt> & { itemSeeds?: ItemSeed[] } = {}
): Receipt {
  const { itemSeeds, ...fields } = overrides;
  const id = state.nextId++;
  const items = (itemSeeds ?? [['Maito', 'Expenses:Groceries', 2.5]]).map(
    ([name, expense_account, price]) => ({
      id: state.nextId++,
      name,
      expense_account,
      price,
    })
  );
  const receipt: Receipt = {
    id,
    payee: 'Prisma',
    description: 'Ruokaostokset',
    date: '2026-10-09',
    total_sum: items.reduce((sum, item) => sum + item.price, 0),
    status: 'unapproved',
    source_account: 'Assets:Checking',
    parsed_by: 'anthropic/claude-haiku-4.5',
    items,
    ocr_notes: { suspicious_date: null },
    document: { url: `/api/v1/documents/receipt-${id}.jpg`, mime_type: 'image/jpeg' },
    job_id: null,
    created_at: '2026-10-09T08:00:00Z',
    ...fields,
  };
  state.receipts.unshift(receipt);
  return receipt;
}

export function seedJob(overrides: Partial<Job> = {}): Job {
  const id = state.nextId++;
  const job: Job = {
    id,
    filename: `1760000000000-camera_capture.jpg`,
    mime_type: 'image/jpeg',
    status: 'processed',
    retry_count: 0,
    analysis_error: null,
    document_url: `/api/v1/documents/job-${id}.jpg`,
    created_at: '2026-10-09T08:00:00Z',
    processed_at: '2026-10-09T08:00:05Z',
    ...overrides,
  };
  state.jobs.unshift(job);
  return job;
}

function summary(receipt: Receipt): ReceiptSummary {
  return {
    id: receipt.id,
    payee: receipt.payee,
    description: receipt.description,
    date: receipt.date,
    total_sum: receipt.total_sum,
    status: receipt.status,
    source_account: receipt.source_account,
    item_count: receipt.items.length,
    has_ocr_issues: Boolean(receipt.ocr_notes?.suspicious_date),
    created_at: receipt.created_at,
  };
}

function page<T>(items: T[], url: URL) {
  const offset = Number(url.searchParams.get('offset') ?? 0);
  const limit = Number(url.searchParams.get('limit') ?? 30);
  return { items: items.slice(offset, offset + limit), total: items.length, offset, limit };
}

function applyRequest(receipt: Receipt, body: ReceiptRequest): Receipt {
  return {
    ...receipt,
    payee: body.payee,
    description: body.description ?? null,
    source_account: body.source_account ?? null,
    date: body.date,
    total_sum: body.total_sum,
    items: body.items.map((item) => ({
      id: item.id ?? state.nextId++,
      name: item.name,
      expense_account: item.expense_account ?? '',
      price: item.price,
    })),
  };
}

function replaceReceipt(receipt: Receipt) {
  state.receipts = state.receipts.map((existing) =>
    existing.id === receipt.id ? receipt : existing
  );
}

const notFound = () =>
  HttpResponse.json(
    { error: 'not_found', message: 'The requested resource was not found.' },
    { status: 404 }
  );

// A 1x1 transparent PNG, for <img> requests of stored documents.
const PIXEL = Uint8Array.from(
  atob(
    'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII='
  ),
  (char) => char.charCodeAt(0)
);

export const fakeApiHandlers = [
  http.get('/api/v1/receipts', ({ request }) => {
    const url = new URL(request.url);
    const status = url.searchParams.get('status');
    const matching = state.receipts.filter((receipt) => !status || receipt.status === status);
    return HttpResponse.json(page(matching.map(summary), url));
  }),

  http.get('/api/v1/receipts/:id', ({ params }) => {
    const receipt = state.receipts.find((r) => r.id === Number(params.id));
    return receipt ? HttpResponse.json(receipt) : notFound();
  }),

  http.post('/api/v1/receipts', async ({ request }) => {
    const body = (await request.json()) as ReceiptRequest;
    const receipt = seedReceipt();
    const created = {
      ...applyRequest(receipt, body),
      parsed_by: 'user',
      ocr_notes: null,
      document: null,
    };
    replaceReceipt(created);
    return HttpResponse.json(created, { status: 201 });
  }),

  http.post('/api/v1/receipts/:id/approve', async ({ params, request }) => {
    const receipt = state.receipts.find((r) => r.id === Number(params.id));
    if (!receipt) return notFound();
    const body = (await request.json()) as ReceiptRequest;
    state.approvals.push({ receiptId: receipt.id, body });
    const edited = applyRequest(receipt, body);
    replaceReceipt(edited);
    if (state.ledgerRejection) {
      return HttpResponse.json(
        {
          error: 'bad_gateway',
          message: `The ledger rejected the receipt: ${state.ledgerRejection}`,
        },
        { status: 502 }
      );
    }
    const approved: Receipt = { ...edited, status: 'approved' };
    replaceReceipt(approved);
    return HttpResponse.json(approved);
  }),

  http.delete('/api/v1/receipts/:id', ({ params }) => {
    const before = state.receipts.length;
    state.receipts = state.receipts.filter((r) => r.id !== Number(params.id));
    return state.receipts.length < before ? new HttpResponse(null, { status: 204 }) : notFound();
  }),

  http.get('/api/v1/ledger/accounts', ({ request }) => {
    const types = new URL(request.url).searchParams.getAll('type');
    const items = ACCOUNTS.filter((account) => types.length === 0 || types.includes(account.type));
    return HttpResponse.json({ items });
  }),

  http.get('/api/v1/ledger/payees', () =>
    HttpResponse.json({ items: ['Alko', 'K-Market', 'Prisma'] })
  ),

  http.get('/api/v1/jobs', ({ request }) =>
    HttpResponse.json(page(state.jobs, new URL(request.url)))
  ),

  http.post('/api/v1/jobs', async ({ request }) => {
    const file = (await request.formData()).get('file');
    if (!(file instanceof File))
      return HttpResponse.json({ detail: [{ msg: 'Field required' }] }, { status: 422 });
    state.uploads.push({ name: file.name, type: file.type, size: file.size });
    const job = seedJob({ status: 'waiting', mime_type: file.type, processed_at: null });
    return HttpResponse.json(job, { status: 201 });
  }),

  http.post('/api/v1/jobs/:id/retry', ({ params }) => {
    const job = state.jobs.find((j) => j.id === Number(params.id));
    if (!job) return notFound();
    const retried: Job = { ...job, status: 'waiting', retry_count: 0, analysis_error: null };
    state.jobs = state.jobs.map((j) => (j.id === job.id ? retried : j));
    return HttpResponse.json(retried);
  }),

  http.get('/api/v1/documents/:name', () =>
    HttpResponse.arrayBuffer(PIXEL.buffer, { headers: { 'Content-Type': 'image/png' } })
  ),
];
