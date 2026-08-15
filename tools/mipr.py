import urllib.request,urllib.parse,json,sys
BASE="https://sige.pr.gov/server/rest/services/MIPR"
def query(svc,lyr,geom,gtype="esriGeometryPoint",outfields="*",geometry=False,sr=4326):
    p={"geometry":geom,"geometryType":gtype,"inSR":str(sr),"outSR":"4326",
       "spatialRel":"esriSpatialRelIntersects","outFields":outfields,
       "returnGeometry":"true" if geometry else "false","f":"json"}
    u=f"{BASE}/{svc}/MapServer/{lyr}/query?"+urllib.parse.urlencode(p)
    return json.load(urllib.request.urlopen(u,timeout=60))
PT="-66.9130,17.9488"
for svc,lyr,label in [("Calificacion",0,"Calificación/Clasificación"),
                      ("Georiesgo_v10B",12,"Área de Desalojo Tsunami"),
                      ("Georiesgo_v10B",10,"Tsunami"),
                      ("Georiesgo_v10B",14,"Zonas Inundables"),
                      ("Georiesgo_v10B",5,"Delim. Zonas Inundables"),
                      ("Georiesgo_v10B",35,"Huracán"),
                      ("Georiesgo_v10B",33,"Susceptibilidad Deslizamientos"),
                      ("Tenencia",0,"Tenencia")]:
    try:
        r=query(svc,lyr,PT)
        f=r.get("features",[])
        print(f"--- {label}: {len(f)} feature(s)")
        for x in f[:3]:
            a={k:v for k,v in x["attributes"].items() if v not in (None,"", " ")}
            print("   ",json.dumps(a,ensure_ascii=False)[:600])
        if "error" in r: print("    ERR",str(r['error'])[:200])
    except Exception as e:
        print(f"--- {label}: EXC {e}")
