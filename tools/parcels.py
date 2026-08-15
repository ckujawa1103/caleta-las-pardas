import urllib.request,urllib.parse,json
BASE="https://sige.pr.gov/server/rest/services/MIPR"
def q(svc,lyr,**kw):
    p={"outSR":"4326","f":"json","returnGeometry":"true","outFields":"*"}; p.update(kw)
    u=f"{BASE}/{svc}/MapServer/{lyr}/query?"+urllib.parse.urlencode(p)
    return json.load(urllib.request.urlopen(u,timeout=90))
# envelope ~1.4km x 1.4km around site
ENV="-66.9200,17.9425,-66.9060,17.9555"
r=q("Calificacion",0,geometry=ENV,geometryType="esriGeometryEnvelope",inSR="4326",
    spatialRel="esriSpatialRelIntersects")
feats=r.get("features",[])
print("parcels:",len(feats),r.get("error",""))
seen={}
for f in feats:
    a=f["attributes"]
    k=(a.get("cali"),a.get("descrip"),a.get("clasi"))
    seen[k]=seen.get(k,0)+1
for k,v in sorted(seen.items(),key=lambda x:-x[1]): print("  ",v,k)
print()
for f in sorted(feats,key=lambda f:-f["attributes"].get("SHAPE.STArea()",0))[:14]:
    a=f["attributes"]
    print(f"  {a.get('num_catast')}  {a.get('cali'):8} {str(a.get('descrip'))[:34]:34} {str(a.get('clasi')):9} {a.get('SHAPE.STArea()',0):>12,.0f} m2")
json.dump(r,open("data/mipr-calificacion.json","w"))
