import json,math
d=json.load(open("data/dem-grid-20m.json")); g=d["grid"]; N=d["n"]
ch=" .:-=+*#%@"
print("DEM 800x800m centered 17.9490,-66.9135  (20 m cells, north up)")
print("   ~ = water/nodata; scale 0-60 m")
for i in range(N-1,-1,-1):
    row=""
    for j in range(N):
        v=g[i][j]
        row += "~" if v is None else ch[min(9,int(v/6.5))]
    print(f"{(i-(N-1)/2)*20:+6.0f} {row}")
print("       "+"".join("|" if j%10==0 else " " for j in range(N)))
