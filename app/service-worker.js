/* Palestinian Arabic — service worker.
 *
 * Two jobs: make the app installable + usable offline, and hold the push handler that the
 * scheduled-notification follow-up will use. CACHE_VERSION is bumped by pipeline/build_app.py so
 * a deploy invalidates old caches. IMPORTANT: the HTML document is fetched NETWORK-FIRST so a new
 * deploy shows up immediately (never a stale shell); data/audio/icons are cache-first for speed
 * and offline. */
const CACHE_VERSION = 'alp-3cc524054c';
const SHELL = ['./index.html', './manifest.webmanifest', './icon-192.png'];

self.addEventListener('install', e => {
  self.skipWaiting();
  e.waitUntil(caches.open(CACHE_VERSION).then(c => c.addAll(SHELL).catch(() => {})));
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(k => k !== CACHE_VERSION).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  const isDoc = req.mode === 'navigate' || url.pathname.endsWith('/index.html') || url.pathname.endsWith('/');
  if (isDoc) {
    // network-first: pick up new deploys instantly, fall back to cache when offline
    e.respondWith(fetch(req)
      .then(r => { const cp = r.clone(); caches.open(CACHE_VERSION).then(c => c.put(req, cp)); return r; })
      .catch(() => caches.match(req).then(m => m || caches.match('./index.html'))));
    return;
  }
  // cache-first for data, audio, icons, scripts — they're versioned or immutable enough
  e.respondWith(caches.match(req).then(m => m || fetch(req).then(r => {
    if (r.ok && /\.(js|css|png|mp3|json|webmanifest)$/.test(url.pathname)) {
      const cp = r.clone(); caches.open(CACHE_VERSION).then(c => c.put(req, cp));
    }
    return r;
  }).catch(() => m)));
});

/* ---- Web Push (follow-up wires the VAPID sender; the handler is ready now) ---- */
self.addEventListener('push', e => {
  let data = {};
  try { data = e.data ? e.data.json() : {}; } catch (err) {}
  e.waitUntil(self.registration.showNotification(data.title || 'Palestinian Arabic', {
    body: data.body || 'Time for today’s practice — a few minutes keeps the streak alive.',
    icon: './icon-192.png', badge: './icon-192.png',
    data: {url: data.url || './index.html'}
  }));
});
self.addEventListener('notificationclick', e => {
  e.notification.close();
  const target = (e.notification.data && e.notification.data.url) || './index.html';
  e.waitUntil(self.clients.matchAll({type: 'window'}).then(cs => {
    for (const c of cs) if ('focus' in c) return c.focus();
    return self.clients.openWindow(target);
  }));
});
