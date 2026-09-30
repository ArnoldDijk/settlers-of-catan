import { describe, expect, it } from 'vitest';
import type { Action } from '../state/types';
import { boardTargets } from './targets';

describe('boardTargets', () => {
  it('turns placements into clickable spots', () => {
    const legal: Action[] = [
      { type: 'buildSettlement', at: { q: 0, r: 0, corner: 0 } },
      { type: 'buildCity', at: { q: 1, r: 0, corner: 2 } },
      { type: 'buildRoad', at: { q: 0, r: 0, edge: 1 } },
      { type: 'endTurn' },
    ];
    const t = boardTargets(legal);
    expect(t.vertices.map(v => v.kind)).toEqual(['settlement', 'city']);
    expect(t.edges).toHaveLength(1);
    expect(t.hexes).toEqual([]);
  });

  it('groups robber moves per hex, one action per victim', () => {
    const legal: Action[] = [
      { type: 'moveRobber', to: { q: 1, r: 0 }, stealFrom: 'p2' },
      { type: 'moveRobber', to: { q: 1, r: 0 }, stealFrom: 'p3' },
      { type: 'moveRobber', to: { q: 0, r: 1 }, stealFrom: null },
    ];
    const t = boardTargets(legal);
    expect(t.hexes).toHaveLength(2);
    expect(t.hexes[0].actions.map(a => a.stealFrom)).toEqual(['p2', 'p3']);
  });

  it('shows nothing when it is not your move', () => {
    expect(boardTargets([])).toEqual({ vertices: [], edges: [], hexes: [] });
  });
});
