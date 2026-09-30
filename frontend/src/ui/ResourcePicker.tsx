import type { Resource } from '../state/types';
import { CARD_COLORS, RESOURCE_NAMES, RESOURCE_TERRAIN } from '../board/palette';
import { RESOURCES } from '../state/selectors';

export type Counts = Partial<Record<Resource, number>>;

export const total = (c: Counts) => RESOURCES.reduce((n, r) => n + (c[r] ?? 0), 0);

/** Only the non-zero entries, as the API expects. */
export const compact = (c: Counts): Record<string, number> =>
  Object.fromEntries(RESOURCES.filter(r => (c[r] ?? 0) > 0).map(r => [r, c[r]!]));

interface Props {
  value: Counts;
  onChange: (next: Counts) => void;
  /** Upper bound per resource (e.g. what's in your hand). */
  max?: Partial<Record<Resource, number>>;
  label: string;
}

/** A row of resource steppers. */
export function ResourcePicker({ value, onChange, max, label }: Props) {
  const set = (r: Resource, n: number) => onChange({ ...value, [r]: Math.max(0, n) });
  return (
    <div className="picker" role="group" aria-label={label}>
      {RESOURCES.map(r => {
        const n = value[r] ?? 0;
        const limit = max?.[r] ?? 19;
        return (
          <div key={r} className="picker-item">
            <div className="res-chip-art picker-art" style={{ background: CARD_COLORS[r] }} aria-hidden="true">
              <svg viewBox="-55 -55 110 110" preserveAspectRatio="xMidYMid slice">
                <use href={`#t-${RESOURCE_TERRAIN[r]}`} />
              </svg>
            </div>
            <div className="picker-name">{RESOURCE_NAMES[r]}</div>
            <div className="stepper">
              <button type="button" onClick={() => set(r, n - 1)} disabled={n === 0} aria-label={`Minder ${RESOURCE_NAMES[r]}`}>−</button>
              <span aria-live="polite">{n}</span>
              <button type="button" onClick={() => set(r, n + 1)} disabled={n >= limit} aria-label={`Meer ${RESOURCE_NAMES[r]}`}>+</button>
            </div>
          </div>
        );
      })}
    </div>
  );
}

/** Pick one resource. */
export function ResourceSelect({ value, onChange, options = RESOURCES, label }: {
  value: Resource | null;
  onChange: (r: Resource) => void;
  options?: Resource[];
  label: string;
}) {
  return (
    <div className="res-select" role="radiogroup" aria-label={label}>
      {RESOURCES.map(r => (
        <button
          key={r}
          type="button"
          role="radio"
          aria-checked={value === r}
          disabled={!options.includes(r)}
          className={`res-select-item${value === r ? ' res-select-active' : ''}`}
          onClick={() => onChange(r)}
        >
          <span className="swatch" style={{ background: CARD_COLORS[r] }} />
          {RESOURCE_NAMES[r]}
        </button>
      ))}
    </div>
  );
}
