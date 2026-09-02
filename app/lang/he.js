/* Modern Hebrew — the language pack.

   Everything that makes the app Hebrew rather than Arabic: the writing system's rules, the verb
   model, the keyboard, the tutor's brief. app.js contains none of it.

   Stage A measured what fills this: 179,033 lexicon rows over 12,662 lemmas at 94.6% coverage of
   live Hebrew news, and 2,084 pointed verb paradigms verified at 98.99% against Wiktionary's own
   romanization of the 3ms past — the cell a flashcard is banked under. See spike/he/FINDINGS.md.

   Hebrew inverts Arabic's difficulty, and the pack shows it. For Arabic, pronunciation is looked
   up per entry and VOCALIZATION is the hard part. For Hebrew, niqqud → Israeli pronunciation is
   deterministic (spike/he/phon.py), so pronunciation is nearly free once you have the pointing —
   and there is no CAPHI-style sub-dialect system to model, which is why `phon.variants` is empty
   where Arabic's carries Wadi Ara. */
// ---------- home artwork --------------------------------------------------------------------
// Inline SVG in the theme's own variables, like the Arabic pack's: it recolors itself in dark
// mode, weighs nothing, and carries no licence.
//
// The band is TESSERAE. Arabic's is tatreez, Palestinian cross-stitch; the Jewish answer to
// "what does this tradition put along an edge" is the mosaic floor -- Beit Alpha, Hammat
// Tiberias, Sepphoris, all of them bordered with rows of small cut stones. So: a course of
// tesserae between two rules, which is what those borders are, rather than a Star of David,
// which is a flag rather than a craft.
let _msN = 0;
function mosaic() {
  const id = 'ms' + (_msN++);                       // pattern ids are document-global
  return `<svg class="tz" height="16" aria-hidden="true"><defs>
    <pattern id="${id}" width="36" height="16" patternUnits="userSpaceOnUse">
      <rect x="1"  y="5.5" width="6" height="6" fill="var(--rubric)"/>
      <rect x="10" y="5.5" width="6" height="6" fill="var(--verdigris)"/>
      <rect x="19" y="5.5" width="6" height="6" fill="var(--rubric)"/>
      <rect x="28" y="5.5" width="6" height="6" fill="var(--ochre)"/>
      <rect x="0" y="0" width="36" height="1.4" fill="var(--ochre)"/>
      <rect x="0" y="14.6" width="36" height="1.4" fill="var(--ochre)"/>
    </pattern></defs>
    <rect width="100%" height="16" fill="url(#${id})"/></svg>`;
}

// SOLOMON'S TEMPLE — בֵּית הַמִּקְדָּשׁ, drawn from the description in 1 Kings 6-7.
//
// A RECONSTRUCTION, and the drawing should not pretend otherwise. Nobody has seen this building
// and no stone of it has been dug up; what exists is a written specification -- the porch, the
// hekhal, the devir behind it, the side chambers in three storeys, the two free-standing pillars
// Yachin and Boaz with their bowl capitals and pomegranates, the bronze Sea on its twelve oxen,
// and the altar in the court. Every one of those is in the text and every one of them is here.
// The proportions are the usual scholarly reading of the cubits; the details the text does not
// give are simply not drawn, which is why this is a silhouette and not a picture.
//
// It is the right subject for a Hebrew home page in a way a photograph of anywhere would not be:
// the building the language's oldest layer was written about, and which every later Jewish place
// in this app's section banners -- the Western Wall, Yavne, the synagogue at Baram -- is either
// the retaining wall of, the answer to, or a substitute for.
const HE_SKYLINE = (() => {
  const {_hills, _cypress, _olive} = SCN;
  // Yachin and Boaz: a shaft, a bowl capital, and the two rows of pomegranates the text hangs
  // on the network above it. They stood FREE, in front of the porch, holding up nothing.
  const pillar = (x) => {
    let pom = '';                            // "two rows of pomegranates upon the network"
    for (let k = 0; k < 7; k++) pom += `<circle cx="${x - 24 + k * 8}" cy="76" r="3.2"/>`;
    for (let k = 0; k < 6; k++) pom += `<circle cx="${x - 20 + k * 8}" cy="85" r="3.2"/>`;
    return `<path d="M${x - 15} 172V92h30v80" fill="var(--paper)"/>
      <path d="M${x - 15} 130h30M${x - 15} 152h30" opacity=".25"/>
      <path d="M${x - 29} 92h58v-6h-58z" fill="var(--paper)"/>
      <path d="M${x - 27} 86a27 27 0 0 1 54 0z" fill="var(--paper)"/>${pom}
      <path d="M${x - 27} 60h54" opacity=".5"/>
      <path d="M${x - 21} 60q10-14 21-14t21 14z" fill="var(--paper)"/>
      <path d="M${x - 22} 172h44v-10h-44z" fill="var(--paper)"/>`;
  };
  // The flight up to the platform, in front of the door rather than along the whole face --
  // three lines across a podium read as a podium with lines on it, not as steps.
  let step = '';
  for (let k = 0; k < 3; k++)
    step += `<path d="M${540 - k * 18} ${172 + k * 8}v8h${120 + k * 36}v-8" fill="var(--paper)"/>`;
  let chamber = '';                          // the side chambers, three storeys of them
  for (const x0 of [286, 838]) {
    chamber += `<path d="M${x0} 172v-62h76v62" fill="var(--paper)"/>`;
    for (let k = 1; k < 3; k++) chamber += `<path d="M${x0} ${172 - k * 21}h76" opacity=".45"/>`;
    for (let k = 0; k < 3; k++)
      chamber += `<path d="M${x0 + 32} ${164 - k * 21}v-9h12v9z" opacity=".6"/>`;
  }
  let ox = '';                               // the Sea stood on twelve oxen, three to a side
  for (let k = 0; k < 4; k++)
    ox += `<path d="M${146 + k * 18} 172v-14M${152 + k * 18} 172v-14" opacity=".55"/>`;
  return `<svg class="hm-sky" viewBox="0 0 1200 210" preserveAspectRatio="xMidYMax meet"
     fill="none" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
    <g stroke="var(--ink-soft)" stroke-width="1.6" opacity=".62">
      ${_hills()}
      ${chamber}
      <path d="M362 172V78h476v94" fill="var(--paper)"/>
      <path d="M350 78h500l-14-14H364z" fill="var(--paper)"/>
      <path d="M424 172V44h352v128" fill="var(--paper)"/>
      <path d="M410 44h380l-16-15H426z" fill="var(--paper)"/>
      <path d="M424 62h352" opacity=".4"/>
      <path d="M556 172V96h88v76" fill="var(--ochre-wash)" stroke="var(--ochre)"/>
      <path d="M600 172V96" stroke="var(--ochre)" opacity=".5"/>
      ${pillar(486)}${pillar(714)}
      <path d="M280 172h640" stroke-width="1.9"/>${step}
      <path d="M120 172v-26h84v26" fill="var(--paper)"/>
      <path d="M112 146a46 46 0 0 0 100 0z" fill="var(--paper)"/>
      <path d="M112 146h100"/><path d="M118 138h88" opacity=".4"/>${ox}
      <path d="M986 172v-40h96v40" fill="var(--paper)"/>
      <path d="M1002 132v-20h64v20" fill="var(--paper)"/>
      <path d="M978 172h112" opacity=".5"/>
      <path d="M1082 172l40-32v32z" fill="var(--paper)" opacity=".9"/>
      <path d="M1016 112c4-12 12-18 18-22-2 12-8 18-18 22z" opacity=".7"/>
    </g>
    <g fill="var(--verdigris)" opacity=".5" stroke="none">
      ${_cypress(60, 60)}${_cypress(104, 46)}${_cypress(1148, 56)}
      ${_olive(238, .78)}${_olive(944, .72)}
    </g>
    <path d="M0 196h1200" stroke="var(--ink-soft)" stroke-width="1.8" opacity=".7"/>
  </svg>`;
})();

// ---------- section banners ----------------------------------------------------------------
// The Arabic pack draws a real Palestinian place behind every section title. This is the same
// idea answered from the other side: thirteen places that matter to Judaism, drawn to the same
// rules so the app still looks like one app -- one viewBox (1200x210), hills behind, a ground
// line at y=196, buildings as plain strokes, trees as verdigris silhouettes, and exactly ONE
// ochre accent per scene, the thing your eye should land on. An engraving, not a postcard.
//
// The set is chosen to be the country and not one postcard of it: Jerusalem four times over but
// never the same Jerusalem, the Galilee at Safed and Tiberias and Baram, the Negev at Beersheba,
// the desert at Ein Gedi and Qumran, and the Jordan. Where a section has an obvious home it gets
// it -- verbs grow from a root, so verbs get Abraham's well and the tamarisk he planted beside
// it; grammar is structure, so grammar gets a columned synagogue front; translation is a
// crossing, so it gets the river the people crossed to get here; the tutor is a question asked
// of a teacher, so it gets Yavne, the academy that outlived the Temple.
//
// Deliberately not drawn: the Temple Mount. What stands on it is the Dome of the Rock, and
// putting a Muslim shrine under a Hebrew section title as "a place important to Judaism" would
// be a claim this app has no business making. The Western Wall is the Jewish approach to that
// place and is what Jews actually pray at, so that is what is drawn.
const HE_ART = (() => {
  const {_hills, _ridge, _ground, _house, _arch, _cypress, _olive, _fig, _palm, _water, _boat,
         _dome, _col, _courses} = SCN;
  return {

  // THE WESTERN WALL — Herodian courses with their drafted margins, Wilson's Arch, the plaza.
  news: {ar: 'חֲדָשׁוֹת', place: 'The Western Wall', placeAr: 'הַכּוֹתֶל הַמַּעֲרָבִי',
    what: 'the great courses of stone', art: () => {
    // A Herodian ashlar is not a brick: it is a huge block with a shallow margin dressed round
    // its face, and drawing that margin is the whole difference between stone and graph paper.
    const block = (x, y, w, h) =>
      `<path d="M${x} ${y}v-${h}h${w}v${h}z" fill="var(--paper)"/>` +
      `<path d="M${x + 7} ${y - 7}v-${h - 14}h${w - 14}v${h - 14}z" opacity=".28"/>`;
    let wall = '';
    for (const [y, h, w, off] of [[196, 34, 196, 0], [162, 34, 196, 98],
                                  [128, 34, 196, 0], [94, 34, 196, 98]])
      for (let x = -off; x < 1200; x += w) wall += block(x, y, w, h);
    // The small Ottoman courses on top, and they stop short of the right edge: the wall's top
    // is stepped, not level, and a level one reads as a wall someone drew rather than built.
    for (const [y, h, w, off, x1] of [[60, 24, 104, 0, 1200], [36, 24, 104, 52, 830]])
      for (let x = -off; x < x1; x += w) wall += block(x, y, w, h);
    let cap = '';                            // capers, rooted in the joints and hanging down
    for (const [x, y, sc] of [[286, 128, 1], [712, 94, .85], [968, 162, .9], [432, 60, .7]])
      cap += `<g transform="translate(${x} ${y}) scale(${sc})">
        <path d="M0 0c-13 3-20 13-17 25 9-2 17-12 17-25zM0 0c13 3 20 13 17 25-9-2-17-12-17-25z"/>
        <path d="M0 2c-4 12-2 22 3 30 4-9 3-20-3-30z"/></g>`;
    return `
    <g stroke="var(--ink-soft)" stroke-width="1.6" opacity=".62" fill="none">
      ${wall}
      <path d="M76 196v-74a86 86 0 0 1 172 0v74"
        fill="var(--ochre-wash)" stroke="var(--ochre)"/>
      <path d="M0 196h1200" opacity=".45"/>
      ${_fig(392, 196, 1.05)}${_fig(438, 196, .92)}${_fig(614, 196, 1)}
      ${_fig(866, 196, 1.05)}${_fig(910, 196, .9)}${_fig(1092, 196, .95)}
    </g>
    <g fill="var(--verdigris)" opacity=".5" stroke="none">${cap}</g>
    ${_ground()}`; }},

  // BEN-YEHUDA'S HOUSE — the room the modern language was assembled in, lamp still on.
  lessons: {ar: 'שִׁעוּרִים', place: 'Ben-Yehuda’s house', placeAr: 'בֵּיתוֹ שֶׁל בֶּן־יְהוּדָה',
    what: 'where the language was made speakable again', art: () => {
    let win = '';                            // Jerusalem stone, arched windows, iron balconies
    for (let k = 0; k < 3; k++) {
      const x = 452 + k * 106;
      win += `<path d="M${x} 130v-40a26 26 0 0 1 52 0v40" fill="var(--paper)"/>
              <path d="M${x + 26} 130V64" opacity=".4"/>
              <path d="M${x - 8} 130h68v10h-68z" fill="var(--paper)"/>`;
      for (let b = 0; b < 6; b++) win += `<path d="M${x - 4 + b * 12} 140v-10" opacity=".5"/>`;
    }
    return `
    <g stroke="var(--ink-soft)" stroke-width="1.6" opacity=".62" fill="none">
      ${_hills()}
      ${_house(120, 116, 62, 3)}${_house(258, 96, 52, 3)}
      ${_house(940, 104, 56, 3)}${_house(1064, 96, 48, 3)}
      <path d="M420 196V54h340v142" fill="var(--paper)"/>
      <path d="M406 54h368l-16-16H422z" fill="var(--paper)"/>
      ${_courses(420, 196, 340, 142, 7, 86)}
      <path d="M406 54h368"/>
      ${win}
      <path d="M556 196v-46a34 34 0 0 1 68 0v46" fill="var(--paper)"/>
      <path d="M590 196v-40" opacity=".4"/>
      <path d="M660 90h44v40h-44z" fill="var(--ochre-wash)" stroke="var(--ochre)"/>
      <path d="M682 90v40M660 110h44" stroke="var(--ochre)" opacity=".5"/>
      <path d="M330 196v-84h10v84" opacity=".7"/>
      <path d="M326 112h18v-10h-18z"/><path d="M335 102v-8"/>
    </g>
    <g fill="var(--verdigris)" opacity=".5" stroke="none">
      ${_cypress(388, 70)}${_cypress(806, 62)}${_cypress(852, 48)}
      ${_olive(224, .74)}${_olive(1150, .7)}
    </g>${_ground()}`; }},

  // SAFED — the town stepping up its ridge, alleys as stairs, a synagogue dome among the roofs.
  stories: {ar: 'סִפּוּרִים', place: 'Safed', placeAr: 'צְפַת',
    what: 'the hill town and its stairs', art: () => {
    let st = '';                             // an alley that is really a staircase
    for (let i = 0; i < 9; i++)
      st += `<path d="M${560 + i * 15} ${196 - i * 13}h58" opacity=".5"/>`;
    return `
    <g stroke="var(--ink-soft)" stroke-width="1.6" opacity=".62" fill="none">
      <path d="M0 196Q210 96 470 108T1200 176" opacity=".38"/>
      ${_house(24, 92, 46, 3, 184)}${_house(136, 84, 44, 3, 162)}${_house(240, 78, 42, 2, 142)}
      ${_house(336, 86, 44, 3, 126)}${_house(786, 82, 42, 3, 130)}${_house(886, 90, 46, 3, 146)}
      ${_house(1000, 88, 44, 3, 166)}
      <path d="M446 126v-52h148v52" fill="var(--paper)"/><path d="M436 74h168"/>
      ${_dome(520, 74, 34)}<path d="M520 40v-14"/>
      <path d="M470 126v-30a20 20 0 0 1 40 0v30M530 126v-30a20 20 0 0 1 40 0v30" opacity=".55"/>
      ${st}
      ${_house(96, 108, 58, 4)}${_house(286, 118, 62, 4)}${_house(680, 104, 56, 4)}
      ${_house(852, 100, 52, 3)}${_house(1006, 94, 50, 3)}
      <path d="M700 196v-40a26 26 0 0 1 52 0v40" fill="var(--ochre-wash)" stroke="var(--ochre)"/>
    </g>
    <g fill="var(--verdigris)" opacity=".5" stroke="none">
      ${_cypress(228, 44, 142)}${_cypress(414, 46, 126)}${_cypress(66, 58)}${_cypress(792, 54)}
      ${_olive(1122, .85)}
    </g>${_ground()}`; }},

  // THE SHRINE OF THE BOOK — the white lid of a scroll jar, the black wall, the water between.
  books: {ar: 'סְפָרִים', place: 'The Shrine of the Book', placeAr: 'הֵיכַל הַסֵּפֶר',
    what: 'the dome, the black wall, the water', art: () => {
    let rib = '';                            // the dome is a jar lid: ribs running to the crown
    for (let k = -6; k <= 6; k++)
      rib += `<path d="M${520 + k * 27} 162Q${520 + k * 12} 92 520 50" opacity=".36"/>`;
    return `
    <g stroke="var(--ink-soft)" stroke-width="1.6" opacity=".62" fill="none">
      ${_hills()}
      <path d="M352 162Q520 -18 688 162z" fill="var(--paper)"/>${rib}
      <path d="M352 162h336"/>
      <path d="M520 50v-22"/><circle cx="520" cy="22" r="7"
        fill="var(--ochre-wash)" stroke="var(--ochre)"/>
      <path d="M792 162l204-96v96z" fill="var(--ink-soft)" opacity=".55" stroke="none"/>
      <path d="M792 162l204-96v96z" stroke-width="1.9"/>
      <path d="M330 168h700" opacity=".45"/>
    </g>
    ${_water(172, 192, 288, 1060)}
    <g fill="var(--verdigris)" opacity=".5" stroke="none">
      ${_cypress(112, 58, 168)}${_cypress(160, 44, 168)}${_cypress(1120, 52, 168)}
    </g>${_ground()}`; }},

  // QUMRAN — the marl terrace cut by its ravines, the caves in the face, the sea beyond it.
  bible: {ar: 'תַּנַ״ךְ', place: 'Qumran', placeAr: 'קוּמְרָאן',
    what: 'the caves above the Dead Sea', art: () => {
    const cave = (x, y, w, h, o = ' fill="var(--ink-soft)" opacity=".32" stroke="none"') =>
      `<path d="M${x} ${y}v-${h - w / 2}a${w / 2} ${w / 2} 0 0 1 ${w} 0v${h - w / 2}z"${o}/>`;
    let gully = '';                          // the ravines that cut the marl into fingers
    for (const [x, t] of [[214, 96], [452, 86], [700, 100], [946, 90]])
      gully += `<path d="M${x} 196L${x + 24} ${t}" opacity=".3"/>
                <path d="M${x + 4} 196L${x + 28} ${t}" opacity=".18"/>`;
    return `
    <g stroke="var(--ink-soft)" stroke-width="1.6" opacity=".62" fill="none">
      <path d="M0 62q220-12 480-4t720-14" opacity=".22"/>
      ${_water(68, 104, 0, 1200)}
      <path d="M0 196V118l112-26 92 18 96-30 118 24 104-28 122 26 96-22 118 20 92-14 150 26v84z"
        fill="var(--paper)"/>
      <path d="M0 118l112-26 92 18 96-30 118 24 104-28 122 26 96-22 118 20 92-14 150 26"
        stroke-width="1.9"/>
      ${gully}
      ${cave(238, 162, 42, 50)}${cave(486, 152, 36, 44)}${cave(982, 158, 38, 46)}
      ${cave(726, 148, 46, 56, ' fill="var(--ochre-wash)" stroke="var(--ochre)"')}
      <path d="M0 184q260 10 600 0t600 10" opacity=".28"/>
    </g>
    <g fill="var(--verdigris)" opacity=".5" stroke="none">
      ${_palm(64, 50)}${_palm(1152, 44)}
    </g>${_ground()}`; }},

  // TEL BE'ER SHEVA — the well at the gate, the tamarisk beside it, the dug-out tell behind.
  verbs: {ar: 'פְּעָלִים', place: 'Tel Be’er Sheva', placeAr: 'תֵּל בְּאֵר שֶׁבַע',
    what: 'the well and the tamarisk', art: () => {
    let drum = '';                           // the well head, course by course
    for (let r = 0; r < 3; r++) {
      const y = 196 - r * 16;
      drum += `<path d="M232 ${y}v-16h116v16z" fill="var(--paper)"/>`;
      for (let k = 1; k < 4; k++)
        drum += `<path d="M${232 + k * 29 - (r % 2) * 14} ${y}v-16" opacity=".4"/>`;
    }
    let tell = '';                           // the tell, excavated back into steps
    for (const [x, w, h] of [[700, 96, 26], [804, 82, 44], [894, 100, 32], [1002, 74, 52], [1084, 92, 24]]) {
      tell += `<path d="M${x} 196v-${h}h${w}v${h}" fill="var(--paper)"/>
               <path d="M${x} ${196 - h}h${w}" opacity=".5"/>`;
      for (let k = 1; k * 30 < w; k++) tell += `<path d="M${x + k * 30} 196v-${h}" opacity=".22"/>`;
    }
    return `
    <g stroke="var(--ink-soft)" stroke-width="1.6" opacity=".62" fill="none">
      ${_hills()}
      ${tell}
      <path d="M676 196v-56h24v56M776 196v-56h24v56" fill="var(--paper)" opacity=".9"/>
      ${drum}
      <ellipse cx="290" cy="148" rx="58" ry="14" fill="var(--paper)"/>
      <ellipse cx="290" cy="148" rx="42" ry="10"
        fill="var(--ochre-wash)" stroke="var(--ochre)"/>
      <path d="M238 148l24-46h56l24 46"/><path d="M262 102h56"/>
      <path d="M290 102v34" opacity=".6"/>
      <path d="M372 196q30-8 46-26" opacity=".35"/>
    </g>
    <g fill="var(--verdigris)" opacity=".5" stroke="none">
      <g transform="translate(516 196)">
        <path d="M0 0v-56M0 -32l-22-16M0 -24l24-18" stroke="var(--ink-soft)"
          stroke-width="2.4" fill="none"/>
        <path d="M-98 -56c-8-22 10-38 32-34 4-16 30-22 46-10 20-10 46 6 44 26 14 6 14 18-2 18z"/>
        <path d="M-58 -46c-4 14-2 24 2 32 4-10 3-22-2-32zM42 -48c4 14 2 24-2 32-4-10-3-22 2-32z"
          opacity=".7"/>
      </g>
      ${_cypress(1160, 44)}${_olive(112, .78)}
    </g>${_ground()}`; }},

  // MAHANE YEHUDA — the lane under its awnings, crates out front, bulbs on a wire.
  vocab: {ar: 'אוֹצַר מִלִּים', place: 'Mahane Yehuda', placeAr: 'מַחֲנֵה יְהוּדָה',
    what: 'the market, stall by stall', art: () => {
    let st = '', bulb = '';
    for (let i = 0; i < 6; i++) {                       // stalls down one side of the lane
      const x = 40 + i * 196;
      st += `<path d="M${x} 196v-58h136v58" fill="var(--paper)"/>
             <path d="M${x - 14} 138h164l-16-20H${x + 2}z" fill="var(--paper)"/>
             <path d="M${x + 16} 156h44v40h-44zM${x + 76} 154h44v18h-44zM${x + 76} 178h44v18h-44z"/>`;
    }
    for (let i = 0; i < 13; i++)
      bulb += `<circle cx="${52 + i * 92}" cy="${64 + (i % 2) * 5}" r="5"/>`;
    return `
    <g stroke="var(--ink-soft)" stroke-width="1.6" opacity=".62" fill="none">
      <path d="M0 58q300 18 600 0t600 18" opacity=".5"/>${bulb}
      ${st}
      <path d="M236 156h44v40h-44z" fill="var(--ochre-wash)" stroke="var(--ochre)"/>
      ${_fig(646, 196, .9)}${_fig(690, 196, .8)}
    </g>${_ground()}`; }},

  // BARAM — the Galilean synagogue front: three doors under one lintel, the porch in front.
  grammar: {ar: 'דִּקְדּוּק', place: 'Baram', placeAr: 'בַּרְעָם',
    what: 'the synagogue front and its columns', art: () => `
    <g stroke="var(--ink-soft)" stroke-width="1.6" opacity=".62" fill="none">
      ${_hills()}
      <path d="M330 196v-108h540v108" fill="var(--paper)"/>
      <path d="M316 88h568l-16-18H332z" fill="var(--paper)"/>
      <path d="M330 70l270-34 270 34" fill="var(--paper)"/>
      <path d="M552 196v-54a48 48 0 0 1 96 0v54" fill="var(--paper)"/>
      <path d="M568 196v-42a32 32 0 0 1 64 0v42" opacity=".5"/>
      <path d="M406 196v-50h64v50M730 196v-50h64v50" fill="var(--paper)"/>
      <path d="M398 146h80M722 146h80"/>
      <path d="M540 118h120v-16H540z" fill="var(--ochre-wash)" stroke="var(--ochre)"/>
      ${_col(372, 88)}${_col(486, 88)}${_col(700, 88)}${_col(818, 88)}
      <path d="M356 108h486v-10H356z" opacity=".55"/>
      <path d="M140 196h116v-10H140zM158 186v-10h80v10z" opacity=".5"/>
      <path d="M960 196h104v-10H960z" opacity=".5"/>
      <path d="M1092 196v-9h56v9z" opacity=".4"/>
    </g>
    <g fill="var(--verdigris)" opacity=".5" stroke="none">
      ${_olive(224, .9)}${_olive(1010, .78)}${_cypress(60, 54)}${_cypress(1164, 46)}
    </g>${_ground()}`},

  // EIN GEDI — the cliff the fall comes off, the pool under it, an ibex on the ledge.
  sounds: {ar: 'צְלִילִים', place: 'Ein Gedi', placeAr: 'עֵין גֶּדִי',
    what: 'the fall in the wilderness', art: () => {
    let strat = '';                          // the limestone, bedded in layers
    for (let k = 0; k < 7; k++)
      strat += `<path d="M0 ${58 + k * 20}q118 ${9 - k} 232 ${5 - k}" opacity="${(.5 - k * .04).toFixed(2)}"/>`;
    let fall = '';                           // the water as strands, not a slab
    for (let k = 0; k < 7; k++)
      fall += `<path d="M${330 + k * 8} 74q${k % 2 ? 10 : -10} 46 ${k % 2 ? -6 : 6} 100"
                 opacity="${(.6 - k * .06).toFixed(2)}"/>`;
    let spray = '';
    for (let k = 0; k < 9; k++)
      spray += `<circle cx="${310 + k * 17}" cy="${164 + (k % 3) * 7}" r="${2 + (k % 2)}" opacity=".34"/>`;
    return `
    <g stroke="var(--ink-soft)" stroke-width="1.6" opacity=".62" fill="none">
      <path d="M0 196V44h132v18h58v12h42l30 88z" fill="var(--paper)"/>
      <path d="M0 44h132v18h58v12h42l30 88" stroke-width="1.9"/>${strat}
      ${fall}${spray}
      <ellipse cx="372" cy="178" rx="98" ry="15"/>
      ${_water(172, 184, 288, 462)}
      <path d="M470 196q150-18 270-8t250-16 210 6" opacity=".3"/>
      <g transform="translate(150 44) scale(.9)" fill="var(--ochre-wash)" stroke="var(--ochre)">
        <path d="M-28 0v-19l10-14h32l14 14V0"/><path d="M-18 0v-10M18 0v-10" fill="none"/>
        <path d="M28 -33l12-6"/><circle cx="44" cy="-43" r="6"/>
        <path d="M47 -49q18-17 8-33M38 -51q19-14 12-32" fill="none"/>
      </g>
    </g>
    <g fill="var(--verdigris)" opacity=".5" stroke="none">
      ${_palm(556, 62)}${_palm(632, 50)}${_palm(1088, 46)}
      <path d="M288 196c-5-30 1-46 8-52 3 23 0 40-3 52zM304 196c-3-28 4-42 13-48-3 23-8 36-10 48z"/>
    </g>${_ground()}`; }},

  // TIBERIAS — the basalt shore wall, the boats, the lake, and the Galilee hills across it.
  reactions: {ar: 'תְּגוּבוֹת', place: 'Tiberias', placeAr: 'טְבֶרְיָה',
    what: 'the lake and the black shore', art: () => `
    <g stroke="var(--ink-soft)" stroke-width="1.6" opacity=".62" fill="none">
      <path d="M0 92Q220 44 470 62T860 46 1200 74" opacity=".34"/>
      ${_water(96, 150, 0, 1200)}
      <path d="M0 150h1200"/>
      ${_courses(0, 196, 1200, 46, 2, 88)}
      ${_boat(300, 140, .8, 1)}${_boat(660, 132, .62, 0)}${_boat(940, 146, .74, 1)}
      ${_house(72, 96, 50, 3, 150)}${_house(196, 84, 42, 3, 150)}
      ${_house(1044, 90, 46, 3, 150)}
      <path d="M846 150v-40h96v40" fill="var(--paper)"/>
      ${_dome(894, 110, 30, ' fill="var(--ochre-wash)" stroke="var(--ochre)"')}
      <path d="M894 80v-12"/>
    </g>
    <g fill="var(--verdigris)" opacity=".5" stroke="none">
      ${_cypress(340, 46, 150)}${_cypress(1128, 50, 150)}${_palm(1006, 44, 150)}
    </g>${_ground()}`},

  // THE JORDAN — the far bank, the water between, the near bank, and the stones set up at the ford.
  translate: {ar: 'תַּרְגּוּם', place: 'The Jordan', placeAr: 'הַיַּרְדֵּן',
    what: 'the crossing into the land', art: () => {
    const reeds = (y, n, x0, step) => {      // a fringe of cane along one bank
      let r = '';
      for (let k = 0; k < n; k++) {
        const x = x0 + k * step, h = 20 + (k % 4) * 9;
        r += `<path d="M${x} ${y}c-2-${(h * .6).toFixed(0)} 0-${(h * .8).toFixed(0)} 3-${h}"/>`;
      }
      return r; };
    return `
    <g stroke="var(--ink-soft)" stroke-width="1.6" opacity=".62" fill="none">
      ${_ridge('.22')}
      <path d="M0 116q170-14 340-4t320-10 540 8V0H0z" fill="var(--paper)"/>
      <path d="M0 116q170-14 340-4t320-10 540 8" stroke-width="1.9"/>
      ${_water(122, 164, 0, 1200)}
      <path d="M0 170q210 16 480 4t720 8" stroke-width="1.9"/>
      <path d="M0 170q210 16 480 4t720 8v26H0z" fill="var(--paper)"/>
      <path d="M0 186q210 14 480 2t720 6" opacity=".3"/>
      <g transform="translate(892 190)" fill="var(--ochre-wash)" stroke="var(--ochre)">
        <path d="M-40 0h80v-16h-80zM-31 -16h62v-15h-62zM-20 -31h40v-14h-40zM-10 -45h20v-13h-20z"/>
      </g>
    </g>
    <g fill="var(--verdigris)" opacity=".5" stroke="none">${_palm(104, 52, 116)}${_palm(1112, 46, 116)}</g>
    <g stroke="var(--verdigris)" stroke-width="1.6" opacity=".55" fill="none">
      ${reeds(116, 16, 24, 74)}${reeds(172, 15, 40, 78)}
    </g>${_ground()}`; }},

  // THE ASCENT TO JERUSALEM — the terraced hills, the road turning back on itself, the walls.
  plan: {ar: 'הַתָּכְנִית', place: 'The ascent to Jerusalem', placeAr: 'מַעֲלֵה יְרוּשָׁלַיִם',
    what: 'the road the pilgrims walked up', art: () => {
    let ter = '';                            // the terraces the hillside is cut into
    for (let k = 0; k < 6; k++)
      ter += `<path d="M0 ${192 - k * 20}q140 -${14 + k * 2} 286 -8t180 -18" opacity="${(.3 - k * .035).toFixed(2)}"/>`;
    let crn = '';
    for (let x = 672; x < 1180; x += 34) crn += `<path d="M${x} 92v-14h18v14"/>`;
    // The road is the point of this one, so it is drawn twice: a pale bed, and a firm centre
    // line on top of it, switching back three times the way the road up the Judean hills does.
    const road = 'M30 194q86-6 150-24t100-40 130-16 118-30 122-8';
    return `
    <g stroke="var(--ink-soft)" stroke-width="1.6" opacity=".62" fill="none">
      <path d="M0 196Q300 122 640 104T1200 92" opacity=".28"/>
      ${ter}
      <path d="${road}" stroke-width="13" opacity=".16" stroke-linecap="round"/>
      <path d="${road}" opacity=".7"/>
      <path d="${road}" stroke-dasharray="10 16" opacity=".35"/>
      <path d="M664 196V92h520v104" fill="var(--paper)"/><path d="M664 92h520"/>${crn}
      <path d="M704 196v-66h62v66M1082 196v-66h62v66" fill="var(--paper)"/>
      <path d="M694 130h82M1072 130h82"/>
      <path d="M712 78v-13h18v13M1090 78v-13h18v13" opacity=".6"/>
      <path d="M876 196v-60a46 46 0 0 1 92 0v60"
        fill="var(--ochre-wash)" stroke="var(--ochre)"/>
      <path d="M898 196v-40a24 24 0 0 1 48 0v40" opacity=".45"/>
      ${_house(786, 66, 36, 3)}${_house(996, 62, 34, 3)}
    </g>
    <g fill="var(--verdigris)" opacity=".5" stroke="none">
      ${_olive(140, .78)}${_olive(392, .68)}${_cypress(566, 50)}${_cypress(616, 42)}
      ${_olive(1168, .6)}
    </g>${_ground()}`; }},

  // YAVNE — the study hall, its arcade, and the scroll open on the reader's desk.
  tutor: {ar: 'מוֹרֶה', place: 'Yavne', placeAr: 'יַבְנֶה',
    what: 'the academy that outlived the Temple', art: () => {
    let arc = '';
    for (let i = 0; i < 5; i++) arc += _arch(150 + i * 132, 96, 74);
    let bench = '';
    for (let i = 0; i < 4; i++)
      bench += `<path d="M${196 + i * 132} 196v-20h60v20M${196 + i * 132} 176h60" opacity=".45"/>`;
    return `
    <g stroke="var(--ink-soft)" stroke-width="1.6" opacity=".62" fill="none">
      ${_hills()}
      <path d="M120 196v-136h692v136" fill="var(--paper)"/>
      <path d="M108 60h716l-16-18H124z" fill="var(--paper)"/>
      ${arc}${bench}
      <path d="M880 196v-64h190v64" fill="var(--paper)" opacity=".9"/>
      <path d="M868 132h214"/>
      <g transform="translate(975 130)" fill="var(--ochre-wash)" stroke="var(--ochre)">
        <path d="M-62 0q62-18 124 0-62 12-124 0z"/>
        <path d="M-62 0v-8q62-18 124 0v8"/>
        <path d="M-70 -6a8 8 0 0 1 16 0v8a8 8 0 0 1-16 0zM54 -6a8 8 0 0 1 16 0v8a8 8 0 0 1-16 0z"/>
      </g>
    </g>
    <g fill="var(--verdigris)" opacity=".5" stroke="none">
      ${_cypress(60, 58)}${_cypress(1136, 54)}${_olive(1116, .7)}
    </g>${_ground()}`; }},

  // MISHKENOT SHA'ANANIM — the windmill, the first row of houses built outside the walls.
  account: {ar: 'חֶשְׁבּוֹן', place: 'Mishkenot Sha’ananim', placeAr: 'מִשְׁכְּנוֹת שַׁאֲנַנִּים',
    what: 'the windmill outside the walls', art: () => {
    let win = '';                            // the long almshouse row, arched window by window
    for (let i = 0; i < 9; i++) {
      const x = 630 + i * 58;
      win += `<path d="M${x} 196v-40a15 15 0 0 1 30 0v40"/>`;
    }
    return `
    <g stroke="var(--ink-soft)" stroke-width="1.6" opacity=".62" fill="none">
      ${_hills()}
      <path d="M600 196v-84h530v84" fill="var(--paper)"/>
      <path d="M588 112h554l-14-16H602z" fill="var(--paper)"/>
      ${win}
      <path d="M264 196l22-118h56l22 118z" fill="var(--paper)"/>
      <path d="M280 100h68M272 140h92M268 168h100" opacity=".45"/>
      <path d="M280 78h68l-34-22z" fill="var(--paper)"/>
      <g transform="translate(314 66)">
        <path d="M0 0v-46M0 0v46M0 0h-46M0 0h46" opacity=".7"/>
        <path d="M-5 -46h10v40h-10zM-5 6h10v40h-10zM-46 -5h40v10h-40zM6 -5h40v10h-40z"
          opacity=".45"/>
      </g>
      <path d="M760 196v-40a15 15 0 0 1 30 0v40" fill="var(--ochre-wash)" stroke="var(--ochre)"/>
    </g>
    <g fill="var(--verdigris)" opacity=".5" stroke="none">
      ${_cypress(462, 62)}${_cypress(510, 50)}${_cypress(1168, 54)}${_olive(140, .8)}
    </g>${_ground()}`; }},
};
})();

defineLang({
  code: 'he',

  // Each tier is described by the gate that admits a story to it (pipeline/he_stories.py), not
  // by how it felt to write one. Advanced makes two claims the tier below cannot: two clauses
  // in most sentences, where intermediate manages that in 38% and beginner in 3%; and a fifth
  // of its words new to the app, so the top tier is the one still teaching vocabulary.
  storyLevels: [
    ['beginner',     'Beginner',     'Short present-tense sentences about an ordinary day.'],
    ['intermediate', 'Intermediate', 'Past tense, small plots, one thought a sentence.'],
    ['advanced',     'Advanced',     'Two clauses a sentence, and words you have not met yet.'],
  ],

  lex: {
    // Hebrew's index is a dictionary in its own right, built from Wiktionary rather than from
    // any text the app ships -- so the corpus, empty or not, cannot stand in for it.
    source: 'lexicon',
    usage: 'ordinary modern spoken Hebrew, which varies by speaker and register',
    name: 'Wiktionary',
    blurb: 'a 12,662-lemma Hebrew lexicon with the pointing, the binyan and the root',
    credit: '<b>English Wiktionary</b> via <a href="https://kaikki.org/dictionary/Hebrew/" '
          + 'target="_blank" rel="noopener" style="color:var(--verdigris)">kaikki.org</a>, '
          + 'CC BY-SA 4.0 — extracted by spike/he/build_lex.py, pronunciation from the pointing.',
  },

  // ---- the writing system ---------------------------------------------------------------
  script: {
    // MUST match he_norm() in spike/he/build_lex.py, which keyed the shipped lexicon: strip
    // cantillation and pointing, drop geresh and gershayim, fold the five final letters.
    // pipeline/verify_he_norm.py compares the two over every key in the index.
    //
    // Deliberately NOT folding ktiv male/haser — the optional yod and vav of unpointed spelling.
    // That is a real ambiguity, and folding it would merge distinct words.
    norm: s => (s || '').normalize('NFC')
      .replace(/[֑-ׇ]/g, '')
      .replace(/[׳״]/g, '')
      .replace(/[ךםןףץ]/g,
               c => 'כמנפצ'['ךםןףץ'.indexOf(c)])
      .trim(),
    run: /([֐-׿יִ-ﭏ][\s֐-׿יִ-ﭏ]*)/,
    // Does a string contain any Hebrew? Asked wherever the app has to tell "the learner
    // typed the target language" from "the learner typed English".
    chars: /[֐-׿יִ-ﭏ]/,
    punct: '.,;:?!…"«»“”\'()-—[]{}–׳״',
    // Hebrew's clitics are a SLOT SYSTEM, not a list of glued words: a conjunction, then a
    // preposition or the relativizer, then the article — וְשֶׁבַּבַּיִת is ו+ש+ב+ה. Shortest first,
    // so the least is cut away; the peeling algorithm itself is language-generic.
    pre: ['ו', 'ב', 'כ', 'ל', 'מ', 'ש', 'ה',
          'וה', 'וב', 'ול', 'ומ', 'וש',
          'שב', 'של', 'שה', 'כש', 'מש',
          'וכש', 'לכש'],
    // Pronominal endings: possessive on nouns, object on verbs and prepositions.
    suf: ['י', 'ך', 'כ', 'ו', 'ה', 'ם', 'ן',
          'נו', 'כם', 'כן', 'הם', 'הן',
          'יו', 'יה', 'יך', 'ים'],
    minStem: 2,                 // Hebrew roots are three letters, but a stem can surface as two
    fixes: {},                  // nothing corrected yet — the honest state before real content
  },

  // No sub-dialect axis. Israeli Hebrew has regional and register variation, but nothing with
  // the systematic, per-phoneme shape Wadi Ara has on the Arabic side, so nothing is claimed.
  phon: {
    fields: {main: 'caphi', urban: 'caphi', raw: 'caphi_raw'},
    variants: [],
  },

  // ---- the verb model -------------------------------------------------------------------
  verb: {
    // THE INFINITIVE, not the 3ms past. Arabic files a verb under its past because it has no
    // infinitive to file it under; Hebrew has one, לִכְתּוֹב, and it is what a Hebrew dictionary
    // lists, what a learner is taught to say, and what survives when a verb has no attested past
    // in the lexicon at all. The binyan names are still built on the past -- that is why the
    // Past column and the binyan blurbs below say כָּתַב -- but the CARD is the infinitive.
    cite: 'inf',
    citeNote: 'the infinitive, the form a Hebrew dictionary lists',
    // Infinitive first, because that is what the deck banks and what a dictionary lists.
    // The past stays beside it: the binyan names are built on it and it is the paradigm's
    // own base, so a learner needs to see both on the same card.
    summary: [['inf', 'Infinitive'], ['past', 'Past'], ['pres', 'Present']],
    classNoun: 'binyan',
    classPlural: 'Binyanim',
    blurb: n => `Hebrew verbs are built on three-letter roots, run through seven patterns called
      <b>binyanim</b> — "buildings". The binyan sets the voice and the flavour of the action;
      the root supplies the meaning. Browse by binyan below, or search across all ${n} verbs.
      Every paradigm here is looked up, fully pointed, from Wiktionary — none of it is derived.`,
    weakBlurb: '',
    // The same renderer as Arabic, driven by a different descriptor. Hebrew's present is four
    // cells (gender × number, no person) where Arabic's is eight, and the infinitive is a single
    // cell — both fall out of the renderer's one rule, skip any row or table with no filled
    // cells, with no `if (LANG.code === 'he')` anywhere in the UI.
    rowSets: {
      pres: [['ms', 'he / I (m)', 'הוא'], ['fs', 'she / I (f)', 'היא'],
             ['mp', 'they (m)', 'הם'], ['fp', 'they (f)', 'הן']],
      imp: [['ata', 'you (m)', 'אתה'], ['at', 'you (f)', 'את'],
            ['atem', 'you (pl)', 'אתם']],
      inf: [['-', 'to …', '']],
    },
    tables: [
      {kind: 'grid', rows: 'persons', cols: [
        {slot: 'past', label: 'Past', short: 'Past'},
        {slot: 'fut',  label: 'Future', short: 'Fut.'}]},
      // Hebrew's present is a participle: it inflects for gender and number, never for person,
      // so "I write / you write / he writes" are one form.
      {kind: 'strip', label: 'Present (gender and number, not person)', rows: 'pres', slot: 'pres'},
      {kind: 'strip', full: true, label: 'Imperative', rows: 'imp', slot: 'imp'},
      {kind: 'strip', full: true, label: 'Infinitive', rows: 'inf', slot: 'inf'},
    ],
    classOrder: ['paal', 'piel', 'hifil', 'nifal', 'hitpael', 'pual', 'hufal'],
    classInfo: {
      paal:    ['Paʿal', 'The base verb — the plain action, and much the biggest group. כָּתַב “he wrote”.'],
      piel:    ['Piʿel', 'Doubled middle root letter. Often intensive, or makes a verb from a noun — דִּבֵּר “he spoke”.'],
      hifil:   ['Hifʿil', 'A hi- prefix. Causative: making someone do the thing — הִכְתִיב “he dictated”.'],
      nifal:   ['Nifʿal', 'An n- prefix. Passive or middle voice of paʿal — נִכְתַב “it was written”.'],
      hitpael: ['Hitpaʿel', 'A hit- prefix. Reflexive or reciprocal — הִתְכַתֵּב “he corresponded”.'],
      pual:    ['Puʿal', 'The passive of piʿel. Mostly met in the present, as a participle — מְדֻבָּר “spoken”.'],
      hufal:   ['Hufʿal', 'The passive of hifʿil. Rare in speech; you meet it in writing and the news.'],
    },
    // No separate weak axis yet. Hebrew's gzarot (פ"נ, ע"ו, ל"ה …) are real and worth teaching, but
    // Wiktionary does not label them and deriving them is its own piece of work. An empty table
    // means no badge and no "irregular" shelf — absent rather than guessed.
    weakInfo: {},
    weakOrder: [],
    persons: [
      ['ani', 'I', 'אֲנִי'], ['ata', 'you (m)', 'אַתָּה'],
      ['at', 'you (f)', 'אַתְּ'], ['hu', 'he', 'הוּא'],
      ['hi', 'she', 'הִיא'], ['anaxnu', 'we', 'אֲנַחְנוּ'],
      ['atem', 'you (pl)', 'אַתֶם'], ['hem', 'they', 'הֵם'],
    ],
    // Difficulty tracks the BINYAN, which is the whole reason this is a function per pack rather
    // than a table shared with Arabic: paʿal is where everyone starts, the passives are last
    // because they are mostly read rather than said.
    tier: v => ({paal: 1, nifal: 2, piel: 2, hifil: 2, hitpael: 3, pual: 3, hufal: 3})[v.form] || 2,
  },

  // Where the plan is trying to get you. Deliberately smaller than Arabic's "a Palestinian
  // family dinner": this curriculum is three phases long because that is how much content
  // exists, and the goal has to be the one it can actually reach.
  planEnd: 'the shelf',
  planGoal: 'to reading published Hebrew \u2014 a chapter of it \u2014 with nothing adjusted to fit you',
  booksBlurb: 'Published Hebrew, not written for you \u2014 short stories from the public '
    + 'domain, transcribed with their vowels by Project Ben-Yehuda\u2019s volunteers and let onto '
    + 'this shelf only if they read like present-day Hebrew rather than like scripture. Every '
    + 'sentence is theirs, verbatim; the English is ours. Tap any word.',
  assessGreetings: '\u05e9\u05dc\u05d5\u05dd, \u05ea\u05d5\u05d3\u05d4, the basics',

  // ---- keyboard, voice ------------------------------------------------------------------
  kbd: {
    toggle: 'א', title: 'Hebrew keyboard',
    numsLabel: '123', lettersLabel: 'א ב ג',
    diacritic: 'ַ', diacriticLabel: 'ִַָ',
    // The standard Israeli layout, which is the one a Hebrew speaker's fingers already know.
    letters: [
      ['ק', 'ר', 'א', 'ט', 'ו', 'ן', 'ם', 'פ'],
      ['ש', 'ד', 'ג', 'כ', 'ע', 'י', 'ח', 'ל', 'ך', 'ף'],
      ['ז', 'ס', 'ב', 'ה', 'נ', 'מ', 'צ', 'ת', 'ץ'],
    ],
    nums: [
      ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
      ['-', '/', ':', ';', '(', ')', '%', '&', '@', '"'],
      [',', '.', '?', '!', '׳', '״', '–'],
    ],
    hold: {
      'כ': ['ך'], 'מ': ['ם'], 'נ': ['ן'],
      'פ': ['ף'], 'צ': ['ץ'],
      // The pointing, on one key: the vowels, then shva, then dagesh.
      'ַ': ['ַ', 'ָ', 'ֵ', 'ֶ', 'ִ', 'ֹ', 'ֻ', 'ְ', 'ּ'],
    },
  },
  tts: {lang: 'he-IL', voiceRe: /^he/i},
  searchHint: 'בית · הלך · house · tired…',
  ornament: () => mosaic(),
  skyline: () => HE_SKYLINE,
  // Hebrew day and month names as Israelis write them: יום ראשון … and the Gregorian months,
  // which is what a calendar in Israel actually says. The Hebrew calendar's own months are a
  // different thing and are not what a date line means here.
  dateLine: d => {
    const DAYS = ['יוֹם רִאשׁוֹן', 'יוֹם שֵׁנִי', 'יוֹם שְׁלִישִׁי', 'יוֹם רְבִיעִי',
                  'יוֹם חֲמִישִׁי', 'יוֹם שִׁישִׁי', 'שַׁבָּת'];
    const MONTHS = ['יָנוּאָר', 'פֶבְּרוּאָר', 'מֶרְץ', 'אַפְּרִיל', 'מַאי', 'יוּנִי',
                    'יוּלִי', 'אוֹגוּסְט', 'סֶפְּטֶמְבֶּר', 'אוֹקְטוֹבֶּר', 'נוֹבֶמְבֶּר', 'דֶּצֶמְבֶּר'];
    return DAYS[d.getDay()] + ', ' + d.getDate() + ' ' + MONTHS[d.getMonth()];
  },

  homeMasthead: () => `<div class="hm-mark">עִבְרִית <em>מְדֻבֶּרֶת</em></div>`,
  chapterPrefix: /^פרק[^—]*—\s*/,

  bibleBlurb: 'ESV ‖ Hebrew, side by side',
  bible: {
    // The Hebrew Bible is a different proposition from the Arabic one, and the page should say
    // so. The Arabic side offers a 19th-century TRANSLATION; the Hebrew Old Testament is the
    // text itself, in the language, already pointed — the strongest reading material in the
    // whole app. What it is not is the language this app teaches, and that has to be as loud.
    intro: 'Read Scripture side by side — <b>ESV</b> in English on the left, Hebrew on the '
         + 'right. The Old Testament is the <b>Westminster Leningrad Codex</b>: not a '
         + 'translation but the original, fully pointed. The New Testament is Franz '
         + 'Delitzsch\u2019s Hebrew, and is written unpointed, the way Hebrew usually is. '
         + 'Tap a book, then a chapter.',
    credit: 'Hebrew: Westminster Leningrad Codex (Old Testament) and Delitzsch, 1877 (New '
          + 'Testament) — both public domain.',
    note: 'Biblical Hebrew is not the Hebrew this app teaches. It is the same language three '
        + 'thousand years apart, and an Israeli reads it the way an English speaker reads '
        + 'Chaucer — recognisably their own, and not how they talk. Read it for the letters, '
        + 'the roots and the pleasure of it.',
    wordNote: '<b>Biblical Hebrew, not modern speech.</b> The meaning above comes from the '
            + 'lexicon and is here to help you read — but the word isn\u2019t added to your '
            + 'vocabulary, which stays modern spoken Hebrew.',
    // No spoken-Hebrew edition to link out to; the Arabic side has one and this does not.
    chapterLink: null,
  },
  tutorStarters: [
    'What’s the difference between לא and אין?',
    'How do I say “I’ve been waiting for an hour” in everyday Hebrew?',
    'When do Israelis actually use the future tense for a request?',
    'Give me 3 natural things to say when someone cooks me a great meal.',
    'Is היננו something people say, or only write?',
  ],

  tutorPrompt: ({grammar, sounds, reactions}) => {
    const gram = grammar.map(l => l.title).filter(Boolean).slice(0, 24).join('; ');
    const snds = sounds.map(L => L.target || L.en).filter(Boolean).join('; ');
    const rxc = reactions.map(c => c.en).filter(Boolean).join('; ');
    return [
      "You are a warm, precise tutor for MODERN SPOKEN ISRAELI HEBREW — the everyday speech of Tel Aviv, Jerusalem and Haifa. The learner is an English speaker in a self-study app, working toward holding their own in ordinary conversation.",
      "",
      "How to answer:",
      "- Answer in SPOKEN Israeli Hebrew, not Biblical or literary Hebrew. Where the spoken form differs from the written register, give the spoken one and note the difference briefly. If the learner's phrase is Biblical or bookish, say so gently and give what people actually say.",
      "- For any Hebrew you give: pointed Hebrew script, then a simple transliteration in parentheses, then the English gloss. Point the Hebrew — the pointing is what makes it readable, and this app shows it everywhere.",
      "- Pronunciation model to reflect in transliterations: ר is uvular; ח and כ (without dagesh) are both a throaty kh; ע and א are silent for most speakers; צ is ts; stress is usually final (milra). e.g. שָׁלוֹם = shaLOM, בֹּקֶר טוֹב = BOker tov.",
      "- Honesty first: if you're not sure something is current spoken usage rather than textbook Hebrew, say so plainly. Never invent a proverb, a “Israelis always say…”, or confident detail you're unsure of.",
      "- You can explain grammar, translate, compare near-synonyms, give example sentences, and role-play short exchanges. Match the learner's level; be encouraging and concrete.",
      "",
      "SAVING PHRASES (important): when your answer teaches a specific Hebrew word or phrase the learner can reuse — above all for “how do I say…” questions — finish your ENTIRE reply with a machine-readable block listing the 1–4 most useful save-worthy items, each on its own line as “Hebrew = English” (Hebrew script only in this block, NO transliteration):",
      "<save>",
      "אֲנִי רוֹצֶה = I want",
      "אֲנִי רוֹצֶה לָלֶכֶת הַבַּיְתָה = I want to go home",
      "</save>",
      "Only list phrases genuinely worth memorizing as-is. For a pure grammar explanation with no single save-worthy phrase, omit the block entirely. Write nothing after </save>.",
      "",
      "This app already teaches the learner these things — reference them naturally, don't just list them:",
      "• Grammar structures: " + (gram || "(various spoken structures)"),
      "• Pronunciation contrasts: " + (snds || "(Israeli sound contrasts)"),
      "• Conversational reaction categories: " + (rxc || "(everyday reactions)"),
    ].join("\n");
  },

  art: HE_ART,
});
