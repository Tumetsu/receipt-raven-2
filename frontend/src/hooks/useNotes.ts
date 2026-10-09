import { useQueryClient } from '@tanstack/react-query';

import {
  getListNotesQueryKey,
  useCreateNote,
  useDeleteNote,
  useListNotes,
} from '@/api/generated/notes/notes';

/**
 * The notes list and the mutations that change it, independent of how they
 * are rendered. Every mutation refetches the list when it succeeds.
 */
export function useNotes() {
  const queryClient = useQueryClient();
  const list = useListNotes();

  const refetchList = () => queryClient.invalidateQueries({ queryKey: getListNotesQueryKey() });
  const create = useCreateNote({ mutation: { onSuccess: refetchList } });
  const remove = useDeleteNote({ mutation: { onSuccess: refetchList } });

  return {
    notes: list.data?.items ?? [],
    isLoading: list.isPending,
    loadFailed: list.isError,
    isCreating: create.isPending,
    createNote: (title: string, body: string) => create.mutateAsync({ data: { title, body } }),
    deleteNote: (noteId: number) => remove.mutate({ noteId }),
  };
}
