import { describe, expect, test } from 'vitest';

import { amountToInput, formatDate, parseAmount } from './format';

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
