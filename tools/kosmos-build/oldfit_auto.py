"""Açar kadrlarda (s, Bakı anker) ən yaxşı oturumu qonşu kadrdan lokal axtarışla tapır (sy/sx=1.10 sabit)."""
import sys, json, cv2, numpy as np
sys.path.insert(0,'.'); import oldmap as O, oldfit as F, mapscene as M
R=1.10; Q=4
def score(mb,s,bx,by):
    w=np.array([[s,0,bx-s*F.BK[0]],[0,s*R,by-s*R*F.BK[1]]],np.float32)
    t=cv2.warpAffine(O.TPL,w,(1080,1920)); t=cv2.GaussianBlur(cv2.resize(t,(1080//Q,1920//Q)),(0,0),2)
    return float((t*mb).sum()/(np.sqrt((t*t).sum())+1e-6))
def refine(mb,s,bx,by):
    best=(score(mb,s,bx,by),s,bx,by)
    for step_s,step_p,it in ((0.04,24,3),(0.015,10,3),(0.006,4,3)):
        for _ in range(it):
            cand=[(s+a*step_s,bx+b*step_p,by+c*step_p) for a in (-1,0,1) for b in (-1,0,1) for c in (-1,0,1)]
            sc=[(score(mb,*c),)+c for c in cand]; b=max(sc)
            if b[0]<=best[0]+1e-6: break
            best=b; _,s,bx,by=b
    return best
if __name__=='__main__':
    d=sys.argv[1]; a,b=int(sys.argv[2]),int(sys.argv[3]); step=int(sys.argv[4]); out=sys.argv[5]
    # 240-dan başla
    s,bx,by=0.88,830,898; res={}
    def mask(f):
        m=O.bright(cv2.imread(f'{d}/o_{f:04d}.png')); return cv2.GaussianBlur(cv2.resize(m,(1080//Q,1920//Q)),(0,0),2)
    cur=(s,bx,by); res[240]=refine(mask(240),*cur)[1:]
    for rng in (range(240+step,b+1,step),range(240-step,a-1,-step)):
        cur=res[240]
        for f in rng:
            sc,s,bx,by=refine(mask(f),*cur); cur=(s,bx,by); res[f]=cur; print(f,round(sc,2),round(s,3),round(bx),round(by),flush=True)
    json.dump({str(k):[v[0],v[0]*R,v[1],v[2]] for k,v in res.items()},open(out,'w'))
