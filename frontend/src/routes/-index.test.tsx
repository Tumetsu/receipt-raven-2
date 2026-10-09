import { describe, expect, test } from 'vitest';

import { renderApp } from '@tests/harness/renderApp';
import { seedNotes } from '@tests/msw/notesApi';

describe('notes page', () => {
  test('lists the stored notes', async () => {
    seedNotes('Groceries', 'Meeting agenda');

    const { screen } = await renderApp({ path: '/' });

    const list = screen.getByRole('list', { name: 'Notes' });
    await expect.element(list.getByText('Meeting agenda')).toBeVisible();
    await expect.element(list.getByText('Groceries')).toBeVisible();
  });

  test('adds a note and clears the form', async () => {
    const { screen } = await renderApp({ path: '/' });
    const title = screen.getByRole('textbox', { name: 'Title' });

    await title.fill('Call the plumber');
    await screen.getByRole('button', { name: 'Add note' }).click();

    await expect
      .element(screen.getByRole('list', { name: 'Notes' }).getByText('Call the plumber'))
      .toBeVisible();
    await expect.element(title).toHaveValue('');
  });

  test('cannot add a note without a title', async () => {
    const { screen } = await renderApp({ path: '/' });

    await screen.getByRole('textbox', { name: 'Title' }).fill('   ');

    await expect.element(screen.getByRole('button', { name: 'Add note' })).toBeDisabled();
  });

  test('deletes a note', async () => {
    seedNotes('Old idea', 'Keep me');
    const { screen } = await renderApp({ path: '/' });

    await screen.getByRole('button', { name: 'Delete Old idea' }).click();

    const list = screen.getByRole('list', { name: 'Notes' });
    await expect.element(list.getByText('Old idea')).not.toBeInTheDocument();
    await expect.element(list.getByText('Keep me')).toBeVisible();
  });
});
