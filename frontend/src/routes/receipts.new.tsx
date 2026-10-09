import { createFileRoute } from '@tanstack/react-router';

import { NewReceiptPage } from '@/components/receipts/ReceiptPage';

export const Route = createFileRoute('/receipts/new')({
  component: NewReceiptPage,
});
