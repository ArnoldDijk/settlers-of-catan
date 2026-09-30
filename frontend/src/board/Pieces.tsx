import type { Building, Road } from '../state/types';
import { corner, edgeMid } from './geometry';

export function RoadPiece({ road, color }: { road: Road; color: string }) {
  const [x, y] = edgeMid(road.at, road.at.edge);
  return <use href="#p-road" color={color} transform={`translate(${x},${y}) rotate(${30 + 60 * road.at.edge})`} />;
}

export function BuildingPiece({ building, color }: { building: Building; color: string }) {
  const [x, y] = corner(building.at, building.at.corner);
  return <use href={`#p-${building.kind}`} color={color} transform={`translate(${x},${y}) scale(1.25)`} />;
}
