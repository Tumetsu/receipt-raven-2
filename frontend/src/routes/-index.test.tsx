import { describe, expect, test } from 'vitest';

import { renderApp } from '@tests/harness/renderApp';
import { seedReceipt } from '@tests/msw/fakeApi';

describe('receipt list', () => {
  test('shows the receipts to review, with a warning on a doubtful date', async () => {
    seedReceipt({ payee: 'Prisma', status: 'unapproved' });
    seedReceipt({
      payee: 'Alko',
      status: 'unapproved',
      ocr_notes: {
        suspicious_date: { level: 'SEVERE', message: 'Date is in previous year (2025)' },
      },
    });
    seedReceipt({ payee: 'Lidl', status: 'approved' });

    const { screen } = await renderApp({ path: '/' });

    const table = screen.getByRole('table', { name: 'Receipts' });
    await expect.element(table.getByRole('link', { name: 'Prisma' })).toBeVisible();
    await expect.element(table.getByRole('link', { name: 'Alko' })).toBeVisible();
    await expect.element(table.getByRole('img', { name: 'Check the date' })).toBeVisible();
    await expect.element(table.getByText('Lidl')).not.toBeInTheDocument();
    await expect.element(screen.getByRole('tab', { name: 'To review (2)' })).toBeVisible();
  });

  test('the All tab includes approved receipts', async () => {
    seedReceipt({ payee: 'Prisma' });
    seedReceipt({ payee: 'Lidl', status: 'approved' });
    const { screen } = await renderApp({ path: '/' });

    await screen.getByRole('tab', { name: 'All' }).click();

    const table = screen.getByRole('table', { name: 'Receipts' });
    await expect.element(table.getByRole('link', { name: 'Lidl' })).toBeVisible();
    await expect.element(table.getByRole('link', { name: 'Prisma' })).toBeVisible();
  });

  test('says when there is nothing to review', async () => {
    const { screen } = await renderApp({ path: '/' });

    await expect.element(screen.getByText('No receipts here')).toBeVisible();
  });
});
