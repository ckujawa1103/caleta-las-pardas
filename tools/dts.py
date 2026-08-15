import json,math
d=json.load(open("data/mipr-calificacion.json"))
def stats(rings):
    xs=[p[0] for r in rings for p in r]; ys=[p[1] for r in rings for p in r]
    return min(xs),min(ys),max(xs),max(ys)
for f in d["features"]:
    a=f["attributes"]
    if a.get("cali") in ("DTS","RE"):
        r=f["geometry"]["rings"]
        x0,y0,x1,y1=stats(r)
        cx=sum(p[0] for rr in r for p in rr)/sum(len(rr) for rr in r)
        cy=sum(p[1] for rr in r for p in rr)/sum(len(rr) for rr in r)
        w=(x1-x0)*111320*math.cos(math.radians(y0)); h=(y1-y0)*110900
        print(a["cali"],a["num_catast"],a["descrip1"] if "descrip1" in a else "",
              f"\n   bbox lon {x0:.5f}..{x1:.5f}  lat {y0:.5f}..{y1:.5f}  ({w:.0f}m x {h:.0f}m)",
              f"\n   centroid {cy:.5f},{cx:.5f}  rings={len(r)} pts={sum(len(rr) for rr in r)}  area={a['SHAPE.STArea()']:,.0f} m2")
