"""Choose the section line objectively.

Wanted: the shore-perpendicular line that (a) starts in the water, (b) crosses
DTS-zoned land, and (c) has the longest continuous run of DTS land inland --
i.e. the place on this parcel where a 140 m waterfront lot actually fits.
"""
import json
import math

LAT_M = 110900.0


def lon_m(lat):
    return 111320.0 * math.cos(math.radians(lat))


def main():
    dem = json.load(open("data/dem-dts-20m.json"))
    cl = json.load(open("data/dem-dts-class.json"))
    g, cls = dem["grid"], cl["cls"]
    ny, nx, step = dem["ny"], dem["nx"], dem["step_m"]

    def xy(i, j):
        return ((j - (nx - 1) / 2) * step, (i - (ny - 1) / 2) * step)

    best = None
    for j in range(nx):
        # walk north from the southern edge; find first land, then count DTS run
        col = [(i, g[i][j], cls[i][j][0]) for i in range(ny)]
        water_below = None
        for i in range(ny):
            if col[i][1] is None:
                water_below = i
            elif water_below is not None:
                # first land cell above water at row i
                run, k, dts_cells = 0, i, 0
                while k < ny and col[k][1] is not None:
                    if col[k][2]:
                        dts_cells += 1
                    run += 1
                    k += 1
                if dts_cells >= 5:
                    inland = dts_cells * step
                    z_top = max(c[1] for c in col[i:k] if c[1] is not None)
                    score = inland
                    if best is None or score > best["inland"]:
                        best = dict(j=j, i_shore=i, inland=inland, run_m=run * step,
                                    z_top=z_top, dts_cells=dts_cells)
                break

    print("best column:", best)
    i, j = best["i_shore"], best["j"]
    x, y = xy(i, j)
    lat = dem["lat0"] + y / LAT_M
    lon = dem["lon0"] + x / lon_m(dem["lat0"])
    print(f"shoreline point: {lat:.6f}, {lon:.6f}   (x={x:+.0f} y={y:+.0f})")

    # local aspect: fit the uphill direction over a 5x5 window inland of the shore
    ii = min(ny - 3, i + 3)
    dz_dy = dz_dx = 0.0
    n = 0
    for a in range(-2, 3):
        for b in range(-2, 3):
            p, q = ii + a, j + b
            if 0 < p < ny - 1 and 0 < q < nx - 1:
                zn, zs = g[p + 1][q], g[p - 1][q]
                ze, zw = g[p][q + 1], g[p][q - 1]
                if None in (zn, zs, ze, zw):
                    continue
                dz_dy += (zn - zs) / (2 * step)
                dz_dx += (ze - zw) / (2 * step)
                n += 1
    if n:
        dz_dy /= n
        dz_dx /= n
    bearing = math.degrees(math.atan2(dz_dx, dz_dy)) % 360
    grade = math.hypot(dz_dx, dz_dy)
    print(f"uphill bearing {bearing:.1f} deg   mean grade {grade*100:.1f}%  (n={n})")
    print(f"\nSuggested transect:\n  START = ({lat:.5f}, {lon:.5f})\n"
          f"  BEARING_DEG = {bearing:.1f}\n"
          f"  DTS land continues ~{best['inland']:.0f} m inland, "
          f"local high {best['z_top']:.1f} m")


if __name__ == "__main__":
    main()
