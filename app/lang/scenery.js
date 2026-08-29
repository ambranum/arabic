/* Shared drawing primitives for the section banners.  window.SCN

   These are GEOGRAPHY, not language. A stone house, an olive, a cypress, a water line and a
   column look the same on both sides of the Green Line, so they stay shared and only the
   scene compositions and their captions live in a language pack. The Hebrew pack will add its
   own pieces here rather than fork the file.

   Every primitive draws into the same 1200x210 stage with the ground line at y=196, and takes
   an optional `y` so a hill town can step its buildings up a slope. Solid masses are filled
   with var(--paper) -- identical in tone to the background, so nothing looks different, but
   the hills behind stop drawing straight through the buildings in front. */
window.SCN = (() => {
const _hills = (o = '') =>
  `<path d="M0 190 Q180 148 380 166 T760 158 T1200 172" opacity=".45"${o}/>
   <path d="M0 208 Q240 180 520 194 T1200 196"/>`;
// A taller ridge, for the places that sit under a mountain — Nablus, Wadi Ara, Jericho.
const _ridge = (o = '.34') =>
  `<path d="M0 196 Q170 92 360 116 T700 82 T1010 122 T1200 104" opacity="${o}"/>`;
const _ground = (y = 196) =>
  `<path d="M0 ${y}h1200" stroke="var(--ink-soft)" stroke-width="1.8" opacity=".7"/>`;
// A flat-roofed stone house with a row of windows — the unit most of these scenes are built
// from. `y` is the line it stands on, so a hill town can step its houses up the slope.
const _house = (x, w, h, win = 3, y = 196) => {
  let g = `<path d="M${x} ${y}v-${h}h${w}v${h}" fill="var(--paper)"/>`;
  const gap = w / (win + 1);
  for (let i = 1; i <= win; i++) g += `<path d="M${x + gap * i - 4} ${y - h + 14}v10h8v-10z"/>`;
  return g; };
const _arch = (x, w, h, y = 196) =>
  `<path d="M${x} ${y}v-${h}a${w / 2} ${w / 2} 0 0 1 ${w} 0v${h}" fill="var(--paper)"/>`;
const _cypress = (x, h, y = 196) =>
  `<path d="M${x} ${y}c0-${h * .8} ${h * .17}-${h} ${h * .23}-${h * 1.07}c${h * .07} ${h * .07} ${h * .23} ${h * .3} ${h * .23} ${h * 1.07}z"/>`;
const _olive = (x, sc = 1, y = 196) => `<g transform="translate(${x} ${y}) scale(${sc})">
    <path d="M-4 0v-30" stroke="var(--ink-soft)" stroke-width="2.4" fill="none"/>
    <path d="M-26 -30c0-20 12-30 22-30s22 10 22 30c-8 6-36 6-44 0z"/></g>`;
const _fig = (x, y, sc = 1) => `<g transform="translate(${x} ${y}) scale(${sc})">
    <circle cx="0" cy="-30" r="8"/><path d="M-11 0v-14a11 11 0 0 1 22 0V0"/></g>`;
// A date palm — Jericho and the Gaza shore. The trunk is drawn, the fronds take the group fill.
const _palm = (x, h = 66, y = 196) => `<g transform="translate(${x} ${y})">
    <path d="M0 0c-3-${Math.round(h * .5)} -3-${Math.round(h * .8)} 0-${h}"
      stroke="var(--ink-soft)" stroke-width="2.4" fill="none"/>
    <g transform="translate(0 -${h})">
      <path d="M0 0c-8-13-26-19-42-16 13 11 27 16 42 16z"/>
      <path d="M0 0c8-13 26-19 42-16-13 11-27 16-42 16z"/>
      <path d="M0 0c-5-15-19-27-35-31 9 15 21 26 35 31z"/>
      <path d="M0 0c5-15 19-27 35-31-9 15-21 26-35 31z"/>
      <path d="M0 0c-2-15-9-29-20-39 2 17 8 30 20 39z"/>
      <path d="M0 0c2-15 9-29 20-39-2 17-8 30-20 39z"/></g></g>`;
// Water: long swells between two heights, over an exact x range so a harbour can end at the
// quay instead of running off under the town.
const _water = (top, bot, x0 = 0, x1 = 1200) => { let s = '';
  for (let i = 0, y = top; y <= bot; y += 9, i++) {
    let x = x0 + (i % 2) * 26, d = `M${x} ${y}`;
    while (x1 - x >= 80) { d += 'q40 -6 80 0'; x += 80; }
    const r = x1 - x; if (r > 8) d += `q${(r / 2).toFixed(1)} -5 ${r} 0`;
    s += `<path d="${d}" opacity="${Math.max(.12, .34 - i * .045).toFixed(2)}"/>`; }
  return s; };
// A fishing boat — hull, and a lateen sail when it wants one.
const _boat = (x, y, sc = 1, sail = 1) => `<g transform="translate(${x} ${y}) scale(${sc})">
    <path d="M-34 0q34 17 68 0z"/><path d="M-37 0h74"/>
    ${sail ? `<path d="M0 0v-48"/><path d="M3 -46q27 13 27 31l-27 4z"/>` : ''}</g>`;
const _minaret = (x, h, y = 196) => `<path d="M${x} ${y}v-${h}h18v${h}" fill="var(--paper)"/>
    <path d="M${x - 5} ${y - h + 26}h28M${x - 5} ${y - h + 34}h28"/>
    <path d="M${x} ${y - h}h18l-9-15z" fill="var(--paper)"/><path d="M${x + 9} ${y - h - 15}v-9"/>`;
const _dome = (cx, y, r, o = ' fill="var(--paper)"') =>
  `<path d="M${cx - r} ${y}a${r} ${r} 0 0 1 ${r * 2} 0z"${o}/>`;
// A column, for the Roman street at Sebastia: shaft, a two-part capital, a base block.
const _col = (x, h, y = 196) => `<path d="M${x + 1} ${y - 7}v-${h - 14}M${x + 14} ${y - 7}v-${h - 14}"/>
    <path d="M${x - 1} ${y - h + 7}h17v-6h-17z" fill="var(--paper)"/>
    <path d="M${x - 5} ${y - h + 1}h25v-7h-25z" fill="var(--paper)"/>
    <path d="M${x - 3} ${y}h21v-7h-21z" fill="var(--paper)"/>`;

  return {_hills, _ridge, _ground, _house, _arch, _cypress, _olive, _fig, _palm, _water, _boat, _minaret, _dome, _col};
})();
