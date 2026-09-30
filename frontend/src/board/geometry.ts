import type { HexCoord } from '../state/types';

// Pointy-top axial grid from the design: R = 100, spacing 173.2 × 150.
export const HEX_R = 100;
export const HEX_PATH = 'M0,-100 L86.6,-50 L86.6,50 L0,100 L-86.6,50 L-86.6,-50 Z';

const rad = (d: number) => (d * Math.PI) / 180;

export const pos = ({ q, r }: HexCoord): [number, number] => [173.2 * (q + r / 2), 150 * r];

/** Corner k (0–5) of a hex. */
export function corner(h: HexCoord, k: number): [number, number] {
  const [x, y] = pos(h);
  return [x + HEX_R * Math.cos(rad(-90 + 60 * k)), y + HEX_R * Math.sin(rad(-90 + 60 * k))];
}

/** Midpoint of edge k (0–5), which runs from corner k to corner k+1. */
export function edgeMid(h: HexCoord, k: number): [number, number] {
  const [x, y] = pos(h);
  const a = rad(-60 + 60 * k);
  return [x + 86.6 * Math.cos(a), y + 86.6 * Math.sin(a)];
}

export const hexDistance = ({ q, r }: HexCoord) => Math.max(Math.abs(q), Math.abs(r), Math.abs(q + r));

/** All hexes at exactly `radius` steps from the centre. */
export function ring(radius: number): HexCoord[] {
  const out: HexCoord[] = [];
  for (let q = -radius; q <= radius; q++)
    for (let r = -radius; r <= radius; r++) if (hexDistance({ q, r }) === radius) out.push({ q, r });
  return out;
}

/** The standard board's sea frame. */
export const SEA_RING = ring(3);

/** Stable key for a board point, so refs from different neighbouring hexes compare equal. */
export const pointKey = ([x, y]: [number, number]) => `${Math.round(x)},${Math.round(y)}`;
