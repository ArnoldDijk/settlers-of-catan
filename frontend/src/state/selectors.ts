import { corner, pointKey } from '../board/geometry';
import type { DevCards, HexCoord, PlayerView, Resource } from './types';

export const RESOURCES: Resource[] = ['lumber', 'brick', 'wool', 'grain', 'ore'];

export const sameHex = (a: HexCoord, b: HexCoord) => a.q === b.q && a.r === b.r;

export const diceSum = (v: { dice: number[] | null }): number | null =>
  v.dice && v.dice.length === 2 ? v.dice[0] + v.dice[1] : null;

export const cardsInHand = (h: { resources: Record<string, number> }) =>
  RESOURCES.reduce((n, r) => n + (h.resources[r] ?? 0), 0);

export const devCardsInHand = (h: { devCards: DevCards }) =>
  h.devCards.knight + h.devCards.roadBuilding + h.devCards.yearOfPlenty + h.devCards.monopoly + h.devCards.victoryPoint;

export const playerById = (v: PlayerView, id: string | null) => v.players.find(p => p.id === id);

export const viewer = (v: PlayerView) => playerById(v, v.viewerId)!;

export const nameOf = (v: PlayerView, id: string | null) => playerById(v, id)?.name ?? '?';

/** Bank trade rate per resource for the viewer (4:1, 3:1 with a generic harbor, 2:1 with a matching one).
 *  Display only: the server decides what is legal. */
export function tradeRates(v: PlayerView): Record<Resource, number> {
  const mine = new Set(
    v.buildings.filter(b => b.owner === v.viewerId).map(b => pointKey(corner(b.at, b.at.corner))),
  );
  const kinds = new Set<string>();
  for (const h of v.board.harbors) {
    const ends = [corner(h, h.edge), corner(h, (h.edge + 1) % 6)].map(pointKey);
    if (ends.some(k => mine.has(k))) kinds.add(h.kind);
  }
  const base = kinds.has('any') ? 3 : 4;
  return Object.fromEntries(RESOURCES.map(r => [r, kinds.has(r) ? 2 : base])) as Record<Resource, number>;
}

/** Who the game is waiting for right now. */
export function waitingFor(v: PlayerView): string[] {
  if (v.phase === 'finished') return [];
  const discards = Object.keys(v.pendingDiscards);
  if (v.turn.step === 'discard') return discards;
  if (v.trade) {
    const open = Object.entries(v.trade.responses).filter(([, answer]) => answer === null).map(([id]) => id);
    if (open.length) return open;
  }
  return [v.turn.currentPlayerId];
}
