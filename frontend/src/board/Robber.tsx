import type { HexCoord } from '../state/types';
import { pos } from './geometry';

/** Robber sits off-centre on its tile so the dimmed token stays readable; it glides when moved. */
export function Robber({ at }: { at: HexCoord }) {
  const [x, y] = pos(at);
  return (
    <g style={{ transform: `translate(${x}px,${y}px)`, transition: 'transform 700ms cubic-bezier(0.2,0.8,0.2,1)' }}>
      <use href="#p-robber" transform="translate(26,-8) scale(1.6)" />
    </g>
  );
}
