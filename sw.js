// Uygulama kabuğunu önbelleğe alır; PDF'ler önbelleğe alınmaz (MEB'den açılır).
const SURUM = "v2";
const KABUK = ["./", "index.html", "veri.js", "manifest.webmanifest", "ikon.svg", "ikon-192.png", "ikon-512.png"];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(SURUM).then(c => c.addAll(KABUK)).then(() => self.skipWaiting()));
});
self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(k => Promise.all(k.filter(x => x !== SURUM).map(x => caches.delete(x))))
    .then(() => self.clients.claim()));
});
// Önce ağ, olmazsa önbellek: bağlantılar güncellenince hemen görünür.
self.addEventListener("fetch", e => {
  const url = new URL(e.request.url);
  if (e.request.method !== "GET" || url.origin !== location.origin) return;
  e.respondWith(
    fetch(e.request).then(r => {
      const kopya = r.clone();
      caches.open(SURUM).then(c => c.put(e.request, kopya));
      return r;
    }).catch(() => caches.match(e.request, {ignoreSearch: true}))
  );
});
