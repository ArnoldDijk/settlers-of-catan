import { type FormEvent, useState } from 'react';
import { api, ApiError } from '../api/client';
import { PLAYER_COLORS } from '../board/palette';
import type { CreateGameResponse } from '../state/types';
import { Button } from '../ui/Button';

/** Start a game: enter 2–4 names, get one personal invite link per player. */
export function Lobby() {
  const [names, setNames] = useState(['', '', '', '']);
  const [created, setCreated] = useState<CreateGameResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const players = names.map(n => n.trim()).filter(Boolean);

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      setCreated(await api.createGame(players));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Er ging iets mis.');
    } finally {
      setBusy(false);
    }
  };

  return (
    <main className="page">
      <header className="turnbar-title">
        <div className="bb-eyebrow">Nieuw spel</div>
        <div className="accent-bar" />
        <h1 className="page-title">Kolonisten van Catan</h1>
      </header>

      {!created ? (
        <form className="card lobby" onSubmit={submit}>
          <h3>Wie speelt er mee?</h3>
          <p className="muted">Vul 2 tot 4 namen in. Elke speler krijgt een eigen uitnodigingslink.</p>
          {names.map((n, i) => (
            <label key={i} className="field">
              <span>Speler {i + 1}</span>
              <input value={n} maxLength={24} autoComplete="off" placeholder={i < 2 ? 'Naam' : 'Naam (optioneel)'}
                     onChange={e => setNames(ns => ns.map((x, j) => (j === i ? e.target.value : x)))} />
            </label>
          ))}
          {error && <div className="form-error" role="alert">{error}</div>}
          <Button type="submit" variant="accent" disabled={busy || players.length < 2}>Maak spel</Button>
        </form>
      ) : (
        <section className="card lobby">
          <h3>Deel de links</h3>
          <p className="muted">
            Stuur elke speler zijn eigen link. Open een link in de browser van die speler — wie meerdere spelers op één
            computer test, gebruikt per speler een apart (privé)venster.
          </p>
          <ul className="seats">
            {created.seats.map(s => {
              const url = `${window.location.origin}${s.joinUrl}`;
              return (
                <li key={s.playerId} className="seat">
                  <span className="dot" style={{ background: PLAYER_COLORS[s.color] }} />
                  <strong>{s.name}</strong>
                  <input className="seat-link" readOnly value={url} aria-label={`Link voor ${s.name}`}
                         onFocus={e => e.target.select()} />
                  <Button size="sm" variant="secondary" onClick={() => void navigator.clipboard?.writeText(url)}>Kopieer</Button>
                  <a className="tab" href={url}>Open</a>
                </li>
              );
            })}
          </ul>
        </section>
      )}
    </main>
  );
}
