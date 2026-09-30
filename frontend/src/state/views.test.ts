import { describe, expect, it } from 'vitest';
import p1 from './__fixtures__/views/p1.json';
import p2 from './__fixtures__/views/p2.json';
import { cardsInHand, diceSum, tradeRates, waitingFor } from './selectors';
import type { PlayerView } from './types';

// Fixtures are exported by the backend (backend/scripts/export_contract.py): real PlayerViews.
const anna = p1 as unknown as PlayerView;
const bram = p2 as unknown as PlayerView;

describe('player views from the backend', () => {
  it("contain the viewer's hand and only counts for others", () => {
    expect(anna.viewerId).toBe('p1');
    expect(cardsInHand(anna.hand)).toBe(anna.players[0].resourceCount);
    for (const p of anna.players) {
      expect(p).not.toHaveProperty('resources');
      expect(p).not.toHaveProperty('devCards');
    }
    expect(JSON.stringify(anna).match(/"resources"/g)).toHaveLength(2); // own hand + bank
  });

  it('keep hidden victory point cards out of public points', () => {
    const annaSeenByBram = bram.players.find(p => p.id === 'p1')!;
    expect(annaSeenByBram.victoryPoints).toBe(3);
    expect(anna.hand.devCards.victoryPoint).toBe(1);
  });

  it('list legal actions only for the player whose turn it is', () => {
    expect(bram.turn.currentPlayerId).toBe('p2');
    expect(bram.legalActions.some(a => a.type === 'endTurn')).toBe(true);
    expect(anna.legalActions).toEqual([]);
  });
});

describe('selectors', () => {
  it('sums the dice', () => {
    expect(diceSum(anna)).toBe(8);
    expect(diceSum({ dice: null })).toBeNull();
  });

  it('waits for the current player, then for trade responses and discards', () => {
    expect(waitingFor(anna)).toEqual(['p2']);
    const trading: PlayerView = {
      ...anna,
      trade: { offerer: 'p2', give: { ore: 1 }, get: { wool: 1 }, to: ['p1', 'p3'], responses: { p1: null, p3: false } },
    };
    expect(waitingFor(trading)).toEqual(['p1']);
    const discarding: PlayerView = { ...anna, turn: { ...anna.turn, step: 'discard' }, pendingDiscards: { p3: 4 } };
    expect(waitingFor(discarding)).toEqual(['p3']);
  });

  it("derives harbor trade rates from the viewer's buildings", () => {
    const none: PlayerView = { ...anna, buildings: [] };
    expect(Object.values(tradeRates(none))).toEqual([4, 4, 4, 4, 4]);
    const h = anna.board.harbors.find(x => x.kind === 'ore')!;
    const onHarbor: PlayerView = {
      ...none,
      buildings: [{ owner: 'p1', kind: 'settlement', at: { q: h.q, r: h.r, corner: h.edge } }],
    };
    expect(tradeRates(onHarbor).ore).toBe(2);
    expect(tradeRates(onHarbor).wool).toBe(4);
    const generic = anna.board.harbors.find(x => x.kind === 'any')!;
    const onGeneric: PlayerView = {
      ...none,
      buildings: [{ owner: 'p1', kind: 'settlement', at: { q: generic.q, r: generic.r, corner: (generic.edge + 1) % 6 } }],
    };
    expect(Object.values(tradeRates(onGeneric))).toEqual([3, 3, 3, 3, 3]);
  });
});
