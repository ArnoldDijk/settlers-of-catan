import type { PlayerView } from '../state/types';
import { diceSum } from '../state/selectors';
import { Die } from './Die';

export function DicePanel({ state }: { state: PlayerView }) {
  const sum = diceSum(state);
  const msg =
    sum == null ? 'Nog niet gegooid deze beurt.'
    : sum === 7 ? 'Zeven! De rover verhuist.'
    : `Tegels met een ${sum} leveren grondstoffen op.`;
  return (
    <section className="card dice-panel">
      <div className="dice-row">
        {state.dice ? (
          state.dice.map((v: number, i: number) => (
            <div key={i} className="die"><Die value={v} which={i as 0 | 1} /></div>
          ))
        ) : (
          <div className="die die-empty" />
        )}
      </div>
      <div className="dice-total">
        <div className="dice-sum">{sum ?? '–'}</div>
        <div>
          <div className="bb-eyebrow">Totaal</div>
          <div className="muted">{msg}</div>
        </div>
      </div>
    </section>
  );
}
