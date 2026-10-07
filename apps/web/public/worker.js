// Only a public offline notice is cached. Never cache API responses or private pages.
const CACHE = 'limitless-public-v2';
self.addEventListener('install', event => {
  event.waitUntil(caches.open(CACHE).then(cache => cache.add('/offline.html')).then(() => self.skipWaiting()));
});
self.addEventListener('activate', event => event.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(key => key !== CACHE && (key.startsWith('skillsetu-public-') || key.startsWith('limitless-public-'))).map(key => caches.delete(key)))).then(() => self.clients.claim())));
self.addEventListener('fetch', event => {
  if (event.request.mode !== 'navigate') return;
  event.respondWith(fetch(event.request).catch(() => caches.match('/offline.html')));
});

