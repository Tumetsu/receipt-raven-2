import { expect, test } from 'vitest';

import { renderApp } from '@tests/harness/renderApp';
import { recorded } from '@tests/msw/fakeApi';

test('enters a receipt by hand, choosing accounts and a new payee', async () => {
  const { screen, router } = await renderApp({ path: '/receipts/new' });

  await screen.getByRole('combobox', { name: 'Payee' }).click();
  await screen.getByRole('combobox', { name: 'Search payee' }).fill('Tori.fi myyjä');
  await screen.getByRole('option', { name: 'Use “Tori.fi myyjä”' }).click();
  await screen.getByRole('combobox', { name: 'Paid from' }).click();
  await screen.getByRole('option', { name: 'Liabilities:CreditCard' }).click();
  await screen.getByRole('textbox', { name: 'Total' }).fill('20,5');
  await screen.getByRole('textbox', { name: 'Name of item 1' }).fill('Polkupyörän lamppu');
  await screen.getByRole('combobox', { name: 'Expense account of item 1' }).click();
  await screen.getByRole('option', { name: 'Expenses:Office' }).click();
  await screen.getByRole('textbox', { name: 'Price of item 1' }).fill('20.50');
  await screen.getByRole('button', { name: 'Save receipt' }).click();

  await expect.element(screen.getByRole('heading', { name: 'Tori.fi myyjä' })).toBeVisible();
  expect(router.state.location.pathname).toMatch(/^\/receipts\/\d+$/);
  expect(recorded.receipts()[0]).toMatchObject({
    payee: 'Tori.fi myyjä',
    source_account: 'Liabilities:CreditCard',
    total_sum: 20.5,
    items: [{ name: 'Polkupyörän lamppu', expense_account: 'Expenses:Office', price: 20.5 }],
  });
});

test('tells what is missing before saving', async () => {
  const { screen } = await renderApp({ path: '/receipts/new' });

  await screen.getByRole('button', { name: 'Save receipt' }).click();

  await expect.element(screen.getByText('Enter the payee')).toBeVisible();
  await expect.element(screen.getByText('Choose the account it was paid from')).toBeVisible();
  await expect.element(screen.getByText('Name the item')).toBeVisible();
  expect(recorded.receipts()).toHaveLength(0);
});
