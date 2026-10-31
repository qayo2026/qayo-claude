import json
from track import frames
from track2 import track_scale
t0,t1=37.2,39.53
fr=frames('ext93.mp4',t0,t1)
print(len(fr))
B={'N2':(668,698,76,38),'N3':(330,868,80,38),'N4':(666,860,74,60),'SR':(30,826,135,52),'SA':(752,598,272,56)}
out={}
for k,r in B.items():
    out[k]=track_scale(fr,t0,38.0,r,R=30,smin=0.8,smax=1.25)
    v=out[k]; print(k,[(round(t0+i/30,2),)+tuple(v[i][:4])+(round(v[i][4],2),) for i in range(0,len(v),8)])
json.dump({'t0':t0,'res':out,'ref':B},open('trO.json','w'))
