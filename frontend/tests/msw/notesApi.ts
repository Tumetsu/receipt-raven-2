import { http, HttpResponse } from 'msw';

import type { NoteListItem, NoteRequest } from '@/api/generated/model';

/**
 * An in-memory notes API, so a test can create a note and see the list change
 * the way it would against the real backend. Reset after every test.
 */
let notes: NoteListItem[] = [];
let nextId = 1;

export function seedNotes(...titles: string[]) {
  for (const title of titles) {
    notes.unshift({
      id: nextId++,
      title,
      body_preview: '',
      updated_at: new Date().toISOString(),
    });
  }
}

export function resetNotesApi() {
  notes = [];
  nextId = 1;
}

export const notesHandlers = [
  http.get('/api/v1/notes', () => HttpResponse.json({ items: notes })),

  http.post('/api/v1/notes', async ({ request }) => {
    const { title, body = '' } = (await request.json()) as NoteRequest;
    const now = new Date().toISOString();
    const note = { id: nextId++, title: title.trim(), body, created_at: now, updated_at: now };
    notes.unshift({ id: note.id, title: note.title, body_preview: body, updated_at: now });
    return HttpResponse.json(note, { status: 201 });
  }),

  http.delete('/api/v1/notes/:noteId', ({ params }) => {
    const id = Number(params.noteId);
    const before = notes.length;
    notes = notes.filter((note) => note.id !== id);
    return new HttpResponse(null, { status: notes.length < before ? 204 : 404 });
  }),
];
