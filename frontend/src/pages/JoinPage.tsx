import { useEffect, useState } from 'react';
import { api, ApiError, isToken } from '../api/client';
import { linkProps, navigate } from '../router';

/** /join#<token>: trade the token for the seat cookie, then open the game. */
export function JoinPage() {
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = window.location.hash.slice(1);
    // Drop the token from the address bar and history right away.
    window.history.replaceState(null, '', '/join');
    if (!isToken(token)) {
      setError('Deze uitnodigingslink is ongeldig.');
      return;
    }
    api.join(token).then(
      ({ gameId }) => navigate(`/games/${gameId}`, true),
      err => setError(err instanceof ApiError ? err.message : 'Er ging iets mis.'),
    );
  }, []);

  return (
    <main className="page">
      <div className="card lobby" role={error ? 'alert' : 'status'}>
        {error ? (
          <>
            <h3>Aanmelden mislukt</h3>
            <p className="muted">{error}</p>
            <a className="tab" {...linkProps('/')}>Nieuw spel</a>
          </>
        ) : (
          <p className="muted">Aanmelden…</p>
        )}
      </div>
    </main>
  );
}
