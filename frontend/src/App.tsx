import { SvgDefs } from './board/SvgDefs';
import { GamePage } from './pages/GamePage';
import { JoinPage } from './pages/JoinPage';
import { Lobby } from './pages/Lobby';
import { linkProps, matchRoute, usePath } from './router';
import { TileSheet } from './tiles/TileSheet';

export function App() {
  const route = matchRoute(usePath());
  return (
    <>
      <SvgDefs />
      <nav className="tabs" aria-label="Navigatie">
        <a {...linkProps('/')} className={route.page === 'lobby' ? 'tab tab-active' : 'tab'}>Nieuw spel</a>
        {route.page === 'game' && <span className="tab tab-active">Spel</span>}
        <a {...linkProps('/tegelset')} className={route.page === 'tiles' ? 'tab tab-active' : 'tab'}>Tegelset</a>
      </nav>
      {route.page === 'lobby' && <Lobby />}
      {route.page === 'join' && <JoinPage />}
      {route.page === 'game' && <GamePage key={route.gameId} gameId={route.gameId} />}
      {route.page === 'tiles' && <TileSheet />}
      {route.page === 'notFound' && (
        <main className="page"><div className="card lobby"><p className="muted">Deze pagina bestaat niet.</p></div></main>
      )}
    </>
  );
}
