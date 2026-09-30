import type { PlayerView, PublicPlayer } from '../state/types';
import { PLAYER_COLORS } from '../board/palette';

/** Public information about one player: counts only, never card contents. */
export function PlayerPanel({ view, player }: { view: PlayerView; player: PublicPlayer }) {
  const color = PLAYER_COLORS[player.color];
  const active = view.turn.currentPlayerId === player.id;
  const isMe = view.viewerId === player.id;
  // Only the viewer knows their own hidden victory point cards.
  const hiddenVp = isMe ? view.hand.devCards.victoryPoint : 0;
  return (
    <article className={`card player${active ? ' player-active' : ''}`}>
      <div className="player-head">
        <span className="dot" style={{ background: color }} />
        <div className="player-name">{player.name}</div>
        {isMe && <span className="pill pill-me">Jij</span>}
        {active && <span className="pill pill-active">Aan zet</span>}
        <div className="player-vp" title={isMe ? 'Overwinningspunten (zichtbaar + jouw geheime kaarten)' : 'Zichtbare overwinningspunten'}>
          {player.victoryPoints}{hiddenVp > 0 && <span className="muted"> +{hiddenVp}</span>}
          <span className="player-vp-label">OP</span>
        </div>
      </div>

      <div className="hand-backs">
        <CardBacks count={player.resourceCount} kind="resource" label="grondstofkaarten" />
        <CardBacks count={player.devCardCount} kind="dev" label="ontwikkelingskaarten" />
        <div className="knights" title="Gespeelde ridders">
          <strong>{player.knightsPlayed}</strong> ridders
        </div>
      </div>

      <div className="player-pieces">
        <Piece href="#p-road" color={color} left={player.piecesLeft.roads} label="Wegen" tf="rotate(-30)" />
        <Piece href="#p-settlement" color={color} left={player.piecesLeft.settlements} label="Dorpen" tf="scale(1.35)" />
        <Piece href="#p-city" color={color} left={player.piecesLeft.cities} label="Steden" tf="translate(0,2) scale(1.1)" />
      </div>

      {(view.awards.longestRoad === player.id || view.awards.largestArmy === player.id) && (
        <div className="player-awards">
          {view.awards.longestRoad === player.id && <span className="pill pill-award">Langste handelsroute</span>}
          {view.awards.largestArmy === player.id && <span className="pill pill-award">Grootste riddermacht</span>}
        </div>
      )}
    </article>
  );
}

/** A fanned stack of face-down cards with a count. */
function CardBacks({ count, kind, label }: { count: number; kind: 'resource' | 'dev'; label: string }) {
  const shown = Math.min(count, 5);
  return (
    <div className="backs" title={`${count} ${label}`}>
      <div className="backs-stack" style={{ width: 18 + Math.max(shown - 1, 0) * 6 }}>
        {shown === 0 && <span className="back back-empty" />}
        {Array.from({ length: shown }, (_, i) => (
          <span key={i} className={`back back-${kind}`} style={{ left: i * 6 }} />
        ))}
      </div>
      <span><strong>{count}</strong> {kind === 'resource' ? 'grondstof' : 'ontwikkeling'}</span>
    </div>
  );
}

function Piece({ href, color, left, label, tf }: { href: string; color: string; left: number; label: string; tf: string }) {
  return (
    <div className="piece" title={`${label} over`}>
      <svg viewBox="-40 -30 80 60"><use href={href} color={color} transform={tf} /></svg>
      <span>×{left}</span>
    </div>
  );
}
