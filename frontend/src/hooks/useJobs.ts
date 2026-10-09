import { useQueryClient } from '@tanstack/react-query';

import {
  getListJobsQueryKey,
  useListJobs,
  useRetryJob,
  useUploadReceipt,
} from '@/api/generated/jobs/jobs';
import type { PaginatedResponseJob } from '@/api/generated/model';
import { getListReceiptsQueryKey } from '@/api/generated/receipts/receipts';

export const JOBS_PAGE_SIZE = 25;
const POLL_INTERVAL_MS = 2000;

function hasWaitingJobs(data: PaginatedResponseJob | undefined): boolean {
  return data?.items.some((job) => job.status === 'waiting') ?? false;
}

/**
 * One page of the analysis queue. While a job is waiting the list polls, and
 * each poll also refreshes the receipts, which finished jobs add to.
 */
export function useJobList(page: number) {
  const queryClient = useQueryClient();
  return useListJobs(
    { offset: (page - 1) * JOBS_PAGE_SIZE, limit: JOBS_PAGE_SIZE },
    {
      query: {
        refetchInterval: (query) => {
          if (!hasWaitingJobs(query.state.data)) return false;
          void queryClient.invalidateQueries({ queryKey: getListReceiptsQueryKey() });
          return POLL_INTERVAL_MS;
        },
      },
    }
  );
}

export function useJobMutations() {
  const queryClient = useQueryClient();
  const refreshJobs = () => queryClient.invalidateQueries({ queryKey: getListJobsQueryKey() });

  const retry = useRetryJob({ mutation: { onSuccess: refreshJobs } });
  const upload = useUploadReceipt({ mutation: { onSuccess: refreshJobs } });

  return {
    isRetrying: retry.isPending,
    isUploading: upload.isPending,
    retryJob: (jobId: number) => retry.mutateAsync({ jobId }),
    uploadReceipt: (file: Blob) => upload.mutateAsync({ data: { file } }),
  };
}
