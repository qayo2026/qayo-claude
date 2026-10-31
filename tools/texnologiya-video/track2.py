import cv2,numpy as np,json,sys
from track import frames,W,H
def track_scale(fr,t0,tr,rect,R=40,smin=0.3,smax=3.0):
    x,y,w,h=rect
    ir=int(round((tr-t0)*30)); tpl=fr[ir][y:y+h,x:x+w]
    res=[None]*len(fr); res[ir]=(x,y,w,h,1.0)
    for rng in (range(ir+1,len(fr)),range(ir-1,-1,-1)):
        cx,cy,s=x+w/2,y+h/2,1.0
        for i in rng:
            best=None
            for ds in np.arange(0.90,1.101,0.02):
                s2=s*ds
                if s2<smin or s2>smax: continue
                tw,th=int(round(w*s2)),int(round(h*s2))
                if tw<12 or th<8: continue
                t2=cv2.resize(tpl,(tw,th),interpolation=cv2.INTER_AREA)
                x0=int(max(cx-tw/2-R,0));y0=int(max(cy-th/2-R,0));x1=int(min(cx+tw/2+R,W));y1=int(min(cy+th/2+R,H))
                if x1-x0<=tw or y1-y0<=th: continue
                m=cv2.matchTemplate(fr[i][y0:y1,x0:x1],t2,cv2.TM_CCOEFF_NORMED)
                _,mx,_,loc=cv2.minMaxLoc(m)
                if best is None or mx>best[0]: best=(mx,x0+loc[0],y0+loc[1],tw,th,s2)
            if best and best[0]>0.4:
                mx,bx,by,tw,th,s=best; cx,cy=bx+tw/2,by+th/2
            else:
                mx=best[0] if best else 0; tw,th=int(round(w*s)),int(round(h*s))
            res[i]=(int(round(cx-tw/2)),int(round(cy-th/2)),tw,th,float(mx))
    return res
if __name__=='__main__':
    t0,t1=23.5,24.7
    fr=frames('ext93.mp4',t0,t1)
    out={}
    B={'FR':(23.65,(42,645,163,40)),'DE':(23.65,(285,590,200,37)),'AZ':(23.65,(450,650,260,65))}
    for k,(tr,r) in B.items():
        out['B_'+k]=track_scale(fr,t0,tr,r)
    C={'US':(24.6,(240,695,92,25)),'FR':(24.6,(350,703,96,25)),'DE':(24.6,(468,682,114,18)),'AZ':(24.6,(505,695,170,36)),'BR':(24.6,(203,802,92,25)),'NG':(24.6,(217,965,98,28))}
    for k,(tr,r) in C.items():
        out['C_'+k]=track_scale(fr,t0,tr,r)
    json.dump({'t0':t0,'res':out},open('tr_ts.json','w'))
    for k,v in out.items(): print(k,[(round(t0+i/30,2),)+v[i][:4]+(round(v[i][4],2),) for i in range(0,len(v),6)])
