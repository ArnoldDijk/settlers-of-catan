import { SVG_DEFS } from './defsMarkup';

/** Mount once per page; every board/card SVG references these ids via <use href="#…">. */
export function SvgDefs() {
  return (
    <svg width="0" height="0" style={{ position: 'absolute' }} aria-hidden="true">
      <defs dangerouslySetInnerHTML={{ __html: SVG_DEFS }} />
    </svg>
  );
}
