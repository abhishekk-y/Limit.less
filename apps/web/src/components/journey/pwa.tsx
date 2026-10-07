'use client';
import { useEffect } from 'react';

export function PWARegistration() {
  useEffect(() => {
    if (!('serviceWorker' in navigator) || process.env.NODE_ENV !== 'production') return;
    void (async () => {
      const registrations = await navigator.serviceWorker.getRegistrations();
      for (const registration of registrations) {
        if (registration.active?.scriptURL.endsWith('/sw.js')) await registration.unregister();
      }
      await navigator.serviceWorker.register('/worker.js');
    })().catch(() => { /* PWA installation is optional; the web app remains usable. */ });
  }, []);
  return null;
}
