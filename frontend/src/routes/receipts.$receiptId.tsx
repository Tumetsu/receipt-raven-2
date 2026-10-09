import { createFileRoute } from '@tanstack/react-router';

import { ReceiptPage } from '@/components/receipts/ReceiptPage';

export const Route = createFileRoute('/receipts/$receiptId')({
  component: function ReceiptRoute() {
    const { receiptId } = Route.useParams();
    // Keyed: moving to another receipt starts its form afresh.
    return <ReceiptPage key={receiptId} receiptId={Number(receiptId)} />;
  },
});
