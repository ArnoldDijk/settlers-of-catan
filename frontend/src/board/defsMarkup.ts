// SVG <defs> ported verbatim from the Claude Design file "Catan Tiles.dc.html".
// Terrain tiles (#t-*), #dock, pieces (#p-*, tinted via currentColor), #p-robber, #token-guide.
export const SVG_DEFS = `
<clipPath id="hexclip"><path d="M0,-100 L86.6,-50 L86.6,50 L0,100 L-86.6,50 L-86.6,-50 Z"></path></clipPath>
<linearGradient id="g-forest" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3E8159"></stop><stop offset="1" stop-color="#22523A"></stop></linearGradient>
<linearGradient id="g-hills" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#DE8A64"></stop><stop offset="1" stop-color="#A94E3B"></stop></linearGradient>
<linearGradient id="g-pasture" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#A6D47C"></stop><stop offset="1" stop-color="#78B255"></stop></linearGradient>
<linearGradient id="g-fields" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F7CF62"></stop><stop offset="1" stop-color="#E3A73A"></stop></linearGradient>
<linearGradient id="g-mountains" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9AA0BE"></stop><stop offset="1" stop-color="#666C8C"></stop></linearGradient>
<linearGradient id="g-desert" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F3E2B6"></stop><stop offset="1" stop-color="#DDC089"></stop></linearGradient>
<linearGradient id="g-sea" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3B72C2"></stop><stop offset="1" stop-color="#23508F"></stop></linearGradient>
<pattern id="p-rows" width="14" height="14" patternUnits="userSpaceOnUse" patternTransform="rotate(-28)">
  <rect width="14" height="7" fill="#F8D46A"></rect><rect y="7" width="14" height="7" fill="#E6AE42"></rect>
  <path d="M0,3.5 h14" stroke="#FCE59A" stroke-width="1" stroke-dasharray="2 3"></path>
</pattern>

<g id="pine">
  <ellipse cx="3" cy="17" rx="15" ry="4" fill="#0B2A1C" opacity="0.35"></ellipse>
  <rect x="-2.5" y="9" width="5" height="9" fill="#5C3A2E"></rect>
  <path d="M0,-4 L19,13 L-19,13 Z" fill="#1B563B"></path><path d="M0,-4 L19,13 L0,13 Z" fill="#2C7650"></path>
  <path d="M0,-15 L15,4 L-15,4 Z" fill="#1E5E41"></path><path d="M0,-15 L15,4 L0,4 Z" fill="#348458"></path>
  <path d="M0,-25 L11,-6 L-11,-6 Z" fill="#21654A"></path><path d="M0,-25 L11,-6 L0,-6 Z" fill="#3E9464"></path>
</g>
<g id="bricks">
  <ellipse cx="0" cy="11" rx="20" ry="4" fill="#5E2A22" opacity="0.35"></ellipse>
  <g stroke="#7A3328" stroke-width="1.2">
    <rect x="-18" y="1" width="12" height="7" fill="#E48D66"></rect><rect x="-6" y="1" width="12" height="7" fill="#D27854"></rect><rect x="6" y="1" width="12" height="7" fill="#E48D66"></rect>
    <rect x="-12" y="-6" width="12" height="7" fill="#D27854"></rect><rect x="0" y="-6" width="12" height="7" fill="#EC9A73"></rect>
    <rect x="-6" y="-13" width="12" height="7" fill="#E48D66"></rect>
  </g>
</g>
<g id="sheep">
  <ellipse cx="2" cy="11" rx="15" ry="3.5" fill="#3F6B2A" opacity="0.35"></ellipse>
  <path d="M-7,6 v6 M-2,7 v6 M4,7 v6 M8,6 v6" stroke="#161E3C" stroke-width="2.2" stroke-linecap="round"></path>
  <g fill="#FBFAF4" stroke="#D8D6C8" stroke-width="1">
    <circle cx="-7" cy="0" r="6"></circle><circle cx="0" cy="-3" r="7"></circle><circle cx="7" cy="0" r="6"></circle><circle cx="0" cy="3" r="6.5"></circle><circle cx="-4" cy="4" r="5"></circle><circle cx="5" cy="4" r="5"></circle>
  </g>
  <ellipse cx="13" cy="-2" rx="4.5" ry="5.5" fill="#161E3C"></ellipse><ellipse cx="11" cy="-7" rx="2.5" ry="1.4" fill="#161E3C" transform="rotate(-30 11 -7)"></ellipse>
  <circle cx="14.5" cy="-3" r="0.9" fill="#FBFAF4"></circle>
</g>
<g id="sheaf">
  <ellipse cx="0" cy="16" rx="12" ry="3" fill="#8A5A1E" opacity="0.35"></ellipse>
  <path d="M0,16 L-8,-8 M0,16 L-3,-12 M0,16 L2,-13 M0,16 L7,-9 M0,16 L10,-4" stroke="#B9822C" stroke-width="1.6"></path>
  <g fill="#F9DE7E" stroke="#B9822C" stroke-width="0.8">
    <ellipse cx="-8" cy="-10" rx="2.4" ry="5" transform="rotate(-18 -8 -10)"></ellipse><ellipse cx="-3" cy="-14" rx="2.4" ry="5" transform="rotate(-8 -3 -14)"></ellipse>
    <ellipse cx="2" cy="-15" rx="2.4" ry="5" transform="rotate(6 2 -15)"></ellipse><ellipse cx="7.5" cy="-11" rx="2.4" ry="5" transform="rotate(18 7.5 -11)"></ellipse><ellipse cx="11" cy="-6" rx="2.4" ry="5" transform="rotate(30 11 -6)"></ellipse>
  </g>
  <rect x="-5" y="5" width="10" height="3.5" rx="1" fill="#A64F6D"></rect>
</g>
<g id="wave"><path d="M-10,0 q5,-5 10,0 t10,0" fill="none" stroke="#8FB0EA" stroke-width="2" stroke-linecap="round"></path></g>

<g id="t-forest">
  <path d="M0,-100 L86.6,-50 L86.6,50 L0,100 L-86.6,50 L-86.6,-50 Z" fill="url(#g-forest)"></path>
  <g clip-path="url(#hexclip)">
    <ellipse cx="0" cy="4" rx="40" ry="30" fill="#4C9468" opacity="0.55"></ellipse>
    <g fill="#2A6A48"><circle cx="-70" cy="-30" r="14"></circle><circle cx="72" cy="20" r="16"></circle><circle cx="-10" cy="88" r="18"></circle><circle cx="30" cy="-90" r="16"></circle></g>
    <use href="#pine" transform="translate(-22,-72) scale(0.9)"></use>
    <use href="#pine" transform="translate(16,-70) scale(1.05)"></use>
    <use href="#pine" transform="translate(-52,-44) scale(1)"></use>
    <use href="#pine" transform="translate(50,-42) scale(1.1)"></use>
    <use href="#pine" transform="translate(-4,-46) scale(0.75)"></use>
    <use href="#pine" transform="translate(-64,-2) scale(1.05)"></use>
    <use href="#pine" transform="translate(64,4) scale(0.95)"></use>
    <use href="#pine" transform="translate(-50,40) scale(1.1)"></use>
    <use href="#pine" transform="translate(48,42) scale(1.05)"></use>
    <use href="#pine" transform="translate(-18,62) scale(1)"></use>
    <use href="#pine" transform="translate(18,66) scale(1.15)"></use>
  </g>
</g>

<g id="t-hills">
  <path d="M0,-100 L86.6,-50 L86.6,50 L0,100 L-86.6,50 L-86.6,-50 Z" fill="url(#g-hills)"></path>
  <g clip-path="url(#hexclip)">
    <path d="M-100,-48 Q-55,-84 -5,-58 T100,-62 L100,100 L-100,100 Z" fill="#D57C58"></path>
    <path d="M-100,-48 Q-55,-84 -5,-58 T100,-62" fill="none" stroke="#EDA07C" stroke-width="3"></path>
    <path d="M-100,4 Q-45,-32 18,-6 T100,-10 L100,100 L-100,100 Z" fill="#BE6146"></path>
    <path d="M-100,4 Q-45,-32 18,-6 T100,-10" fill="none" stroke="#DB8462" stroke-width="3"></path>
    <path d="M-100,56 Q-30,26 30,52 T100,44 L100,100 L-100,100 Z" fill="#9E4736"></path>
    <path d="M-100,56 Q-30,26 30,52 T100,44" fill="none" stroke="#C0664C" stroke-width="3"></path>
    <ellipse cx="-42" cy="-24" rx="16" ry="6" fill="#8E3F31"></ellipse><ellipse cx="-42" cy="-25" rx="12" ry="4" fill="#6E2F26"></ellipse>
    <g fill="#8E3F31" opacity="0.6"><circle cx="-60" cy="-58" r="2"></circle><circle cx="30" cy="-30" r="2"></circle><circle cx="60" cy="20" r="2.5"></circle><circle cx="-20" cy="30" r="2"></circle><circle cx="-60" cy="70" r="2.5"></circle></g>
    <use href="#bricks" transform="translate(44,-44)"></use>
    <use href="#bricks" transform="translate(-40,64) scale(1.1)"></use>
    <use href="#bricks" transform="translate(52,62) scale(0.8)"></use>
  </g>
</g>

<g id="t-pasture">
  <path d="M0,-100 L86.6,-50 L86.6,50 L0,100 L-86.6,50 L-86.6,-50 Z" fill="url(#g-pasture)"></path>
  <g clip-path="url(#hexclip)">
    <ellipse cx="-30" cy="-50" rx="45" ry="20" fill="#B6DD8E" opacity="0.7"></ellipse>
    <ellipse cx="40" cy="50" rx="50" ry="22" fill="#6DA84B" opacity="0.5"></ellipse>
    <g stroke="#5E9A3E" stroke-width="1.6" stroke-linecap="round" fill="none">
      <path d="M-60,-20 l3,-6 l3,6"></path><path d="M40,-20 l3,-6 l3,6"></path><path d="M-30,30 l3,-6 l3,6"></path><path d="M60,10 l3,-6 l3,6"></path><path d="M-10,80 l3,-6 l3,6"></path><path d="M10,-80 l3,-6 l3,6"></path><path d="M-70,50 l3,-6 l3,6"></path>
    </g>
    <g fill="#F9F871"><circle cx="-50" cy="-8" r="2"></circle><circle cx="30" cy="-58" r="2"></circle><circle cx="66" cy="34" r="2"></circle><circle cx="-24" cy="46" r="2"></circle></g>
    <g fill="#FBFAF4"><circle cx="-44" cy="-4" r="1.6"></circle><circle cx="36" cy="-62" r="1.6"></circle><circle cx="8" cy="72" r="1.6"></circle></g>
    <g stroke="#8A5A3C" stroke-width="2.5" stroke-linecap="round">
      <path d="M-90,-66 L-20,-96" stroke-width="2"></path><path d="M-90,-58 L-20,-88" stroke-width="2"></path>
      <path d="M-78,-76 v14"></path><path d="M-60,-84 v14"></path><path d="M-42,-92 v14"></path>
    </g>
    <use href="#sheep" transform="translate(-44,-38)"></use>
    <use href="#sheep" transform="translate(46,-36) scale(-1,1)"></use>
    <use href="#sheep" transform="translate(-50,40) scale(1.05)"></use>
    <use href="#sheep" transform="translate(42,52) scale(-0.95,0.95)"></use>
    <use href="#sheep" transform="translate(4,-70) scale(0.8)"></use>
  </g>
</g>

<g id="t-fields">
  <path d="M0,-100 L86.6,-50 L86.6,50 L0,100 L-86.6,50 L-86.6,-50 Z" fill="url(#g-fields)"></path>
  <g clip-path="url(#hexclip)">
    <path d="M-100,-100 L100,-100 L100,-18 Q20,-4 -100,-30 Z" fill="url(#p-rows)"></path>
    <path d="M-100,30 Q0,50 100,18 L100,100 L-100,100 Z" fill="url(#p-rows)" transform="rotate(4)"></path>
    <path d="M-100,-30 Q20,-4 100,-18 L100,18 Q0,50 -100,30 Z" fill="#EFBD50"></path>
    <path d="M-100,-2 Q10,22 100,0" fill="none" stroke="#D9A04A" stroke-width="7" stroke-linecap="round"></path>
    <path d="M-100,-2 Q10,22 100,0" fill="none" stroke="#F4D38A" stroke-width="2" stroke-dasharray="3 6"></path>
    <use href="#sheaf" transform="translate(-48,-56)"></use>
    <use href="#sheaf" transform="translate(44,-60) scale(1.1)"></use>
    <use href="#sheaf" transform="translate(-56,52) scale(1.05)"></use>
    <use href="#sheaf" transform="translate(50,50)"></use>
    <use href="#sheaf" transform="translate(-4,72) scale(0.85)"></use>
  </g>
</g>

<g id="t-mountains">
  <path d="M0,-100 L86.6,-50 L86.6,50 L0,100 L-86.6,50 L-86.6,-50 Z" fill="url(#g-mountains)"></path>
  <g clip-path="url(#hexclip)">
    <path d="M-100,30 Q0,0 100,24 L100,100 L-100,100 Z" fill="#747A99"></path>
    <path d="M-2,-92 L44,-18 L-48,-18 Z" fill="#6A7090"></path><path d="M-2,-92 L-48,-18 L-12,-18 Z" fill="#A9AFCB"></path>
    <path d="M-2,-92 L10,-73 L2,-76 L-6,-68 L-12,-75 Z" fill="#F4F6FB"></path>
    <path d="M-44,-58 L-8,0 L-86,0 Z" fill="#5E6484"></path><path d="M-44,-58 L-86,0 L-50,0 Z" fill="#9CA3C4"></path>
    <path d="M-44,-58 L-35,-44 L-42,-47 L-49,-41 L-54,-46 Z" fill="#F4F6FB"></path>
    <path d="M46,-62 L90,6 L6,6 Z" fill="#5A6082"></path><path d="M46,-62 L6,6 L38,6 Z" fill="#A2A9C8"></path>
    <path d="M46,-62 L56,-46 L48,-49 L40,-42 L35,-48 Z" fill="#F4F6FB"></path>
    <path d="M-40,40 L-10,86 L-74,86 Z" fill="#5E6484"></path><path d="M-40,40 L-74,86 L-46,86 Z" fill="#949BBC"></path>
    <path d="M44,44 L72,88 L16,88 Z" fill="#5A6082"></path><path d="M44,44 L16,88 L40,88 Z" fill="#949BBC"></path>
    <g stroke="#3A4263" stroke-width="1" fill="#6D8AF5">
      <path d="M-58,20 l4,-10 l4,10 z"></path><path d="M-52,22 l3,-7 l3,7 z" fill="#A9BBFF"></path>
      <path d="M58,24 l4,-11 l4,11 z"></path><path d="M52,26 l3,-7 l3,7 z" fill="#A9BBFF"></path>
      <path d="M6,90 l3,-8 l3,8 z" fill="#A9BBFF"></path>
    </g>
    <g fill="#5A6082"><ellipse cx="-20" cy="38" rx="6" ry="3"></ellipse><ellipse cx="28" cy="30" rx="5" ry="2.5"></ellipse></g>
  </g>
</g>

<g id="t-desert">
  <path d="M0,-100 L86.6,-50 L86.6,50 L0,100 L-86.6,50 L-86.6,-50 Z" fill="url(#g-desert)"></path>
  <g clip-path="url(#hexclip)">
    <path d="M-100,-44 Q-40,-76 20,-50 T100,-58 L100,-100 L-100,-100 Z" fill="#F7EAC6"></path>
    <path d="M-100,-44 Q-40,-76 20,-50 T100,-58" fill="none" stroke="#D5B47A" stroke-width="2"></path>
    <path d="M-100,50 Q-20,24 40,48 T100,40 L100,100 L-100,100 Z" fill="#D8BA80"></path>
    <path d="M-100,50 Q-20,24 40,48 T100,40" fill="none" stroke="#F3E2B6" stroke-width="2.5"></path>
    <g fill="none" stroke="#D5B47A" stroke-width="1.4" stroke-linecap="round">
      <path d="M-60,-20 q10,-4 20,0"></path><path d="M30,-24 q12,-5 24,0"></path><path d="M-30,72 q10,-4 20,0"></path><path d="M40,70 q8,-3 16,0"></path>
    </g>
    <g><ellipse cx="-50" cy="12" rx="12" ry="7" fill="#B8956A"></ellipse><ellipse cx="-53" cy="9" rx="7" ry="3" fill="#D1B083"></ellipse><ellipse cx="-36" cy="16" rx="6" ry="4" fill="#A6845C"></ellipse></g>
    <g><ellipse cx="54" cy="20" rx="9" ry="5" fill="#B8956A"></ellipse><ellipse cx="52" cy="18" rx="5" ry="2" fill="#D1B083"></ellipse></g>
    <g transform="translate(46,-60)">
      <ellipse cx="0" cy="18" rx="10" ry="3" fill="#8A6A3E" opacity="0.35"></ellipse>
      <path d="M0,18 V-10" stroke="#5E8A4F" stroke-width="8" stroke-linecap="round"></path>
      <path d="M0,6 H-7 V-4 M0,0 H7 V-8" fill="none" stroke="#5E8A4F" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"></path>
      <path d="M1.5,16 V-9" stroke="#7FA36A" stroke-width="2" stroke-linecap="round"></path>
    </g>
    <g fill="#B8956A"><circle cx="-10" cy="-62" r="1.8"></circle><circle cx="-70" cy="30" r="1.6"></circle><circle cx="20" cy="84" r="1.8"></circle><circle cx="70" cy="-10" r="1.4"></circle></g>
  </g>
</g>

<g id="t-sea">
  <path d="M0,-100 L86.6,-50 L86.6,50 L0,100 L-86.6,50 L-86.6,-50 Z" fill="url(#g-sea)"></path>
  <g clip-path="url(#hexclip)">
    <ellipse cx="-20" cy="-40" rx="50" ry="22" fill="#4A82CF" opacity="0.5"></ellipse>
    <ellipse cx="30" cy="50" rx="46" ry="18" fill="#1E4782" opacity="0.5"></ellipse>
    <use href="#wave" transform="translate(-46,-62)"></use><use href="#wave" transform="translate(22,-74)"></use>
    <use href="#wave" transform="translate(52,-30)"></use><use href="#wave" transform="translate(-62,-12)"></use>
    <use href="#wave" transform="translate(-30,30)"></use><use href="#wave" transform="translate(50,18)"></use>
    <use href="#wave" transform="translate(-54,62)"></use><use href="#wave" transform="translate(14,76)"></use>
    <use href="#wave" transform="translate(4,-20) scale(0.8)"></use>
  </g>
</g>

<g id="dock">
  <g stroke-linecap="butt">
    <path d="M0,0 L-80,-46 M0,0 L-80,46" stroke="#6B432C" stroke-width="13"></path>
    <path d="M0,0 L-80,-46 M0,0 L-80,46" stroke="#B07A52" stroke-width="10"></path>
    <path d="M0,0 L-80,-46 M0,0 L-80,46" stroke="#6B432C" stroke-width="10" stroke-dasharray="1.4 5.6"></path>
  </g>
  <g fill="#4A2E1F"><circle cx="-80" cy="-46" r="4.5"></circle><circle cx="-80" cy="46" r="4.5"></circle><circle cx="-44" cy="-31" r="3.2"></circle><circle cx="-44" cy="31" r="3.2"></circle></g>
</g>
<g id="p-road">
  <rect x="-33" y="-5" width="70" height="14" rx="4" fill="#161E3C" opacity="0.3"></rect>
  <rect x="-35" y="-7" width="70" height="14" rx="4" fill="currentColor" stroke="#161E3C" stroke-width="2.5"></rect>
  <rect x="-31" y="-4.5" width="62" height="3.5" rx="1.75" fill="#FFFFFF" opacity="0.4"></rect>
  <path d="M-12,-7 V7 M12,-7 V7" stroke="#161E3C" stroke-width="1.2" opacity="0.35"></path>
</g>
<g id="p-settlement">
  <ellipse cx="3" cy="18" rx="20" ry="5" fill="#161E3C" opacity="0.3"></ellipse>
  <path d="M-15,-1 L0,-17 L15,-1 V16 H-15 Z" fill="currentColor"></path>
  <path d="M0,-17 L15,-1 V16 H0 Z" fill="#161E3C" opacity="0.18"></path>
  <path d="M-11,-3 L0,-14.5" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" opacity="0.45"></path>
  <path d="M-15,-1 H15" stroke="#161E3C" stroke-width="2"></path>
  <rect x="-4" y="5" width="8" height="11" rx="1.5" fill="#161E3C"></rect>
  <path d="M-15,-1 L0,-17 L15,-1 V16 H-15 Z" fill="none" stroke="#161E3C" stroke-width="2.5" stroke-linejoin="round"></path>
</g>
<g id="p-city">
  <ellipse cx="3" cy="20" rx="28" ry="5.5" fill="#161E3C" opacity="0.3"></ellipse>
  <path d="M-24,18 V0 L-12,-12 L0,0 V-12 L12,-26 L24,-12 V18 Z" fill="currentColor"></path>
  <path d="M12,-26 L24,-12 V18 H12 Z" fill="#161E3C" opacity="0.18"></path>
  <path d="M-12,-12 L0,0 V18 H-12 Z" fill="#161E3C" opacity="0.1"></path>
  <path d="M3,-13 L12,-23 M-21,-2 L-12,-10" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" opacity="0.45"></path>
  <path d="M-24,0 H0 M0,-12 H24" stroke="#161E3C" stroke-width="2"></path>
  <rect x="-16" y="6" width="8" height="12" rx="1.5" fill="#161E3C"></rect>
  <rect x="8" y="-7" width="8" height="8" rx="1" fill="#161E3C"></rect>
  <rect x="8" y="6" width="8" height="7" rx="1" fill="#161E3C"></rect>
  <path d="M-24,18 V0 L-12,-12 L0,0 V-12 L12,-26 L24,-12 V18 Z" fill="none" stroke="#161E3C" stroke-width="2.5" stroke-linejoin="round"></path>
</g>
<g id="p-robber">
  <ellipse cx="4" cy="23" rx="20" ry="5.5" fill="#0B1128" opacity="0.4"></ellipse>
  <ellipse cx="0" cy="21" rx="17" ry="5" fill="#161E3C"></ellipse>
  <path d="M-15,20 Q-18,2 -9,-6 L9,-6 Q18,2 15,20 Q0,25 -15,20 Z" fill="#3A4263"></path>
  <path d="M2,-6 L9,-6 Q18,2 15,20 Q8,23 2,23 Z" fill="#161E3C" opacity="0.35"></path>
  <path d="M-11,17 Q-13,4 -6,-3" fill="none" stroke="#FFFFFF" stroke-width="2.5" stroke-linecap="round" opacity="0.25"></path>
  <path d="M-9,-6 Q0,0 9,-6" fill="none" stroke="#161E3C" stroke-width="2"></path>
  <path d="M0,-27 Q13,-26 12,-12 Q11,-4 0,-3 Q-11,-4 -12,-12 Q-13,-26 0,-27 Z" fill="#3A4263"></path>
  <path d="M0,-27 Q13,-26 12,-12 Q11,-4 0,-3 Z" fill="#161E3C" opacity="0.3"></path>
  <ellipse cx="0" cy="-12" rx="6.5" ry="7" fill="#0B1128"></ellipse>
  <circle cx="-2.6" cy="-12.5" r="1.5" fill="#F9F871"></circle><circle cx="2.6" cy="-12.5" r="1.5" fill="#F9F871"></circle>
  <path d="M-15,20 Q-18,2 -9,-6 M9,-6 Q18,2 15,20 Q0,25 -15,20 M0,-27 Q13,-26 12,-12 Q11,-4 0,-3 Q-11,-4 -12,-12 Q-13,-26 0,-27 Z" fill="none" stroke="#0B1128" stroke-width="2.5" stroke-linejoin="round"></path>
</g>
<g id="token-guide"><circle r="32" fill="none" stroke="#F9F871" stroke-width="2" stroke-dasharray="5 4"></circle><path d="M-6,0 H6 M0,-6 V6" stroke="#F9F871" stroke-width="1.5"></path></g>
  
`;
