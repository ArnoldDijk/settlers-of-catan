// Game types, generated from the backend's OpenAPI schema (src/api/schema.ts, `npm run gen:api`).
// The backend owns the full game; the browser only ever receives a PlayerView: public
// information plus the viewer's own hand.

import type { components } from '../api/schema';

type S = components['schemas'];

export type Resource = 'lumber' | 'brick' | 'wool' | 'grain' | 'ore';
export type Terrain = S['Tile']['terrain'];
export type PlayerColor = S['PublicPlayer']['color'];

/** Hex corner k sits at angle -90° + 60°·k (0 = top, clockwise). */
export type Corner = 0 | 1 | 2 | 3 | 4 | 5;
/** Hex edge k runs from corner k to corner k+1; its midpoint is at -60° + 60°·k. */
export type EdgeIx = 0 | 1 | 2 | 3 | 4 | 5;

export type HexCoord = S['HexCoord'];
export type VertexRef = S['VertexRef'];
export type EdgeRef = S['EdgeRef'];
export type Tile = S['Tile'];
export type Harbor = S['Harbor'];
export type Building = S['Building'];
export type Road = S['Road'];
export type DevCards = S['DevCards'];
export type PublicPlayer = S['PublicPlayer'];
export type Hand = S['Hand'];
export type TradeOffer = S['TradeOfferView'];
export type PlayerView = S['PlayerView'];
export type Step = S['Turn']['step'];

export type Action = PlayerView['legalActions'][number];
export type ActionType = Action['type'];
export type ActionOf<T extends ActionType> = Extract<Action, { type: T }>;

export type Seat = S['Seat'];
export type CreateGameResponse = S['CreateGameResponse'];
export type JoinResponse = S['JoinResponse'];
