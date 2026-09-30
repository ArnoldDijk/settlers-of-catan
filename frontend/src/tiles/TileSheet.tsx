import { useEffect, useRef, useState, type ReactNode } from 'react';
import type { Building, Corner, EdgeIx, Harbor, PlayerColor, Resource, Road, Terrain } from '../state/types';
import { HEX_PATH } from '../board/geometry';
import { HarborToken } from '../board/HarborToken';
import { Hex } from '../board/Hex';
import { NumberToken } from '../board/NumberToken';
import { CARD_COLORS, INK, PLAYER_COLORS, RESOURCE_NAMES, RESOURCE_TERRAIN } from '../board/palette';
import { BuildingPiece, RoadPiece } from '../board/Pieces';
import { Robber } from '../board/Robber';
import { Button } from '../ui/Button';
import { Die } from '../ui/Die';

// Port of the Claude Design file "Catan Tiles.dc.html" — the tile-set reference sheet.

const TERRAINS: { terrain: Terrain | 'sea'; name: string; resource: string; count: string }[] = [
  { terrain: 'forest', name: 'Bos', resource: 'Levert hout', count: '×4' },
  { terrain: 'hills', name: 'Heuvels', resource: 'Levert stenen', count: '×3' },
  { terrain: 'pasture', name: 'Weiland', resource: 'Levert wol', count: '×4' },
  { terrain: 'fields', name: 'Akkers', resource: 'Levert graan', count: '×4' },
  { terrain: 'mountains', name: 'Gebergte', resource: 'Levert erts', count: '×3' },
  { terrain: 'desert', name: 'Woestijn', resource: 'Geen grondstof · startplek rover', count: '×1' },
  { terrain: 'sea', name: 'Zee', resource: 'Rand · basis voor havens', count: '×18' },
];

const HARBORS: { kind: Harbor['kind']; name: string; count: string }[] = [
  { kind: 'any', name: 'Algemeen', count: '×4' },
  { kind: 'lumber', name: 'Hout', count: '×1' },
  { kind: 'brick', name: 'Stenen', count: '×1' },
  { kind: 'wool', name: 'Wol', count: '×1' },
  { kind: 'grain', name: 'Graan', count: '×1' },
  { kind: 'ore', name: 'Erts', count: '×1' },
];

const TOKENS = [2, 3, 4, 5, 6, 8, 9, 10, 11, 12];
const RESOURCES: Resource[] = ['lumber', 'brick', 'wool', 'grain', 'ore'];
const SHEET_PLAYERS: { color: PlayerColor; name: string }[] = [
  { color: 'red', name: 'Speler rood' },
  { color: 'blue', name: 'Speler blauw' },
  { color: 'orange', name: 'Speler oranje' },
  { color: 'white', name: 'Speler wit' },
];

// The 7-tile test cluster from the design.
const CLUSTER_LAND: [number, number, Terrain, number][] = [
  [0, 0, 'fields', 9], [1, 0, 'forest', 6], [1, -1, 'hills', 4], [0, -1, 'mountains', 10],
  [-1, 0, 'pasture', 8], [-1, 1, 'desert', 0], [0, 1, 'forest', 3],
];
const CLUSTER_SEA: [number, number][] = [
  [2, 0], [2, -1], [2, -2], [1, -2], [0, -2], [-1, -1], [-2, 0], [-2, 1], [-2, 2], [-1, 2], [0, 2], [1, 1],
];
const CLUSTER_HARBORS: Harbor[] = [
  { q: 2, r: -2, edge: 3, kind: 'any' }, { q: 0, r: -2, edge: 2, kind: 'wool' }, { q: -2, r: 0, edge: 1, kind: 'any' },
  { q: -2, r: 2, edge: 0, kind: 'ore' }, { q: 0, r: 2, edge: 5, kind: 'grain' }, { q: 2, r: 0, edge: 4, kind: 'lumber' },
];
const road = (q: number, r: number, edge: EdgeIx, owner: PlayerColor): Road => ({ owner, at: { q, r, edge } });
const bld = (kind: Building['kind'], q: number, r: number, corner: Corner, owner: PlayerColor): Building => ({ owner, kind, at: { q, r, corner } });
const CLUSTER_ROADS: Road[] = [
  road(0, 0, 0, 'red'), road(0, 0, 1, 'red'), road(-1, 0, 0, 'blue'), road(-1, 0, 5, 'blue'), road(-1, 1, 3, 'blue'),
  road(1, -1, 1, 'orange'), road(1, -1, 2, 'orange'), road(0, 1, 1, 'orange'), road(0, -1, 4, 'white'), road(0, -1, 5, 'white'), road(1, 0, 3, 'white'),
];
const CLUSTER_BUILDINGS: Building[] = [
  bld('city', 0, 0, 0, 'red'), bld('settlement', 0, 0, 2, 'red'), bld('settlement', -1, 0, 0, 'blue'), bld('city', -1, 1, 3, 'blue'),
  bld('settlement', 1, -1, 1, 'orange'), bld('city', 0, 1, 1, 'orange'), bld('settlement', 0, -1, 5, 'white'), bld('settlement', 1, 0, 3, 'white'),
];

const DEV_CARDS = [
  { title: 'Ridder', text: 'Verplaats de rover en steel één grondstof van een speler bij die tegel.', count: '×14', art: <KnightArt /> },
  { title: 'Stratenbouw', text: 'Bouw meteen twee wegen, zonder grondstoffen te betalen.', count: '×2', art: <RoadBuildingArt /> },
  { title: 'Uitvinding', text: 'Neem twee grondstoffen naar keuze uit de voorraad.', count: '×2', art: <InventionArt /> },
  { title: 'Monopolie', text: 'Noem een grondstof. Iedereen geeft jou al zijn kaarten van die soort.', count: '×2', art: <MonopolyArt /> },
  { title: 'Overwinningspunt', text: 'Houd deze kaart geheim. Hij telt als één overwinningspunt.', count: '×5', art: <VictoryPointArt /> },
];

interface DieAnim { v: number; x: number; y: number; rot: number; h: number }

function useDiceRoll() {
  const [dice, setDice] = useState<DieAnim[]>([
    { v: 3, x: 40, y: 50, rot: -8, h: 0 },
    { v: 4, x: 60, y: 48, rot: 12, h: 0 },
  ]);
  const [rolling, setRolling] = useState(false);
  const [sum, setSum] = useState<number | null>(null);
  const [robber, setRobber] = useState(5);
  const raf = useRef(0);
  useEffect(() => () => cancelAnimationFrame(raf.current), []);

  const roll = () => {
    if (rolling) return;
    const r6 = () => 1 + Math.floor(Math.random() * 6);
    const final = [r6(), r6()];
    const paths = final.map((_, i) => ({
      x0: -12 - i * 6, y0: 30 + Math.random() * 40,
      x1: 38 + i * 22 + (Math.random() - 0.5) * 10, y1: 42 + (Math.random() - 0.5) * 24,
      r0: Math.random() * 360, spin: (540 + Math.random() * 540) * (i ? -1 : 1),
      delay: i * 70,
    }));
    const start = performance.now();
    const D = 1500;
    let lastFace = 0;
    let faces = [r6(), r6()];
    setRolling(true);
    setSum(null);
    const frame = (now: number) => {
      const el = now - start;
      if (el - lastFace > 70 + el / 12) { faces = [r6(), r6()]; lastFace = el; }
      const next = paths.map((p, i) => {
        const t = Math.max(0, Math.min(1, (el - p.delay) / D));
        const ease = 1 - Math.pow(1 - t, 3);
        const h = Math.abs(Math.sin(Math.PI * 3 * Math.pow(t, 0.55))) * Math.pow(1 - t, 1.3);
        return { v: t < 0.82 ? faces[i] : final[i], x: p.x0 + (p.x1 - p.x0) * ease, y: p.y0 + (p.y1 - p.y0) * ease, rot: p.r0 + p.spin * ease, h };
      });
      if (el < D + 70) {
        setDice(next);
        raf.current = requestAnimationFrame(frame);
      } else {
        const total = final[0] + final[1];
        setDice(next.map((d, i) => ({ ...d, v: final[i], h: 0 })));
        setRolling(false);
        setSum(total);
        if (total === 7) setRobber(cur => [0, 1, 2, 3, 4, 5, 6].filter(i => i !== cur)[Math.floor(Math.random() * 6)]);
      }
    };
    raf.current = requestAnimationFrame(frame);
  };
  return { dice, rolling, sum, robber, roll };
}

export function TileSheet() {
  const { dice, rolling, sum, robber, roll } = useDiceRoll();
  const rollMsg = rolling ? 'De dobbelstenen rollen…'
    : sum == null ? 'Klik op de knop om te gooien.'
    : sum === 7 ? 'Zeven! De rover verhuist naar een andere tegel.'
    : `Alle tegels met een ${sum} leveren grondstoffen op.`;
  const [rq, rr] = CLUSTER_LAND[robber];

  return (
    <div className="sheet">
      <header className="sheet-header">
        <div className="bb-eyebrow">Tegelset · 01</div>
        <div className="accent-bar" />
        <h1 className="sheet-title">Landschapstegels &amp; havens</h1>
        <p className="sheet-lead">
          Zeshoekige SVG-tegels met de punt naar boven, één <code className="code">&lt;g id="t-*"&gt;</code> per landschap.
          Details liggen langs de rand, zodat het midden vrij blijft voor het getalfiche.
        </p>
      </header>

      <Section title="Landschappen">
        <div className="grid" style={{ ['--min' as string]: '210px' }}>
          {TERRAINS.map(t => (
            <div key={t.terrain} className="card card-lift sheet-card">
              <TileSvg terrain={t.terrain}>
                <path d={HEX_PATH} transform="scale(0.955)" fill="none" stroke="#FFFFFF" strokeOpacity={0.28} strokeWidth={3} />
              </TileSvg>
              <Caption name={t.name} sub={t.resource} count={t.count} />
            </div>
          ))}
        </div>
      </Section>

      <Section title="Havens" lead={<>Zeetegel met steiger erbovenop. De steiger wijst standaard naar de linkerrand; draai de groep <code className="code">#dock</code> in stappen van 60° naar elke landrand. Het fiche blijft rechtop staan.</>}>
        <div className="grid" style={{ ['--min' as string]: '170px' }}>
          {HARBORS.map(h => (
            <div key={h.kind} className="card sheet-card">
              <TileSvg terrain="sea">
                <use href="#dock" />
                <HarborToken kind={h.kind} />
              </TileSvg>
              <Caption name={h.name} count={h.count} />
            </div>
          ))}
        </div>
      </Section>

      <Section title="Getalfiches" lead="Eén fiche per landtegel, behalve de woestijn. De stipjes tonen hoe vaak het getal valt; 6 en 8 komen het vaakst en zijn daarom rood.">
        <div className="grid" style={{ ['--min' as string]: '104px' }}>
          {TOKENS.map(n => (
            <div key={n} className="card token-card">
              <svg viewBox="-44 -44 88 88" style={{ width: '100%', maxWidth: 88, display: 'block' }}>
                <NumberToken n={n} highlight={sum === n} />
              </svg>
              <div className="token-meta">
                <span className="pill">{n === 2 || n === 12 ? '×1' : '×2'}</span>
                <span className="muted small">{6 - Math.abs(7 - n)}/36</span>
              </div>
            </div>
          ))}
        </div>
      </Section>

      <Section title="Wegen, dorpen & steden" lead={<>Eén set vormen per stuk, gekleurd via <code className="code">currentColor</code> — zet <code className="code">color</code> op de <code className="code">&lt;use&gt;</code> voor de spelerskleur. Wegen liggen op randen, dorpen en steden op hoekpunten.</>}>
        <div className="grid" style={{ ['--min' as string]: '260px' }}>
          {SHEET_PLAYERS.map(p => (
            <div key={p.color} className="card sheet-card">
              <div className="player-head">
                <span className="dot" style={{ background: PLAYER_COLORS[p.color] }} />
                <div className="player-name">{p.name}</div>
              </div>
              <div className="piece-grid">
                <PieceTile href="#p-road" color={PLAYER_COLORS[p.color]} tf="rotate(-30)" label="Weg" count="×15" />
                <PieceTile href="#p-settlement" color={PLAYER_COLORS[p.color]} tf="scale(1.35)" label="Dorp" count="×5" />
                <PieceTile href="#p-city" color={PLAYER_COLORS[p.color]} tf="translate(0,2) scale(1.1)" label="Stad" count="×4" />
              </div>
            </div>
          ))}
        </div>
      </Section>

      <Section title="De rover" lead="Begint in de woestijn. Na een 7 of een ridderkaart verhuist hij; de tegel waar hij staat levert niets op, dus het fiche wordt gedimd.">
        <div className="grid" style={{ ['--min' as string]: '210px' }}>
          <div className="card sheet-card">
            <div className="robber-solo">
              <svg viewBox="-40 -40 80 80" style={{ width: '62%', display: 'block' }}>
                <use href="#p-robber" transform="translate(0,6) scale(1.2)" />
              </svg>
            </div>
            <Caption name="Rover" sub="Eén stuk, neutraal" />
          </div>
          <div className="card sheet-card">
            <TileSvg terrain="desert"><use href="#p-robber" transform="translate(0,-4) scale(1.6)" /></TileSvg>
            <Caption name="Startpositie" sub="Midden op de woestijn" />
          </div>
          <div className="card sheet-card">
            <TileSvg terrain="forest">
              <NumberToken n={6} blocked />
              <use href="#p-robber" transform="translate(26,-8) scale(1.5)" />
            </TileSvg>
            <Caption name="Blokkeert een tegel" sub="Fiche gedimd · geen opbrengst" />
          </div>
        </div>
      </Section>

      <Section title="Grondstofkaarten" lead="De illustratie komt uit dezelfde tegel, zodat kaart en landschap meteen bij elkaar horen. 19 kaarten per grondstof.">
        <div className="grid" style={{ ['--min' as string]: '160px' }}>
          {RESOURCES.map(r => (
            <div key={r} className="game-card game-card-lift">
              <div className="game-card-art" style={{ background: CARD_COLORS[r] }}>
                <svg viewBox="-55 -55 110 110" preserveAspectRatio="xMidYMid slice"><use href={`#t-${RESOURCE_TERRAIN[r]}`} /></svg>
              </div>
              <div className="game-card-foot">
                <div className="game-card-name">{RESOURCE_NAMES[r]}</div>
                <div className="swatch" style={{ background: CARD_COLORS[r] }} />
              </div>
            </div>
          ))}
          <CardBack bg={INK} inner="#A64F6D" label="GRONDSTOF" />
        </div>
      </Section>

      <Section title="Ontwikkelingskaarten" lead="25 kaarten in één pruimkleurige familie, zodat ze nooit met grondstoffen verward worden.">
        <div className="grid" style={{ ['--min' as string]: '160px' }}>
          {DEV_CARDS.map(c => (
            <div key={c.title} className="game-card game-card-lift dev-card">
              <div className="dev-card-title">{c.title}</div>
              <div className="dev-card-art">{c.art}</div>
              <div className="dev-card-text">{c.text}</div>
              <div className="dev-card-count">{c.count}</div>
            </div>
          ))}
          <CardBack bg="#5C3660" inner={INK} label="ONTWIKKELING" star />
        </div>
      </Section>

      <Section title="Dobbelstenen" lead="Twee dobbelstenen, wit en oranje. Gooi ze en de getalfiches met jouw totaal lichten op, hierboven en op het bord eronder.">
        <div className="dice-tray">
          <div className="dice-tray-inner" />
          {dice.map((d, i) => (
            <div key={i}>
              <div
                className="tray-die-shadow"
                style={{
                  left: `${d.x}%`, top: `${d.y}%`,
                  transform: `translate(-50%,-50%) translate(${d.h * 14}px,${d.h * 18}px) rotate(${d.rot}deg) scale(${1 + d.h * 0.2})`,
                  filter: `blur(${2 + d.h * 10}px)`,
                }}
              />
              <div
                className="tray-die"
                style={{
                  left: `${d.x}%`, top: `${d.y}%`,
                  transform: `translate(-50%,-50%) translate(${-d.h * 10}px,${-d.h * 26}px) rotate(${d.rot}deg) scale(${1 + d.h * 0.45})`,
                }}
              >
                <Die value={d.v} which={i as 0 | 1} stroke="#0B1128" />
              </div>
            </div>
          ))}
        </div>
        <div className="card roll-bar">
          <div className="dice-total">
            <div className="dice-sum">{sum ?? '–'}</div>
            <div>
              <div className="bb-eyebrow">Totaal</div>
              <div className="muted">{rollMsg}</div>
            </div>
          </div>
          <Button size="lg" onClick={roll} disabled={rolling}>Gooi de dobbelstenen</Button>
        </div>
        <div className="grid" style={{ ['--min' as string]: '64px', gap: 12 }}>
          {([0, 1] as const).flatMap(which => [1, 2, 3, 4, 5, 6].map(v => (
            <div key={`${which}${v}`} style={{ aspectRatio: '1' }}><Die value={v} which={which} /></div>
          )))}
        </div>
      </Section>

      <Section title="Aansluiting controleren" lead="Tegels op het axiale raster — afstand 173,2 × 150 bij R = 100.">
        <div className="board-frame">
          <svg viewBox="-450 -415 900 830" style={{ width: '100%', maxWidth: 760, height: 'auto', display: 'block', margin: '0 auto' }}>
            {CLUSTER_LAND.map(([q, r, t, n], i) => (
              <Hex key={`l${q},${r}`} at={{ q, r }} terrain={t}>
                {n > 0 && <NumberToken n={n} highlight={sum === n} blocked={i === robber} />}
              </Hex>
            ))}
            {CLUSTER_SEA.map(([q, r]) => {
              const h = CLUSTER_HARBORS.find(hb => hb.q === q && hb.r === r);
              return (
                <Hex key={`s${q},${r}`} at={{ q, r }} terrain="sea">
                  {h && (
                    <>
                      <g transform={`rotate(${60 * (h.edge - 4)})`}><use href="#dock" /></g>
                      <HarborToken kind={h.kind} />
                    </>
                  )}
                </Hex>
              );
            })}
            {CLUSTER_ROADS.map((rd, i) => <RoadPiece key={i} road={rd} color={PLAYER_COLORS[rd.owner as PlayerColor]} />)}
            {CLUSTER_BUILDINGS.map((b, i) => <BuildingPiece key={i} building={b} color={PLAYER_COLORS[b.owner as PlayerColor]} />)}
            <Robber at={{ q: rq, r: rr }} />
          </svg>
        </div>
      </Section>
    </div>
  );
}

function Section({ title, lead, children }: { title: string; lead?: ReactNode; children: ReactNode }) {
  return (
    <section className="sheet-section">
      <div className="sheet-section-head">
        <h2>{title}</h2>
        {lead && <p className="muted">{lead}</p>}
      </div>
      {children}
    </section>
  );
}

function TileSvg({ terrain, children }: { terrain: Terrain | 'sea'; children?: ReactNode }) {
  return (
    <svg viewBox="-92 -106 184 212" style={{ width: '100%', height: 'auto', display: 'block' }}>
      <use href={`#t-${terrain}`} />
      {children}
      <path d={HEX_PATH} fill="none" stroke={INK} strokeWidth={3} strokeLinejoin="round" />
    </svg>
  );
}

function Caption({ name, sub, count }: { name: string; sub?: string; count?: string }) {
  return (
    <div className="caption">
      <div>
        <div className="caption-name">{name}</div>
        {sub && <div className="muted small">{sub}</div>}
      </div>
      {count && <span className="pill">{count}</span>}
    </div>
  );
}

function PieceTile({ href, color, tf, label, count }: { href: string; color: string; tf: string; label: string; count: string }) {
  return (
    <div className="piece-tile">
      <svg viewBox="-40 -30 80 60"><use href={href} color={color} transform={tf} /></svg>
      <div className="piece-tile-label">{label}</div>
      <div className="muted small">{count}</div>
    </div>
  );
}

function CardBack({ bg, inner, label, star = false }: { bg: string; inner: string; label: string; star?: boolean }) {
  return (
    <div className="game-card card-back" style={{ background: bg }}>
      <div className="card-back-inner">
        <svg viewBox="-60 -60 120 120" style={{ width: '56%', display: 'block' }}>
          <path d="M0,-50 L43.3,-25 L43.3,25 L0,50 L-43.3,25 L-43.3,-25 Z" fill="none" stroke="#F9F871" strokeWidth="4" />
          <path d="M0,-34 L29.4,-17 L29.4,17 L0,34 L-29.4,17 L-29.4,-17 Z" fill={inner} stroke="#FFFFFF" strokeWidth="2" />
          {star
            ? <path d="M0,-18 L4.5,-5 H18 L7,3 L11,17 L0,8 L-11,17 L-7,3 L-18,-5 H-4.5 Z" fill="#F9F871" />
            : <path d="M0,-34 L29.4,-17 L0,0 Z" fill="#FFFFFF" opacity="0.2" />}
        </svg>
        <div className="card-back-label">{label}</div>
      </div>
    </div>
  );
}

// --- Development card illustrations (verbatim from the design) ---

function KnightArt() {
  return (
    <svg viewBox="-50 -50 100 100">
      <circle r="46" fill="#ECE4EE" />
      <path d="M-30,32 L28,-26" stroke="#A9AEC4" strokeWidth="7" strokeLinecap="round" /><path d="M-30,32 L28,-26" stroke="#E4E6EE" strokeWidth="2" />
      <path d="M-26,18 L-14,30" stroke="#5C3A2E" strokeWidth="6" strokeLinecap="round" />
      <path d="M0,-30 L25,-21 V1 Q25,23 0,34 Q-25,23 -25,1 V-21 Z" fill="#A64F6D" stroke="#161E3C" strokeWidth="3" strokeLinejoin="round" />
      <path d="M0,-30 L25,-21 V1 Q25,23 0,34 Z" fill="#161E3C" opacity="0.18" />
      <path d="M0,-22 V26 M-17,-2 H17" stroke="#F9F871" strokeWidth="5" />
    </svg>
  );
}

function RoadBuildingArt() {
  return (
    <svg viewBox="-50 -50 100 100">
      <circle r="46" fill="#ECE4EE" />
      <path d="M0,-40 L34.6,-20 L34.6,20 L0,40 L-34.6,20 L-34.6,-20 Z" fill="none" stroke="#A9AEC4" strokeWidth="2" strokeDasharray="4 4" />
      <use href="#p-road" color="#FFB35E" transform="translate(-17.3,-30) rotate(-30) scale(0.55)" />
      <use href="#p-road" color="#FFB35E" transform="translate(17.3,-30) rotate(30) scale(0.55)" />
      <circle cy="-40" r="5" fill="#FFFFFF" stroke="#161E3C" strokeWidth="2" />
      <path d="M-14,8 H14 M0,-6 V22" stroke="#5C3660" strokeWidth="7" strokeLinecap="round" />
    </svg>
  );
}

function InventionArt() {
  return (
    <svg viewBox="-50 -50 100 100">
      <circle r="46" fill="#ECE4EE" />
      <g transform="translate(-6,4)" fill="#6D8AF5" stroke="#161E3C" strokeWidth="2.5" strokeLinejoin="round">
        {[0, 45, 90, 135, 180, 225, 270, 315].map(a => (
          <rect key={a} x="-5" y="-30" width="10" height="12" rx="2" transform={`rotate(${a})`} />
        ))}
        <circle r="21" />
      </g>
      <circle cx="-6" cy="4" r="8" fill="#ECE4EE" stroke="#161E3C" strokeWidth="2.5" />
      <path d="M-6,-17 A21,21 0 0 1 13,-4" fill="none" stroke="#FFFFFF" strokeWidth="3" strokeLinecap="round" opacity="0.6" />
      <g transform="translate(24,-24)">
        <circle r="11" fill="#F9F871" stroke="#161E3C" strokeWidth="2.5" />
        <path d="M0,-5 V5 M-5,0 H5" stroke="#161E3C" strokeWidth="2.5" strokeLinecap="round" />
      </g>
    </svg>
  );
}

function MonopolyArt() {
  return (
    <svg viewBox="-50 -50 100 100">
      <circle r="46" fill="#ECE4EE" />
      <g stroke="#161E3C" strokeWidth="2.5" strokeLinejoin="round">
        <rect x="-13" y="-26" width="26" height="36" rx="4" fill="#E3A73A" transform="rotate(-22 0 18)" />
        <rect x="-13" y="-26" width="26" height="36" rx="4" fill="#EDB94A" transform="rotate(-7 0 18)" />
        <rect x="-13" y="-26" width="26" height="36" rx="4" fill="#F2C14E" transform="rotate(8 0 18)" />
        <rect x="-13" y="-26" width="26" height="36" rx="4" fill="#F7CF62" transform="rotate(23 0 18)" />
      </g>
      <use href="#sheaf" transform="translate(9,-10) rotate(23) scale(0.7)" />
      <path d="M-30,30 Q0,40 30,30" fill="none" stroke="#5C3660" strokeWidth="5" strokeLinecap="round" />
      <path d="M22,24 L30,30 L22,36" fill="none" stroke="#5C3660" strokeWidth="5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function VictoryPointArt() {
  return (
    <svg viewBox="-50 -50 100 100">
      <circle r="46" fill="#ECE4EE" />
      <path d="M-30,22 H30 L26,32 H-26 Z" fill="#A9AEC4" stroke="#161E3C" strokeWidth="2.5" strokeLinejoin="round" />
      <use href="#p-city" color="#F9F871" transform="translate(0,-2) scale(1.05)" />
      <g transform="translate(26,-26)">
        <circle r="12" fill="#A64F6D" stroke="#161E3C" strokeWidth="2.5" />
        <path d="M-5,0 H5 M0,-5 V5" stroke="#FFFFFF" strokeWidth="3" strokeLinecap="round" />
      </g>
    </svg>
  );
}
