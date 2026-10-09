import { describe, expect, test } from 'vitest';

import { isBalanced, itemsSum, mergeItems, missingAmount } from './receiptMath';

const items = [
  { id: 1, name: 'Kahvi', expense_account: 'Expenses:Groceries', price: 12.99 },
  { id: 2, name: 'Vihko', expense_account: 'Expenses:Office', price: 4.99 },
  { id: 3, name: 'Kynä', expense_account: 'Expenses:Office', price: 1.99 },
  { id: 4, name: 'Pulla', expense_account: 'Expenses:Dining', price: 5.99 },
];

describe('receipt arithmetic', () => {
  test('sums to the cent despite floating point', () => {
    expect(itemsSum([0.1, 0.2])).toBe(0.3);
    expect(isBalanced(0.3, [0.1, 0.2])).toBe(true);
  });

  test('reports how much the items are short of the total', () => {
    expect(missingAmount(20, [12.99, 4.99])).toBe(2.02);
    expect(missingAmount(10, [12.5])).toBe(-2.5);
    expect(isBalanced(10, [9.99])).toBe(false);
  });
});

describe('mergeItems', () => {
  test('replaces the selected items with one at the first one’s place', () => {
    const merged = mergeItems(items, new Set([0, 2]));

    expect(merged).toEqual([
      { name: 'Kahvi, Kynä', expense_account: 'Expenses:Office', price: 14.98 },
      items[1],
      items[3],
    ]);
  });

  test('rounds the merged price to cents', () => {
    const odd = [
      { name: 'A', expense_account: 'X', price: 1.111 },
      { name: 'B', expense_account: 'X', price: 2.222 },
    ];

    expect(mergeItems(odd, new Set([0, 1]))).toEqual([
      { name: 'A, B', expense_account: 'X', price: 3.33 },
    ]);
  });

  test('needs at least two items', () => {
    expect(mergeItems(items, new Set([1]))).toEqual(items);
  });
});
