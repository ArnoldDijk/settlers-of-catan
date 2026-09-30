import type { PlayerColor, Resource, Terrain } from '../state/types';

// Colours and Dutch labels taken from the "Catan Tiles" design.

export const INK = '#161E3C';

export const PLAYER_COLORS: Record<PlayerColor, string> = {
  red: '#A64F6D',
  blue: '#6D8AF5',
  orange: '#FFB35E',
  white: '#FFFFFF',
};

/** Harbor ring colours. */
export const HARBOR_COLORS: Record<Resource, string> = {
  lumber: '#2E7D57',
  brick: '#C2654A',
  wool: '#8CC265',
  grain: '#E3A73A',
  ore: '#6A7191',
};

/** Resource card colours. */
export const CARD_COLORS: Record<Resource, string> = {
  lumber: '#2F6B4A',
  brick: '#C2654A',
  wool: '#8CC265',
  grain: '#EDB94A',
  ore: '#7A7F9E',
};

export const RESOURCE_NAMES: Record<Resource, string> = {
  lumber: 'Hout',
  brick: 'Stenen',
  wool: 'Wol',
  grain: 'Graan',
  ore: 'Erts',
};

export const RESOURCE_TERRAIN: Record<Resource, Exclude<Terrain, 'desert'>> = {
  lumber: 'forest',
  brick: 'hills',
  wool: 'pasture',
  grain: 'fields',
  ore: 'mountains',
};

export const TERRAIN_NAMES: Record<Terrain, string> = {
  forest: 'Bos',
  hills: 'Heuvels',
  pasture: 'Weiland',
  fields: 'Akkers',
  mountains: 'Gebergte',
  desert: 'Woestijn',
};
