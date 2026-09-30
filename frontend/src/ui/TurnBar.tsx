import type { PlayerView } from '../state/types';
import { PLAYER_COLORS } from '../board/palette';
import { playerById } from '../state/selectors';

const PHASES: Record<PlayerView['phase'], string> = { setup: 'Opbouwfase', playing: 'Spel bezig', finished: 'Afgelopen' };

export function TurnBar({ view }: { view: PlayerView }) {
  const current = playerById(view, view.turn.currentPlayerId);
  const winner = playerById(view, view.winnerId);
  const myTurn = view.turn.currentPlayerId === view.viewerId;
  const step = view.turn.step === 'roll' ? 'moet gooien' : 'is aan zet';
  return (
    <header className="turnbar">
      <div className="turnbar-title">
        <div className="bb-eyebrow">Beurt {view.turn.number} · {PHASES[view.phase]}</div>
        <div className="accent-bar" />
        <h1>Kolonisten van Catan</h1>
      </div>
      {current && (
        <div className={`card turnbar-current${myTurn ? ' turnbar-mine' : ''}`}>
          <span className="dot" style={{ background: PLAYER_COLORS[(winner ?? current).color] }} />
          <span>
            {winner ? <><strong>{winner.id === view.viewerId ? 'Jij hebt' : `${winner.name} heeft`}</strong> gewonnen!</>
              : myTurn ? <><strong>Jij</strong> {view.turn.step === 'roll' ? 'moet gooien' : 'bent aan zet'}</>
              : <><strong>{current.name}</strong> {step}</>}
          </span>
        </div>
      )}
    </header>
  );
}
