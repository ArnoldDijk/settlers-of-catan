import { describe, expect, it } from 'vitest';
import { corner, edgeMid, pos, SEA_RING } from './geometry';

const close = (a: [number, number], b: [number, number]) => Math.hypot(a[0] - b[0], a[1] - b[1]) < 0.5;

describe('hex geometry', () => {
  it('places the centre tile at the origin', () => {
    expect(pos({ q: 0, r: 0 })).toEqual([0, 0]);
  });

  it('has an 18-tile sea ring', () => {
    expect(SEA_RING).toHaveLength(18);
  });

  it('shares corners between neighbouring tiles', () => {
    // Top corner of (0,0) is corner 2 (lower-right) of (0,-1)... and corner 4 of (1,-1).
    expect(close(corner({ q: 0, r: 0 }, 0), corner({ q: 0, r: -1 }, 2))).toBe(true);
    expect(close(corner({ q: 0, r: 0 }, 0), corner({ q: 1, r: -1 }, 4))).toBe(true);
  });

  it('shares edges between neighbouring tiles', () => {
    // Right edge (1) of (0,0) is the left edge (4) of (1,0).
    expect(close(edgeMid({ q: 0, r: 0 }, 1), edgeMid({ q: 1, r: 0 }, 4))).toBe(true);
  });
});
