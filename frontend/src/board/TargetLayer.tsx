import type { KeyboardEvent } from 'react';
import type { Action } from '../state/types';
import { corner, HEX_PATH, pos } from './geometry';
import type { HexTarget, Targets } from './targets';

interface Props {
  targets: Targets;
  disabled: boolean;
  onAction: (a: Action) => void;
  onHex: (t: HexTarget) => void;
}

const LABELS = { settlement: 'Bouw hier een dorp', city: 'Maak hier een stad' } as const;

/** Clickable highlights for every legal placement. Keyboard: Tab to a spot, Enter/Space to pick. */
export function TargetLayer({ targets, disabled, onAction, onHex }: Props) {
  const activate = (fn: () => void) => ({
    role: 'button',
    tabIndex: disabled ? -1 : 0,
    'aria-disabled': disabled,
    onClick: () => !disabled && fn(),
    onKeyDown: (e: KeyboardEvent) => {
      if (!disabled && (e.key === 'Enter' || e.key === ' ')) {
        e.preventDefault();
        fn();
      }
    },
  });

  return (
    <g className={`targets${disabled ? ' targets-disabled' : ''}`}>
      {targets.hexes.map(t => {
        const [x, y] = pos(t.at);
        return (
          <g key={`h${t.at.q},${t.at.r}`} transform={`translate(${x},${y})`} className="target target-hex"
             aria-label="Verplaats de rover hierheen" {...activate(() => onHex(t))}>
            <path d={HEX_PATH} transform="scale(0.93)" />
          </g>
        );
      })}
      {targets.edges.map(t => {
        const [x1, y1] = corner(t.at, t.at.edge);
        const [x2, y2] = corner(t.at, (t.at.edge + 1) % 6);
        return (
          <g key={`e${t.at.q},${t.at.r},${t.at.edge}`} className="target target-edge" aria-label="Leg hier een weg"
             {...activate(() => onAction(t.action))}>
            <line x1={x1} y1={y1} x2={x2} y2={y2} className="target-hit" />
            <line x1={x1} y1={y1} x2={x2} y2={y2} className="target-mark" />
          </g>
        );
      })}
      {targets.vertices.map(t => {
        const [x, y] = corner(t.at, t.at.corner);
        return (
          <g key={`v${t.at.q},${t.at.r},${t.at.corner}`} transform={`translate(${x},${y})`}
             className={`target target-vertex target-${t.kind}`} aria-label={LABELS[t.kind]}
             {...activate(() => onAction(t.action))}>
            <circle r={24} className="target-hit" />
            <circle r={t.kind === 'city' ? 22 : 13} className="target-mark" />
          </g>
        );
      })}
    </g>
  );
}
