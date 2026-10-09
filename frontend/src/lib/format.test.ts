import { describe, expect, test } from 'vitest';

import { amountToInput, formatCurrency, formatDate, parseAmount } from './format';

describe('parseAmount', () => {
  test.each([
    ['12,50', 12.5],
    ['12.50', 12.5],
    [' 1 234,5 € ', 1234.5],
    ['-3', -3],
    [',5', 0.5],
  ])('reads %j as %d', (text, expected) => {
    expect(parseAmount(text)).toBe(expected);
  });

  test.each(['', 'abc', '1,2,3', '12e3'])('rejects %j', (text) => {
    expect(parseAmount(text)).toBeNull();
  });
});

test('formats calendar dates and input amounts the Finnish way', () => {
  expect(formatDate('2026-10-09')).toBe('9.10.2026');
  expect(amountToInput(3)).toBe('3,00');
});

test('formats amounts with the decimals of their currency', () => {
  expect(amountToInput(1500, 'JPY')).toBe('1500');
  expect(formatCurrency(1500, 'JPY').replace(/\s/g, ' ')).toBe('1 500 ¥');
  expect(formatCurrency(12.5).replace(/\s/g, ' ')).toBe('12,50 €');
  expect(formatCurrency(3, 'XYZ').replace(/\s/g, ' ')).toBe('3,00 XYZ');
});
