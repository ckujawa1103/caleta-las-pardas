"""Fuse the 3DEP terrain grid with the MIPR regulatory layers.

Answers, for the DTS parcel at Caleta Las Pardas:
  - where the buildable (DTS) polygon actually sits relative to the shore
  - where the tsunami evacuation line crosses it
  - where the FEMA VE / X boundary sits
  - the real ground profile along a shore-perpendicular section line
"""
import json
import math

LAT_M = 110900.0


def lon_m(lat):
    return 111320.0 * math.cos(math.radians(lat))


def pip(pt, rings):
    """Point in polygon, even-odd, holes handled by parity across all rings."""
    x, y = pt
    inside = False
    for ring in rings:
        n = len(ring)
        for i in range(n):
            x0, y0 = ring[i][0], ring[i][1]
            x1, y1 = ring[(i + 1) % n][0], ring[(i + 1) % n][1]
            if (y0 > y) != (y1 > y):
                xin = x0 + (y - y0) * (x1 - x0) / (y1 - y0)
                if x < xin:
                    inside = not inside
    return inside


def load():
    dem = json.load(open("data/dem-dts-20m.json"))
    geom = json.load(open("data/mipr-geometry.json"))
    return dem, geom


def cell_ll(dem, i, j):
    lat = dem["lat0"] + (i - (dem["ny"] - 1) / 2) * dem["step_m"] / LAT_M
    lon = dem["lon0"] + (j - (dem["nx"] - 1) / 2) * dem["step_m"] / lon_m(dem["lat0"])
    return lat, lon


def main():
    dem, geom = load()
    g = dem["grid"]
    ny, nx = dem["ny"], dem["nx"]

    zoning = [f for f in geom["zoning"]["features"]]
    dts = [f for f in zoning if f["attributes"].get("cali") == "DTS"]
    tez = geom["tez"]["features"]
    flood = geom["flood"]["features"]
    ve = [f for f in flood if f["attributes"].get("FLD_ZONE") == "VE"]

    print(f"DTS polygons: {len(dts)}   TEZ: {len(tez)}   VE: {len(ve)}")

    # classify every cell
    cls = [[None] * nx for _ in range(ny)]
    for i in range(ny):
        for j in range(nx):
            lat, lon = cell_ll(dem, i, j)
            p = (lon, lat)
            in_dts = any(pip(p, f["geometry"]["rings"]) for f in dts)
            in_tez = any(pip(p, f["geometry"]["rings"]) for f in tez)
            in_ve = any(pip(p, f["geometry"]["rings"]) for f in ve)
            cls[i][j] = (in_dts, in_tez, in_ve)

    ch = " .:-=+*#%@"
    print("\nTerrain (north up). letters = DTS-zoned land, digits = elevation band")
    print("  ~ water/nodata   lowercase = inside tsunami evacuation zone\n")
    for i in range(ny - 1, -1, -1):
        row = ""
        for j in range(nx):
            v = g[i][j]
            in_dts, in_tez, _ = cls[i][j]
            if v is None:
                row += "~"
                continue
            c = ch[min(9, int(v / 6.0))]
            if in_dts:
                c = "ABCDEFGHIJ"[min(9, int(v / 6.0))]
                if in_tez:
                    c = c.lower()
            row += c
        y = (i - (ny - 1) / 2) * dem["step_m"]
        print(f"{y:+6.0f} {row}")

    # DTS extent + elevation stats
    el = [g[i][j] for i in range(ny) for j in range(nx)
          if cls[i][j][0] and g[i][j] is not None]
    if el:
        print(f"\nDTS cells with terrain: {len(el)}  "
              f"elev min {min(el):.1f}  max {max(el):.1f}  mean {sum(el)/len(el):.1f} m")

    # how high does the tsunami evacuation zone reach?
    tez_el = [g[i][j] for i in range(ny) for j in range(nx)
              if cls[i][j][1] and g[i][j] is not None]
    out_el = [g[i][j] for i in range(ny) for j in range(nx)
              if not cls[i][j][1] and g[i][j] is not None]
    if tez_el:
        print(f"Inside TEZ : n={len(tez_el):5}  elev {min(tez_el):.1f} .. {max(tez_el):.1f} m")
    if out_el:
        print(f"Outside TEZ: n={len(out_el):5}  elev {min(out_el):.1f} .. {max(out_el):.1f} m")

    json.dump({"ny": ny, "nx": nx, "cls": cls}, open("data/dem-dts-class.json", "w"))


if __name__ == "__main__":
    main()
