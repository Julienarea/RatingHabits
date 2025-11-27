// Minimal Service Worker for offline caching
const CACHE_NAME = 'ratinghabits-cache-v1';
const PRECACHE_URLS = [
    '/',
    '/manifest.json',
    // CSS/JS
    '/static/css/style.css',
    '/static/js/script.js',
    // Icons & images used commonly (add more as needed)
    '/static/images/logo.png'
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => cache.addAll(PRECACHE_URLS))
    );
});

self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((keys) => Promise.all(
            keys.map((key) => {
                if (key !== CACHE_NAME) {
                    return caches.delete(key);
                }
            })
        ))
    );
});

// Cache-first for GET requests
self.addEventListener('fetch', (event) => {
    if (event.request.method !== 'GET') return;
    event.respondWith(
        caches.match(event.request).then((cached) => {
            const networkFetch = fetch(event.request).then((response) => {
                const clone = response.clone();
                caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone)).catch(() => {});
                return response;
            }).catch(() => cached);
            return cached || networkFetch;
        })
    );
});