const CACHE_NAME = 'lovio-v1';
const urlsToCache = [
    '/',
    '/dashboard',
    '/static/manifest.json',
    'https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap'
];

// Install event
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => {
            return cache.addAll(urlsToCache).catch(err => {
                console.log('Cache addAll error:', err);
            });
        })
    );
    self.skipWaiting();
});

// Activate event
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheName !== CACHE_NAME) {
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
    self.clients.claim();
});

// Fetch event - Network first, then cache
self.addEventListener('fetch', event => {
    if (event.request.method !== 'GET') {
        return;
    }
    
    event.respondWith(
        fetch(event.request)
            .then(response => {
                // Clone the response
                const responseClone = response.clone();
                
                // Cache valid responses
                if (response.status === 200) {
                    caches.open(CACHE_NAME).then(cache => {
                        cache.put(event.request, responseClone);
                    });
                }
                
                return response;
            })
            .catch(() => {
                // Return cached version if network fails
                return caches.match(event.request)
                    .then(response => {
                        return response || new Response('Offline - content not available', {
                            status: 503,
                            statusText: 'Service Unavailable',
                            headers: new Headers({
                                'Content-Type': 'text/plain'
                            })
                        });
                    });
            })
    );
});

// Push notifications
self.addEventListener('push', event => {
    const options = {
        body: event.data.text(),
        icon: '/static/icons/icon-192.png',
        badge: '/static/icons/icon-96.png',
        tag: 'lovio-notification',
        requireInteraction: false
    };
    
    event.waitUntil(
        self.registration.showNotification('LOVIO', options)
    );
});

// Notification click
self.addEventListener('notificationclick', event => {
    event.notification.close();
    event.waitUntil(
        clients.matchAll({ type: 'window', includeUncontrolled: true })
            .then(clientList => {
                for (let client of clientList) {
                    if (client.url === '/' && 'focus' in client) {
                        return client.focus();
                    }
                }
                if (clients.openWindow) {
                    return clients.openWindow('/dashboard');
                }
            })
    );
});
