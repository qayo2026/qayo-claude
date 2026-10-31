import numpy as np, cv2
H,W=1920,1080
def band_rows(fr):
    g=cv2.cvtColor(fr,cv2.COLOR_RGB2GRAY).astype(np.float32)
    # row activity: spread along x
    act=np.abs(g-np.median(g,axis=1,keepdims=True)).mean(1)
    act=cv2.GaussianBlur(act.reshape(-1,1),(1,0),3).ravel() if False else np.convolve(act,np.ones(9)/9,'same')
    m=act>5.0
    # close gaps <=45 rows
    idx=np.nonzero(m)[0]
    if len(idx)==0: return None
    runs=[]; s=idx[0]; p=idx[0]
    for i in idx[1:]:
        if i-p>45: runs.append((s,p)); s=i
        p=i
    runs.append((s,p))
    runs=[r for r in runs if r[1]-r[0]>=250]
    if not runs: return None
    r=max(runs,key=lambda r:r[1]-r[0]); return r
def compose(fr,band,amax=0.80,reach=420,dark=0.55):
    y0,y1=band; y0=max(0,y0-6); y1=min(H-1,y1+6)
    # per-row flat navy estimate and caption residue
    F=np.median(fr,axis=1,keepdims=True)           # H,1,3
    D=np.clip(fr.astype(np.float32)-F.astype(np.float32),0,255)
    # mirror-extend band vertically, work at 1/6 res
    s=6; bs=cv2.resize(fr[y0:y1+1],(W//s,max(2,(y1-y0+1)//s)),interpolation=cv2.INTER_AREA).astype(np.float32)
    hb=bs.shape[0]
    top_need=y0//s+2; bot_need=(H-1-y1)//s+2
    def refl(a,n):
        out=[];cur=a
        while sum(x.shape[0] for x in out)<n:
            out.append(cur); cur=cur[::-1]
        return np.concatenate(out,0)[:n]
    top=refl(bs[::1],top_need)[::-1] if False else refl(bs,top_need)  # rows moving away from edge
    bot=refl(bs[::-1],bot_need)                                       # starts at bottom edge going down
    top_full=top[:top_need][::-1]
    ext=np.concatenate([top_full[-(y0//s):] if y0//s>0 else top_full[:0],bs,bot[:(H-1-y1)//s]],0)
    ext=cv2.resize(ext,(W,H),interpolation=cv2.INTER_LINEAR)
    ext=cv2.GaussianBlur(ext,(0,0),38)
    lum=ext.mean(2,keepdims=True); ext=ext*np.clip(105/np.maximum(lum,1),0.4,1.0)
    yy=np.arange(H,dtype=np.float32)
    d=np.where(yy<y0,y0-yy,np.where(yy>y1,yy-y1,0))
    a=(amax*np.exp(-(d/reach)**1.5)).reshape(H,1,1)
    navy=F.astype(np.float32)
    bg=navy*(1-a)+ext*dark*a*1.0 + 0
    # keep captions/glow additive; feather band edges
    out=bg+D
    w=np.zeros(H,np.float32); w[y0:y1+1]=1; w=cv2.GaussianBlur(w.reshape(-1,1),(1,0),8).ravel() if False else np.convolve(w,np.ones(25)/25,'same')
    w=w.reshape(H,1,1)
    res=out*(1-w)+fr.astype(np.float32)*w
    return np.clip(res,0,255).astype(np.uint8)
