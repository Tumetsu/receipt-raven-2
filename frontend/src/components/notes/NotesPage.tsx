import { Loader2, Trash2 } from 'lucide-react';
import { useState, type FormEvent } from 'react';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { useNotes } from '@/hooks/useNotes';

/** The example page: create, list and delete notes. Replace it with your own. */
export function NotesPage() {
  const { notes, isLoading, loadFailed, isCreating, createNote, deleteNote } = useNotes();
  const [title, setTitle] = useState('');
  const [body, setBody] = useState('');

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    await createNote(title, body);
    setTitle('');
    setBody('');
  };

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-3xl font-semibold tracking-tight">Notes</h1>

      <Card>
        <CardContent>
          <form onSubmit={submit} className="flex flex-col gap-4">
            <div className="flex flex-col gap-2">
              <Label htmlFor="note-title">Title</Label>
              <Input id="note-title" value={title} onChange={(e) => setTitle(e.target.value)} />
            </div>
            <div className="flex flex-col gap-2">
              <Label htmlFor="note-body">Body</Label>
              <Textarea id="note-body" value={body} onChange={(e) => setBody(e.target.value)} />
            </div>
            <div>
              <Button type="submit" disabled={!title.trim() || isCreating}>
                Add note
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      {isLoading && <Loader2 aria-label="Loading notes" className="animate-spin" />}
      {loadFailed && (
        <p role="alert" className="text-destructive">
          The notes could not be loaded.
        </p>
      )}
      {!isLoading && !loadFailed && notes.length === 0 && (
        <p className="text-muted-foreground">No notes yet.</p>
      )}

      <ul aria-label="Notes" className="flex flex-col gap-3">
        {notes.map((note) => (
          <li key={note.id}>
            <Card>
              <CardHeader className="flex flex-row items-start justify-between">
                <div className="flex flex-col gap-1">
                  <CardTitle>{note.title}</CardTitle>
                  <p className="text-muted-foreground text-sm">{note.body_preview}</p>
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  aria-label={`Delete ${note.title}`}
                  onClick={() => deleteNote(note.id)}
                >
                  <Trash2 />
                </Button>
              </CardHeader>
            </Card>
          </li>
        ))}
      </ul>
    </div>
  );
}
