import { z } from 'zod';

import type { Receipt, ReceiptRequest } from '@/api/generated/model';
import { amountToInput, parseAmount, todayIsoDate } from '@/lib/format';

/** Amounts stay text while edited, so "12," can be typed on the way to "12,50". */
const amount = z
  .string()
  .trim()
  .refine((value) => parseAmount(value) !== null, 'Enter an amount, such as 12,50');

const itemSchema = z.object({
  id: z.number().optional(),
  name: z.string().trim().min(1, 'Name the item'),
  expense_account: z.string().min(1, 'Choose an expense account'),
  price: amount,
});

export const receiptFormSchema = z.object({
  source_account: z.string().min(1, 'Choose the account it was paid from'),
  payee: z.string().trim().min(1, 'Enter the payee'),
  date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, 'Choose a date'),
  description: z.string(),
  total_sum: amount,
  items: z.array(itemSchema).min(1, 'Add at least one item'),
});

export type ReceiptFormValues = z.infer<typeof receiptFormSchema>;
export type ReceiptFormItem = ReceiptFormValues['items'][number];

export const emptyItem = (): ReceiptFormItem => ({ name: '', expense_account: '', price: '' });

export function toFormValues(receipt: Receipt | undefined): ReceiptFormValues {
  if (!receipt) {
    return {
      source_account: '',
      payee: '',
      date: todayIsoDate(),
      description: '',
      total_sum: '',
      items: [emptyItem()],
    };
  }
  return {
    source_account: receipt.source_account ?? '',
    payee: receipt.payee,
    date: receipt.date,
    description: receipt.description ?? '',
    total_sum: amountToInput(receipt.total_sum),
    items: receipt.items.map((item) => ({
      id: item.id,
      name: item.name,
      expense_account: item.expense_account,
      price: amountToInput(item.price),
    })),
  };
}

/** The amount in a form field, or 0 while it is not a number yet. */
export function amountOf(text: string | undefined): number {
  return parseAmount(text ?? '') ?? 0;
}

export function toRequest(values: ReceiptFormValues): ReceiptRequest {
  return {
    payee: values.payee.trim(),
    description: values.description.trim() || null,
    source_account: values.source_account,
    date: values.date,
    total_sum: amountOf(values.total_sum),
    items: values.items.map((item) => ({
      id: item.id ?? null,
      name: item.name.trim(),
      expense_account: item.expense_account,
      price: amountOf(item.price),
    })),
  };
}
