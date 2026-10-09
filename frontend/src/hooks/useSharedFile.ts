import { useEffect, useState } from 'react';

/** Must match `public/sw.js`, which stores what the share sheet sends. */
const SHARE_CACHE = 'share-target-cache-v1';
const SHARE_KEY = '/shared-file';

/**
 * A file another app shared to Receipt Raven (the PWA share target).
 *
 * The service worker catches the share's POST to /upload, keeps the file in
 * the Cache API and redirects to `/upload?shared=true`. Reading takes the file
 * out of the cache, so it is offered once.
 */
export function useSharedFile(shared: boolean): File | null {
  const [file, setFile] = useState<File | null>(null);

  useEffect(() => {
    if (!shared || !('caches' in window)) return;
    const effect = { cancelled: false };
    void (async () => {
      const cache = await caches.open(SHARE_CACHE);
      const response = await cache.match(SHARE_KEY);
      if (!response || effect.cancelled) return;
      const blob = await response.blob();
      await cache.delete(SHARE_KEY);
      const name = decodeURIComponent(response.headers.get('X-Filename') ?? 'shared-receipt');
      // Set even if cancelled meanwhile: this run took the file out of the cache.
      setFile(new File([blob], name, { type: blob.type }));
    })().catch((error: unknown) => console.error('Could not read the shared file', error));
    return () => {
      effect.cancelled = true;
    };
  }, [shared]);

  return file;
}
