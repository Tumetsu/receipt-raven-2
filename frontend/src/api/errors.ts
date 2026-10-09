import { isAxiosError } from 'axios';

/**
 * A message to show the user for a failed request. The backend answers errors
 * as `{ error, message }`, and validation failures as `{ detail: [...] }`.
 */
export function apiErrorMessage(error: unknown, fallback = 'Something went wrong.'): string {
  if (isAxiosError(error)) {
    const data: unknown = error.response?.data;
    if (data && typeof data === 'object') {
      if ('message' in data && typeof data.message === 'string') return data.message;
      if ('detail' in data && Array.isArray(data.detail)) {
        const [first] = data.detail as { msg?: string }[];
        if (first?.msg) return first.msg;
      }
    }
    if (!error.response) return 'The server could not be reached.';
  }
  return fallback;
}
