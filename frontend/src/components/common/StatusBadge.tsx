import { CheckCircle2, CircleDashed, Clock, XCircle } from 'lucide-react';

import type { JobStatus, ReceiptStatus } from '@/api/generated/model';
import { cn } from '@/lib/utils';

const STYLES = {
  approved: { label: 'Approved', icon: CheckCircle2, className: 'bg-success/12 text-success' },
  unapproved: { label: 'To review', icon: CircleDashed, className: 'bg-primary/10 text-primary' },
  waiting: {
    label: 'Analysing',
    icon: Clock,
    className: 'bg-warning/15 text-warning-foreground dark:text-warning',
  },
  processed: { label: 'Done', icon: CheckCircle2, className: 'bg-success/12 text-success' },
  failed: { label: 'Failed', icon: XCircle, className: 'bg-destructive/10 text-destructive' },
} as const;

export function StatusBadge({ status }: { status: ReceiptStatus | JobStatus }) {
  const { label, icon: Icon, className } = STYLES[status];
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium whitespace-nowrap',
        className
      )}
    >
      <Icon className={cn('size-3.5', status === 'waiting' && 'animate-pulse')} />
      {label}
    </span>
  );
}
