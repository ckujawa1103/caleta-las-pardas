# Handoff — The Guánica Compound

Paste this whole file into a fresh Claude Code session opened on this
repository. It contains everything needed to continue; you do not need the
conversation that produced the work so far.

---

## 0. Rules for this project — read first

**Never use the `AskUserQuestion` tool.** Not once, for any reason. The
multiple-choice pop-up it renders breaks the user's chat client and costs them
the session. If you need a decision:

1. Prefer making it yourself. Pick the option a careful colleague would pick,
   state the choice and the reasoning in plain prose, and keep building.
2. If you genuinely cannot proceed, ask in **plain text in your reply** — a
   sentence or two, no tool call — and continue with everything that does not
   depend on the answer.

Other standing rules for this repo:

- **Static site, no build step in the deploy sense.** GitHub Pages serves the
  committed files directly. The scripts in `tools/` are generators whose output
  is committed; that is allowed and intended. Never introduce a bundler,
  framework, or CI build.
- **No third-party runtime requests, ever.** No CDNs, no Google Fonts, no
  analytics, no tracking, no remote images. Fonts are self-hosted in
  `assets/fonts/`. Three.js is vendored in `assets/js/three/`. Every byte the
  page loads comes from this repository. This is a hard constraint from the
  brief, and Google Fonts violating it is exactly why the fonts were vendored.
- **Mobile is the primary reading device.** The owner reads this on a phone far
  more than on a desktop. Check every change at 390 px wide before committing.
- **Verify visually.** Chromium and Playwright are available; the screenshot
  helper is `tools/shot.mjs`. Take a screenshot and actually look at it rather
  than assuming the CSS worked.
- **Branch:** work on `claude/new-session-03dxfn` and push there.
  `git push -u origin claude/new-session-03dxfn`.
- Do not open a pull request unless the user asks for one.

---

## 1. What this is

A static, GitHub Pages–hosted interactive site documenting a fictional
ultra-high-end fortified off-grid compound on a limestone headland in Guánica,
Puerto Rico. It is a **lottery daydream** — an imagined property, not a live
project — but the engineering reasoning is real and must be preserved
precisely.

Three deliverables:

1. **The Document** — a long-form reference site covering the full design. Done.
2. **The Section** — an interactive cross-section of the headland, the signature
   visual. Done.
3. **The Walkthrough** — a first-person 3D walk ending in the reveal of the
   buried club. See status below.

---

## 2. The most important thing to know

**The survey data contradicted the original brief, and the site now documents
that rather than papering over it.** Before writing any code, the parcel was
checked against primary sources. Findings, all from live queries:

| Finding | Source |
|---|---|
| The coordinate the brief was written around (17.9488 N, 66.9130 W) is **not** in the tourism district. It falls in **B-Q Bosque / SREP-E**, protected forest. The DTS land is ~1.4 km west-southwest. | MIPR |
| Zoning is **DTS — Distrito Turístico Selectivo** on Suelo Rústico Común, catastro 429-000-006-01, barrio Montalva, resolution JP-ZIT-71-72-01 | MIPR |
| **The buildable parcel does not reach the sea.** From the waterline: CR conservation to 42 m, road corridor, then DTS from **44 m to 284 m**, then protected forest. | MIPR |
| Ground rises **+7.2 m to +26.2 m over 240 m** — a steady 8% grade. The three-band scheme holds. | USGS 3DEP 1 m |
| Tsunami evacuation zone reaches only **+3.1 m, 12 m inland**. FEMA **VE** (BFE 3.4 m) stops at 8 m; the parcel is Zone **X**. Both hazard limits are seaward of the road. | MIPR, FEMA FIRM 72000C |
| Lot areas surveyed at 8,000.1571 / 8,000.0006 / 8,000.0005 / 8,061.2339 m² = **7.92 acres**. No unit error ever existed. | listing surveys |
| Mean range of tide **0.65 ft**; MSL sits 0.05 ft above PRVD02, so DEM elevations and sea level are the same line here. | NOAA 9759110 |

**Consequences already worked into the design:** a fourth band ("Band 0") in
front for the land nobody owns; the three bands re-measured from the parcel's
seaward edge; no boat ramp, no beach palapa, no private shoreline; the boat
moved to Guánica Bay; the sea sally port reduced to an easement question;
privacy flipped to face inland at the road; and the sacrificial ground floor
kept as a good idea rather than a code requirement.

**Do not "fix" the document back to the original brief's premises.** The
divergence is the most interesting thing about it.

---

## 3. Repository map

```
index.html                 the whole document — GENERATED, see below
partials/document.html     the document body, section 4 onward. EDIT THIS.
assets/css/tokens.css      palette, type, the underground token swap
assets/css/document.css    document layout and components
assets/css/section.css     the section drawing
assets/css/hero.css        hero
assets/js/section.js       section-cut interaction (progressive enhancement)
assets/js/three/           vendored Three.js r169 + licence
assets/fonts/              self-hosted Fraunces, Karla, IBM Plex Mono
data/                      cached terrain + regulatory data (see below)
tools/                     the generators and the data harvesters
```

### index.html is generated — do not hand-edit the marked regions

Two spliced regions:

- `<!-- DOCUMENT:START -->` … `<!-- DOCUMENT:END -->` ← from `partials/document.html`
- `<!-- SECTION:START -->` … `<!-- SECTION:END -->` ← from `tools/build_section.py`

Everything outside those markers (head, hero, contents nav, the first three
sections, footer) lives in `index.html` itself and is edited directly.

**To rebuild both:** `python3 tools/build_page.py`

Edits to `partials/document.html` are lost unless you run that. Edits made
directly inside the marked regions of `index.html` are lost too.

---

## 4. The data

All cached as JSON and committed, so the page never makes a network call and
the tools do not need to re-run.

| File | What |
|---|---|
| `data/section-profile.json` | **The important one.** 301 stations at 2 m along the section line, each with elevation, zoning code, and tsunami/flood flags. Drives the section drawing. |
| `data/dem-dts-20m.json` | 20 m DEM grid over the DTS parcel, 42 × 64 |
| `data/dem-grid-20m.json` | 20 m DEM grid over the original (wrong) coordinate |
| `data/dem-dts-class.json` | per-cell DTS / tsunami / flood classification |
| `data/parcel-context.json` | local parcel polygons + the ZMT reference line |

Not committed (large, re-fetchable, gitignored): `data/mipr-geometry.json`,
`data/mipr-calificacion.json`. Regenerate with `python3 tools/geom.py`.

### Regenerating from scratch

```sh
python3 tools/harvest.py        # 20 m DEM grid, 800 m square (~2 min)
python3 tools/harvest2.py       # 20 m DEM grid over the DTS parcel (~3 min)
python3 tools/geom.py           # MIPR zoning, hazard, ZMT geometry
python3 tools/analyze.py        # fuse terrain with regulatory layers
python3 tools/pick_section.py   # choose the section line objectively
python3 tools/transect.py       # 2 m profile + per-station regulation (needs geom.py first)
python3 tools/build_page.py     # assemble index.html
```

### Live endpoints that work from this environment

- **USGS 3DEP elevation**, no key:
  `https://epqs.nationalmap.gov/v1/json?x=<lon>&y=<lat>&units=Meters&wkid=4326`
  Returns `-1` for nodata/water. 1 m resolution over this headland.
- **PR Planning Board MIPR**, no key:
  `https://sige.pr.gov/server/rest/services/MIPR/<service>/MapServer/<layer>/query`
  Useful services: `Calificacion` (layer 0, zoning), `Georiesgo_v10B`
  (layer 12 tsunami evacuation, 14 FEMA flood zones), `Tenencia` (layer 11
  Zona Marítimo Terrestre).
- **NOAA CO-OPS**, no key:
  `https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations/9759110/datums.json`
- **Blocked by network policy:** `developer.nrel.gov` (PVWatts). The solar
  figure of 5.5 peak sun hours is an estimate and is labelled as one.

---

## 5. Design system

Read `/mnt/skills/public/frontend-design/SKILL.md` before changing anything
visual.

**Palette** (`assets/css/tokens.css`) — Guánica's actual arid coast: bleached
limestone, sage-grey thorn scrub, hard white light, deep blue-green water.
Closer to Baja than San Juan.

```
--abyss  #0B1F26   deep water — page ground, deliberately not black
--shelf  #14343B   panels
--reef   #4FB3A8   turquoise — used sparingly
--bone   #E4DFD2   bleached limestone — body text
--lamp   #E0A857   brass lamplight — the underground accent
--scrub  #7C8A6F   dry forest sage — labels, utility
--alarm  #CF7A5C   legal walls and hazards; earthen, not fire-engine
```

Surface tokens (`--ground --panel --ink --accent --edge`) are what components
actually paint with, so the underground swap works by redefining those on
`[data-depth='under']`.

**Type:** Fraunces (display, restrained), Karla (body), IBM Plex Mono
(technical — datums, tables, figures, annotations).

**The structural device: elevation datums.** Every section carries a real
ground elevation from the 3DEP transect. This is not decoration — vertical
position *is* the organizing principle, and the contents list is keyed by
elevation rather than by section number for the same reason.

**The one atmospheric move:** the contiguous run of underground sections
(`#tunnels` → `#shelter`) warms the page from blue-black to lamp gold and back.
One orchestrated transition, not scattered effects. Do not add more.

**Avoid** (these read as AI-templated): cream `#F4F1EA` with a high-contrast
serif and terracotta `#D97757`; near-black with a single acid-green accent;
broadsheet hairline-rule newspaper columns.

---

## 6. Status

| Phase | State |
|---|---|
| 0 — Integration survey | Done. USGS 3DEP + MIPR + NOAA approved and used; PVWatts blocked; image generation, Mapbox and the Anthropic Q&A declined. |
| 1 — Repo, tokens, typography, one section | Done |
| 2 — The full document | Done — 22 sections |
| 3 — The interactive section cut | Done — 20 interactive elements, generated from real data |
| 4 — The 3D walkthrough | Built — `walkthrough.html`. Rough in places; see below. |
| 5 — Polish: performance, mobile, a11y, reduced motion, self-critique | Not started |

### The walkthrough, as built

`walkthrough.html` + `assets/js/walkthrough.js`. Guided tour by default, free
walk available, touch-first, no pointer lock, quality toggle, and deep links:
`#terrace`, `#library`, `#descent`, `#gallery`, `#still`, `#club`, `#games`.
The terrain is displaced from the same `section-profile.json` the drawing uses,
so the ground you walk is the surveyed ground.

Four bugs are already fixed and worth not reintroducing: Three's default camera
forward is **−Z**, not +X, so yaw of 0 looks down −Z; interior surfaces need
`side: THREE.DoubleSide` or they vanish from inside; gallery segments must be
**tilted to the local grade** rather than built level and stacked, or the floor
slabs ahead rise into the sightline; and point-light intensity is in physical
units since r155, so room lighting wants values in the tens, not around 1.

Still rough, in rough order of payoff:

- **The house is a massing block.** No library interior, and the bookcase
  prompt is a button rather than a visible bookcase that swings. Route stop 5
  (`gate: true`) is where that belongs.
- **The club reveal is off-axis.** Arrival yaw is set per-stop now, but the
  lanes sit at the left edge rather than centred down the view. Tune
  `ROUTE[8].yaw` and the entry station.
- **No side passages** branch off the gallery yet — the spec calls for
  labelled branches to the casita, the shelter and the sally port.
- **The range, shelter, clinic and armory** are not modelled at all.
- **Untested on real hardware.** Every render here came from software
  rasterization in headless Chromium; frame rate on an actual mid-range phone
  is unknown, and the low-quality path has never been exercised.

### Known gaps and next steps

1. **Phase 5 has not been done at all.** No Lighthouse pass, no reduced-motion
   audit beyond the CSS already in place, no keyboard walkthrough of the
   section drawing on a real device.
2. **The section drawing's range box** sits below the club at greater depth,
   which is justified in its tooltip (sound isolation, open excavation) but
   still reads oddly. Worth a second look.
3. **The hero is quiet.** It was left deliberately restrained so the section
   drawing carries the boldness, per the brief's "spend your boldness in one
   place." Re-evaluate once the walkthrough exists.
4. **A site plan in plan view** does not exist and would pair well with the
   section. `data/parcel-context.json` already holds the parcel polygons and
   the ZMT line for exactly this.
5. **Asking price** ($675K vs $800K per lot) is still unresolved and the ledger
   assumes $675K.

---

## 7. The walkthrough spec

First-person, Three.js, static-hosted, touch-first. **A designed sequence, not a
free-roam sandbox:**

1. **Band A, the terrace.** Hard white sun, thorn scrub, the palapa, the view
   south across the conservation strip and the road to the reef flats.
2. **Up to Band B.** Through the open sacrificial ground level — carport, boats,
   breezeway — then up to the living deck. Trade winds through the pierced
   building. Pool behind.
3. **The library.** Find the bookcase. Interact with it. **It swings.**
4. **The descent.** Stair down into the gallery. Light temperature shifts from
   hard daylight to warm cove lamplight. Barrel vault, lime plaster, arched
   alcoves.
5. **The 200-foot walk.** **Do not shorten it.** The length is the point. Side
   passages branch off, labelled — to the casita, to the shelter, to the sally
   port.
6. **The Club.** The reveal. Two lit lanes, the bar, the games hall, warm and
   alive.
7. **Optional branches:** the range, the shelter, the clinic, the armory.

**Priorities, in order:** lighting (the daylight-to-lamplight transition is the
whole emotional arc) → correct scale (the tunnel really is 8×8 ft; the lanes
really are 60 ft to the headpin; the descent is ~12–15 ft) → performance on a
mid-range phone → labels that surface the engineering reasoning.

A clean, atmospheric massing model with correct dimensions and excellent
lighting will land far harder than an over-detailed model that stutters on a
phone. Include a **guided tour mode** (auto-play along the route) alongside free
movement — on a phone that will be the better experience. Controls: touch drag
to look, on-screen stick or tap-to-move on mobile; WASD + mouse on desktop.
Never trap the pointer without an obvious escape.

---

## 8. Tone

- **Direct and opinionated.** State the answer, then the reasoning. No
  motivational framing, no aspirational filler.
- **Lead with the constraint that actually binds.** The interesting content is
  always the thing that turned out to be the real limit: not power but morale;
  not shielding but air; not zoning but the maritime-terrestrial zone; not the
  equipment but the licence; and now, not the hazards but the fact that the
  parcel does not touch the water.
- **Flag uncertainty out loud.** Where a number is estimated, say so. Where a
  fact needs verification, name the agency that would settle it.
- **Never soften a legal wall.** The cannabis cultivation ban, the ATF conflict,
  the DEA limits, the ZMT. These get the `.wall` treatment and plain language.
- **The engineering asides are the good part.** Why string pinsetters beat
  free-fall on an island. Why propane pools on a buried floor. Why a
  smokeless-powder magazine wants wooden cabinets. Why a failed freshwater well
  is a successful RO feed. Keep every one of them.
- It is a daydream, and it should be **fun to read.** Precision and delight are
  not in tension here.
