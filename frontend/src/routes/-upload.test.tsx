import { expect, test } from 'vitest';

import { renderApp } from '@tests/harness/renderApp';
import { recorded } from '@tests/msw/fakeApi';

test('uploads a chosen PDF for analysis', async () => {
  const { screen } = await renderApp({ path: '/upload' });
  const pdf = new File(['%PDF-1.4'], 'lasku.pdf', { type: 'application/pdf' });

  await screen.getByLabelText('Choose a file').upload(pdf);
  await expect.element(screen.getByText('lasku.pdf')).toBeVisible();
  await screen.getByRole('button', { name: 'Analyse receipt' }).click();

  await expect.element(screen.getByText('Receipt sent for analysis')).toBeVisible();
  expect(recorded.uploads()).toEqual([{ name: 'lasku.pdf', type: 'application/pdf', size: 8 }]);
});

test('refuses files that are not images or PDFs', async () => {
  const { screen } = await renderApp({ path: '/upload' });

  await screen
    .getByLabelText('Choose a file')
    .upload(new File(['hi'], 'notes.txt', { type: 'text/plain' }));

  await expect.element(screen.getByText('Choose a photo or a PDF of the receipt.')).toBeVisible();
  expect(recorded.uploads()).toHaveLength(0);
});
