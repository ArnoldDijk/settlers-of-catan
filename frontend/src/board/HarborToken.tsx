import type { Harbor } from '../state/types';
import { HARBOR_COLORS, INK, RESOURCE_NAMES } from './palette';

/** Upright harbor token: trade ratio plus what it accepts. */
export function HarborToken({ kind }: { kind: Harbor['kind'] }) {
  const any = kind === 'any';
  return (
    <g>
      <circle r={31} fill={INK} opacity={0.25} cy={3} />
      <circle r={30} fill="#FFFFFF" stroke={any ? INK : HARBOR_COLORS[kind]} strokeWidth={6} />
      <text y={4} textAnchor="middle" fontFamily="Montserrat" fontWeight={800} fontSize={19} fill={INK}>
        {any ? '3:1' : '2:1'}
      </text>
      <text y={17} textAnchor="middle" fontFamily="Montserrat" fontWeight={700} fontSize={7} letterSpacing={0.8} fill="#6A7191">
        {any ? 'ELK' : RESOURCE_NAMES[kind].toUpperCase()}
      </text>
    </g>
  );
}
