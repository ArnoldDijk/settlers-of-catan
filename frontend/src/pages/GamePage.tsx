import { useState } from 'react';
import { useGame } from '../api/useGame';
import { Board } from '../board/Board';
import { boardTargets, type HexTarget } from '../board/targets';
import { nameOf } from '../state/selectors';
import type { PlayerView } from '../state/types';
import { linkProps } from '../router';
import { ActionPanel } from '../ui/ActionPanel';
import { BankPanel } from '../ui/BankPanel';
import { Button } from '../ui/Button';
import { DicePanel } from '../ui/DicePanel';
import { HandPanel } from '../ui/HandPanel';
import { PlayerPanel } from '../ui/PlayerPanel';
import { TurnBar } from '../ui/TurnBar';

export function GamePage({ gameId }: { gameId: string }) {
  const { view, error, connection, busy, act, clearError } = useGame(gameId);
  const [steal, setSteal] = useState<HexTarget | null>(null);

  if (!view) {
    return (
      <main className="page">
        <div className="card lobby" role={error ? 'alert' : 'status'}>
          {error ? (
            <>
              <h3>Kan het spel niet laden</h3>
              <p className="muted">{error.message}</p>
              <a className="tab" {...linkProps('/')}>Nieuw spel</a>
            </>
          ) : (
            <p className="muted">Spel laden…</p>
          )}
        </div>
      </main>
    );
  }

  const targets = boardTargets(view.legalActions);
  const pickHex = (t: HexTarget) => (t.actions.length === 1 ? act(t.actions[0]) : setSteal(t));

  return (
    <main className="game">
      <TurnBar view={view} />
      {connection === 'lost' && <div className="banner" role="status">Verbinding verbroken — opnieuw verbinden…</div>}
      {error && (
        <div className="banner banner-error" role="alert">
          {error.message}
          <button type="button" className="banner-close" onClick={clearError} aria-label="Sluiten">×</button>
        </div>
      )}
      <div className="game-layout">
        <div className="board-frame">
          <Board state={view} targets={targets} disabled={busy} onAction={a => void act(a)} onHex={pickHex} />
        </div>
        <aside className="side">
          {steal && <StealPicker view={view} target={steal} onDone={() => setSteal(null)} act={act} />}
          <ActionPanel view={view} busy={busy} act={a => void act(a)} />
          <DicePanel state={view} />
          <HandPanel view={view} />
          {view.players.map(p => <PlayerPanel key={p.id} view={view} player={p} />)}
          <BankPanel state={view} />
        </aside>
      </div>
    </main>
  );
}

function StealPicker({ view, target, act, onDone }: {
  view: PlayerView;
  target: HexTarget;
  act: (a: HexTarget['actions'][number]) => Promise<void>;
  onDone: () => void;
}) {
  return (
    <section className="card actions" aria-label="Kies van wie je steelt">
      <h3>Van wie steel je?</h3>
      <div className="action-row">
        {target.actions.map(a => (
          <Button key={a.stealFrom ?? 'none'} size="sm" variant="accent"
                  onClick={() => { onDone(); void act(a); }}>
            {a.stealFrom ? nameOf(view, a.stealFrom) : 'Niemand'}
          </Button>
        ))}
        <Button size="sm" variant="ghost" onClick={onDone}>Annuleer</Button>
      </div>
    </section>
  );
}
