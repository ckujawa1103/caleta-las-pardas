import urllib.request,urllib.parse,json,math
BASE="https://sige.pr.gov/server/rest/services/MIPR"
ENV="-66.9330,17.9420,-66.9060,17.9560"
def q(svc,lyr,**kw):
    p={"outSR":"4326","f":"json","returnGeometry":"true","outFields":"*",
       "geometry":ENV,"geometryType":"esriGeometryEnvelope","inSR":"4326",
       "spatialRel":"esriSpatialRelIntersects"}
    p.update(kw)
    return json.load(urllib.request.urlopen(f"{BASE}/{svc}/MapServer/{lyr}/query?"+urllib.parse.urlencode(p),timeout=120))
out={}
for key,svc,lyr in [("zmt","Tenencia",11),("tez","Georiesgo_v10B",12),
                    ("flood","Georiesgo_v10B",14),("zoning","Calificacion",0)]:
    r=q(svc,lyr)
    out[key]=r
    n=len(r.get("features",[]))
    pts=sum(len(g) for f in r.get("features",[]) for g in f["geometry"].get("rings",f["geometry"].get("paths",[])))
    print(key,n,"features",pts,"vertices",r.get("error",""))
json.dump(out,open("data/mipr-geometry.json","w"))
# where does the ZMT line run?
for f in out["zmt"]["features"]:
    for p in f["geometry"].get("paths",[]):
        xs=[a[0] for a in p]; ys=[a[1] for a in p]
        print("  ZMT path",len(p),"pts  lon",round(min(xs),5),round(max(xs),5)," lat",round(min(ys),5),round(max(ys),5))
