"""Build the authoritative section profile for the signature drawing.

For every 2 m station along a shore-perpendicular line through the DTS parcel,
record ground elevation (USGS 3DEP 1 m) plus the regulatory facts that govern
what may be built there (MIPR zoning, tsunami evacuation zone, FEMA flood zone).

The three-band scheme is a claim about this profile. This is the check.
"""
import concurrent.futures
import json
import math
import time
import urllib.request

LAT_M = 110900.0

# Chosen by tools/pick_section.py: the shoreline cell on the DTS parcel with the
# longest continuous run of DTS-zoned land inland, and the local fall line there.
SHORE = (17.94444, -66.92446)
BEARING_DEG = 317.6      # uphill / inland
SEAWARD_M = 150.0        # start this far out into the water
INLAND_M = 450.0
STEP_M = 2.0


def lon_m(lat):
    return 111320.0 * math.cos(math.radians(lat))


def point_at(d):
    b = math.radians(BEARING_DEG)
    lat = SHORE[0] + (d * math.cos(b)) / LAT_M
    lon = SHORE[1] + (d * math.sin(b)) / lon_m(SHORE[0])
    return lat, lon


def pip(pt, rings):
    x, y = pt
    inside = False
    for ring in rings:
        n = len(ring)
        for i in range(n):
            x0, y0 = ring[i][0], ring[i][1]
            x1, y1 = ring[(i + 1) % n][0], ring[(i + 1) % n][1]
            if (y0 > y) != (y1 > y):
                if x < x0 + (y - y0) * (x1 - x0) / (y1 - y0):
                    inside = not inside
    return inside


def elev(args):
    d, lat, lon = args
    u = (f"https://epqs.nationalmap.gov/v1/json?x={lon:.7f}&y={lat:.7f}"
         f"&units=Meters&wkid=4326")
    for a in range(4):
        try:
            v = float(json.load(urllib.request.urlopen(u, timeout=40))["value"])
            return (d, lat, lon, None if v <= -0.99 else v)
        except Exception:
            time.sleep(1 + a)
    return (d, lat, lon, None)


def main():
    geom = json.load(open("data/mipr-geometry.json"))
    zoning = geom["zoning"]["features"]
    tez = geom["tez"]["features"]
    ve = [f for f in geom["flood"]["features"]
          if f["attributes"].get("FLD_ZONE") == "VE"]

    n = int((SEAWARD_M + INLAND_M) / STEP_M) + 1
    pts = [(i * STEP_M - SEAWARD_M,) + point_at(i * STEP_M - SEAWARD_M)
           for i in range(n)]
    t = time.time()
    with concurrent.futures.ThreadPoolExecutor(12) as ex:
        rows = list(ex.map(elev, pts))
    print(f"{len(rows)} stations in {time.time()-t:.0f}s")

    out = []
    for d, lat, lon, z in rows:
        p = (lon, lat)
        cali = None
        for f in zoning:
            if pip(p, f["geometry"]["rings"]):
                cali = f["attributes"].get("cali")
                if cali == "DTS":
                    break
        out.append({
            "d": round(d, 1), "lat": round(lat, 7), "lon": round(lon, 7),
            "z": None if z is None else round(z, 2),
            "cali": cali,
            "tez": any(pip(p, f["geometry"]["rings"]) for f in tez),
            "ve": any(pip(p, f["geometry"]["rings"]) for f in ve),
        })

    json.dump({
        "source_terrain": "USGS 3DEP 1 m DEM via National Map EPQS",
        "source_regulatory": "PR Junta de Planificacion MIPR (sige.pr.gov)",
        "datum": "PRVD02; MSL is 0.05 ft above it at Magueyes Island (NOAA 9759110)",
        "shore_point": SHORE, "bearing_deg": BEARING_DEG, "step_m": STEP_M,
        "profile": out,
    }, open("data/section-profile.json", "w"), indent=1)

    # summary
    land = [r for r in out if r["z"] is not None]
    water = [r for r in out if r["z"] is None]
    dts = [r for r in land if r["cali"] == "DTS"]
    print(f"land stations {len(land)}, water {len(water)}, DTS {len(dts)}")
    if dts:
        print(f"DTS runs d={dts[0]['d']:.0f}..{dts[-1]['d']:.0f} m, "
              f"z {min(r['z'] for r in dts):.1f}..{max(r['z'] for r in dts):.1f} m")
    tezr = [r for r in land if r["tez"]]
    ver = [r for r in land if r["ve"]]
    if tezr:
        print(f"tsunami evac zone up to d={max(r['d'] for r in tezr):.0f} m, "
              f"z={max(r['z'] for r in tezr):.1f} m")
    if ver:
        print(f"FEMA VE up to d={max(r['d'] for r in ver):.0f} m, "
              f"z={max(r['z'] for r in ver):.1f} m")
    print()
    zmax = max(r["z"] for r in land)
    for r in out[::6]:
        z = r["z"]
        if z is None:
            print(f"{r['d']:6.0f}   ~~~~~ water")
        else:
            flag = ("D" if r["cali"] == "DTS" else (r["cali"] or "-")[:4]).ljust(5)
            hz = ("T" if r["tez"] else " ") + ("V" if r["ve"] else " ")
            print(f"{r['d']:6.0f} {z:6.1f} {flag}{hz} "
                  + "#" * int(max(0, z) / zmax * 46))


if __name__ == "__main__":
    main()
