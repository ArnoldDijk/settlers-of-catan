import type { Action, ActionOf, EdgeRef, HexCoord, VertexRef } from '../state/types';

// Which board spots the viewer can click right now, derived only from the server's legalActions.

export interface VertexTarget {
  at: VertexRef;
  kind: 'settlement' | 'city';
  action: Action;
}
export interface EdgeTarget {
  at: EdgeRef;
  action: Action;
}
export interface HexTarget {
  at: HexCoord;
  /** One per possible victim (or a single one without a victim). */
  actions: ActionOf<'moveRobber'>[];
}
export interface Targets {
  vertices: VertexTarget[];
  edges: EdgeTarget[];
  hexes: HexTarget[];
}

export function boardTargets(legal: Action[]): Targets {
  const t: Targets = { vertices: [], edges: [], hexes: [] };
  const hexes = new Map<string, HexTarget>();
  for (const a of legal) {
    switch (a.type) {
      case 'placeSetupSettlement':
      case 'buildSettlement':
        t.vertices.push({ at: a.at, kind: 'settlement', action: a });
        break;
      case 'buildCity':
        t.vertices.push({ at: a.at, kind: 'city', action: a });
        break;
      case 'placeSetupRoad':
      case 'buildRoad':
        t.edges.push({ at: a.at, action: a });
        break;
      case 'moveRobber': {
        const key = `${a.to.q},${a.to.r}`;
        const entry = hexes.get(key) ?? { at: a.to, actions: [] };
        entry.actions.push(a);
        hexes.set(key, entry);
        break;
      }
      default:
        break;
    }
  }
  t.hexes = [...hexes.values()];
  return t;
}

export const noTargets: Targets = { vertices: [], edges: [], hexes: [] };
