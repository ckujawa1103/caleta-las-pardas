import json,urllib.request,concurrent.futures,time
def q(pt):
    lat,lon=pt
    u=f"https://epqs.nationalmap.gov/v1/json?x={lon:.6f}&y={lat:.6f}&units=Meters&wkid=4326"
    for _ in range(3):
        try:
            d=json.load(urllib.request.urlopen(u,timeout=30))
            return (lat,lon,float(d["value"]),d.get("resolution"))
        except Exception as e:
            time.sleep(1)
    return (lat,lon,None,None)
pts=[(17.9488+dy*0.0009,-66.9130+dx*0.0009) for dy in range(-4,5) for dx in range(-4,5)]
t=time.time()
with concurrent.futures.ThreadPoolExecutor(8) as ex:
    r=list(ex.map(q,pts))
print("secs",round(time.time()-t,1),"n",len(r),"fails",sum(1 for x in r if x[2] is None))
for lat,lon,v,res in r:
    print(f"{lat:.4f} {lon:.4f} {v} {res}")
