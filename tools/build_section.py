"""Generate the signature drawing: a cross-section through the headland.

Terrain comes from data/section-profile.json (USGS 3DEP 1 m, sampled every 2 m
along the fall line through the DTS parcel). The regulatory bands come from the
same file, sampled against the PR Planning Board's MIPR layers. Nothing in the
ground line is drawn by hand.

Output is spliced into index.html between the SECTION markers. It is committed,
so GitHub Pages serves static SVG; JavaScript only adds interaction.
"""
import json
import re

# ---- projection -----------------------------------------------------------
D0, D1 = -150.0, 450.0          # metres along the section line
Z0, Z1 = -14.0, 40.0            # metres elevation (PRVD02)
SX = 2.0                        # px per metre horizontal
VE = 2.5                        # vertical exaggeration — stated on the drawing
SY = SX * VE
PAD_L, PAD_T, PAD_B = 58, 72, 62
W = int((D1 - D0) * SX) + PAD_L + 22
H = int((Z1 - Z0) * SY) + PAD_T + PAD_B

CHAR_W = 6.1                    # px per char, IBM Plex Mono at 10.5px


def px(d):
    return PAD_L + (d - D0) * SX


def py(z):
    return PAD_T + (Z1 - z) * SY


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


# ---- programme ------------------------------------------------------------
# (d0, d1, height_m, id, short label, full label, detail)
SURFACE = [
    (60, 82, 2.6, 'palapa', 'Palapa', 'Palapa & fire pit',
     'Open palapa, fire pit, outdoor shower, boat ramp and davit. Expendable by '
     'design — nothing buried here but re-pullable conduit. On this parcel it '
     'also sits on land zoned CR, seaward of the road, which the design has to '
     'reckon with.'),
    (44, 56, 2.4, 'berm', 'Berm', 'Sea grape berm',
     'Landscape, privacy screen and genuine wave-energy dissipator at once. '
     'Privacy here has to be architectural — elevation, berm and building mass — '
     'because the shoreline itself is public domain and people may legally walk it.'),
    (90, 108, 6.5, 'casita', 'Casita', 'Guest casita',
     'On its own lot, for genuine separation. Reached from the main house by a '
     '200 ft tunnel run, which is how a guest ends up walking the gallery after '
     'dinner and deciding it is the best part of the property.'),
    (118, 144, 13.0, 'house', 'Main house', 'Main house — 4,500 sq ft',
     'Long axis east–west so the two big faces look north and south, and the '
     'building pierced so the easterly trades blow straight through. Ground '
     'level is sacrificial: carport, boat storage, outdoor kitchen, breezeway. '
     'Living space starts on a concrete deck 12–15 ft up. Roof terrace doubles '
     'as vertical evacuation refuge.'),
    (150, 170, 1.2, 'pool', 'Pool', 'Pool',
     'Behind the house, so building mass screens it from the public shoreline. '
     'Saltwater chlorination, no heating — you will never once want warmer '
     'water. Quietly infrastructure: thermal mass, fire reserve, and ~20,000 '
     'gallons of flushing water after a storm.'),
    (194, 218, 5.5, 'workshop', 'Workshop', 'Workshop & boathouse',
     'Band C surface. The concealed panel into the armory is in this wall, and '
     'the shelter entry is at the back of it.'),
    (226, 242, 1.0, 'cistern', 'Cisterns', 'Cistern field & utility vault',
     '50,000 gallons of buried concrete cistern under the terrace, sized to '
     'carry Christmas to May. Guánica is the driest place in Puerto Rico, so '
     'water is the genuinely hard problem here — not power.'),
    (250, 276, 1.6, 'solar', 'Array', 'Ground solar array',
     'One of five separate subarrays, each on its own MPPT. The splitting is '
     'the point: a hurricane that takes one does not take the system. Fixed, '
     'low-tilt, mechanically fastened through to concrete, never ballasted — '
     'and never a tracker, because a tracker in hurricane country is a sail.'),
    (292, 326, 0.6, 'helipad', 'Helipad', 'Helipad — 40×40 TLOF',
     'Set back from the bluff edge, because easterly trades rolling over a '
     'bluff face make mechanical turbulence exactly where an approach ends. '
     'Sized for a twin so charter operators can use it. Rotor downwash would '
     'strip the ground array, so the two are kept well apart.'),
]

# (d0, d1, drop_below_grade, height_m, id, short, full, detail, kind)
BURIED = [
    (192, 216, 4.2, 3.4, 'shelter', 'Shelter', 'The shelter',
     'Eight bunks, galley, air plant, stores, comms, Faraday cage. Designed '
     'like a small hotel rather than a submarine: daylight tubes, real '
     'ventilation, separate spaces. The binding constraints on thirty days '
     'sealed in are filter media and morale — not power, water or food.', 'room'),
    (220, 232, 3.8, 2.8, 'armory', 'Armory', 'The armory',
     'Deliberately not inside the shelter — you do not want a magazine in the '
     'room you are sealed into for a month. The dominant design problem is '
     'salt, not burglary: 35–45% RH held steady, desiccant backup that works '
     'at zero watts, open racks and never soft cases.', 'room'),
    (236, 248, 3.8, 2.8, 'clinic', 'Clinic', 'The clinic',
     'Shares a wall with the shelter so it is reachable fully sealed, and '
     'shares the shelter air plant. The equipment is the easy part; the licence '
     'to use it is not. A retained medical director with 24/7 telemedicine is '
     'what converts a room of expensive props into an actual clinic.', 'room'),
    (252, 282, 5.0, 4.2, 'club', 'THE CLUB', 'The Club — 4,500 sq ft',
     'Two synthetic lanes with string pinsetters, a games hall, the bar at the '
     'junction so it serves both, kitchen and lounge. All-electric, because '
     'propane is heavier than air and a leak in a buried room pools on the '
     'floor and waits. On a 300 kWh bank it runs right through a lockdown. The '
     'bunks are where you sleep for a month; this is where you actually live.',
     'club'),
    (258, 274, 10.4, 3.2, 'range', 'Range \u22a5', 'The range — 50 m, two lanes',
     'Cut across, not along: the 50 m run goes perpendicular to this section, out across the width of the parcel, so what you see here is a section through its two lanes. '
     'It is cut deeper than the rest of the gallery on purpose: more rock overhead is the cheapest sound isolation there is, and the excavation is already open. Granulated rubber backstop, laminar downrange airflow, HEPA exhaust. At '
     '15–25 kW while running it is the single largest load on the compound — '
     'and the one thing that cannot operate in lockdown.', 'room'),
]


def load():
    return json.load(open('data/section-profile.json'))['profile']


def ground_at(prof, d):
    best = None
    for r in prof:
        if r['z'] is None:
            continue
        if best is None or abs(r['d'] - d) < abs(best['d'] - d):
            best = r
    return best['z'] if best else 0.0


def stagger(items, gap=8):
    """Assign each (x_centre, width) label a lane so lanes never collide.
    Greedy: take the lowest lane whose last label ends before this one starts."""
    lanes = []
    out = []
    for i, (cx, w) in enumerate(items):
        x0, x1 = cx - w / 2, cx + w / 2
        placed = None
        for li, end in enumerate(lanes):
            if x0 >= end + gap:
                lanes[li] = x1
                placed = li
                break
        if placed is None:
            lanes.append(x1)
            placed = len(lanes) - 1
        out.append(placed)
    return out


def main():
    prof = load()

    wl_i = 0
    for i, r in enumerate(prof):
        if r['z'] is None or r['z'] <= 0.2:
            wl_i = i
    waterline_d = prof[wl_i]['d']

    shore = [r for r in prof if r['d'] >= waterline_d and r['z'] is not None]
    pts = [(px(r['d']), py(r['z'])) for r in shore]
    ground_d = ' '.join(f'{x:.1f},{y:.1f}' for x, y in pts)
    ground_fill = (f'M {pts[0][0]:.1f},{py(Z0):.1f} L '
                   + ' L '.join(f'{x:.1f},{y:.1f}' for x, y in pts)
                   + f' L {pts[-1][0]:.1f},{py(Z0):.1f} Z')
    # a thin regolith skin, so the surface reads as ground rather than as a void
    skin = (' L '.join(f'{x:.1f},{y:.1f}' for x, y in pts)
            + ' L ' + ' L '.join(f'{x:.1f},{y+9:.1f}' for x, y in reversed(pts)))

    land = [r for r in prof if r['z'] is not None]
    dts = [r for r in land if r['cali'] == 'DTS']
    dts_d0, dts_d1 = dts[0]['d'], dts[-1]['d']
    tez = [r for r in land if r['tez']]
    ve = [r for r in land if r['ve']]
    tez_d, tez_z = max(r['d'] for r in tez), max(r['z'] for r in tez)
    ve_d, ve_z = max(r['d'] for r in ve), max(r['z'] for r in ve)

    zone_runs, cur = [], None
    for r in land:
        c = r['cali'] or 'none'
        if cur is None or cur[0] != c:
            if cur:
                zone_runs.append(cur)
            cur = [c, r['d'], r['d']]
        else:
            cur[2] = r['d']
    if cur:
        zone_runs.append(cur)

    o = []
    a = o.append
    a(f'<svg id="sectioncut" viewBox="0 0 {W} {H}" role="img" '
      f'aria-labelledby="sc-title sc-desc" preserveAspectRatio="xMidYMid meet">')
    a('<title id="sc-title">Cross-section through the headland at Caleta Las '
      'Pardas</title>')
    a('<desc id="sc-desc">Ground profile surveyed from USGS 3DEP one-metre '
      'elevation data along a shore-perpendicular line, with the compound '
      'programme laid over it. The sea is at left; the ridge rises to the '
      'right. Surface structures sit on the ground line, and the buried gallery '
      'threads below it in warm gold with the club, shelter, clinic, armory and '
      'range hanging off it.</desc>')

    a('<defs>')
    a('<linearGradient id="sea" x1="0" y1="0" x2="0" y2="1">'
      '<stop offset="0" stop-color="#1d5560"/>'
      '<stop offset="1" stop-color="#0a1b21"/></linearGradient>')
    a('<linearGradient id="lampglow" x1="0" y1="0" x2="0" y2="1">'
      '<stop offset="0" stop-color="#e0a857" stop-opacity="0.34"/>'
      '<stop offset="1" stop-color="#e0a857" stop-opacity="0.05"/></linearGradient>')
    a('<pattern id="karst" width="26" height="18" patternUnits="userSpaceOnUse">'
      '<path d="M0 9h26M13 0v4M6 13v4M20 13v4" stroke="#39605c" '
      'stroke-width="0.7" opacity="0.5" fill="none"/></pattern>')
    a('</defs>')

    a(f'<rect x="0" y="0" width="{W}" height="{H}" fill="#0b1f26"/>')

    # --- sea ---------------------------------------------------------------
    sea_x1 = px(waterline_d)
    a(f'<rect x="{PAD_L}" y="{py(0):.1f}" width="{sea_x1-PAD_L:.1f}" '
      f'height="{py(Z0)-py(0):.1f}" fill="url(#sea)"/>')
    for k in range(4):
        yy = py(0) + 9 + k * 13
        a(f'<path d="M{PAD_L},{yy:.1f} h{sea_x1-PAD_L:.1f}" stroke="#4fb3a8" '
          f'stroke-width="0.7" opacity="{0.15-k*0.032:.3f}"/>')
    a(f'<text class="sc-note" x="{(PAD_L+sea_x1)/2:.1f}" y="{py(0)+42:.1f}" '
      f'text-anchor="middle">Shallow reef shelf — small craft only</text>')
    a(f'<text class="sc-note-s" x="{(PAD_L+sea_x1)/2:.1f}" y="{py(0)+56:.1f}" '
      f'text-anchor="middle">(3DEP carries no bathymetry; depth not surveyed here)</text>')

    # --- rock mass ---------------------------------------------------------
    a(f'<path d="{ground_fill}" fill="#16303a"/>')
    a(f'<path d="{ground_fill}" fill="url(#karst)"/>')
    a(f'<path d="M {skin} Z" fill="#2b4a48" opacity="0.85"/>')
    a(f'<polyline points="{ground_d}" fill="none" stroke="#dfe3d8" '
      f'stroke-width="1.8" stroke-linejoin="round"/>')

    # --- datums and grid ----------------------------------------------------
    for z in range(0, int(Z1) + 1, 10):
        op = 0.55 if z else 0.0
        if z:
            a(f'<line x1="{PAD_L}" y1="{py(z):.1f}" x2="{W-22}" y2="{py(z):.1f}" '
              f'stroke="#23474f" stroke-width="0.6" opacity="{op}"/>')
        a(f'<text class="sc-tick" x="{PAD_L-9}" y="{py(z)+3.5:.1f}" '
          f'text-anchor="end">{z} m</text>')
    a(f'<line x1="{PAD_L}" y1="{py(0):.1f}" x2="{W-22}" y2="{py(0):.1f}" '
      f'stroke="#4fb3a8" stroke-width="1" stroke-dasharray="7 5" opacity="0.6"/>')

    for d in range(-100, int(D1) + 1, 50):
        a(f'<text class="sc-tick" x="{px(d):.1f}" y="{H-10}" '
          f'text-anchor="middle">{d:+d} m</text>')

    # --- zoning strip -------------------------------------------------------
    strip_y = H - PAD_B + 26
    zcolor = {'DTS': '#4fb3a8', 'CR': '#7c8a6f', 'B-Q': '#46614f',
              'VIAL': '#a08a63', 'none': '#22333a'}
    zname = {'DTS': 'DTS — Distrito Turístico Selectivo, the buildable parcel',
             'CR': 'CR — Conservación de Recursos',
             'B-Q': 'B-Q — Bosque, protected forest',
             'VIAL': 'Road corridor', 'none': 'unclassified'}
    a(f'<text class="sc-axis" x="{PAD_L}" y="{strip_y-7:.1f}">'
      f'Zoning along the section — PR Junta de Planificación, MIPR</text>')
    for code, d0, d1 in zone_runs:
        x0, x1 = px(d0), px(min(d1 + 2, D1))
        if x1 - x0 < 1:
            continue
        a(f'<rect class="sc-zone" x="{x0:.1f}" y="{strip_y:.1f}" '
          f'width="{x1-x0:.1f}" height="10" fill="{zcolor.get(code,"#22333a")}" '
          f'opacity="0.85"><title>{esc(zname.get(code,code))} — station '
          f'{d0:.0f} to {d1:.0f} m</title></rect>')

    # --- parcel bracket + bands ---------------------------------------------
    by = 22
    a('<g class="sc-bracket">')
    a(f'<line x1="{px(dts_d0):.1f}" y1="{by}" x2="{px(dts_d1):.1f}" y2="{by}" '
      f'stroke="#4fb3a8" stroke-width="1.2"/>')
    for xx in (px(dts_d0), px(dts_d1)):
        a(f'<line x1="{xx:.1f}" y1="{by-5}" x2="{xx:.1f}" y2="{by+5}" '
          f'stroke="#4fb3a8" stroke-width="1.2"/>')
    a(f'<text class="sc-bracket-t" x="{(px(dts_d0)+px(dts_d1))/2:.1f}" '
      f'y="{by-9}" text-anchor="middle">Buildable parcel — DTS zoning, '
      f'{dts_d1-dts_d0:.0f} m deep, +{ground_at(prof, dts_d0):.1f} m to '
      f'+{ground_at(prof, dts_d1):.1f} m</text>')
    a('</g>')

    bands = [('0', -6, 44, 'The public strip',
               'Conservation zoning, the maritime-terrestrial zone and the road, '
               'in that order. Not the parcel. The compound looks across it to '
               'the water and builds nothing on it — which is also why the boat '
               'lives in Guánica Bay rather than on a ramp below the house.'),
              ('A', 44, 100, 'Band A — the terrace',
               'The parcel starts here, at +7.2 m, behind the road. This is the '
               'outdoor room: palapa, fire pit, pool, the long view south over '
               'the reef flats. Expendable by design, and now expendable to '
               'wind rather than to water.'),
              ('B', 100, 190, 'Band B — the house',
               'Elevated, hardened, comfortable, +9 m to +18 m. Ground level '
               'open and sacrificial; living space above it on a concrete deck.'),
              ('C', 190, 284, 'Band C — the fortress',
               'Utilities, stores, and everything buried, climbing to +26 m at '
               'the back boundary. Nearly eight acres is what lets the septic '
               'drip field, the range and the helipad all fit without fighting '
               'each other.')]
    for code, d0, d1, name, detail in bands:
        x0, x1 = px(d0), px(d1)
        a(f'<g class="sc-band" data-id="band{code}" tabindex="0" role="button" '
          f'aria-label="{esc(name)}">')
        a(f'<rect class="sc-band-hit" x="{x0:.1f}" y="{PAD_T-26:.1f}" '
          f'width="{x1-x0:.1f}" height="{H-PAD_B-PAD_T+26:.1f}" fill="#4fb3a8" '
          f'opacity="0"/>')
        a(f'<line x1="{x0:.1f}" y1="{by+12}" x2="{x0:.1f}" y2="{H-PAD_B:.1f}" '
          f'stroke="#e4dfd2" stroke-width="0.5" opacity="0.16"/>')
        a(f'<text class="sc-band-t" x="{(x0+x1)/2:.1f}" y="{by+24}" '
          f'text-anchor="middle">BAND {code}</text>')
        a(f'<title>{esc(name)} — {esc(detail)}</title>')
        a('</g>')

    # --- hazard limits: rotated so two close lines never collide -------------
    for hid, hd, hz, label, dx in (
            ('ve', ve_d, ve_z, 'FEMA VE — BFE 3.4 m', -13),
            ('tez', tez_d, tez_z, f'Tsunami evac — +{tez_z:.1f} m', 5)):
        x = px(hd) + dx
        a(f'<g class="sc-haz" data-id="{hid}" tabindex="0" role="button" '
          f'aria-label="{esc(label)}">')
        htop = PAD_T + 4
        a(f'<line x1="{x:.1f}" y1="{py(hz):.1f}" x2="{x:.1f}" y2="{htop:.1f}" '
          f'stroke="#cf7a5c" stroke-width="1" stroke-dasharray="4 4" '
          f'opacity="0.9"/>')
        ty = py(hz) - 10
        a(f'<text class="sc-haz-t" x="{x-3:.1f}" y="{ty:.1f}" '
          f'transform="rotate(-90 {x-3:.1f} {ty:.1f})">{esc(label)}</text>')
        a(f'<title>{esc(label)} — Both hazard limits stop seaward of the road, '
          f'below +3.2 m. Every hardened part of this compound sits above +7 m, '
          f'outside them. The vertical-evacuation refuge stays worth owning; it '
          f'is no longer what the building is for.</title>')
        a('</g>')

    # --- the gallery --------------------------------------------------------
    gal = [(px(d), py(ground_at(prof, d) - 3.4)) for d in range(130, 300, 4)]
    gal_d = ' '.join(f'{x:.1f},{y:.1f}' for x, y in gal)
    a('<g class="sc-gallery">')
    a(f'<polyline points="{gal_d}" fill="none" stroke="#e0a857" '
      f'stroke-width="9" opacity="0.15" stroke-linecap="round"/>')
    a(f'<polyline points="{gal_d}" fill="none" stroke="#e0a857" '
      f'stroke-width="2.6" stroke-linecap="round"/>')
    a('</g>')

    # sally port: descends from the house, daylights through the bluff face
    sp = [(px(d), py(max(3.0, min(ground_at(prof, 130) - 3.4,
                                  ground_at(prof, d) - 1.4))))
          for d in range(130, 42, -4)]
    sp_d = ' '.join(f'{x:.1f},{y:.1f}' for x, y in sp)
    a('<g class="sc-room" data-id="sallyport" tabindex="0" role="button" '
      'aria-label="Sea sally port">')
    a(f'<polyline points="{sp_d}" fill="none" stroke="#e0a857" '
      f'stroke-width="8" opacity="0.11" stroke-linecap="round"/>')
    a(f'<polyline points="{sp_d}" fill="none" stroke="#e0a857" '
      f'stroke-width="1.8" stroke-dasharray="7 4" stroke-linecap="round"/>')
    a('<title>Sea sally port — Descends from the house and daylights through '
      'the bluff face above water, gravity-drained, closed at the uphill end by '
      'a marine watertight bulkhead door. Anything at or below the water table '
      'on limestone becomes a hull you pump forever, so it is never allowed to '
      'go below. In a tsunami you dog it down; the tunnel floods and drains.'
      '</title>')
    a('</g>')

    # --- buried rooms, labels laddered below --------------------------------
    boxes = []
    for d0, d1, drop, hgt, rid, short, full, detail, kind in BURIED:
        gz = ground_at(prof, (d0 + d1) / 2)
        top = gz - drop
        boxes.append((px(d0), px(d1), py(top), py(top - hgt), rid, short, full,
                      detail, kind))
    lanes = stagger([((b[0] + b[1]) / 2, len(b[5]) * CHAR_W + 10) for b in boxes])

    for (x0, x1, y0, y1, rid, short, full, detail, kind), lane in zip(boxes, lanes):
        cx = (x0 + x1) / 2
        ly = y1 + 15 + lane * 14
        cls = 'sc-room sc-room--club' if kind == 'club' else 'sc-room'
        a(f'<g class="{cls}" data-id="{rid}" tabindex="0" role="button" '
          f'aria-label="{esc(full)}">')
        if kind == 'club':
            a(f'<rect x="{x0-7:.1f}" y="{y0-7:.1f}" width="{x1-x0+14:.1f}" '
              f'height="{y1-y0+14:.1f}" fill="url(#lampglow)" rx="3"/>')
        a(f'<rect class="sc-room-box" x="{x0:.1f}" y="{y0:.1f}" '
          f'width="{x1-x0:.1f}" height="{y1-y0:.1f}" rx="2"/>')
        a(f'<line x1="{cx:.1f}" y1="{y1:.1f}" x2="{cx:.1f}" y2="{ly-9:.1f}" '
          f'stroke="#e0a857" stroke-width="0.7" opacity="0.55"/>')
        tcls = 'sc-room-t sc-room-t--club' if kind == 'club' else 'sc-room-t'
        a(f'<text class="{tcls}" x="{cx:.1f}" y="{ly:.1f}" '
          f'text-anchor="middle">{esc(short)}</text>')
        a(f'<title>{esc(full)} — {esc(detail)}</title>')
        a('</g>')

    # the walk: the distance is the point, so it gets a dimension line
    wx0, wx1 = px(131), px(267)
    wy = max(b[3] for b in boxes) + 15 + (max(lanes) + 1) * 14 + 8
    a('<g class="sc-dim">')
    a(f'<line x1="{wx0:.1f}" y1="{wy:.1f}" x2="{wx1:.1f}" y2="{wy:.1f}" '
      f'stroke="#e0a857" stroke-width="0.8" opacity="0.7"/>')
    for xx in (wx0, wx1):
        a(f'<line x1="{xx:.1f}" y1="{wy-4:.1f}" x2="{xx:.1f}" y2="{wy+4:.1f}" '
          f'stroke="#e0a857" stroke-width="0.8" opacity="0.7"/>')
    a(f'<text class="sc-dim-t" x="{(wx0+wx1)/2:.1f}" y="{wy+14:.1f}" '
      f'text-anchor="middle">200 ft — library bookcase to the lanes</text>')
    a('</g>')

    # --- surface structures, labels laddered above --------------------------
    sboxes = []
    for d0, d1, hgt, sid, short, full, detail in SURFACE:
        gz = ground_at(prof, (d0 + d1) / 2)
        sboxes.append((px(d0), px(d1), py(gz), py(gz + hgt), sid, short, full,
                       detail))
    slanes = stagger([((b[0] + b[1]) / 2, len(b[5]) * CHAR_W + 10)
                      for b in sboxes])

    for (x0, x1, y0, y1, sid, short, full, detail), lane in zip(sboxes, slanes):
        cx = (x0 + x1) / 2
        ly = y1 - 9 - lane * 14
        a(f'<g class="sc-struct" data-id="{sid}" tabindex="0" role="button" '
          f'aria-label="{esc(full)}">')
        a(f'<rect class="sc-struct-box" x="{x0:.1f}" y="{y1:.1f}" '
          f'width="{x1-x0:.1f}" height="{y0-y1:.1f}" rx="1.5"/>')
        a(f'<line x1="{cx:.1f}" y1="{y1:.1f}" x2="{cx:.1f}" y2="{ly+4:.1f}" '
          f'stroke="#c9d2c2" stroke-width="0.7" opacity="0.45"/>')
        a(f'<text class="sc-struct-t" x="{cx:.1f}" y="{ly:.1f}" '
          f'text-anchor="middle">{esc(short)}</text>')
        a(f'<title>{esc(full)} — {esc(detail)}</title>')
        a('</g>')

    a(f'<text class="sc-axis" x="{W-22}" y="{16}" text-anchor="end">'
      f'Vertical exaggeration {VE:g}×</text>')
    a('</svg>')

    svg = '\n'.join(o)
    html = open('index.html', encoding='utf8').read()
    new = re.sub(r'(<!-- SECTION:START -->).*?(<!-- SECTION:END -->)',
                 lambda m: m.group(1) + '\n' + svg + '\n' + m.group(2),
                 html, flags=re.S)
    open('index.html', 'w', encoding='utf8').write(new)
    print(f'section {W}×{H}, {len(svg):,} bytes, '
          f'{len(SURFACE)+len(BURIED)+len(bands)+2} interactive elements')
    print(f'  surface label lanes {max(slanes)+1}, buried label lanes {max(lanes)+1}')


if __name__ == '__main__':
    main()
