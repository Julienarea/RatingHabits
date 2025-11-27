// PWA bootstrap: register Service Worker and basic offline handling
(function() {
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', function() {
            navigator.serviceWorker.register('/static/js/pwa/sw.js')
                .then(function(reg) {
                    console.log('ServiceWorker registered:', reg.scope);
                })
                .catch(function(err) {
                    console.log('ServiceWorker registration failed:', err);
                });
        });
    }

    // Optional: simple install prompt handling (for supported browsers)
    let deferredPrompt;
    window.addEventListener('beforeinstallprompt', (e) => {
        e.preventDefault();
        deferredPrompt = e;
        console.log('PWA install prompt is available');
        // You can show a custom install UI and call deferredPrompt.prompt() on user action
    });
})();