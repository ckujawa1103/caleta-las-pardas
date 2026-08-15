/* The Guánica Compound — first-person walkthrough.
 *
 * Massing model at true scale, built on the same surveyed profile the section
 * drawing uses. The emotional arc is entirely in the lighting: hard white
 * Caribbean sun above ground, warm cove lamplight below, and a long walk
 * between them. Geometry is kept deliberately cheap so a mid-range phone can
 * hold frame rate; the budget goes to lights and to getting the dimensions
 * right.
 *
 * World axes: X = metres inland along the section line (station d)
 *             Y = metres elevation, PRVD02
 *             Z = metres across the parcel
 */
import * as THREE from './three/three.module.min.js';

const FT = 0.3048;

/* ---------------------------------------------------------------- constants */
const TUNNEL_W = 8 * FT;          // 8 ft wide inside, per spec
const TUNNEL_H = 8 * FT;          // 8 ft tall inside
const EYE = 1.65;                 // eye height
const GALLERY_DROP = 3.4;         // gallery floor below grade

const CLUB = { x0: 252, x1: 284, hz: 13, h: 4.2, fy: 0 };

const STATION = {                 // metres along the section
  terrace: 76,
  houseFront: 118,
  houseBack: 144,
  stairTop: 131,
  clubFront: 252,
  clubBack: 282,
};

/* ------------------------------------------------------------------ profile */
let profile = null;

function groundAt(x) {
  if (!profile) return 8;
  if (x <= profile[0].d) return profile[0].z;
  for (let i = 1; i < profile.length; i++) {
    const a = profile[i - 1], b = profile[i];
    if (x <= b.d) {
      const t = (x - a.d) / (b.d - a.d);
      return a.z + (b.z - a.z) * t;
    }
  }
  return profile[profile.length - 1].z;
}

/* -------------------------------------------------------------------- setup */
const canvas = document.getElementById('scene');
const renderer = new THREE.WebGLRenderer({
  canvas, antialias: false, powerPreference: 'high-performance',
});
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
renderer.setClearColor(0x9fc4cc);

const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0x9fc4cc, 40, 340);

const camera = new THREE.PerspectiveCamera(
  62, window.innerWidth / window.innerHeight, 0.1, 600);

let quality = 'auto';
function applyQuality() {
  const dpr = window.devicePixelRatio || 1;
  const cap = quality === 'low' ? 1 : quality === 'high' ? 2 : 1.5;
  renderer.setPixelRatio(Math.min(dpr, cap));
  renderer.setSize(window.innerWidth, window.innerHeight, false);
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
}

/* ------------------------------------------------------------------ palette */
const C = {
  limestone: 0xdcd5bf,
  scrub: 0x59684d,
  concrete: 0xe6e2d6,
  plaster: 0xe8d9bd,
  lamp: 0xe0a857,
  water: 0x1d6270,
  lane: 0xd8c9a2,
  felt: 0x2f6b56,
  dark: 0x241a12,
};

const mat = {};
function makeMats() {
  const m = (c, o = {}) => new THREE.MeshLambertMaterial(
    Object.assign({ color: c }, o));
  mat.ground = m(C.limestone);
  mat.scrub = m(C.scrub);
  mat.concrete = m(C.concrete);
  // every plaster surface is viewed from inside the room it encloses
  mat.plaster = m(C.plaster, { side: THREE.DoubleSide });
  mat.rock = m(0x8b8574);
  mat.water = m(C.water);
  mat.lane = m(C.lane);
  mat.felt = m(C.felt);
  mat.dark = m(C.dark);
  mat.floor = m(0x6f6553, { side: THREE.DoubleSide });
  mat.rib = m(0x8a7857, { side: THREE.DoubleSide });
  mat.glass = new THREE.MeshLambertMaterial({
    color: 0x9fd6d6, transparent: true, opacity: 0.28,
  });
  mat.lampGlow = new THREE.MeshBasicMaterial({ color: 0xffd9a0 });
  mat.laneLight = new THREE.MeshBasicMaterial({ color: 0xfff2d8 });
}

/* ------------------------------------------------------------------ terrain */
function buildTerrain() {
  const X0 = 0, X1 = 340, Z0 = -70, Z1 = 70;
  const nx = 110, nz = 40;
  const g = new THREE.PlaneGeometry(X1 - X0, Z1 - Z0, nx, nz);
  g.rotateX(-Math.PI / 2);
  const p = g.attributes.position;
  for (let i = 0; i < p.count; i++) {
    const x = p.getX(i) + (X0 + X1) / 2;
    const z = p.getZ(i);
    // real profile along X, gentle cross-fall in Z so it is not a ruled surface
    const base = groundAt(x);
    const cross = Math.cos(z * 0.014) * 1.6 - 1.6;
    const noise = Math.sin(x * 0.19 + z * 0.11) * 0.35
      + Math.sin(x * 0.07 - z * 0.23) * 0.5;
    p.setY(i, base + cross + noise);
    p.setX(i, x);
  }
  g.computeVertexNormals();
  const mesh = new THREE.Mesh(g, mat.ground);
  scene.add(mesh);

  // the sea, out past the waterline
  const sea = new THREE.Mesh(new THREE.PlaneGeometry(400, 400), mat.water);
  sea.rotation.x = -Math.PI / 2;
  sea.position.set(-190, 0, 0);
  scene.add(sea);

  // thorn scrub and columnar cactus, instanced
  const cactus = new THREE.CylinderGeometry(0.16, 0.2, 2.6, 5);
  const bush = new THREE.SphereGeometry(0.9, 6, 4);
  const nC = 260, nB = 340;
  const ci = new THREE.InstancedMesh(cactus, mat.scrub, nC);
  const bi = new THREE.InstancedMesh(bush, mat.scrub, nB);
  const dummy = new THREE.Object3D();
  let seed = 7;
  const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
  for (let i = 0; i < nC; i++) {
    const x = 40 + rnd() * 290, z = (rnd() - 0.5) * 130;
    dummy.position.set(x, groundAt(x) + 1.3, z);
    dummy.scale.setScalar(0.7 + rnd() * 0.8);
    dummy.updateMatrix();
    ci.setMatrixAt(i, dummy.matrix);
  }
  for (let i = 0; i < nB; i++) {
    const x = 20 + rnd() * 310, z = (rnd() - 0.5) * 135;
    dummy.position.set(x, groundAt(x) + 0.5, z);
    dummy.scale.set(1 + rnd(), 0.5 + rnd() * 0.4, 1 + rnd());
    dummy.updateMatrix();
    bi.setMatrixAt(i, dummy.matrix);
  }
  scene.add(ci, bi);
}

/* --------------------------------------------------------------- structures */
function box(w, h, d, m, x, y, z, parent) {
  const b = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), m);
  b.position.set(x, y, z);
  (parent || scene).add(b);
  return b;
}

function buildSurface() {
  // --- the palapa on the terrace
  const g = groundAt(STATION.terrace);
  for (const dz of [-4, 4]) {
    for (const dx of [-4, 4]) {
      box(0.24, 3, 0.24, mat.concrete, STATION.terrace + dx, g + 1.5, dz);
    }
  }
  const roof = box(10, 0.3, 10, mat.concrete, STATION.terrace, g + 3.1, 0);
  roof.rotation.y = 0;

  // --- the main house: open sacrificial ground level, two living levels above
  const hg = groundAt(131);
  const W = 26, D = 15;          // long axis across the section (east–west)
  // columns at grade
  for (const dx of [-11, 0, 11]) {
    for (const dz of [-6.5, 6.5]) {
      box(0.6, 4.2, 0.6, mat.concrete, 131 + dx, hg + 2.1, dz);
    }
  }
  // the living deck at 12–15 ft up
  box(W, 0.5, D, mat.concrete, 131, hg + 4.4, 0);
  // level 1 volume, pierced so the trades blow through
  box(W, 3.2, 5.5, mat.concrete, 131, hg + 6.2, -4.6);
  box(W, 3.2, 5.5, mat.concrete, 131, hg + 6.2, 4.6);
  box(W, 0.45, D, mat.concrete, 131, hg + 8.0, 0);
  // level 2, set back
  box(17, 3.0, 10, mat.concrete, 131, hg + 9.7, 0);
  // brise-soleil on the south (−X) face
  for (let i = 0; i < 7; i++) {
    box(W, 0.16, 1.5, mat.concrete, 131, hg + 5.2 + i * 0.62, -7.9);
  }
  // glazing
  box(W - 1, 2.6, 0.1, mat.glass, 131, hg + 6.2, -7.3);
  box(W - 1, 2.6, 0.1, mat.glass, 131, hg + 6.2, 7.3);
  // roof terrace parapet — the vertical evacuation refuge
  box(17, 0.9, 0.2, mat.concrete, 131, hg + 11.6, -5);
  box(17, 0.45, 10, mat.concrete, 131, hg + 11.3, 0);

  // --- the pool, behind the house
  box(18, 0.4, 8, mat.water, 160, groundAt(160) + 0.2, 0);

  // --- the casita
  const cg = groundAt(99);
  box(14, 5, 10, mat.concrete, 99, cg + 2.5, -26);

  // --- Band C surface: workshop, cisterns, array, pad
  box(20, 5, 12, mat.concrete, 206, groundAt(206) + 2.5, 8);
  for (let i = 0; i < 5; i++) {
    const px = 250 + i * 5.5;
    const pv = box(4.6, 0.14, 9, mat.dark, px, groundAt(px) + 1.5, -22);
    pv.rotation.z = -0.16;
  }
  const pad = box(24, 0.3, 24, mat.concrete, 305, groundAt(305) + 0.2, 26);
  pad.name = 'helipad';
}

/* ---------------------------------------------------------- the underground */
const lampLights = [];

function buildGallery() {
  // The gallery follows grade at constant cover, so it drains seaward: never
  // flat is a spec item, not a drawing convenience.
  const x0 = STATION.stairTop, x1 = CLUB.x0;
  const step = 4;
  const half = TUNNEL_W / 2;

  // A full open-ended tube rather than a half shell: the floor slab hides the
  // invert, and a closed tube cannot end up rotated open-side-sideways.
  const vault = new THREE.CylinderGeometry(
    half, half, step + 0.1, 14, 1, true);

  for (let x = x0; x <= x1; x += step) {
    const fy = groundAt(x) - GALLERY_DROP;
    // The gallery climbs at about eight per cent. Building each segment level
    // would stack them like stairs, and the floor slabs ahead would rise into
    // the sightline and read as a blank wall. Every piece is tilted to the
    // local grade instead — which is also what "never flat" actually means.
    const grade = (groundAt(x + step / 2) - groundAt(x - step / 2)) / step;
    const a = Math.atan(grade);
    const half2 = TUNNEL_W / 2;

    const fl = box(step + 0.2, 0.12, TUNNEL_W, mat.floor, x, fy, 0);
    fl.rotation.z = a;
    const ch = box(step + 0.2, 0.05, 0.22, mat.dark, x, fy + 0.07, 0);
    ch.rotation.z = a;

    for (const sd of [-1, 1]) {
      const w = box(step + 0.2, TUNNEL_H - half, 0.2, mat.plaster,
        x, fy + (TUNNEL_H - half) / 2, sd * half);
      w.rotation.z = a;
      const dd = box(step + 0.2, 0.16, 0.1, mat.rib,
        x, fy + TUNNEL_H - half - 0.3, sd * (half - 0.06));
      dd.rotation.z = a;
    }

    const v = new THREE.Mesh(vault, mat.plaster);
    v.rotation.z = Math.PI / 2 + a;
    v.position.set(x, fy + TUNNEL_H - half, 0);
    scene.add(v);

    const rib = new THREE.Mesh(
      new THREE.TorusGeometry(half - 0.01, 0.1, 6, 18), mat.rib);
    rib.rotation.set(0, Math.PI / 2, a);
    rib.position.set(x - step / 2, fy + TUNNEL_H - half - grade * step / 2, 0);
    scene.add(rib);
  }

  // warm cove lighting, every 11 m — sparse enough to stay cheap, close
  // enough that the tunnel never goes dark
  for (let x = x0 + 5; x < x1; x += 9) {
    const fy = groundAt(x) - GALLERY_DROP;
    for (const s of [-1, 1]) {
      const l = new THREE.PointLight(0xffb765, 14, 14, 2);
      l.position.set(x, fy + TUNNEL_H - half + 0.06, s * (half - 0.16));
      scene.add(l);
      lampLights.push(l);
      const b = new THREE.Mesh(new THREE.BoxGeometry(2.2, 0.05, 0.09),
        mat.lampGlow);
      b.position.set(x, fy + TUNNEL_H - half - 0.02, s * (half - 0.09));
      scene.add(b);
    }
  }

  // arched alcoves for wine and storage, alternating sides
  for (let i = 0, x = x0 + 14; x < x1 - 12; x += 12, i++) {
    const fy = groundAt(x) - GALLERY_DROP;
    const s = i % 2 ? 1 : -1;
    box(2.4, 2.0, 1.2, mat.dark, x, fy + 1.0, s * (half + 0.6));
  }

  // the descent: a stair from the library down into the gallery
  const topY = groundAt(STATION.stairTop) + 4.4;   // library is on the deck
  const botY = groundAt(STATION.stairTop) - GALLERY_DROP;
  const rise = topY - botY;
  const nSteps = Math.round(rise / 0.18);
  for (let i = 0; i < nSteps; i++) {
    const t = i / nSteps;
    box(0.28, 0.18, 1.2, mat.plaster,
      STATION.stairTop - 6 + t * 6, topY - t * rise, 0);
  }
}

function buildClub() {
  // The club floor is flat and meets the gallery exactly at the threshold, so
  // you walk in rather than stepping into a wall.
  const fy = groundAt(CLUB.x0) - GALLERY_DROP;
  CLUB.fy = fy;
  const W = CLUB.x1 - CLUB.x0, D = CLUB.hz * 2, cx = (CLUB.x0 + CLUB.x1) / 2;

  box(W, 0.2, D, mat.plaster, cx, fy - 0.1, 0);              // floor
  box(W, CLUB.h, 0.3, mat.plaster, cx, fy + CLUB.h / 2, -CLUB.hz);
  box(W, CLUB.h, 0.3, mat.plaster, cx, fy + CLUB.h / 2, CLUB.hz);
  box(0.3, CLUB.h, D, mat.plaster, CLUB.x1, fy + CLUB.h / 2, 0);
  box(W, 0.3, D, mat.plaster, cx, fy + CLUB.h, 0);           // ceiling
  // the entry wall, with the gallery opening left in it
  for (const dz of [-1, 1]) {
    box(0.3, CLUB.h, CLUB.hz - TUNNEL_W / 2, mat.plaster, CLUB.x0,
      fy + CLUB.h / 2, dz * (CLUB.hz + TUNNEL_W / 2) / 2);
  }

  // two lanes: 60 ft from foul line to headpin, so the run is real
  const foul = CLUB.x0 + 4;
  const laneLen = 60 * FT;
  for (const dz of [-4.4, -2.2]) {
    box(laneLen, 0.1, 1.05, mat.lane, foul + laneLen / 2, fy + 0.1, dz);
    box(2.4, 0.1, 1.4, mat.dark, foul - 1.4, fy + 0.1, dz);      // approach
    box(1.05, 0.05, 1.05, mat.laneLight, foul + laneLen, fy + 0.16, dz);
    box(1.3, 2.4, 1.5, mat.dark, foul + laneLen + 1.4, fy + 1.2, dz); // pit
  }
  for (let i = 0; i < 3; i++) {
    const l = new THREE.PointLight(0xfff0d2, 55, 26, 2);
    l.position.set(foul + 3 + i * 7.5, fy + CLUB.h - 0.5, -3.3);
    scene.add(l);
    lampLights.push(l);
  }

  // the bar at the junction, serving lanes and game floor from one position
  box(9, 1.1, 1.0, mat.dark, cx, fy + 0.55, 2.2);
  box(9.4, 0.1, 1.3, mat.lampGlow, cx, fy + 1.15, 2.2);
  const bl = new THREE.PointLight(0xffc27a, 60, 22, 2);
  bl.position.set(cx, fy + 2.8, 2.6);
  scene.add(bl);
  lampLights.push(bl);
  box(9, 2.2, 0.5, mat.dark, cx, fy + 1.6, 4.4);            // back bar

  // games hall, sightlines clear of one another
  box(2.8, 0.8, 1.6, mat.felt, cx - 6, fy + 0.4, 8.5);      // 9 ft pool table
  box(6.7, 0.8, 0.6, mat.lane, cx + 4, fy + 0.4, 7.4);      // 22 ft shuffleboard
  box(2.0, 0.8, 1.1, mat.dark, cx + 11, fy + 0.4, 9.6);     // air hockey
  for (let i = 0; i < 2; i++) {
    const gl = new THREE.PointLight(0xffd9a0, 45, 22, 2);
    gl.position.set(cx - 6 + i * 14, fy + CLUB.h - 0.5, 8);
    scene.add(gl);
    lampLights.push(gl);
  }
}

/* ------------------------------------------------------------------ lighting */
let sun, sky, hemi, underAmb;
function buildLights() {
  // hard white Caribbean light: strong sun, bright sky bounce off limestone
  sun = new THREE.DirectionalLight(0xfff4dc, 2.0);
  sun.position.set(60, 78, -150);     // low and from the south: raking light
  scene.add(sun);
  // bounce off bleached limestone is genuinely strong here, and it is what
  // keeps undersides from going black without shadow maps
  hemi = new THREE.HemisphereLight(0xcfe8ee, 0xbeb094, 1.05);
  scene.add(hemi);
  sky = new THREE.AmbientLight(0xffffff, 0.1);
  scene.add(sky);
  const fill = new THREE.DirectionalLight(0xdfeef2, 0.5);
  fill.position.set(-90, 40, 120);
  scene.add(fill);
  underAmb = new THREE.AmbientLight(0xffc98f, 0);
  scene.add(underAmb);
}

/* -------------------------------------------------------------------- route */
const ROUTE = [
  { x: 46, z: 0, look: 1, label: 'Band A — the terrace',
    text: 'The parcel starts at +7.2 m, behind the road. Everything here is '
        + 'expendable by design — to wind, not to water: this is Zone X, above '
        + 'both the tsunami evacuation line and the FEMA VE zone.' },
  { x: 96, z: 0, look: 1, label: 'Toward the house',
    text: 'The ground climbs eight per cent, steadily, all the way to the back '
        + 'boundary. That gradient is the entire plan.' },
  { x: 124, z: 0, look: 1, label: 'Under the house',
    text: 'Ground level is sacrificial: carport, boat storage, outdoor kitchen, '
        + 'breezeway. Open at grade so wind and water pass through, with the '
        + 'living deck twelve to fifteen feet up on concrete.' },
  { x: 131, z: 0, y: 4.4, look: 1, label: 'The living deck',
    text: 'Long axis east–west, so the two big faces look north and south. The '
        + 'building is pierced so the easterly trades blow straight through.' },
  { x: 128, z: 0, y: 4.4, look: 1, label: 'The library',
    text: 'The bookcase is counterbalanced on a pivot, with an electric release '
        + 'and a concealed trigger — and mechanical override from both sides, '
        + 'always. A power-dependent door in a compound built around outages is '
        + 'a trap, not a feature.', gate: true },
  { x: 140, z: 0, under: true, look: 1, label: 'The descent',
    text: 'Down into the gallery. Barrel-vaulted, lime-plastered, warm cove '
        + 'lighting. Napa wine cave, not missile silo.' },
  { x: 190, z: 0, under: true, look: 1, label: 'The gallery',
    text: 'Eight feet by eight feet inside, three feet of cover minimum, and '
        + 'never flat — it grades seaward to daylight. Every run of power, '
        + 'water, data and RO piping is on cable tray in here, because '
        + 'direct-buried conduit in salt air corrodes and then you excavate a '
        + 'landscape to fix a wire.' },
  { x: 232, z: 0, under: true, look: 1, label: 'Still walking',
    text: 'A hundred metres in. The distance is what sells it: long enough to '
        + 'stop being a doorway trick and start being a journey.' },
  { x: 258, z: -3.3, under: true, yaw: -Math.PI / 2, label: 'The Club',
    text: 'Two lit lanes, the bar at the junction, the games hall beyond. '
        + 'Four hundred and forty feet from the library. On a 300 kWh bank this '
        + 'room runs right through a lockdown — which is the point, because the '
        + 'binding constraint on thirty days sealed in is morale.' },
  { x: 268, z: 6, under: true, yaw: -Math.PI / 2.6, label: 'The games hall',
    text: 'Nine-foot pool table, twenty-two-foot shuffleboard, air hockey, two '
        + 'dart lanes — with sightlines arranged so no game blocks any other. '
        + 'Learned the hard way on an earlier version of this design.' },
];

/* ----------------------------------------------------------------- controls */
const state = {
  pos: new THREE.Vector3(ROUTE[0].x, 0, ROUTE[0].z),
  yaw: 0, pitch: 0,
  vel: new THREE.Vector3(),
  under: false,
  guided: true,
  leg: 0, legT: 0,
  keys: {},
  touchLook: null,
  stick: { active: false, dx: 0, dy: 0 },
};

function floorAt(x, under) {
  if (!under) return groundAt(x);
  return x >= CLUB.x0 ? CLUB.fy : groundAt(x) - GALLERY_DROP;
}

/* ------------------------------------------------------------------ the HUD */
const hud = {
  label: document.getElementById('hud-label'),
  text: document.getElementById('hud-text'),
  datum: document.getElementById('hud-datum'),
  prompt: document.getElementById('hud-prompt'),
};
let gateOpen = false;

function showStop(i) {
  const r = ROUTE[i];
  hud.label.textContent = r.label;
  hud.text.textContent = r.text;
  document.body.classList.toggle('is-under', !!r.under);
}

/* ------------------------------------------------------------------ the run */
let last = performance.now();

function tick(now) {
  const dt = Math.min(0.05, (now - last) / 1000);
  last = now;

  if (state.guided) {
    const a = ROUTE[state.leg], b = ROUTE[Math.min(state.leg + 1, ROUTE.length - 1)];
    if (a.gate && !gateOpen) {
      hud.prompt.hidden = false;
    } else {
      hud.prompt.hidden = true;
      const dist = Math.hypot(b.x - a.x, b.z - a.z) || 1;
      // the tunnel is long on purpose; move a little faster through it so the
      // guided tour stays watchable without shortening the geometry
      const speed = (a.under && b.under) ? 7.5 : 3.6;
      state.legT += (speed * dt) / dist;
      if (state.legT >= 1) {
        state.legT = 0;
        if (state.leg < ROUTE.length - 2) {
          state.leg++;
          showStop(state.leg);
        } else {
          state.guided = false;
          document.body.classList.add('is-free');
        }
      }
      const t = state.legT;
      state.pos.x = a.x + (b.x - a.x) * t;
      state.pos.z = a.z + (b.z - a.z) * t;
      state.under = t > 0.5 ? !!b.under : !!a.under;
      let target = Math.atan2(-(b.x - a.x), -(b.z - a.z));
      if (b.yaw !== undefined && state.legT > 0.55) target = b.yaw;
      let d = target - state.yaw;
      while (d > Math.PI) d -= Math.PI * 2;
      while (d < -Math.PI) d += Math.PI * 2;
      state.yaw += d * Math.min(1, dt * 2.2);
      const wantPitch = state.under
        ? Math.atan((groundAt(state.pos.x + 6) - groundAt(state.pos.x - 6)) / 12)
        : 0;
      state.pitch += (wantPitch - state.pitch) * Math.min(1, dt * 2);
    }
  } else {
    const fwd = (state.keys.w ? 1 : 0) - (state.keys.s ? 1 : 0)
      - state.stick.dy;
    const str = (state.keys.d ? 1 : 0) - (state.keys.a ? 1 : 0)
      + state.stick.dx;
    const sp = state.keys.shift ? 7 : 3.2;
    // forward = (-sin yaw, -cos yaw); right = (cos yaw, -sin yaw)
    const cos = Math.cos(state.yaw), sin = Math.sin(state.yaw);
    state.pos.x += (-fwd * sin + str * cos) * sp * dt;
    state.pos.z += (-fwd * cos - str * sin) * sp * dt;
    // the gallery is a corridor: stay in it while under, and surface at the
    // stair rather than walking through rock
    if (state.under) {
      const inClub = state.pos.x > CLUB.x0 + 0.5;
      const hz = inClub ? CLUB.hz - 0.5 : TUNNEL_W / 2 - 0.35;
      state.pos.z = THREE.MathUtils.clamp(state.pos.z, -hz, hz);
      state.pos.x = THREE.MathUtils.clamp(
        state.pos.x, STATION.stairTop, CLUB.x1 - 0.5);
    }
  }

  const fy = floorAt(state.pos.x, state.under);
  const y = (state.guided && ROUTE[state.leg].y && !state.under)
    ? groundAt(state.pos.x) + ROUTE[state.leg].y : fy;
  camera.position.set(state.pos.x, y + EYE, state.pos.z);
  camera.rotation.set(0, 0, 0, 'YXZ');
  camera.rotateY(state.yaw);
  camera.rotateX(state.pitch);

  // the atmospheric move, in three dimensions: daylight gives way to lamplight
  const u = state.under ? 1 : 0;
  const k = Math.min(1, dt * 2.4);
  sun.intensity += ((u ? 0.02 : 2.15) - sun.intensity) * k;
  hemi.intensity += ((u ? 0.06 : 0.85) - hemi.intensity) * k;
  sky.intensity += ((u ? 0.0 : 0.1) - sky.intensity) * k;
  underAmb.intensity += ((u ? 0.1 : 0) - underAmb.intensity) * k;
  const fogNear = u ? 3 : 40, fogFar = u ? 60 : 340;
  scene.fog.near += (fogNear - scene.fog.near) * k;
  scene.fog.far += (fogFar - scene.fog.far) * k;
  const bg = u ? 0x120c07 : 0x9fc4cc;
  scene.fog.color.lerp(new THREE.Color(bg), k);
  renderer.setClearColor(scene.fog.color);

  hud.datum.textContent = state.under
    ? `station ${state.pos.x.toFixed(0)} m · floor +${y.toFixed(1)} m · `
      + `${(groundAt(state.pos.x) - y).toFixed(1)} m below grade`
    : `station ${state.pos.x.toFixed(0)} m · +${y.toFixed(1)} m MSL`;

  renderer.render(scene, camera);
  requestAnimationFrame(tick);
}

/* -------------------------------------------------------------------- input */
function bindInput() {
  addEventListener('keydown', (e) => {
    const k = e.key.toLowerCase();
    if (['w', 'a', 's', 'd'].includes(k)) state.keys[k] = true;
    if (k === 'shift') state.keys.shift = true;
    if (k === 'e' && !gateOpen) openGate();
    if (k === 'escape') exitFree();
  });
  addEventListener('keyup', (e) => {
    const k = e.key.toLowerCase();
    if (['w', 'a', 's', 'd'].includes(k)) state.keys[k] = false;
    if (k === 'shift') state.keys.shift = false;
  });

  // drag to look — works with a mouse and with a finger, no pointer lock, so
  // there is never a state the reader cannot get out of
  let dragging = false, lx = 0, ly = 0;
  const dn = (x, y) => { dragging = true; lx = x; ly = y; };
  const mv = (x, y) => {
    if (!dragging) return;
    state.yaw -= (x - lx) * 0.0045;
    state.pitch = THREE.MathUtils.clamp(
      state.pitch - (y - ly) * 0.0045, -1.2, 1.2);
    lx = x; ly = y;
  };
  canvas.addEventListener('pointerdown', (e) => {
    if (state.guided) return;
    dn(e.clientX, e.clientY);
    canvas.setPointerCapture(e.pointerId);
  });
  canvas.addEventListener('pointermove', (e) => mv(e.clientX, e.clientY));
  canvas.addEventListener('pointerup', () => { dragging = false; });

  // on-screen stick
  const stick = document.getElementById('stick');
  const knob = document.getElementById('knob');
  let sx = 0, sy = 0;
  stick.addEventListener('pointerdown', (e) => {
    state.stick.active = true;
    const r = stick.getBoundingClientRect();
    sx = r.left + r.width / 2; sy = r.top + r.height / 2;
    stick.setPointerCapture(e.pointerId);
  });
  stick.addEventListener('pointermove', (e) => {
    if (!state.stick.active) return;
    const dx = THREE.MathUtils.clamp((e.clientX - sx) / 42, -1, 1);
    const dy = THREE.MathUtils.clamp((e.clientY - sy) / 42, -1, 1);
    state.stick.dx = dx; state.stick.dy = dy;
    knob.style.transform = `translate(${dx * 26}px, ${dy * 26}px)`;
  });
  const rel = () => {
    state.stick.active = false;
    state.stick.dx = state.stick.dy = 0;
    knob.style.transform = 'translate(0,0)';
  };
  stick.addEventListener('pointerup', rel);
  stick.addEventListener('pointercancel', rel);

  document.getElementById('btn-free').addEventListener('click', () => {
    state.guided = false;
    document.body.classList.add('is-free');
    hud.prompt.hidden = true;
  });
  document.getElementById('btn-restart').addEventListener('click', () => {
    state.guided = true; state.leg = 0; state.legT = 0; gateOpen = false;
    state.pos.set(ROUTE[0].x, 0, ROUTE[0].z);
    state.under = false;
    document.body.classList.remove('is-free');
    showStop(0);
  });
  document.getElementById('btn-gate').addEventListener('click', openGate);
  const q = document.getElementById('quality');
  q.addEventListener('change', () => { quality = q.value; applyQuality(); });

  addEventListener('resize', applyQuality);
}

function openGate() {
  gateOpen = true;
  hud.prompt.hidden = true;
}

function exitFree() {
  state.keys = {};
}

/* --------------------------------------------------------------------- boot */
async function boot() {
  const res = await fetch('data/section-profile.json');
  const json = await res.json();
  profile = json.profile.filter((r) => r.z !== null);

  makeMats();
  buildLights();
  buildTerrain();
  buildSurface();
  buildGallery();
  buildClub();
  applyQuality();

  const want = decodeURIComponent(location.hash.slice(1)).toLowerCase();
  if (want) {
    const i = ROUTE.findIndex((r) => r.label.toLowerCase().includes(want));
    if (i > -1) { state.leg = i; gateOpen = true; }
  }
  state.pos.set(ROUTE[state.leg].x, 0, ROUTE[state.leg].z);
  state.under = !!ROUTE[state.leg].under;
  state.yaw = -Math.PI / 2;   // look inland, up the section line
  showStop(state.leg);
  bindInput();
  document.getElementById('loading').hidden = true;
  requestAnimationFrame((t) => { last = t; tick(t); });
}

boot().catch((e) => {
  document.getElementById('loading').textContent =
    'The walkthrough could not start: ' + e.message
    + ' — the document itself is unaffected.';
});
