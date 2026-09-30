import type { Action, PlayerView } from '../state/types';
import { diceSum, sameHex } from '../state/selectors';
import { SEA_RING } from './geometry';
import { HarborToken } from './HarborToken';
import { Hex } from './Hex';
import { NumberToken } from './NumberToken';
import { PLAYER_COLORS } from './palette';
import { BuildingPiece, RoadPiece } from './Pieces';
import { Robber } from './Robber';
import type { HexTarget, Targets } from './targets';
import { TargetLayer } from './TargetLayer';

interface Props {
  state: PlayerView;
  targets?: Targets;
  disabled?: boolean;
  onAction?: (a: Action) => void;
  onHex?: (t: HexTarget) => void;
}

/** Renders the whole board — tiles, harbors, tokens, pieces, robber and clickable targets — from a PlayerView. */
export function Board({ state, targets, disabled = false, onAction = () => {}, onHex = () => {} }: Props) {
  const { tiles, harbors, robber } = state.board;
  const rolled = diceSum(state);
  const colorOf = (owner: string) => {
    const p = state.players.find(pl => pl.id === owner);
    return p ? PLAYER_COLORS[p.color] : '#161E3C';
  };

  return (
    <svg viewBox="-620 -565 1240 1130" style={{ width: '100%', height: 'auto', display: 'block' }} role="img" aria-label="Spelbord">
      {SEA_RING.map(h => {
        const harbor = harbors.find(hb => sameHex(hb, h));
        return (
          <Hex key={`s${h.q},${h.r}`} at={h} terrain="sea">
            {harbor && (
              <>
                <g transform={`rotate(${60 * (harbor.edge - 4)})`}>
                  <use href="#dock" />
                </g>
                <HarborToken kind={harbor.kind} />
              </>
            )}
          </Hex>
        );
      })}

      {tiles.map(t => (
        <Hex key={`l${t.q},${t.r}`} at={t} terrain={t.terrain}>
          {t.number != null && (
            <NumberToken n={t.number} highlight={t.number === rolled} blocked={sameHex(t, robber)} />
          )}
        </Hex>
      ))}

      {state.roads.map(r => (
        <RoadPiece key={`r${r.at.q},${r.at.r},${r.at.edge}`} road={r} color={colorOf(r.owner)} />
      ))}
      {state.buildings.map(b => (
        <BuildingPiece key={`b${b.at.q},${b.at.r},${b.at.corner}`} building={b} color={colorOf(b.owner)} />
      ))}

      <Robber at={robber} />

      {targets && <TargetLayer targets={targets} disabled={disabled} onAction={onAction} onHex={onHex} />}
    </svg>
  );
}
