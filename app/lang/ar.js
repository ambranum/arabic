/* Palestinian Arabic language pack.  Loaded before app.js; registers itself via defineLang().

   Everything here is what makes the app ARABIC rather than what makes it an app: the writing
   system's rules, the verb model, the keyboard, the tutor's brief, and the seventeen section
   banners. app.js reads all of it through LANG and contains no Arabic of its own.

   The Hebrew pack is app/lang/he.js and answers the same shape. */
(() => {
  const {_hills, _ridge, _ground, _house, _arch, _cypress, _olive, _fig, _palm, _water, _boat, _minaret, _dome, _col} = SCN;

  // ---------- home artwork ----------
  // The app ships as one folder with no external assets, so the homepage's "pictures" are inline
  // SVG drawn in the theme's own variables: they recolor themselves in dark mode, weigh nothing,
  // and carry no licence. Two pieces: a tatreez band (Palestinian cross-stitch — the diamond
  // motif), and a Jerusalem skyline with the Dome of the Rock, drawn as a line engraving.
  let _tzN = 0;
  function tatreez() {
    const id = 'tz' + (_tzN++);                       // pattern ids are document-global
    return `<svg class="tz" height="16" aria-hidden="true"><defs>
      <pattern id="${id}" width="32" height="16" patternUnits="userSpaceOnUse">
        <rect x="12" y="4" width="8" height="8" transform="rotate(45 16 8)" fill="var(--rubric)"/>
        <rect x="14.6" y="6.6" width="2.8" height="2.8" transform="rotate(45 16 8)" fill="var(--paper)"/>
        <rect x="0" y="6.7" width="2.6" height="2.6" transform="rotate(45 1.3 8)" fill="var(--verdigris)"/>
        <rect x="29.4" y="6.7" width="2.6" height="2.6" transform="rotate(45 30.7 8)" fill="var(--verdigris)"/>
        <rect x="0" y="0" width="32" height="1.4" fill="var(--ochre)"/>
        <rect x="0" y="14.6" width="32" height="1.4" fill="var(--ochre)"/>
      </pattern></defs>
      <rect width="100%" height="16" fill="url(#${id})"/></svg>`;
  }
  // Jerusalem, looking at the Old City: hills, the wall, cypresses and olives, a minaret, and the
  // Dome of the Rock. Strokes only, one accent fill on the dome — an engraving, not a postcard.
  const HOME_SKYLINE = `<svg class="hm-sky" viewBox="0 0 1200 210" preserveAspectRatio="xMidYMax meet"
     fill="none" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
    <g stroke="var(--ink-soft)" stroke-width="1.6" opacity=".62">
      <path d="M0 190 Q180 148 380 166 T760 158 T1200 172" opacity=".45"/>
      <path d="M0 208 Q240 180 520 194 T1200 196"/>
      <circle cx="1010" cy="52" r="24" fill="var(--ochre-wash)" stroke="var(--ochre)"/>
      <path d="M120 196v-32h34v32M124 164v-7h6v7M137 164v-7h6v7M150 164v-7h6v7"/>
      <path d="M690 196v-26h30v26M694 170v-6h5v6M705 170v-6h5v6M716 170v-6h5v6"/>
      <path d="M580 196V86m22 110V86M580 92h22M580 86l11-12 11 12M585 120h12M584 146h14"/>
      <path d="M591 62l0-10m0 0a4 4 0 1 1 3-7" stroke="var(--ochre)"/>
      <path d="M575 120h32l-4 8h-24z" opacity=".8"/>
      <path d="M244 196v-60l26-14v74M250 148v-10h7v10M262 148v-10h7v10"/>
      <path d="M840 196v-44h56v44M848 176v-24a8 8 0 0 1 16 0v24M872 176v-24a8 8 0 0 1 16 0v24"/>
      <path d="M950 196v-30h40v30M958 186v-20a6 6 0 0 1 12 0v20"/>
    </g>
    <g>
      <path d="M292 196v-58h136v58" stroke="var(--ink-soft)" stroke-width="1.8"/>
      <path d="M300 138l60-26 68 26" stroke="var(--ink-soft)" stroke-width="1.8"/>
      <path d="M316 196v-26a9 9 0 0 1 18 0v26M356 196v-26a9 9 0 0 1 18 0v26M396 196v-26a9 9 0 0 1 18 0v26"
         stroke="var(--ink-soft)" stroke-width="1.6" opacity=".8"/>
      <path d="M312 112 C312 74 344 52 360 46 C376 52 408 74 408 112"
         fill="var(--ochre-wash)" stroke="var(--ochre)" stroke-width="2.2"/>
      <path d="M360 46V30m0 0a5 5 0 1 1 4-8" stroke="var(--ochre)" stroke-width="2"/>
      <path d="M322 112c8-4 68-4 76 0" stroke="var(--ochre)" stroke-width="1.6" opacity=".7"/>
    </g>
    <g fill="var(--verdigris)" opacity=".5" stroke="none">
      <path d="M96 196c0-30 10-52 14-58 4 6 14 28 14 58z"/>
      <path d="M198 196c0-24 8-42 11-47 3 5 11 23 11 47z"/>
      <path d="M478 196c0-34 11-58 15-64 4 6 15 30 15 64z"/>
      <path d="M772 196c0-26 8-45 12-50 4 5 12 24 12 50z"/>
      <path d="M1084 196c0-22 7-38 10-43 3 5 10 21 10 43z"/>
      <path d="M1150 178c-10-2-16-10-16-18 6-4 16-4 22 2 6-6 16-6 22-2 0 8-6 16-16 18v18h-12z" opacity=".9"/>
    </g>
    <path d="M0 196h1200" stroke="var(--ink-soft)" stroke-width="1.8" opacity=".7"/>
  </svg>`;

  // ---------- section heroes ------------------------------------------------------------------
  // The home page has a visual identity — a broadsheet masthead, a tatreez band, the Old City on
  // the horizon — and every other page opened as a bare list. Each section now gets its own
  // header: its name set large in Arabic, over a drawing of a real Palestinian place.
  //
  // One skeleton, so the app still feels like one app: wordmark, English label, then a full-bleed
  // band of art, and a small note in the corner saying where the drawing is. Only the scene and
  // the group colour change.
  // ---------- section banners ----------------------------------------------------------------
  // Drawn the same way as the Old City on the home page, because that is the one everybody liked:
  // one viewBox (1200x210), hills behind, a ground line at y=196, buildings as plain strokes,
  // trees as verdigris silhouettes, and exactly ONE ochre accent per scene — the thing your eye
  // should land on. An engraving, not a postcard.
  //
  // Every scene is a REAL PLACE, and says which one in the corner: Jaffa's harbour, the sea wall
  // at Akka, Nazareth stepped up its hill, the Bahá'í terraces over Haifa bay, the Roman street
  // at Sebastia, the oldest olive tree at al-Walaja, Battir's terraces, the covered souq in
  // al-Khalil, Damascus Gate, Ramallah's Manara, the Gaza shore, Bethlehem's rooftops, the lake
  // at Tabariyya, the Jordan, Jericho's palms, Nablus and its soap works, and Wadi Ara — the
  // valley whose accent this app keeps telling you about. Coast, Galilee, the hills and the
  // valley, so the set is the whole country and not one postcard of it.
  //
  // Where a section has an obvious home it gets it: verbs grow from a root, so verbs get the
  // ancient olive; grammar is structure, so grammar gets a colonnade; translation is a crossing,
  // so it gets the river with both banks.
  const SEC_ART = {
    // NAZARETH — the old town stepped up its hill, the basilica's lantern, a minaret.
    stories: {ar: 'قِصَص', place: 'Nazareth', placeAr: 'النَّاصِرة',
      what: 'the old town on its hill', art: () => `
      <g stroke="var(--ink-soft)" stroke-width="1.6" opacity=".62" fill="none">
        <path d="M0 196Q250 124 500 116T1200 188" opacity=".38"/>
        ${_house(30, 88, 44, 3, 182)}${_house(140, 82, 42, 3, 160)}${_house(248, 76, 40, 2, 142)}
        ${_house(770, 84, 44, 3, 134)}${_house(884, 90, 48, 3, 146)}${_house(1002, 86, 44, 3, 164)}
        <path d="M380 124v-56h200v56" fill="var(--paper)"/><path d="M368 68h224"/>
        <path d="M406 124v-32a24 24 0 0 1 48 0v32M506 124v-32a24 24 0 0 1 48 0v32"/>
        <path d="M440 68v-18h80v18z" fill="var(--paper)"/>
        <path d="M452 50l28-42 28 42z" fill="var(--ochre-wash)" stroke="var(--ochre)"/>
        ${_minaret(690, 102, 130)}
        ${_house(120, 104, 56, 3)}${_house(300, 116, 62, 4)}${_house(646, 108, 58, 4)}
        ${_house(830, 104, 54, 3)}${_house(980, 96, 50, 3)}
      </g>
      <g fill="var(--verdigris)" opacity=".5" stroke="none">
        ${_cypress(232, 44, 142)}${_cypress(618, 46, 132)}${_cypress(96, 58)}${_cypress(778, 52)}
        ${_olive(440, .8)}${_olive(1130, .9)}
      </g>${_ground()}`},

    // DAMASCUS GATE — the wall, the crenellations, the steps down into the Old City.
    news: {ar: 'أخْبار', place: 'Damascus Gate', placeAr: 'باب العامود',
      what: 'the way into the Old City', art: () => {
      let m = ''; for (let x = 4; x < 1200; x += 40) m += `<path d="M${x} 100v-15h22v15"/>`;
      let st = ''; for (let i = 0; i < 3; i++)
        st += `<path d="M${492 + i * 22} ${196 - i * 6}h${216 - i * 44}" opacity="${(.45 - i * .1).toFixed(2)}"/>`;
      return `
      <g stroke="var(--ink-soft)" stroke-width="1.6" opacity=".62" fill="none">
        <path d="M0 196v-96h1200v96" fill="var(--paper)" opacity=".9"/><path d="M0 100h1200"/>${m}
        <path d="M430 196v-128h84v128" fill="var(--paper)"/>
        <path d="M686 196v-128h84v128" fill="var(--paper)"/>
        <path d="M422 68h100M678 68h100"/>
        <path d="M436 54v-12h20v12M478 54v-12h20v12M692 54v-12h20v12M734 54v-12h20v12"/>
        <path d="M430 68v-14h84M686 68v-14h84" opacity=".5"/>
        <path d="M540 196v-58l60-52 60 52v58" fill="var(--paper)"/>
        <path d="M558 196v-44a42 42 0 0 1 84 0v44"/>
        <path d="M600 108v18"/>
        <circle cx="600" cy="138" r="11" fill="var(--ochre-wash)" stroke="var(--ochre)"/>
        ${st}
        <path d="M170 196v-58h116v58" fill="var(--paper)"/>
        <path d="M156 138h144l-14-15H170z" fill="var(--paper)"/>
        <path d="M186 154h42v42h-42zM244 152h34v18h-34zM244 176h34v18h-34z"/>
        <path d="M194 162h26M194 172h26M194 182h18" opacity=".5"/>
        ${_fig(346, 196, .95)}${_fig(860, 196, 1)}${_fig(906, 196, .85)}
      </g>
      <g fill="var(--verdigris)" opacity=".5" stroke="none">${_cypress(104, 56)}${_cypress(1050, 52)}</g>
      ${_ground()}`; }},

    // AKKA — Khan al-Umdan's arcaded court, its clock tower, and the harbour beyond the wall.
    books: {ar: 'كُتُب', place: 'Akka', placeAr: 'عكّا',
      what: 'Khan al-Umdan and the harbour', art: () => {
      let a = '', c = '';
      for (let i = 0; i < 6; i++) a += _arch(120 + i * 112, 86, 74);
      for (let i = 0; i < 7; i++) c += `<path d="M${112 + i * 112} 196v-82h16v82"/>`;
      return `
      <g stroke="var(--ink-soft)" stroke-width="1.6" opacity=".62" fill="none">
        ${_hills()}
        <path d="M96 196V66h740v130" fill="var(--paper)" opacity=".9"/>
        <path d="M96 66h740M96 54h740" opacity=".75"/>
        ${a}${c}
        <path d="M120 148h692" opacity=".28"/>
        <path d="M846 196v-146h74v146" fill="var(--paper)"/><path d="M838 50h90"/>
        <path d="M854 50v-16h58v16"/>${_dome(883, 34, 29)}<path d="M883 5v-9"/>
        <circle cx="883" cy="104" r="21" fill="var(--ochre-wash)" stroke="var(--ochre)"/>
        <path d="M883 104v-13M883 104l11 7" stroke="var(--ochre)"/>
        <path d="M940 172h260" opacity=".5"/>
        ${_water(180, 194, 940, 1200)}
        ${_boat(1064, 190, .78, 0)}
      </g>
      <g fill="var(--verdigris)" opacity=".5" stroke="none">${_cypress(60, 60)}${_olive(1160, .8, 166)}</g>
      ${_ground()}`; }},

    // AL-WALAJA — al-Badawi, reckoned the oldest olive tree in Palestine. A verb has a root too.
    verbs: {ar: 'أفْعال', place: 'Al-Walaja', placeAr: 'الوَلَجة',
      what: 'al-Badawi, the oldest olive tree', art: () => `
      <g stroke="var(--ink-soft)" stroke-width="1.6" opacity=".62" fill="none">
        ${_hills()}
        <path d="M700 196v-16h160v16M860 180v-16h170v16M1030 164v-16h170v16" opacity=".42"/>
        <path d="M40 196v-14h150v14M190 182v-14h160v14" opacity=".42"/>
        <path d="M552 196v-66c-17-13-21-31-11-42" stroke-width="3.2"/>
        <path d="M604 196v-72c17-13 23-29 17-40" stroke-width="3.2"/>
        <path d="M558 130c-11 17-31 25-48 21M600 124c13 15 33 19 48 13" stroke-width="2.4"/>
        <path d="M546 196c-21-4-39 0-51 11M556 196c-15 2-27 9-35 17M612 196c19-7 39-3 51 9M602 196c15 4 25 11 31 19"
          stroke-width="1.8" opacity=".68"/>
        ${_house(232, 74, 44, 3, 168)}${_house(1058, 84, 50, 3, 148)}
        <circle cx="240" cy="50" r="21" fill="var(--ochre-wash)" stroke="var(--ochre)"/>
      </g>
      <g fill="var(--verdigris)" opacity=".5" stroke="none">
        <path d="M484 126c0-45 39-69 94-69s94 24 94 69c-26 16-162 16-188 0z"/>
        ${_olive(360, 1.05)}${_olive(790, .95)}${_olive(920, .8, 180)}${_cypress(1140, 56, 148)}
      </g>${_ground()}`},

    // AL-KHALIL — the covered souq: the mesh overhead, a lamp, and a shelf of Hebron glass.
    vocab: {ar: 'كَلِمات', place: 'Al-Khalil (Hebron)', placeAr: 'الخَليل',
      what: 'the covered souq', art: () => {
      let mesh = ''; for (let x = 236; x <= 966; x += 26) mesh += `<path d="M${x} 58l20-20" opacity=".2"/>`;
      let jars = ''; [478, 528, 582, 640, 692].forEach((x, i) => { const r = 14 + (i % 3) * 3;
        jars += `<circle cx="${x}" cy="${150 - r}" r="${r}"/><path d="M${x - 5} ${150 - 2 * r}v-8h10v8"/>`; });
      let cr = ''; let cx = 300;
      for (let i = 0; i < 3; i++) { const w = 96, h = 34 + (i % 2) * 9;
        cr += `<path d="M${cx} 196v-${h}h${w}v${h}z"/><path d="M${cx} ${196 - h + 12}h${w}"/>`;
        for (let j = 0; j < 4; j++) cr += `<circle cx="${cx + 15 + j * 22}" cy="${196 - h - 7}" r="8"/>`;
        cx += w + 12; }
      return `
      <g stroke="var(--ink-soft)" stroke-width="1.6" opacity=".62" fill="none">
        ${_hills()}
        <path d="M50 196V56h190v140M960 196V56h190v140" fill="var(--paper)" opacity=".9"/>
        ${_arch(248, 88, 92)}${_arch(360, 88, 92)}${_arch(752, 88, 92)}${_arch(864, 88, 92)}
        <path d="M236 58h730M236 38h730" opacity=".35"/>${mesh}
        <path d="M462 150h268"/><path d="M470 150v46M722 150v46" opacity=".45"/>
        ${jars}${cr}
        <path d="M600 58v22"/>
        <path d="M584 80h32l-7 24h-18z" fill="var(--ochre-wash)" stroke="var(--ochre)"/>
        ${_fig(790, 196, 1)}
      </g>
      <g fill="var(--verdigris)" opacity=".5" stroke="none">${_cypress(1178, 46)}</g>
      ${_ground()}`; }},

    // SEBASTIA — the Roman colonnaded street. Grammar is the part that stays standing.
    grammar: {ar: 'قَواعِد', place: 'Sebastia', placeAr: 'سَبَسْطية',
      what: 'the Roman colonnaded street', art: () => {
      let co = ''; [92, 206, 318, 430, 542, 654].forEach((x, i) =>
        co += _col(x, 86 + (i % 3) * 9, 192 - i * 3));
      let dr = ''; for (let i = 0; i < 5; i++)
        dr += `<circle cx="${800 + i * 34}" cy="184" r="13" fill="var(--paper)"/>`;
      return `
      <g stroke="var(--ink-soft)" stroke-width="1.6" opacity=".62" fill="none">
        ${_hills()}
        <path d="M0 196q200-22 420-26t780 8" opacity=".32"/>
        <path d="M74 196h620v-8h-620z" fill="var(--paper)" opacity=".8"/>
        ${co}
        <path d="M80 100h242v-11h-242z" fill="var(--paper)"/>
        ${dr}
        <path d="M1000 196v-34h44v34" fill="var(--paper)"/><path d="M994 162h56"/>
        <circle cx="1104" cy="52" r="21" fill="var(--ochre-wash)" stroke="var(--ochre)"/>
      </g>
      <g fill="var(--verdigris)" opacity=".5" stroke="none">
        ${_olive(752, .9)}${_olive(1160, .85)}${_cypress(40, 62)}${_olive(490, .75, 176)}
      </g>${_ground()}`; }},

    // NABLUS — the old city under the mountain, and a soap works with its towers of soap.
    lessons: {ar: 'دُروس', place: 'Nablus', placeAr: 'نابُلس',
      what: 'the old city and its soap works', art: () => {
      let tw = ''; for (let i = 0; i < 7; i++)
        tw += `<path d="M${623 + i * 1.6} ${186 - i * 15}h${42 - i * 3}" stroke="var(--ochre)" opacity=".65"/>`;
      return `
      <g stroke="var(--ink-soft)" stroke-width="1.6" opacity=".62" fill="none">
        ${_ridge()}
        ${_house(40, 128, 92, 4)}${_house(190, 108, 76, 3)}
        ${_dome(96, 104, 30)}${_dome(236, 120, 24)}
        ${_minaret(322, 128)}
        <path d="M420 196v-116h330v116" fill="var(--paper)"/><path d="M406 80h358"/>
        <path d="M420 80v-14h330v14" opacity=".5"/>
        ${_arch(452, 84, 66)}${_arch(602, 84, 66)}
        <path d="M619 196h50l-14-116h-22z" fill="var(--ochre-wash)" stroke="var(--ochre)"/>${tw}
        <path d="M800 196v-134h34v134" fill="var(--paper)"/><path d="M793 62h48"/><path d="M806 62v-10h22v10"/>
        ${_house(880, 118, 94, 4)}${_house(1024, 130, 82, 4)}${_dome(1089, 114, 28)}
        ${_fig(390, 196, .95)}
      </g>
      <g fill="var(--verdigris)" opacity=".5" stroke="none">${_cypress(772, 54)}${_olive(1180, .8)}</g>
      ${_ground()}`; }},

    // RAMALLAH — al-Manara, the square everyone means when they say "downtown".
    reactions: {ar: 'رُدود', place: 'Ramallah', placeAr: 'رام الله',
      what: 'al-Manara, the middle of town', art: () => {
      const lion = (x, s) => `<g transform="translate(${x} 196) scale(${s} 1)" fill="var(--paper)">
        <path d="M-2 0v-13q0-11 13-11h28q6 0 8 6l4 11V0z"/><circle cx="53" cy="-31" r="10"/>
        <g fill="none" opacity=".55"><path d="M53 -41v-6M62 -38l5-4"/>
          <path d="M-2 -13q-10-2-12-11"/><path d="M18 0v-9M38 0v-9"/></g></g>`;
      return `
      <g stroke="var(--ink-soft)" stroke-width="1.6" opacity=".62" fill="none">
        ${_hills()}
        ${_house(30, 128, 118, 4)}${_house(186, 108, 94, 3)}
        ${_house(936, 128, 110, 4)}${_house(1086, 100, 86, 3)}
        <path d="M0 196l320-42M1200 196l-320-42" opacity=".22"/>
        <path d="M536 196h128M548 189h104v7h-104zM562 177h76v12h-76z"/>
        <path d="M582 177v-82h36v82"/><path d="M574 95h52M580 89h40"/>
        <circle cx="600" cy="70" r="14" fill="var(--ochre-wash)" stroke="var(--ochre)"/>
        <path d="M600 56v-11" stroke="var(--ochre)"/>
        ${lion(524, -1)}${lion(676, 1)}
        ${_fig(370, 196, 1)}${_fig(418, 196, .9)}${_fig(772, 196, 1)}${_fig(818, 196, .85)}
        <path d="M382 176q30-16 46 0" opacity=".55"/>
        <path d="M784 176q28-16 44 0" opacity=".45"/>
      </g>
      <g fill="var(--verdigris)" opacity=".5" stroke="none">${_cypress(300, 50)}${_cypress(896, 46)}</g>
      ${_ground()}`; }},

    // JAFFA — the old port: the town on its rock, the clock tower, and boats on the water.
    sounds: {ar: 'أصْوات', place: 'Jaffa', placeAr: 'يافا',
      what: 'the old port', art: () => {
      return `
      <g stroke="var(--ink-soft)" stroke-width="1.6" opacity=".62" fill="none">
        ${_hills()}
        <path d="M0 152q180-16 420-14t780 12" opacity=".35"/>
        ${_house(80, 104, 70, 4, 150)}${_house(210, 92, 60, 3, 146)}
        <path d="M330 144v-88h44v88" fill="var(--paper)"/><path d="M322 56h60"/>
        <path d="M336 56v-14h32v14" fill="var(--paper)"/>
        <path d="M338 40l14-18 14 18z"/>
        <circle cx="352" cy="96" r="17" fill="var(--ochre-wash)" stroke="var(--ochre)"/>
        <path d="M352 96v-11M352 96l9 6" stroke="var(--ochre)"/>
        ${_house(400, 96, 62, 3, 144)}${_minaret(520, 96, 142)}${_house(566, 104, 66, 3, 142)}
        ${_house(700, 88, 56, 3, 144)}${_house(806, 96, 60, 3, 146)}
        <path d="M0 166h1200" opacity=".45"/>
        ${_water(172, 194, 0, 1200)}
        ${_boat(250, 188, .95)}${_boat(700, 182, .8)}${_boat(1030, 192, 1.05)}
      </g>
      <g fill="var(--verdigris)" opacity=".5" stroke="none">${_cypress(920, 48, 148)}${_cypress(972, 40, 150)}</g>
      ${_ground()}`; }},

    // GAZA — the shore, the boats, and a table laid on the sand. The section is hospitality.
    table: {ar: 'سُفْرة', place: 'Gaza', placeAr: 'غزّة',
      what: 'the shore, and a table laid on it', art: () => {
      let cu = ''; [320, 392, 812, 884].forEach(x =>
        cu += `<path d="M${x} 152v14a10 10 0 0 0 20 0v-14z"/><path d="M${x - 6} 152h32"/>`);
      return `
      <g stroke="var(--ink-soft)" stroke-width="1.6" opacity=".62" fill="none">
        <path d="M0 118h1200" opacity=".3"/>
        ${_house(20, 96, 62, 3, 118)}${_minaret(140, 92, 118)}${_house(190, 84, 52, 3, 118)}
        ${_dome(60, 56, 26)}
        ${_water(124, 142, 300, 1200)}
        ${_boat(560, 138, .7, 1)}${_boat(880, 132, .6, 1)}${_boat(1100, 142, .8, 0)}
        <path d="M0 150q260 10 600 4t600 6" opacity=".38"/>
        <path d="M180 176h840" stroke-width="2.2"/><path d="M244 196v-20M956 196v-20"/>
        <path d="M474 176c0-25 30-38 126-38s126 13 126 38z" fill="var(--paper)"/>
        <path d="M512 138c0-28 39-42 88-42s88 14 88 42" opacity=".5"/>
        <path d="M542 96c0-15 26-23 58-23s58 8 58 23" fill="var(--ochre-wash)" stroke="var(--ochre)"/>
        ${cu}
        <g transform="translate(760 100)">
          <path d="M0 72V44a23 23 0 0 1 23-23h11a23 23 0 0 1 23 23v28Z" fill="var(--paper)"/>
          <path d="M23 21v-8h11v8"/><path d="M57 40c15 2 21 11 21 19s-8 15-19 15"/>
          <path d="M0 50c-11 0-17-7-17-15s7-13 15-13"/></g>
        ${_fig(254, 172, .95)}${_fig(946, 172, .95)}
      </g>
      <g fill="var(--verdigris)" opacity=".5" stroke="none">${_palm(1120, 62)}${_palm(90, 52)}</g>
      ${_ground()}`; }},

    // THE JORDAN — two banks and a crossing between them. That is what translating is.
    // First draft laid a plank the whole width of the frame and it read as a dam; the river has
    // to narrow into the distance, and the crossing has to be small enough to be a crossing.
    translate: {ar: 'تَرْجَمة', place: 'The Jordan', placeAr: 'نَهر الأُردُن',
      what: 'both banks, and the crossing', art: () => {
      let riv = ''; for (let i = 0; i < 8; i++) { const y = 190 - i * 9, w = 300 - i * 32;
        riv += `<path d="M${600 - w / 2} ${y}q${w / 4} -5 ${w / 2} 0t${w / 2} 0"
          opacity="${(.34 - i * .03).toFixed(2)}"/>`; }
      let rd = ''; [70, 96, 124, 154, 1046, 1076, 1104, 1130].forEach(x => {
        const d = x < 600 ? 1 : -1;
        rd += `<path d="M${x} 196c${-3 * d}-26 ${1 * d}-38 ${7 * d}-50"/>`; });
      return `
      <g stroke="var(--ink-soft)" stroke-width="1.6" opacity=".62" fill="none">
        ${_hills()}
        <path d="M0 190q240-18 450-66" opacity=".45"/>
        <path d="M1200 190q-240-18-450-66" opacity=".45"/>
        ${riv}
        <path d="M505 150h190v-8h-190z" fill="var(--paper)"/>
        <path d="M516 158v12M684 158v12" opacity=".7"/>
        <path d="M505 142q95-13 190 0" opacity=".55"/>
        <path d="M512 142v-13M600 136v-12M688 142v-13" opacity=".45"/>
        <path d="M505 129q95-12 190 0" opacity=".4"/>
        ${rd}
        ${_house(160, 78, 44, 3, 168)}${_house(1010, 70, 40, 2, 170)}
        <circle cx="948" cy="56" r="21" fill="var(--ochre-wash)" stroke="var(--ochre)"/>
      </g>
      <g fill="var(--verdigris)" opacity=".5" stroke="none">
        ${_olive(250, .9)}${_cypress(360, 52, 178)}${_olive(60, .8)}
        ${_olive(940, .9)}${_cypress(852, 50, 178)}${_olive(1160, .85)}
      </g>${_ground()}`; }},

    // HAIFA — the terraces climbing Carmel over the bay. Tending something, step by step.
    tutor: {ar: 'مُعَلِّم', place: 'Haifa', placeAr: 'حَيفا',
      what: 'the terraces on Carmel', art: () => {
      let st = ''; for (let i = 0; i < 6; i++) { const y = 196 - i * 15, w = 340 - i * 30;
        st += `<path d="M${568 - w / 2} ${y}v-15h${w}v15" opacity="${(.55 - i * .04).toFixed(2)}"/>`; }
      const up = '';
      return `
      <g stroke="var(--ink-soft)" stroke-width="1.6" opacity=".62" fill="none">
        <path d="M0 196q210-98 540-128t660-24" opacity=".36"/>
        ${st}${up}
        <path d="M552 196v-90M584 196v-90" opacity=".35"/>
        <path d="M528 106v-32h80v32"/><path d="M520 74h96"/>
        ${_dome(568, 74, 32, ' fill="var(--ochre-wash)" stroke="var(--ochre)"')}
        <path d="M568 42v-10" stroke="var(--ochre)"/>
        <path d="M534 106v-24M602 106v-24" opacity=".5"/>
        ${_house(60, 96, 58, 3)}${_house(180, 84, 48, 3, 184)}${_house(900, 90, 52, 3, 178)}
        <path d="M760 196h440" opacity=".3"/>
        ${_water(178, 194, 780, 1200)}
        ${_boat(1080, 190, .85, 0)}
      </g>
      <g fill="var(--verdigris)" opacity=".5" stroke="none">
        ${_cypress(500, 46, 166)}${_cypress(640, 46, 166)}${_cypress(478, 40, 136)}${_cypress(662, 40, 136)}
        ${_cypress(300, 58)}${_olive(720, .85)}
      </g>${_ground()}`; }},

    // THE SEA OF GALILEE — the lake, the far hills, and a boat. The Gospels' own geography.
    bible: {ar: 'الكِتاب', place: 'Sea of Galilee', placeAr: 'بُحَيْرة طَبَريّا',
      what: 'the lake and the far shore', art: () => {
      let rd = ''; [40, 62, 82, 104, 1108, 1130, 1152, 1174].forEach((x, i) =>
        rd += `<path d="M${x} 196c${x < 600 ? '-3' : '3'}-28 ${x < 600 ? '1' : '-1'}-40 ${x < 600 ? '7' : '-7'}-52"/>`);
      return `
      <g stroke="var(--ink-soft)" stroke-width="1.6" opacity=".62" fill="none">
        <path d="M0 116Q220 82 470 96T900 78T1200 108" opacity=".38"/>
        <path d="M0 132q260 12 520 6t680 8" opacity=".26"/>
        ${_house(300, 62, 30, 2, 132)}${_house(386, 54, 26, 2, 132)}
        ${_water(140, 192, 0, 1200)}
        ${_boat(400, 176, 1.15)}${_boat(830, 160, .75)}
        ${rd}
        <circle cx="920" cy="94" r="21" fill="var(--ochre-wash)" stroke="var(--ochre)"/>
        <path d="M906 148h28M910 162h20M914 176h12M916 188h8" stroke="var(--ochre)" opacity=".45"/>
      </g>
      <g fill="var(--verdigris)" opacity=".5" stroke="none">${_cypress(180, 50, 134)}${_olive(1050, .8, 130)}</g>
      ${_ground()}`; }},

    // BATTIR — the terraces and the Roman water channel that still feeds them. A path in stages.
    plan: {ar: 'خُطّة', place: 'Battir', placeAr: 'بتّير',
      what: 'the terraces and the water channel', art: () => {
      let t = ''; for (let i = 0; i < 5; i++)
        t += `<path d="M${i * 30} ${196 - i * 26}h${1200 - i * 72}" opacity="${(.55 - i * .06).toFixed(2)}"/>`;
      let ch = ''; for (let x = 20; x < 1010; x += 46) ch += `<path d="M${x} 144v8"/>`;
      return `
      <g stroke="var(--ink-soft)" stroke-width="1.6" opacity=".62" fill="none">
        ${_hills()}${t}
        <path d="M0 144h1010" opacity=".55"/><path d="M0 152h1010" opacity=".35"/>${ch}
        <path d="M120 196q120-30 180-32t160-24 190-26 200-22" stroke-width="2.6" opacity=".8"/>
        <circle cx="120" cy="196" r="6" fill="var(--ink-soft)" stroke="none"/>
        <circle cx="470" cy="140" r="6" fill="var(--ink-soft)" stroke="none"/>
        <circle cx="850" cy="92" r="6" fill="var(--ink-soft)" stroke="none"/>
        ${_house(930, 88, 52, 3, 92)}${_house(1046, 78, 46, 3, 78)}
        <circle cx="180" cy="52" r="21" fill="var(--ochre-wash)" stroke="var(--ochre)"/>
      </g>
      <g fill="var(--verdigris)" opacity=".5" stroke="none">
        ${_olive(250, .8)}${_olive(560, .8, 170)}${_olive(760, .75, 144)}
        ${_cypress(400, 44, 170)}${_cypress(890, 40, 118)}${_olive(1150, .8, 78)}
      </g>${_ground()}`; }},

    // BETHLEHEM — the rooftops: dishes, tanks, and the basilica's bell tower behind them.
    videos: {ar: 'فيديو', place: 'Bethlehem', placeAr: 'بيت لَحم',
      what: 'rooftops, dishes and tanks', art: () => {
      let d = ''; [220, 400, 620, 840].forEach((x, i) => {
        d += `<g transform="translate(${x} ${150 - (i % 2) * 10})">
          <path d="M0 46V16"/><path d="M-22 16a22 14 0 0 1 44 0z"/><path d="M0 16v-10"/></g>`; });
      return `
      <g stroke="var(--ink-soft)" stroke-width="1.6" opacity=".62" fill="none">
        ${_hills()}
        <path d="M296 146v-104h68v104" fill="var(--paper)"/>
        <path d="M288 42h84l-42-25z" fill="var(--paper)"/>
        <path d="M312 74h36v30h-36z" opacity=".5"/><path d="M312 118h36" opacity=".4"/>
        <path d="M60 196v-50h1080v50" fill="var(--paper)" opacity=".9"/><path d="M60 146h1080"/>
        ${_house(120, 118, 92, 4)}${_house(500, 138, 104, 4)}${_house(884, 128, 86, 4)}
        ${d}
        <path d="M700 146v-30h44v30zM700 116a22 8 0 0 1 44 0"/>
        <path d="M956 146v-26h34v26zM956 120a17 6 0 0 1 34 0"/>
        <circle cx="1058" cy="54" r="21" fill="var(--ochre-wash)" stroke="var(--ochre)"/>
      </g>
      <g fill="var(--verdigris)" opacity=".5" stroke="none">${_cypress(1176, 48)}${_cypress(30, 54)}</g>
      ${_ground()}`; }},

    // WADI ARA — the valley the road runs through, villages on the ridge. The accent is here.
    listening: {ar: 'سَماع', place: 'Wadi Ara', placeAr: 'وادي عارة',
      what: 'the valley and its villages', art: () => {
      let w = ''; for (let i = 1; i <= 4; i++)
        w += `<path d="M470 ${150 - i * 8}q${i * 28} -${i * 20} ${i * 54} 0" opacity="${(.42 - i * .07).toFixed(2)}"/>`;
      return `
      <g stroke="var(--ink-soft)" stroke-width="1.6" opacity=".62" fill="none">
        <path d="M0 128q190 40 380 28t360-44 460-18" opacity=".3"/>
        <path d="M0 196q230-74 520-78t680 46" opacity=".45"/>
        ${_house(226, 80, 44, 3, 140)}${_house(336, 72, 40, 3, 128)}${_house(438, 84, 46, 3, 122)}
        ${_minaret(552, 88, 122)}${_house(602, 74, 40, 2, 124)}
        ${_house(80, 88, 50, 3, 176)}${_house(196, 76, 42, 3, 156)}
        <path d="M640 196q56-40 176-58t384-30" stroke-width="2.4" opacity=".75"/>
        <path d="M660 196q52-34 168-50t372-26" opacity=".3"/>
        <path d="M760 168h30M840 154h30M930 142h28M1030 132h26" opacity=".4"/>
        ${w}
        <circle cx="120" cy="52" r="21" fill="var(--ochre-wash)" stroke="var(--ochre)"/>
      </g>
      <g fill="var(--verdigris)" opacity=".5" stroke="none">
        ${_cypress(318, 42, 128)}${_olive(700, .85, 160)}${_olive(500, .75, 178)}${_cypress(880, 40, 176)}
      </g>${_ground()}`; }},

    // JERICHO — palms, the tell, and the star window of Hisham's Palace. The oldest address.
    account: {ar: 'حِساب', place: 'Jericho', placeAr: 'أريحا',
      what: "palms and Hisham's Palace", art: () => `
      <g stroke="var(--ink-soft)" stroke-width="1.6" opacity=".62" fill="none">
        ${_ridge('.3')}
        <path d="M0 196q150-42 320-40t280 40" opacity=".35"/>
        <path d="M620 196v-102h250v102" fill="var(--paper)"/><path d="M606 94h278"/>
        <path d="M620 94v-14h250v14" opacity=".5"/>
        <path d="M660 196v-54a29 29 0 0 1 58 0v54"/>
        <path d="M676 196v-38h26v38" opacity=".45"/>
        <circle cx="812" cy="132" r="27" fill="var(--ochre-wash)" stroke="var(--ochre)"/>
        <path d="M812 105l7 20 20 7-20 7-7 20-7-20-20-7 20-7z" stroke="var(--ochre)"/>
        <path d="M793 113l38 38M831 113l-38 38" stroke="var(--ochre)" opacity=".5"/>
        ${_house(120, 96, 56, 3, 168)}${_house(950, 104, 60, 3)}
        ${_fig(560, 196, .95)}
      </g>
      <g fill="var(--verdigris)" opacity=".5" stroke="none">
        ${_palm(230, 78)}${_palm(330, 62)}${_palm(430, 70)}${_palm(1090, 74)}${_palm(1176, 58)}
      </g>${_ground()}`},
  };


const WADI = {Q:'k', J:'j', K:'ch', T:'th', D:'dh', Z:'dh'};
function wadiAra(w) {
  const raw = w.caphi_raw, urb = w.caphi_urban || w.caphi;
  if (!raw) return null;
  const out = String(raw).split(' ').map(tok => {
    if (!tok) return '';
    if (tok.includes('||')) { const [a, b] = tok.split('||'); return WADI[b.trim()] || a.trim(); }
    if (WADI[tok]) return WADI[tok];
    if (!tok.includes('.')) for (const v in WADI) tok = tok.split(v).join(WADI[v]);
    return tok;
  }).join('');
  return out && out !== urb ? out : null;
}

  // Flag, name and font are NOT here: lang/languages.js owns them, because the boot script has
  // to read them before deciding whether to fetch this file at all. defineLang folds them in.
  defineLang({
    code: 'ar',

    // Which licensed lexicon stands behind every word, said once and shown wherever the app
    // makes that claim -- the home page's promise and each word card's provenance line.
    storyLevels: [
      ['beginner',     'Beginner',     'Short, present-tense, everyday life. A few sentences each.'],
      ['intermediate', 'Intermediate', 'Longer past-tense stories with small plots and connectors.'],
      ['advanced',     'Advanced',     'Full stories — dialogue, idioms, and richer situations.'],
    ],

    lex: {
      // Arabic's word index is derived from the corpus, so either file can answer a lookup.
      source: 'corpus',
      // How to describe the variety the curated prose describes, where a lesson has to
      // qualify itself. Neither language is 'the language': one is urban Palestinian, the
      // other is what people actually say in Israel rather than what a textbook prints.
      usage: 'common urban Palestinian usage, which varies by speaker and region',
      name: 'Maknuune',
      blurb: 'a 36,000-entry Palestinian lexicon compiled by linguists',
      credit: 'the <b>Maknuune Palestinian Arabic Lexicon</b> (Dibas, Khairallah, Habash et al., '
            + 'WANLP 2022) — <a href="https://palestine-lexicon.org/" target="_blank" '
            + 'rel="noopener" style="color:var(--verdigris)">palestine-lexicon.org</a>, CC BY-SA 4.0.',
    },

    // ---- the writing system -------------------------------------------------------------
    script: {
    // Strips harakat and tatweel, folds the hamza-carrying alefs, ta-marbuta and alef-maqsura.
    norm: s => (s || '').replace(/[ً-ْٰـ]/g, '')
  .replace(/[أإآٱ]/g, 'ا').replace(/ة/g, 'ه').replace(/ى/g, 'ي').trim(),
    run: /([\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF][\s\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF\u064B-\u0652]*)/,
    // Does a string contain any of this language's script? Asked wherever the app has to tell
    // "the learner typed the target language" from "the learner typed English".
    chars: /[\u0600-\u06FF\u0750-\u077F]/,
    punct: '،.؟!:؛…"«»“”\'()-—[]{}–,;?',
    // Clitics, longest first. The peeling ALGORITHM is generic; only these tables are Arabic.
    pre: ['و', 'ب', 'ك', 'ف', 'ل', 'ال', 'لل', 'وال', 'بال', 'كال', 'فال'],
    suf: ['ك', 'ه', 'ي', 'ها', 'هم', 'هن', 'كم', 'كن', 'نا', 'ني'],
    minStem: 3,                    // never leave a one- or two-letter stem behind
    fixes: {
        'الله':  {lemma: 'الله',    gloss: 'God',                 analysis: 'NOUN_PROP', caphi: '2al.l.a'},
        'لله':   {lemma: 'لله',     gloss: 'to God, for God',     analysis: 'NOUN_PROP', caphi: '2il.l.a'},
        'الهوا': {lemma: 'الهَوا',  gloss: 'the air, the wind',   analysis: 'NOUN:MS',   caphi: '2ilhawa'},
        'الاله': {lemma: 'الآلة',   gloss: 'the machine, the instrument', analysis: 'NOUN:FS', caphi: '2il2aale'},
        'الامن': {lemma: 'الأَمن',  gloss: 'security, safety',    analysis: 'NOUN:MS',   caphi: '2il2amn'},
        'كلهم':  {lemma: 'كُلُّهُم', gloss: 'all of them',         analysis: 'NOUN_QUANT',caphi: 'kullhum'},
        // بدّ + ending is how Palestinians say "want", and it is everywhere. The corpus resolves بدّي
        // to a Maknuune entry meaning "be altruistic towards sb and prioritize him/her" — so the
        // commonest word in the dialect had a gloss no learner could make sense of. Making the lesson
        // reading passages tappable is what put it in front of a reader often enough to notice.
        // The readings below are the app's OWN curated paradigm, pipeline/grammar.py:273 — the same
        // table the "Wanting — بدّي" grammar lesson teaches from. Nothing new is asserted here.
        'بدي':   {lemma: 'بِدّي',   gloss: 'I want',              analysis: 'PART', caphi: 'baddi'},
        'بدك':   {lemma: 'بِدّك',   gloss: 'you want (m/f)',      analysis: 'PART', caphi: 'baddak'},
        'بده':   {lemma: 'بِدّه',   gloss: 'he wants',            analysis: 'PART', caphi: 'baddo'},
        'بدها':  {lemma: 'بِدّها',  gloss: 'she wants',           analysis: 'PART', caphi: 'baddha'},
        'بدنا':  {lemma: 'بِدّنا',  gloss: 'we want',             analysis: 'PART', caphi: 'baddna'},
        'بدكم':  {lemma: 'بِدّكم',  gloss: 'you want (plural)',   analysis: 'PART', caphi: 'baddkom'},
        'بدهم':  {lemma: 'بِدّهم',  gloss: 'they want',           analysis: 'PART', caphi: 'baddhom'},
      },
  },

    // ---- pronunciation ------------------------------------------------------------------
    phon: {
    fields: {main: 'caphi', urban: 'caphi_urban', raw: 'caphi_raw'},
    // Sub-dialects are a list so a language can have none (Hebrew) or several later
    // (Gazan, Galilean) without touching the app.
    variants: [{id: 'wadi', label: 'Wadi Ara', apply: wadiAra}],
  },

  // ---- the verb model -------------------------------------------------------------------
  verb: {
    // WHICH FORM A VERB IS FILED UNDER -- in the deck, in the verb list, and on the verb page.
    // Arabic has no infinitive, so the dictionary form is the 3ms past, and it is also what the
    // rest of the paradigm is built from. Hebrew's answer is the infinitive; see he.js.
    cite: 'past',
    citeNote: 'the \u201Che\u201D past, the form the whole paradigm is built from',
    // The principal parts a browse card shows. The citation form has to be among them --
    // a card that never shows the form it banks under is a card you can't recognise later.
    summary: [['past', 'Past'], ['pres', 'Present'], ['imp', 'Command']],
    classNoun: 'form',
    classPlural: 'Forms',
    blurb: n => `Arabic verbs are built on three- or four-letter roots, run through a set of
      patterns called <b>forms</b> (measures I–X). The form shapes the meaning; the root
      supplies it. Browse by form below, or search across all ${n} verbs. Every root, gloss and
      pronunciation is from the Maknuune lexicon — the form is computed, the conjugations are
      not invented.`,
    weakBlurb: 'Verbs whose root has a و, ي or ء that shifts or drops — grouped by how they '
             + 'bend. These exist inside every form.',
    // The shape of the conjugation display. `rows` names a rowSet; `cols` are the tenses shown
    // side by side; `full: true` means the full verb page only, not the word-sheet popup.
    // Hebrew's descriptor is a different list against the same renderer -- a 2-column past/
    // future grid, a separate 4-cell present, an imperative strip and an infinitive.
    rowSets: {
      imp: [['inta', 'you (m)', 'إنت'], ['inti', 'you (f)', 'إنتي'], ['intu', 'you (pl)', 'إنتو']],
      gn:  [['m', 'm', ''], ['f', 'f', ''], ['p', 'pl', '']],
    },
    tables: [
      {kind: 'grid', rows: 'persons', cols: [
        {slot: 'perf',  label: 'Past',           short: 'Past'},
        {slot: 'impf',  label: 'Present',        short: 'Pres.'},
        {slot: 'bimpf', label: 'Present + بـ',   short: '+بـ'}]},
      {kind: 'strip', full: true, label: 'Command (imperative)', rows: 'imp', slot: 'imp'},
      {kind: 'strip', full: true, label: 'Active participle (doing / having done)',
       rows: 'gn', slot: 'ap'},
    ],
    classOrder: ['I','II','III','IV','V','VI','VII','VIII','X','Q'],
    classInfo: {
        I:   ['Form I',        'The base verb — the plain action. كتب “he wrote”.'],
        II:  ['Form II',       'Doubled middle root letter. Often intensive or causative — درّس “he taught”.'],
        III: ['Form III',      'Long vowel after the first letter. Doing something to or with someone — كاتب “he corresponded”.'],
        IV:  ['Form IV',       'Causative. Rare in dialect; usually surfaces as Form I or II instead.'],
        V:   ['Form V',        'Form II with a t- prefix. Reflexive of II — تعلّم “he learned”.'],
        VI:  ['Form VI',       'Form III with a t- prefix. Reciprocal — تكاتبوا “they wrote to each other”.'],
        VII: ['Form VII',      'n- prefix. Passive or medio-passive — انكسر “it broke”.'],
        VIII:['Form VIII',     'Infixed -t-. Often middle voice or reflexive — اشتغل “he worked”.'],
        X:   ['Form X',        'ista- prefix. Seeking or considering — استعمل “he used”.'],
        Q:   ['Quadriliteral', 'Four-consonant roots, including loanwords — تلفن “he phoned”.'],
      },
    weakInfo: {
        hollow:      ['Hollow',      'Middle root letter is و or ي and drops or shifts — راح / يروح.'],
        defective:   ['Defective',   'Final root letter is و or ي — مشي / يمشي.'],
        doubled:     ['Doubled',     'Last two root letters are the same, written with shadda — حبّ / يحبّ.'],
        assimilated: ['Assimilated', 'First root letter is و and often drops in the present — وصل / يوصل.'],
        hamzated:    ['Hamzated',    'A root letter is hamza (ء) — أكل / ياكل.'],
      },
    weakOrder: ['hollow','defective','doubled','assimilated','hamzated'],
    persons: [
        ['ana','I','أنا'], ['inta','you (m)','إنت'], ['inti','you (f)','إنتي'],
        ['huwwe','he','هو'], ['hiyye','she','هي'], ['i7na','we','إحنا'],
        ['intu','you (pl)','إنتو'], ['humme','they','هم'],
      ],
    // A FUNCTION, not a map: Arabic difficulty tracks the weak class, Hebrew's tracks the
    // binyan at least as much as the gzara, so the judgement belongs to the pack.
    tier: v => ({sound: 1, doubled: 2, hollow: 2, defective: 3, assimilated: 3, hamzated: 3, irregular: 3, quad: 3})[v.weak] || 2,
  },

    // ---- keyboard, voice ----------------------------------------------------------------
    kbd: {
    toggle: '\u0639', title: 'Arabic keyboard',
    numsLabel: '١٢٣', lettersLabel: 'ا ب ج',
    diacritic: 'ّ', diacriticLabel: 'ـّ',
    letters: [
        ['ض','ص','ث','ق','ف','غ','ع','ه','خ','ح','ج'],
        ['ش','س','ي','ب','ل','ا','ت','ن','م','ك','ة'],
        ['ء','ظ','ط','ذ','د','ز','ر','و','ى'],
      ],
    nums: [
        ['١','٢','٣','٤','٥','٦','٧','٨','٩','٠'],
        ['-','/',':','؛','(',')','%','&','@','"'],
        ['،','.','؟','!','’','«','»'],
      ],
    hold: {
        'ا': ['أ','إ','آ','ٱ'], 'و': ['ؤ'], 'ي': ['ى','ئ'], 'ه': ['ة'],
        'ء': ['أ','إ','ؤ','ئ','آ'], 'ل': ['لا','لأ','لإ','لآ'],
        'ّ': ['َ','ُ','ِ','ً','ٌ','ٍ','ْ','ّ'],
      },
  },
    tts: {lang: 'ar-SA', voiceRe: /^ar/i},
    searchHint: 'بيت · راح · house · tired…',
    // The masthead's dateline in the target language. Levantine month names (كانون التاني,
    // شباط…), not the Gulf/Egyptian numbered ones.
    dateLine: d => {
      const DAYS = ['الأحد', 'الاتنين', 'التلات', 'الأربعا', 'الخميس', 'الجمعة', 'السبت'];
      const MONTHS = ['كانون التاني', 'شباط', 'آذار', 'نيسان', 'أيار', 'حزيران',
                      'تموز', 'آب', 'أيلول', 'تشرين الأول', 'تشرين التاني', 'كانون الأول'];
      return DAYS[d.getDay()] + '، ' + d.getDate() + ' ' + MONTHS[d.getMonth()];
    },
    // Where the plan ENDS, named in two or three words for the journey page's kicker.
    // It used to be hardcoded as "the table", which is this language's destination and not
    // the app's -- the Hebrew plan ends at a different place and now says so.
    planEnd: 'the table',
    planGoal: 'all the way to holding your own at a Palestinian family dinner',
    booksBlurb: 'Whole stories to read start to finish — graded for learners, in spoken '
      + 'Palestinian, with tap-any-word for every word. A connected book, with vocabulary that '
      + 'comes back again and again, sticks far better than scattered paragraphs. Read online or '
      + 'download a PDF. The retellings are adapted by Claude (not native-checked); every '
      + 'word\u2019s meaning and root is from the lexicon.',
    assessGreetings: 'Salaam, shukran, the basics',
    // The home page's own decoration: a tatreez band (Palestinian cross-stitch, the diamond
    // motif) and the Old City skyline. Both are inline SVG in the theme's variables -- no
    // external assets, no licence -- and both are this language's, not the app's.
    ornament: () => tatreez(),
    skyline: () => HOME_SKYLINE,

    // The masthead wordmark, and the chapter-number prefix a book title carries.
    homeMasthead: () => `<div class="hm-mark">عَرَبي <em>فَلَسطيني</em></div>`,
    chapterPrefix: /^الفصل[^—]*—\s*/,

    tutorPrompt: ({grammar, sounds, reactions}) => {
      const gram = grammar.map(l => l.title).filter(Boolean).slice(0, 24).join('; ');
      const snds = sounds.map(L => L.target || L.en).filter(Boolean).join('; ');
      const rxc = reactions.map(c => c.en).filter(Boolean).join('; ');
      return [
        "You are a warm, precise tutor for SPOKEN PALESTINIAN ARABIC — the urban Levantine city speech of Jerusalem, Ramallah, and Nablus. The learner is an English speaker in a self-study app, working toward holding their own at a Palestinian family dinner table.",
        "",
        "How to answer:",
        "- Answer in SPOKEN Palestinian, NOT Modern Standard Arabic (فصحى). When the spoken form differs from MSA, give the spoken one and briefly note the difference. If the learner's own phrase is MSA or another dialect, gently flag it and give the Palestinian equivalent.",
        "- For any Arabic you give: Arabic script, then a simple transliteration in parentheses, then the English gloss. Keep it tight — one clear answer with an example or two beats a wall of grammar.",
        "- Urban pronunciation model to reflect in transliterations: ق is a glottal stop (ء, an apostrophe '); ث→t, ذ→d; ج is a soft “zh/j”. e.g. قهوة = ʼahwe, هيك = heek.",
        "- Honesty first: if you're not sure a form is specifically Palestinian (vs. general Levantine), say so plainly. Never invent a proverb, a “they always say…”, or confident detail you're unsure of. It's fine to say you're not certain.",
        "- You can explain grammar, translate, compare near-synonyms, give example sentences, and role-play short dinner-table exchanges. Match the learner's level; be encouraging and concrete.",
        "",
        "SAVING PHRASES (important): when your answer teaches a specific Palestinian word or phrase the learner can reuse — above all for “how do I say…” questions — finish your ENTIRE reply with a machine-readable block listing the 1–4 most useful save-worthy items, each on its own line as “Arabic = English” (Arabic script only in this block, NO transliteration):",
        "<save>",
        "بدي = I want",
        "بدي أروح عالبيت = I want to go home",
        "</save>",
        "Only list phrases genuinely worth memorizing as-is. For a pure grammar explanation with no single save-worthy phrase, omit the block entirely. Write nothing after </save>.",
        "",
        "This app already teaches the learner these things — reference them naturally, don't just list them:",
        "• Grammar structures: " + (gram || "(various spoken structures)"),
        "• Pronunciation contrasts: " + (snds || "(urban sound contrasts)"),
        "• Conversational reaction categories: " + (rxc || "(everyday reactions)"),
      ].join("\n");
    },

    // What a verb's derivational class is CALLED, for the Verbs status line. Arabic has forms
    // (measures); Hebrew has binyanim.
    bibleBlurb: 'ESV \u2016 Arabic, side by side',
    bible: {
      intro: 'Read Scripture side by side — <b>ESV</b> in English on the left, the classical '
           + 'Arabic <b>Van Dyck</b> on the right, the version read aloud in Arabic churches. '
           + 'Tap a book, then a chapter.',
      credit: 'Arabic: Van Dyck (1865), public domain.',
      note: 'The spoken Palestinian/Galilean New Testament isn’t freely available as text; '
          + 'where it exists, each New-Testament chapter links out to it.',
      wordNote: "<b>Classical Arabic, not dialect.</b> This is the Van Dyck translation (1865). "
              + "The meaning above comes from the Palestinian lexicon and is here to help you "
              + "read — but the word isn't added to your vocabulary, which stays spoken "
              + "Palestinian.",
      // A spoken-dialect New Testament exists (Galilean) but only inside YouVersion — display
      // only, nothing embeddable. So for NT books we link out to it, chapter by chapter.
      chapterLink: (id, ch) => ({
        MAT:1,MRK:1,LUK:1,JHN:1,ACT:1,ROM:1,'1CO':1,'2CO':1,GAL:1,EPH:1,PHP:1,COL:1,'1TH':1,
        '2TH':1,'1TI':1,'2TI':1,TIT:1,PHM:1,HEB:1,JAS:1,'1PE':1,'2PE':1,'1JN':1,'2JN':1,
        '3JN':1,JUD:1,REV:1}[id] ? `https://www.bible.com/bible/2437/${id}.${ch}` : null),
    },
    tutorStarters: [
      "Why do Palestinians say بدي instead of أريد for “I want”?",
      "How do I say “I've been waiting for an hour” in spoken Palestinian?",
      "What's the difference between شو and إيش?",
      "Give me 3 natural things to say when someone cooks me a great meal.",
      "Is مبسوط spoken Palestinian or MSA? How do I say “I'm happy”?",
    ],

    art: SEC_ART,
  });
})();
