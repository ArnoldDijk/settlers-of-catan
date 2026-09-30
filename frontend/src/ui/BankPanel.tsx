import type { PlayerView } from '../state/types';
import { RESOURCES } from '../state/selectors';
import { ResourceChip } from './ResourceChip';

export function BankPanel({ state }: { state: PlayerView }) {
  return (
    <section className="card bank">
      <div className="bank-head">
        <h3>Bank</h3>
        <span className="pill">{state.bank.devCardsLeft} ontwikkelingskaarten</span>
      </div>
      <div className="res-row">
        {RESOURCES.map(r => <ResourceChip key={r} resource={r} count={state.bank.resources[r] ?? 0} />)}
      </div>
    </section>
  );
}
