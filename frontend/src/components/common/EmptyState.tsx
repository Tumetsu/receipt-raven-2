import type { LucideIcon } from 'lucide-react';
import type { ReactNode } from 'react';

export function EmptyState({
  icon: Icon,
  title,
  children,
}: {
  icon: LucideIcon;
  title: string;
  children?: ReactNode;
}) {
  return (
    <div className="flex flex-col items-center rounded-xl border border-dashed px-6 py-14 text-center">
      <span className="bg-muted text-muted-foreground mb-4 grid size-12 place-items-center rounded-full">
        <Icon className="size-6" />
      </span>
      <p className="font-medium">{title}</p>
      {children && <div className="text-muted-foreground mt-1 max-w-sm text-sm">{children}</div>}
    </div>
  );
}
