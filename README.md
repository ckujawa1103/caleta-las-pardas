# The Guánica Compound — Caleta Las Pardas

An interactive design document for an imagined fortified off-grid compound on a
limestone headland in Guánica, Puerto Rico. A lottery daydream, engineered
seriously — and then checked against primary survey data, which disagreed with
several of its premises.

Static site. No build step, no tracking, no third-party requests: fonts, and
every byte of data the page reads, are served from this repository.

## What is here

| Path | |
|---|---|
| `index.html` | The document, including the signature cross-section |
| `assets/` | Styles, self-hosted fonts, and the section's interaction script |
| `data/` | Terrain and regulatory data, cached as JSON so the page never calls out |
| `tools/` | The scripts that fetched that data and generate the drawing |

## The data is real

The site itself is fiction. The ground under it is not.

- **Terrain** — USGS 3DEP 1 m DEM, via the National Map elevation point query
  service. The section profile is sampled every 2 m along a shore-perpendicular
  line; the surrounding grids are sampled at 20 m.
- **Zoning, tsunami evacuation zone, flood zones, maritime-terrestrial reference
  line** — PR Junta de Planificación, [MIPR](https://gis.jp.pr.gov/mipr/),
  queried per station along the same line.
- **Tidal datums** — NOAA CO-OPS station 9759110, Magueyes Island, epoch
  1983–2001.

Elevations are PRVD02. At Magueyes Island mean sea level sits 0.05 ft above that
datum, so at the scale of these drawings the two are the same line.

## Regenerating

```sh
python3 tools/harvest.py        # 20 m DEM grid, 800 m square
python3 tools/harvest2.py       # 20 m DEM grid over the DTS parcel
python3 tools/geom.py           # MIPR zoning, hazard and ZMT geometry
python3 tools/analyze.py        # fuse terrain with the regulatory layers
python3 tools/pick_section.py   # choose the section line objectively
python3 tools/transect.py       # 2 m section profile + per-station regulation
python3 tools/build_section.py  # regenerate the drawing into index.html
```

Cached outputs are committed, so none of this needs to run to serve the site.

## Not advice

An imagined property. Nothing here is a construction document, and the legal,
medical and firearms material is reasoning, not advice.
