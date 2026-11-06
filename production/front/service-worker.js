// Retire le service worker de l'ancien Stremio Web installé sur ce domaine :
// il vide ses caches, se désinscrit et recharge les pages ouvertes sur la nouvelle application.
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', (event) => {
  event.waitUntil((async () => {
    for (const key of await caches.keys()) await caches.delete(key);
    await self.registration.unregister();
    for (const client of await self.clients.matchAll({ type: 'window' })) client.navigate(client.url);
  })());
});
