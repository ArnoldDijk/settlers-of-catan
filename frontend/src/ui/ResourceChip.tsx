import type { Resource } from '../state/types';
import { CARD_COLORS, RESOURCE_NAMES, RESOURCE_TERRAIN } from '../board/palette';

/** Mini resource card: terrain illustration from the tile plus a count. */
export function ResourceChip({ resource, count }: { resource: Resource; count: number }) {
  return (
    <div className={`res-chip${count === 0 ? ' res-chip-empty' : ''}`} title={RESOURCE_NAMES[resource]}>
      <div className="res-chip-art" style={{ background: CARD_COLORS[resource] }}>
        <svg viewBox="-55 -55 110 110" preserveAspectRatio="xMidYMid slice">
          <use href={`#t-${RESOURCE_TERRAIN[resource]}`} />
        </svg>
      </div>
      <div className="res-chip-count">{count}</div>
      <div className="res-chip-name">{RESOURCE_NAMES[resource]}</div>
    </div>
  );
}
