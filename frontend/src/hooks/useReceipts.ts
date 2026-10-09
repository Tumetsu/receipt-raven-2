import { useQueryClient } from '@tanstack/react-query';

import type { ListReceiptsStatus, ReceiptRequest } from '@/api/generated/model';
import {
  getGetReceiptQueryKey,
  getListReceiptsQueryKey,
  useApproveReceipt,
  useCreateReceipt,
  useDeleteReceipt,
  useListReceipts,
} from '@/api/generated/receipts/receipts';

export const PAGE_SIZE = 25;

/** One page of the receipt list. `status` undefined lists every receipt. */
export function useReceiptList(page: number, status: ListReceiptsStatus | undefined) {
  return useListReceipts({ offset: (page - 1) * PAGE_SIZE, limit: PAGE_SIZE, status });
}

/** How many receipts wait for review: the total of a one-item page. */
export function useUnapprovedCount(): number | undefined {
  return useListReceipts({ status: 'unapproved', limit: 1 }).data?.total;
}

/** The create, approve and delete mutations. Each refreshes the lists when it succeeds. */
export function useReceiptMutations() {
  const queryClient = useQueryClient();
  const refreshLists = () => queryClient.invalidateQueries({ queryKey: getListReceiptsQueryKey() });

  const create = useCreateReceipt({ mutation: { onSuccess: refreshLists } });
  const approve = useApproveReceipt({
    mutation: {
      onSuccess: async (receipt) => {
        queryClient.setQueryData(getGetReceiptQueryKey(receipt.id), receipt);
        await refreshLists();
      },
      // A rejected receipt still saved the edits; show them.
      onError: (_error, { receiptId }) =>
        queryClient.invalidateQueries({ queryKey: getGetReceiptQueryKey(receiptId) }),
    },
  });
  const remove = useDeleteReceipt({ mutation: { onSuccess: refreshLists } });

  return {
    isSaving: create.isPending || approve.isPending,
    isDeleting: remove.isPending,
    createReceipt: (data: ReceiptRequest) => create.mutateAsync({ data }),
    approveReceipt: (receiptId: number, data: ReceiptRequest) =>
      approve.mutateAsync({ receiptId, data }),
    deleteReceipt: (receiptId: number) => remove.mutateAsync({ receiptId }),
  };
}
