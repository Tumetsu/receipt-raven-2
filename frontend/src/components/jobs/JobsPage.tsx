import { FileText, Image as ImageIcon, ListChecks, Loader2, RotateCw } from 'lucide-react';
import { useState } from 'react';
import { toast } from 'sonner';

import { apiErrorMessage } from '@/api/errors';
import type { Job } from '@/api/generated/model';
import { DocumentPreview } from '@/components/common/DocumentPreview';
import { EmptyState } from '@/components/common/EmptyState';
import { PageHeader } from '@/components/common/PageHeader';
import { PaginationBar } from '@/components/common/PaginationBar';
import { StatusBadge } from '@/components/common/StatusBadge';
import { Button } from '@/components/ui/button';
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from '@/components/ui/sheet';
import { Skeleton } from '@/components/ui/skeleton';
import { JOBS_PAGE_SIZE, useJobList, useJobMutations } from '@/hooks/useJobs';
import { formatDateTime } from '@/lib/format';

const MAX_ATTEMPTS = 3;

function attemptsText(job: Job): string | null {
  if (job.retry_count === 0) return null;
  return job.status === 'failed'
    ? `Failed ${job.retry_count} times`
    : `Attempt ${job.retry_count + 1} of ${MAX_ATTEMPTS}`;
}

function JobDetails({ job, onRetried }: { job: Job; onRetried: () => void }) {
  const { retryJob, isRetrying } = useJobMutations();

  const retry = async () => {
    try {
      await retryJob(job.id);
      toast.success('The receipt is queued for analysis again');
      onRetried();
    } catch (error) {
      toast.error(apiErrorMessage(error, 'The job could not be retried.'));
    }
  };

  return (
    <div className="flex flex-col gap-6 px-4 pb-6">
      <DocumentPreview url={job.document_url} mimeType={job.mime_type} />
      <dl className="grid grid-cols-[auto_1fr] gap-x-4 gap-y-2 text-sm">
        <dt className="text-muted-foreground">Status</dt>
        <dd>
          <StatusBadge status={job.status} />
        </dd>
        <dt className="text-muted-foreground">File</dt>
        <dd className="break-all">{job.filename}</dd>
        <dt className="text-muted-foreground">Uploaded</dt>
        <dd>{formatDateTime(job.created_at)}</dd>
        {job.processed_at && (
          <>
            <dt className="text-muted-foreground">Analysed</dt>
            <dd>{formatDateTime(job.processed_at)}</dd>
          </>
        )}
        {job.retry_count > 0 && (
          <>
            <dt className="text-muted-foreground">Attempts</dt>
            <dd>{job.retry_count} failed</dd>
          </>
        )}
      </dl>
      {job.analysis_error && (
        <div
          role="alert"
          className="border-destructive/40 bg-destructive/5 text-destructive rounded-lg border p-3 text-sm break-words"
        >
          {job.analysis_error}
        </div>
      )}
      {job.status === 'failed' && (
        <Button onClick={() => void retry()} disabled={isRetrying}>
          {isRetrying ? <Loader2 className="animate-spin" /> : <RotateCw />}
          Retry analysis
        </Button>
      )}
    </div>
  );
}

/** The analysis queue: every upload, its status, and a retry for failures. */
export function JobsPage({
  page,
  onPageChange,
}: {
  page: number;
  onPageChange: (page: number) => void;
}) {
  const list = useJobList(page);
  const [openJobId, setOpenJobId] = useState<number | null>(null);
  const openJob = list.data?.items.find((job) => job.id === openJobId);

  return (
    <>
      <PageHeader
        title="Analysis queue"
        description="Uploaded receipts are read one at a time. A failed analysis is retried up to three times."
      />

      {list.isPending && <Skeleton aria-label="Loading jobs" className="h-48 w-full" />}
      {list.isError && (
        <p role="alert" className="text-destructive">
          The queue could not be loaded.
        </p>
      )}
      {list.data?.items.length === 0 && (
        <EmptyState icon={ListChecks} title="The queue is empty">
          Upload a receipt and it shows up here while it is analysed.
        </EmptyState>
      )}
      {list.data && list.data.items.length > 0 && (
        <>
          <ul aria-label="Jobs" className="bg-card divide-y overflow-hidden rounded-xl border">
            {list.data.items.map((job) => {
              const Icon = job.mime_type === 'application/pdf' ? FileText : ImageIcon;
              const attempts = attemptsText(job);
              return (
                <li key={job.id}>
                  <button
                    type="button"
                    onClick={() => setOpenJobId(job.id)}
                    className="hover:bg-muted/50 flex w-full items-center gap-3 px-4 py-3 text-left"
                  >
                    <span className="bg-muted text-muted-foreground grid size-9 shrink-0 place-items-center rounded-lg">
                      <Icon className="size-4" />
                    </span>
                    <span className="min-w-0 flex-1">
                      <span className="block truncate font-medium">Upload #{job.id}</span>
                      <span className="text-muted-foreground block truncate text-xs">
                        {formatDateTime(job.created_at)}
                        {attempts && ` · ${attempts}`}
                      </span>
                    </span>
                    <StatusBadge status={job.status} />
                  </button>
                </li>
              );
            })}
          </ul>
          <PaginationBar
            page={page}
            pageSize={JOBS_PAGE_SIZE}
            total={list.data.total}
            onPageChange={onPageChange}
          />
        </>
      )}

      <Sheet open={openJob !== undefined} onOpenChange={(open) => !open && setOpenJobId(null)}>
        <SheetContent className="w-full overflow-y-auto sm:max-w-md">
          {openJob && (
            <>
              <SheetHeader className="pr-14">
                <SheetTitle>Upload #{openJob.id}</SheetTitle>
                <SheetDescription>The document and how its analysis went.</SheetDescription>
              </SheetHeader>
              <JobDetails job={openJob} onRetried={() => setOpenJobId(null)} />
            </>
          )}
        </SheetContent>
      </Sheet>
    </>
  );
}
