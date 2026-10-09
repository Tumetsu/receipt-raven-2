import { expect, test } from 'vitest';

import { renderApp } from '@tests/harness/renderApp';
import { seedJob } from '@tests/msw/fakeApi';

test('shows a failed analysis and retries it', async () => {
  seedJob({ status: 'processed' });
  const failed = seedJob({
    status: 'failed',
    retry_count: 3,
    analysis_error: 'Receipt analysis failed: model overloaded',
    processed_at: null,
  });
  const { screen } = await renderApp({ path: '/jobs' });

  await screen.getByRole('button', { name: new RegExp(`Upload #${failed.id}`) }).click();
  const sheet = screen.getByRole('dialog', { name: `Upload #${failed.id}` });
  await expect.element(sheet.getByRole('alert')).toHaveTextContent('model overloaded');
  await sheet.getByRole('button', { name: 'Retry analysis' }).click();

  await expect.element(screen.getByText('The receipt is queued for analysis again')).toBeVisible();
  const row = screen.getByRole('button', { name: new RegExp(`Upload #${failed.id}`) });
  await expect.element(row).toHaveTextContent('Analysing');
});
