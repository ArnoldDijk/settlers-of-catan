import type { DevCards, PlayerView } from '../state/types';
import { PLAYER_COLORS } from '../board/palette';
import { cardsInHand, devCardsInHand, RESOURCES, viewer } from '../state/selectors';
import { ResourceChip } from './ResourceChip';

const DEV_NAMES: Record<keyof DevCards, string> = {
  knight: 'Ridder',
  roadBuilding: 'Stratenbouw',
  yearOfPlenty: 'Uitvinding',
  monopoly: 'Monopolie',
  victoryPoint: 'Overwinningspunt',
};

/** The viewer's own, secret cards. */
export function HandPanel({ view }: { view: PlayerView }) {
  const me = viewer(view);
  const { hand } = view;
  const fresh = devCardsInHand({ devCards: hand.newDevCards });
  return (
    <section className="card hand" style={{ borderTop: `6px solid ${PLAYER_COLORS[me.color]}` }}>
      <div className="bank-head">
        <h3>Jouw hand</h3>
        <span className="small">Alleen zichtbaar voor jou</span>
      </div>
      <div className="res-row">
        {RESOURCES.map(r => <ResourceChip key={r} resource={r} count={hand.resources[r] ?? 0} />)}
      </div>
      <div className="small">{cardsInHand(hand)} grondstofkaarten · {devCardsInHand(hand)} ontwikkelingskaarten</div>
      {devCardsInHand(hand) > 0 && (
        <div className="dev-list">
          {(Object.keys(DEV_NAMES) as (keyof DevCards)[])
            .filter(k => hand.devCards[k] > 0)
            .map(k => (
              <span key={k} className="dev-chip">
                {DEV_NAMES[k]} <strong>×{hand.devCards[k]}</strong>
              </span>
            ))}
        </div>
      )}
      {fresh > 0 && <div className="small">{fresh} deze beurt gekocht: speelbaar vanaf je volgende beurt.</div>}
    </section>
  );
}
