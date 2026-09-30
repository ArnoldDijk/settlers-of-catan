const PIPS: Record<number, [number, number][]> = {
  1: [[50, 50]],
  2: [[27, 27], [73, 73]],
  3: [[27, 27], [50, 50], [73, 73]],
  4: [[27, 27], [73, 27], [27, 73], [73, 73]],
  5: [[27, 27], [73, 27], [50, 50], [27, 73], [73, 73]],
  6: [[27, 27], [73, 27], [27, 50], [73, 50], [27, 73], [73, 73]],
};

/** The two dice from the design: white and orange. */
export const DIE_STYLES = [
  { fill: '#FFFFFF', pip: '#161E3C' },
  { fill: '#FFB35E', pip: '#161E3C' },
] as const;

interface Props {
  value: number;
  /** 0 = white die, 1 = orange die. */
  which?: 0 | 1;
  stroke?: string;
}

export function Die({ value, which = 0, stroke = '#161E3C' }: Props) {
  const { fill, pip } = DIE_STYLES[which];
  return (
    <svg viewBox="0 0 100 100" style={{ width: '100%', height: '100%', display: 'block', overflow: 'visible' }}>
      <rect x="4" y="4" width="92" height="92" rx="20" fill={fill} stroke={stroke} strokeWidth="4" />
      <rect x="12" y="10" width="76" height="28" rx="13" fill="#FFFFFF" opacity="0.3" />
      {PIPS[value].map(([x, y], i) => <circle key={i} cx={x} cy={y} r="9" fill={pip} />)}
    </svg>
  );
}
