// Service worker for the Web Share Target: another app shares a receipt photo
// or PDF to Receipt Raven, which POSTs it to /upload (see manifest.json). The
// file is kept in the Cache API and the upload page picks it up from there
// (src/hooks/useSharedFile.ts reads the same cache and key).
const SHARE_CACHE = 'share-target-cache-v1';
const SHARE_KEY = '/shared-file';

self.addEventListener('install', (event) => {
  event.waitUntil(self.skipWaiting());
});

self.addEventListener('activate', (event) => {
  event.waitUntil(self.clients.claim());
});

self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);
  if (event.request.method === 'POST' && url.pathname === '/upload') {
    event.respondWith(receiveShare(event.request));
  }
});

async function receiveShare(request) {
  try {
    const formData = await request.formData();
    const file = formData.get('file') ?? formData.get('image');
    if (file instanceof File) {
      const cache = await caches.open(SHARE_CACHE);
      await cache.put(
        SHARE_KEY,
        new Response(file, {
          headers: { 'Content-Type': file.type, 'X-Filename': encodeURIComponent(file.name) },
        }),
      );
      return Response.redirect('/upload?shared=true', 303);
    }
  } catch (error) {
    console.error('Could not receive the shared file', error);
  }
  return Response.redirect('/upload', 303);
}
