import { createFileRoute } from '@tanstack/react-router';

import { ReceiptsPage, type ReceiptFilter } from '@/components/receipts/ReceiptsPage';
import { optionalOneOf, optionalPage } from '@/lib/search';

const FILTERS: readonly ReceiptFilter[] = ['unapproved', 'approved', 'all'];

export const Route = createFileRoute('/')({
  validateSearch: (search: Record<string, unknown>): { filter?: ReceiptFilter; page?: number } => ({
    filter: optionalOneOf(search.filter, FILTERS),
    page: optionalPage(search.page),
  }),
  component: function ReceiptsRoute() {
    const { filter = 'unapproved', page = 1 } = Route.useSearch();
    return <ReceiptsPage filter={filter} page={page} />;
  },
});
