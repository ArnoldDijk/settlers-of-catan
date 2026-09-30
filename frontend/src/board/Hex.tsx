import type { ReactNode } from 'react';
import type { HexCoord, Terrain } from '../state/types';
import { HEX_PATH, pos } from './geometry';
import { INK } from './palette';

interface Props {
  at: HexCoord;
  terrain: Terrain | 'sea';
  children?: ReactNode;
}

/** One terrain tile with the ink outline, positioned on the axial grid. */
export function Hex({ at, terrain, children }: Props) {
  const [x, y] = pos(at);
  return (
    <g transform={`translate(${x},${y})`}>
      <use href={`#t-${terrain}`} />
      <path d={HEX_PATH} fill="none" stroke={INK} strokeWidth={3} strokeLinejoin="round" />
      {children}
    </g>
  );
}
