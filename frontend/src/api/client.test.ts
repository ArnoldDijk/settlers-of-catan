import { afterEach, describe, expect, it, vi } from 'vitest';
import type { PlayerView } from '../state/types';
import { api, ApiError, isToken, messageFor, socketUrl } from './client';
import { backoff, newer } from './useGame';

const respond = (status: number, body: unknown) =>
  vi.fn(async () => new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } }));

afterEach(() => vi.unstubAllGlobals());

describe('api client', () => {
  it('sends JSON to same-origin paths', async () => {
    const fetch = respond(200, { gameId: 'abcdefgh', playerId: 'p1' });
    vi.stubGlobal('fetch', fetch);
    await api.join('x'.repeat(43));
    const [url, init] = fetch.mock.calls[0] as unknown as [string, RequestInit];
    expect(url).toBe('/api/join');
    expect(init.credentials).toBe('same-origin');
    expect(JSON.parse(String(init.body))).toEqual({ token: 'x'.repeat(43) });
  });

  it('maps server error codes to Dutch messages', async () => {
    vi.stubGlobal('fetch', respond(422, { detail: { code: 'cannotAfford', detail: 'x' } }));
    const err = await api.view('abcdefgh').catch((e: unknown) => e);
    expect(err).toBeInstanceOf(ApiError);
    expect((err as ApiError).code).toBe('cannotAfford');
    expect((err as ApiError).message).toBe('Daar heb je niet genoeg grondstoffen voor.');
  });

  it('handles validation errors and network failures', async () => {
    vi.stubGlobal('fetch', respond(422, { detail: [{ msg: 'bad' }] }));
    expect(((await api.view('abcdefgh').catch((e: unknown) => e)) as ApiError).code).toBe('invalidRequest');
    vi.stubGlobal('fetch', vi.fn(async () => { throw new TypeError('offline'); }));
    expect(((await api.view('abcdefgh').catch((e: unknown) => e)) as ApiError).code).toBe('network');
  });

  it('has a fallback message for unknown codes', () => {
    expect(messageFor('somethingNew')).toContain('somethingNew');
  });

  it('builds the WebSocket URL from the page origin', () => {
    expect(socketUrl('abcdefgh', { protocol: 'https:', host: 'catan.example' })).toBe('wss://catan.example/api/games/abcdefgh/ws');
    expect(socketUrl('abcdefgh', { protocol: 'http:', host: 'localhost:8081' })).toBe('ws://localhost:8081/api/games/abcdefgh/ws');
  });

  it('accepts only well-formed join tokens', () => {
    expect(isToken('A'.repeat(43))).toBe(true);
    expect(isToken('short')).toBe(false);
    expect(isToken('bad token with spaces and more text')).toBe(false);
  });
});

describe('live updates', () => {
  it('never replaces a newer view with an older one', () => {
    const v = (version: number) => ({ version }) as PlayerView;
    expect(newer(null, v(3)).version).toBe(3);
    expect(newer(v(5), v(4)).version).toBe(5);
    expect(newer(v(5), v(6)).version).toBe(6);
  });

  it('backs off exponentially up to 10 s', () => {
    expect([0, 1, 2, 3, 10].map(backoff)).toEqual([500, 1000, 2000, 4000, 10_000]);
  });
});
