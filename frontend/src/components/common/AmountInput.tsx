import type { ComponentProps } from 'react';

import { Input } from '@/components/ui/input';
import { amountToInput, parseAmount } from '@/lib/format';
import { cn } from '@/lib/utils';

/**
 * An amount as text. Accepts a comma or a dot while typing and rewrites the
 * value with the currency's decimals ("12,50", or "1500" for yen) when left.
 */
export function AmountInput({
  value,
  onChange,
  onBlur,
  className,
  currency,
  ...props
}: Omit<ComponentProps<typeof Input>, 'value' | 'onChange' | 'onBlur'> & {
  currency: string;
  value: string;
  onChange: (value: string) => void;
  onBlur?: () => void;
}) {
  return (
    <Input
      inputMode="decimal"
      placeholder="0,00"
      className={cn('tabular-nums', className)}
      value={value}
      onChange={(event) => onChange(event.target.value)}
      onBlur={() => {
        const amount = parseAmount(value);
        if (amount !== null) onChange(amountToInput(amount, currency));
        onBlur?.();
      }}
      {...props}
    />
  );
}
