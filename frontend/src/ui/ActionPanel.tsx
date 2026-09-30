import { type ReactNode, useState } from 'react';
import type { Action, ActionOf, ActionType, PlayerView, Resource } from '../state/types';
import { RESOURCE_NAMES } from '../board/palette';
import { boardTargets } from '../board/targets';
import { nameOf, RESOURCES, tradeRates, viewer, waitingFor } from '../state/selectors';
import { Button } from './Button';
import { compact, type Counts, ResourcePicker, ResourceSelect, total } from './ResourcePicker';

interface Props {
  view: PlayerView;
  busy: boolean;
  act: (a: Action) => void;
}

const of = <T extends ActionType>(legal: Action[], type: T) =>
  legal.filter((a): a is ActionOf<T> => a.type === type);

const bundleText = (b: Record<string, number>) =>
  Object.entries(b).map(([r, n]) => `${n}× ${RESOURCE_NAMES[r as Resource].toLowerCase()}`).join(', ');

/** What the viewer can do right now. Every control is built from `legalActions`. */
export function ActionPanel({ view, busy, act }: Props) {
  const legal = view.legalActions;
  const step = view.turn.step;
  const t = boardTargets(legal);
  const onBoard = t.vertices.length + t.edges.length + t.hexes.length > 0;

  let body: ReactNode;
  if (view.phase === 'finished') {
    body = <p className="action-hint"><strong>{view.winnerId === view.viewerId ? 'Jij hebt' : `${nameOf(view, view.winnerId)} heeft`}</strong> gewonnen!</p>;
  } else if (legal.length === 0) {
    const names = waitingFor(view).map(id => nameOf(view, id)).join(', ');
    body = (
      <>
        <p className="action-hint">Wachten op <strong>{names}</strong>…</p>
        {view.trade && (
          <p className="small">
            {nameOf(view, view.trade.offerer)} biedt {bundleText(view.trade.give)} voor {bundleText(view.trade.get)}.
          </p>
        )}
      </>
    );
  } else if (view.trade && of(legal, 'respondTrade').length) {
    body = <RespondToOffer view={view} busy={busy} act={act} />;
  } else if (view.trade && view.trade.offerer === view.viewerId) {
    body = <OwnOffer view={view} busy={busy} act={act} />;
  } else if (step === 'discard') {
    body = <DiscardForm view={view} busy={busy} act={act} />;
  } else {
    body = (
      <>
        <p className="action-hint">{hintFor(step, view, onBoard)}</p>
        {step === 'moveRobber' || step.startsWith('setup') || step === 'roadBuilding' ? null : (
          <MainActions view={view} busy={busy} act={act} />
        )}
      </>
    );
  }

  return (
    <section className="card actions" aria-label="Acties" aria-busy={busy}>
      <div className="bank-head">
        <h3>Jouw zet</h3>
        {busy && <span className="small">Bezig…</span>}
      </div>
      {body}
    </section>
  );
}

function hintFor(step: PlayerView['turn']['step'], view: PlayerView, onBoard: boolean): string {
  switch (step) {
    case 'setupSettlement':
      return 'Kies op het bord een plek voor je dorp.';
    case 'setupRoad':
      return 'Leg een weg aan je nieuwe dorp.';
    case 'moveRobber':
      return 'Klik op een tegel om de rover te verplaatsen.';
    case 'roadBuilding':
      return `Leg nog ${view.roadBuildingLeft} gratis ${view.roadBuildingLeft === 1 ? 'weg' : 'wegen'}.`;
    case 'roll':
      return 'Gooi de dobbelstenen (of speel eerst een ontwikkelingskaart).';
    default:
      return onBoard ? 'Klik op een gemarkeerde plek om te bouwen, of kies hieronder.' : 'Kies wat je wilt doen.';
  }
}

function MainActions({ view, busy, act }: Props) {
  const legal = view.legalActions;
  const first = <T extends ActionType>(type: T) => of(legal, type)[0];
  const roll = first('roll');
  const buy = first('buyDevCard');
  const end = first('endTurn');
  const knight = first('playKnight');
  const roads = first('playRoadBuilding');
  const plenty = of(legal, 'playYearOfPlenty');
  const monopoly = of(legal, 'playMonopoly');
  const bank = of(legal, 'bankTrade');
  const canOffer = of(legal, 'offerTrade').length > 0;
  const [open, setOpen] = useState<'plenty' | 'monopoly' | 'bank' | 'offer' | null>(null);
  const toggle = (k: typeof open) => setOpen(o => (o === k ? null : k));

  return (
    <div className="action-stack">
      <div className="action-row">
        {roll && <Button variant="accent" disabled={busy} onClick={() => act(roll)}>Gooi de dobbelstenen</Button>}
        {buy && <Button variant="secondary" size="sm" disabled={busy} onClick={() => act(buy)}>Koop ontwikkelingskaart</Button>}
        {bank.length > 0 && <Button variant="secondary" size="sm" onClick={() => toggle('bank')}>Handel met de bank</Button>}
        {canOffer && <Button variant="secondary" size="sm" onClick={() => toggle('offer')}>Handel met spelers</Button>}
      </div>
      {(knight || roads || plenty.length > 0 || monopoly.length > 0) && (
        <div className="action-row">
          <span className="small">Speel:</span>
          {knight && <Button variant="ghost" size="sm" disabled={busy} onClick={() => act(knight)}>Ridder</Button>}
          {roads && <Button variant="ghost" size="sm" disabled={busy} onClick={() => act(roads)}>Stratenbouw</Button>}
          {plenty.length > 0 && <Button variant="ghost" size="sm" onClick={() => toggle('plenty')}>Uitvinding</Button>}
          {monopoly.length > 0 && <Button variant="ghost" size="sm" onClick={() => toggle('monopoly')}>Monopolie</Button>}
        </div>
      )}
      {open === 'bank' && <BankTradeForm view={view} options={bank} busy={busy} act={act} />}
      {open === 'offer' && <OfferForm view={view} busy={busy} act={act} />}
      {open === 'plenty' && <PlentyForm options={plenty} busy={busy} act={act} />}
      {open === 'monopoly' && <MonopolyForm options={monopoly} busy={busy} act={act} />}
      {end && (
        <div className="action-row action-end">
          <Button disabled={busy} onClick={() => act(end)}>Einde beurt</Button>
        </div>
      )}
    </div>
  );
}

function BankTradeForm({ view, options, busy, act }: { view: PlayerView; options: ActionOf<'bankTrade'>[]; busy: boolean; act: (a: Action) => void }) {
  const rates = tradeRates(view);
  const gives = RESOURCES.filter(r => options.some(o => o.give === r));
  const [give, setGive] = useState<Resource | null>(gives[0] ?? null);
  const gets = RESOURCES.filter(r => options.some(o => o.give === give && o.get === r));
  const [get, setGet] = useState<Resource | null>(null);
  const choice = options.find(o => o.give === give && o.get === get);
  return (
    <div className="subform">
      <div className="small">Geef ({give ? `${rates[give]}:1` : '—'})</div>
      <ResourceSelect label="Geef aan de bank" value={give} options={gives} onChange={r => { setGive(r); setGet(null); }} />
      <div className="small">Ontvang 1</div>
      <ResourceSelect label="Ontvang van de bank" value={get} options={gets} onChange={setGet} />
      <Button size="sm" disabled={busy || !choice} onClick={() => choice && act(choice)}>Ruil</Button>
    </div>
  );
}

function OfferForm({ view, busy, act }: Props) {
  const me = viewer(view);
  const others = view.players.filter(p => p.id !== me.id);
  const [give, setGive] = useState<Counts>({});
  const [get, setGet] = useState<Counts>({});
  const [to, setTo] = useState<string[]>(others.map(p => p.id));
  const overlap = RESOURCES.some(r => (give[r] ?? 0) > 0 && (get[r] ?? 0) > 0);
  const valid = total(give) > 0 && total(get) > 0 && !overlap && to.length > 0;
  const hand = view.hand.resources as Partial<Record<Resource, number>>;
  return (
    <div className="subform">
      <div className="small">Jij geeft</div>
      <ResourcePicker label="Jij geeft" value={give} onChange={setGive} max={hand} />
      <div className="small">Jij vraagt</div>
      <ResourcePicker label="Jij vraagt" value={get} onChange={setGet} />
      <div className="action-row" role="group" aria-label="Aan wie">
        {others.map(p => (
          <label key={p.id} className="check">
            <input type="checkbox" checked={to.includes(p.id)}
                   onChange={e => setTo(t => (e.target.checked ? [...t, p.id] : t.filter(x => x !== p.id)))} />
            {p.name}
          </label>
        ))}
      </div>
      {overlap && <div className="small form-error">Je kunt niet dezelfde grondstof geven én vragen.</div>}
      <Button size="sm" disabled={busy || !valid}
              onClick={() => act({ type: 'offerTrade', give: compact(give), get: compact(get), to })}>
        Doe voorstel
      </Button>
    </div>
  );
}

function PlentyForm({ options, busy, act }: { options: ActionOf<'playYearOfPlenty'>[]; busy: boolean; act: (a: Action) => void }) {
  const [pick, setPick] = useState<Counts>({});
  const wanted = compact(pick);
  const choice = options.find(o => JSON.stringify(Object.entries(o.resources).sort()) === JSON.stringify(Object.entries(wanted).sort()));
  return (
    <div className="subform">
      <div className="small">Kies 2 grondstoffen uit de bank</div>
      <ResourcePicker label="Uitvinding" value={pick} onChange={v => total(v) <= 2 && setPick(v)} />
      <Button size="sm" disabled={busy || !choice} onClick={() => choice && act(choice)}>Neem</Button>
    </div>
  );
}

function MonopolyForm({ options, busy, act }: { options: ActionOf<'playMonopoly'>[]; busy: boolean; act: (a: Action) => void }) {
  const [res, setRes] = useState<Resource | null>(null);
  const choice = options.find(o => o.resource === res);
  return (
    <div className="subform">
      <div className="small">Iedereen geeft jou al zijn kaarten van:</div>
      <ResourceSelect label="Monopolie" value={res} onChange={setRes} />
      <Button size="sm" disabled={busy || !choice} onClick={() => choice && act(choice)}>Speel monopolie</Button>
    </div>
  );
}

function DiscardForm({ view, busy, act }: Props) {
  const need = view.pendingDiscards[view.viewerId] ?? 0;
  const hand = view.hand.resources as Partial<Record<Resource, number>>;
  const [pick, setPick] = useState<Counts>({});
  return (
    <div className="subform">
      <p className="action-hint">Zeven! Leg <strong>{need}</strong> kaarten af ({total(pick)}/{need}).</p>
      <ResourcePicker label="Afleggen" value={pick} onChange={setPick} max={hand} />
      <Button variant="accent" disabled={busy || total(pick) !== need}
              onClick={() => act({ type: 'discard', resources: compact(pick) })}>
        Leg af
      </Button>
    </div>
  );
}

function RespondToOffer({ view, busy, act }: Props) {
  const t = view.trade!;
  const accept = of(view.legalActions, 'respondTrade').find(a => a.accept);
  return (
    <div className="subform">
      <p className="action-hint">
        <strong>{nameOf(view, t.offerer)}</strong> biedt {bundleText(t.give)} voor {bundleText(t.get)}.
      </p>
      <div className="action-row">
        <Button variant="accent" size="sm" disabled={busy || !accept} onClick={() => accept && act(accept)}>Accepteer</Button>
        <Button variant="secondary" size="sm" disabled={busy} onClick={() => act({ type: 'respondTrade', accept: false })}>Weiger</Button>
      </div>
      {!accept && <div className="small">Je hebt niet genoeg kaarten om te accepteren.</div>}
    </div>
  );
}

function OwnOffer({ view, busy, act }: Props) {
  const t = view.trade!;
  const confirms = of(view.legalActions, 'confirmTrade');
  return (
    <div className="subform">
      <p className="action-hint">Je biedt {bundleText(t.give)} voor {bundleText(t.get)}.</p>
      <ul className="responses">
        {Object.entries(t.responses).map(([id, answer]) => (
          <li key={id}>
            {nameOf(view, id)}: {answer === null ? 'denkt na…' : answer ? 'accepteert' : 'weigert'}
            {confirms.some(c => c.withPlayer === id) && (
              <Button size="sm" variant="accent" disabled={busy}
                      onClick={() => act({ type: 'confirmTrade', withPlayer: id })} style={{ marginLeft: 8 }}>
                Ruil met {nameOf(view, id)}
              </Button>
            )}
          </li>
        ))}
      </ul>
      <Button variant="secondary" size="sm" disabled={busy} onClick={() => act({ type: 'cancelTrade' })}>Trek voorstel in</Button>
    </div>
  );
}
