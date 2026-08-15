import json,urllib.request,concurrent.futures,time,sys,math
LAT0,LON0=17.9490,-66.9135
M_LAT=110900.0
M_LON=111320.0*math.cos(math.radians(LAT0))
def q(pt):
    i,j,lat,lon=pt
    u=f"https://epqs.nationalmap.gov/v1/json?x={lon:.7f}&y={lat:.7f}&units=Meters&wkid=4326"
    for a in range(4):
        try:
            d=json.load(urllib.request.urlopen(u,timeout=40))
            v=float(d["value"])
            return (i,j,lat,lon,None if v<=-0.99 else v)
        except Exception:
            time.sleep(1+a)
    return (i,j,lat,lon,None)
N=41; STEP=20.0
pts=[]
for i in range(N):
    for j in range(N):
        dy=(i-(N-1)/2)*STEP; dx=(j-(N-1)/2)*STEP
        pts.append((i,j,LAT0+dy/M_LAT,LON0+dx/M_LON))
t=time.time(); out=[]
with concurrent.futures.ThreadPoolExecutor(12) as ex:
    for n,r in enumerate(ex.map(q,pts)):
        out.append(r)
        if n%200==0: print(n,round(time.time()-t),flush=True)
grid=[[None]*N for _ in range(N)]
for i,j,lat,lon,v in out: grid[i][j]=v
json.dump({"lat0":LAT0,"lon0":LON0,"step_m":STEP,"n":N,"note":"USGS 3DEP 1m; row i = +north, col j = +east; null = nodata/water","grid":grid},open("data/dem-grid-20m.json","w"))
print("done",round(time.time()-t),"nulls",sum(1 for r in out if r[4] is None))
