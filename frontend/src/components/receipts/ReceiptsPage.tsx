import { Link, useNavigate } from '@tanstack/react-router';
import { AlertTriangle, ChevronRight, Plus, ReceiptText } from 'lucide-react';

import type { ReceiptSummary } from '@/api/generated/model';
import { EmptyState } from '@/components/common/EmptyState';
import { PageHeader } from '@/components/common/PageHeader';
import { PaginationBar } from '@/components/common/PaginationBar';
import { StatusBadge } from '@/components/common/StatusBadge';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { PAGE_SIZE, useReceiptList, useUnapprovedCount } from '@/hooks/useReceipts';
import { formatCurrency, formatDate } from '@/lib/format';

export type ReceiptFilter = 'unapproved' | 'approved' | 'all';

const EMPTY_TEXT: Record<ReceiptFilter, string> = {
  unapproved: 'Nothing to review. Upload a receipt, and it appears here once analysed.',
  approved: 'No approved receipts yet.',
  all: 'No receipts yet. Upload a photo of one, or enter it by hand.',
};

function OcrWarning() {
  return (
    <AlertTriangle
      role="img"
      aria-label="Check the date"
      className="text-warning-foreground dark:text-warning size-4 shrink-0"
    >
      <title>The analysis doubts the date: check it</title>
    </AlertTriangle>
  );
}

function ReceiptTable({ receipts }: { receipts: ReceiptSummary[] }) {
  const navigate = useNavigate();
  const open = (id: number) =>
    void navigate({ to: '/receipts/$receiptId', params: { receiptId: String(id) } });

  return (
    <div className="bg-card hidden overflow-hidden rounded-xl border md:block">
      <Table aria-label="Receipts">
        <TableHeader>
          <TableRow className="bg-muted/40 hover:bg-muted/40">
            <TableHead className="pl-4">Date</TableHead>
            <TableHead>Payee</TableHead>
            <TableHead>Description</TableHead>
            <TableHead className="text-right">Items</TableHead>
            <TableHead className="text-right">Amount</TableHead>
            <TableHead>Status</TableHead>
            <TableHead className="w-8" />
          </TableRow>
        </TableHeader>
        <TableBody>
          {receipts.map((receipt) => (
            <TableRow key={receipt.id} className="cursor-pointer" onClick={() => open(receipt.id)}>
              <TableCell className="pl-4 tabular-nums">
                <span className="flex items-center gap-1.5">
                  {formatDate(receipt.date)}
                  {receipt.has_ocr_issues && receipt.status === 'unapproved' && <OcrWarning />}
                </span>
              </TableCell>
              <TableCell className="font-medium">
                <Link
                  to="/receipts/$receiptId"
                  params={{ receiptId: String(receipt.id) }}
                  onClick={(event) => event.stopPropagation()}
                  className="hover:underline"
                >
                  {receipt.payee}
                </Link>
              </TableCell>
              <TableCell className="text-muted-foreground max-w-64 truncate">
                {receipt.description}
              </TableCell>
              <TableCell className="text-right tabular-nums">{receipt.item_count}</TableCell>
              <TableCell className="text-right font-medium tabular-nums">
                {formatCurrency(receipt.total_sum)}
              </TableCell>
              <TableCell>
                <StatusBadge status={receipt.status} />
              </TableCell>
              <TableCell>
                <ChevronRight className="text-muted-foreground size-4" />
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}

function ReceiptCards({ receipts }: { receipts: ReceiptSummary[] }) {
  return (
    <ul aria-label="Receipts" className="flex flex-col gap-2 md:hidden">
      {receipts.map((receipt) => (
        <li key={receipt.id}>
          <Link
            to="/receipts/$receiptId"
            params={{ receiptId: String(receipt.id) }}
            className="bg-card active:bg-accent flex items-center gap-3 rounded-xl border p-4"
          >
            <div className="min-w-0 flex-1">
              <div className="text-muted-foreground flex items-center gap-1.5 text-xs">
                {formatDate(receipt.date)}
                {receipt.has_ocr_issues && receipt.status === 'unapproved' && <OcrWarning />}
              </div>
              <p className="truncate font-medium">{receipt.payee}</p>
              {receipt.description && (
                <p className="text-muted-foreground truncate text-sm">{receipt.description}</p>
              )}
            </div>
            <div className="flex flex-col items-end gap-1">
              <span className="font-semibold tabular-nums">
                {formatCurrency(receipt.total_sum)}
              </span>
              <StatusBadge status={receipt.status} />
            </div>
          </Link>
        </li>
      ))}
    </ul>
  );
}

export function ReceiptsPage({ filter, page }: { filter: ReceiptFilter; page: number }) {
  const navigate = useNavigate();
  const list = useReceiptList(page, filter === 'all' ? undefined : filter);
  const unapproved = useUnapprovedCount();

  const go = (next: { filter?: ReceiptFilter; page?: number }) =>
    void navigate({
      to: '/',
      search: { filter: next.filter ?? filter, page: next.page ?? 1 },
    });

  return (
    <>
      <PageHeader
        title="Receipts"
        description="Check what the analysis read, then approve to book it to the ledger."
        actions={
          <Button asChild>
            <Link to="/receipts/new">
              <Plus /> New receipt
            </Link>
          </Button>
        }
      />

      <Tabs value={filter} onValueChange={(value) => go({ filter: value as ReceiptFilter })}>
        <TabsList className="mb-4">
          <TabsTrigger value="unapproved">
            To review{unapproved ? ` (${unapproved})` : ''}
          </TabsTrigger>
          <TabsTrigger value="approved">Approved</TabsTrigger>
          <TabsTrigger value="all">All</TabsTrigger>
        </TabsList>
      </Tabs>

      {list.isPending && (
        <div aria-label="Loading receipts" className="flex flex-col gap-2">
          {[0, 1, 2].map((key) => (
            <Skeleton key={key} className="h-16 w-full" />
          ))}
        </div>
      )}
      {list.isError && (
        <p role="alert" className="text-destructive">
          The receipts could not be loaded.
        </p>
      )}
      {list.data && list.data.items.length === 0 && (
        <EmptyState icon={ReceiptText} title="No receipts here">
          {EMPTY_TEXT[filter]}
        </EmptyState>
      )}
      {list.data && list.data.items.length > 0 && (
        <>
          <ReceiptTable receipts={list.data.items} />
          <ReceiptCards receipts={list.data.items} />
          <PaginationBar
            page={page}
            pageSize={PAGE_SIZE}
            total={list.data.total}
            onPageChange={(next) => go({ page: next })}
          />
        </>
      )}
    </>
  );
}
