import { useEffect, useState } from 'react';

// Minimal History-API router (nginx serves index.html for every path).

export function navigate(path: string, replace = false) {
  if (replace) window.history.replaceState(null, '', path);
  else window.history.pushState(null, '', path);
  window.dispatchEvent(new PopStateEvent('popstate'));
}

export function usePath(): string {
  const [path, setPath] = useState(window.location.pathname);
  useEffect(() => {
    const on = () => setPath(window.location.pathname);
    window.addEventListener('popstate', on);
    return () => window.removeEventListener('popstate', on);
  }, []);
  return path;
}

export type Route =
  | { page: 'lobby' }
  | { page: 'join' }
  | { page: 'game'; gameId: string }
  | { page: 'tiles' }
  | { page: 'notFound' };

export function matchRoute(path: string): Route {
  if (path === '/' || path === '') return { page: 'lobby' };
  if (path === '/join') return { page: 'join' };
  if (path === '/tegelset') return { page: 'tiles' };
  const m = /^\/games\/([A-Za-z0-9_-]{8,32})\/?$/.exec(path);
  return m ? { page: 'game', gameId: m[1] } : { page: 'notFound' };
}

/** Link that navigates without a full page load. */
export function linkProps(path: string) {
  return {
    href: path,
    onClick: (e: { preventDefault: () => void; metaKey: boolean; ctrlKey: boolean; button: number }) => {
      if (e.metaKey || e.ctrlKey || e.button !== 0) return;
      e.preventDefault();
      navigate(path);
    },
  };
}
