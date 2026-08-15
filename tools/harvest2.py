import json,urllib.request,concurrent.futures,time,math
LAT0,LON0=17.9476,-66.9238
M_LAT=110900.0; M_LON=111320.0*math.cos(math.radians(LAT0))
def q(pt):
    i,j,lat,lon=pt
    u=f"https://epqs.nationalmap.gov/v1/json?x={lon:.7f}&y={lat:.7f}&units=Meters&wkid=4326"
    for a in range(4):
        try:
            v=float(json.load(urllib.request.urlopen(u,timeout=40))["value"])
            return (i,j,None if v<=-0.99 else v)
        except Exception: time.sleep(1+a)
    return (i,j,None)
NY,NX,STEP=42,64,20.0
pts=[(i,j,LAT0+(i-(NY-1)/2)*STEP/M_LAT,LON0+(j-(NX-1)/2)*STEP/M_LON) for i in range(NY) for j in range(NX)]
t=time.time(); grid=[[None]*NX for _ in range(NY)]
with concurrent.futures.ThreadPoolExecutor(12) as ex:
    for n,(i,j,v) in enumerate(ex.map(q,pts)):
        grid[i][j]=v
        if n%400==0: print(n,round(time.time()-t),flush=True)
json.dump({"lat0":LAT0,"lon0":LON0,"step_m":STEP,"ny":NY,"nx":NX,
           "note":"USGS 3DEP 1m over the DTS parcel; row i=+north, col j=+east; null=nodata/water",
           "grid":grid},open("data/dem-dts-20m.json","w"))
print("done",round(time.time()-t))
