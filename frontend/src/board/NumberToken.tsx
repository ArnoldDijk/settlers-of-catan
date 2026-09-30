import { INK } from './palette';

interface Props {
  n: number;
  /** Yellow ring: this number was just rolled. */
  highlight?: boolean;
  /** Robber is on the tile: dimmed, never highlighted. */
  blocked?: boolean;
}

/** Number token ("getalfiche"): pips show the odds, 6 and 8 are mauve. */
export function NumberToken({ n, highlight = false, blocked = false }: Props) {
  const dots = 6 - Math.abs(7 - n);
  const ink = n === 6 || n === 8 ? '#A64F6D' : INK;
  return (
    <g opacity={blocked ? 0.4 : 1}>
      {highlight && !blocked && <circle r={38} fill="none" stroke="#F9F871" strokeWidth={7} />}
      <circle r={31} cy={3} fill={INK} opacity={0.28} />
      <circle r={30} fill="#FBF6E9" stroke={INK} strokeWidth={2.5} />
      <circle r={25.5} fill="none" stroke="#E4D9BD" strokeWidth={1.2} />
      <text y={6} textAnchor="middle" fontFamily="Montserrat" fontWeight={800} fontSize={25} fill={ink}>
        {n}
      </text>
      {Array.from({ length: dots }, (_, k) => (
        <circle key={k} cx={(k - (dots - 1) / 2) * 6} cy={17} r={2.2} fill={ink} />
      ))}
    </g>
  );
}
