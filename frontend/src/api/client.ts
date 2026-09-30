import type { Action, CreateGameResponse, JoinResponse, PlayerView } from '../state/types';

// Thin wrapper around the backend API (same origin, proxied by nginx or the Vite dev server).
// The seat cookie is HttpOnly: this code never sees or stores the player's token.

const MESSAGES: Record<string, string> = {
  network: 'Geen verbinding met de server.',
  notJoined: 'Je bent niet aangemeld voor dit spel. Open je persoonlijke uitnodigingslink.',
  wrongGame: 'Deze uitnodiging hoort bij een ander spel.',
  invalidToken: 'Deze uitnodigingslink is ongeldig.',
  gameNotFound: 'Dit spel bestaat niet.',
  staleVersion: 'Het spel is intussen veranderd. Probeer het opnieuw.',
  notYourTurn: 'Je bent niet aan de beurt.',
  wrongStep: 'Dat kan nu niet.',
  cannotAfford: 'Daar heb je niet genoeg grondstoffen voor.',
  illegalPlacement: 'Daar mag je niet bouwen.',
  noPiecesLeft: 'Je hebt geen stukken meer over.',
  devCardAlreadyPlayed: 'Je hebt deze beurt al een ontwikkelingskaart gespeeld.',
  noSuchCard: 'Je hebt die kaart niet (of je kocht hem deze beurt).',
  deckEmpty: 'Er zijn geen ontwikkelingskaarten meer.',
  bankEmpty: 'De bank heeft die grondstof niet meer.',
  wrongAmount: 'Verkeerd aantal kaarten.',
  illegalRobberHex: 'De rover moet naar een andere tegel.',
  illegalVictim: 'Van die speler kun je niet stelen.',
  invalidOffer: 'Dit handelsvoorstel is ongeldig.',
  tooManyOffers: 'Je hebt deze beurt al genoeg voorstellen gedaan.',
  noOpenTrade: 'Er is geen open handelsvoorstel.',
  notAccepted: 'Die speler heeft het voorstel niet aangenomen.',
  notAddressed: 'Dit voorstel is niet aan jou gericht.',
  tradeOpen: 'Sluit eerst het open handelsvoorstel.',
  badReference: 'Die plek bestaat niet op het bord.',
  invalidRequest: 'Ongeldig verzoek.',
  bodyTooLarge: 'Verzoek te groot.',
};

export const messageFor = (code: string) => MESSAGES[code] ?? `Er ging iets mis (${code}).`;

export class ApiError extends Error {
  constructor(readonly status: number, readonly code: string) {
    super(messageFor(code));
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(path, {
      ...init,
      credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
    });
  } catch {
    throw new ApiError(0, 'network');
  }
  if (!res.ok) {
    let code = res.status === 422 ? 'invalidRequest' : `http${res.status}`;
    try {
      const body: unknown = await res.json();
      const detail = (body as { detail?: unknown })?.detail;
      if (detail && typeof detail === 'object' && typeof (detail as { code?: unknown }).code === 'string') {
        code = (detail as { code: string }).code;
      }
    } catch {
      // not JSON: keep the status-based code
    }
    throw new ApiError(res.status, code);
  }
  return (await res.json()) as T;
}

const gamePath = (gameId: string) => `/api/games/${encodeURIComponent(gameId)}`;

export const api = {
  createGame: (players: string[]) =>
    request<CreateGameResponse>('/api/games', { method: 'POST', body: JSON.stringify({ players }) }),
  join: (token: string) => request<JoinResponse>('/api/join', { method: 'POST', body: JSON.stringify({ token }) }),
  view: (gameId: string) => request<PlayerView>(`${gamePath(gameId)}/view`),
  act: (gameId: string, expectedVersion: number, action: Action) =>
    request<PlayerView>(`${gamePath(gameId)}/actions`, {
      method: 'POST',
      body: JSON.stringify({ expectedVersion, action }),
    }),
};

export function socketUrl(gameId: string, loc: Pick<Location, 'protocol' | 'host'> = window.location): string {
  return `${loc.protocol === 'https:' ? 'wss' : 'ws'}://${loc.host}${gamePath(gameId)}/ws`;
}

/** Join tokens are URL-safe base64; anything else is not worth sending. */
export const isToken = (t: string) => /^[A-Za-z0-9_-]{20,100}$/.test(t);
