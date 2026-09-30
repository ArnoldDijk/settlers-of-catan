import { useCallback, useEffect, useRef, useState } from 'react';
import type { Action, PlayerView } from '../state/types';
import { api, ApiError, socketUrl } from './client';

/** Keep whichever view is newest (WebSocket pushes and HTTP responses can cross). */
export const newer = (prev: PlayerView | null, next: PlayerView) => (!prev || next.version >= prev.version ? next : prev);

/** Reconnect delay: 0.5 s, 1 s, 2 s … capped at 10 s. */
export const backoff = (attempt: number) => Math.min(10_000, 500 * 2 ** attempt);

export type Connection = 'connecting' | 'open' | 'lost';

export interface GameHandle {
  view: PlayerView | null;
  error: ApiError | null;
  /** 'lost' only after a live connection dropped (or a reconnect failed). */
  connection: Connection;
  busy: boolean;
  act: (action: Action) => Promise<void>;
  clearError: () => void;
}

/** Live view of one game: initial GET, then WebSocket pushes; actions go over HTTP. */
export function useGame(gameId: string): GameHandle {
  const [view, setView] = useState<PlayerView | null>(null);
  const [error, setError] = useState<ApiError | null>(null);
  const [connection, setConnection] = useState<Connection>('connecting');
  const [busy, setBusy] = useState(false);
  const viewRef = useRef<PlayerView | null>(null);
  viewRef.current = view;

  const load = useCallback(async () => {
    try {
      const v = await api.view(gameId);
      setView(prev => newer(prev, v));
      return true;
    } catch (e) {
      setError(e instanceof ApiError ? e : new ApiError(0, 'network'));
      return !(e instanceof ApiError && (e.status === 401 || e.status === 403 || e.status === 404));
    }
  }, [gameId]);

  useEffect(() => {
    let socket: WebSocket | null = null;
    let timer: ReturnType<typeof setTimeout> | undefined;
    let stopped = false;
    let attempt = 0;

    const connect = () => {
      if (stopped) return;
      socket = new WebSocket(socketUrl(gameId));
      socket.onopen = () => {
        attempt = 0;
        setConnection('open');
      };
      socket.onmessage = e => {
        try {
          setView(prev => newer(prev, JSON.parse(String(e.data)) as PlayerView));
        } catch {
          // ignore malformed messages
        }
      };
      socket.onclose = () => {
        if (!stopped) setConnection('lost');
        if (!stopped) timer = setTimeout(connect, backoff(attempt++));
      };
    };

    load().then(ok => {
      if (ok) connect();
    });
    return () => {
      stopped = true;
      clearTimeout(timer);
      socket?.close();
    };
  }, [gameId, load]);

  const act = useCallback(
    async (action: Action) => {
      const current = viewRef.current;
      if (!current) return;
      setBusy(true);
      try {
        const v = await api.act(gameId, current.version, action);
        setView(prev => newer(prev, v));
        setError(null);
      } catch (e) {
        const err = e instanceof ApiError ? e : new ApiError(0, 'network');
        setError(err);
        if (err.code === 'staleVersion') await load();
      } finally {
        setBusy(false);
      }
    },
    [gameId, load],
  );

  return { view, error, connection, busy, act, clearError: () => setError(null) };
}
