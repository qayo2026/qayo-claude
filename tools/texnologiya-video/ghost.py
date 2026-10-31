import numpy as np, cv2
BY=408  # band top in frame coords
# word -> list of (t, x0,y0,x1,y1) in band coords
G={
 'veb':[(29.00,300,175,440,235),(29.25,440,140,610,215),(29.55,445,120,640,205),(29.85,430,110,630,200),(30.02,430,105,630,195)],
 'mob':[(31.30,210,515,340,575),(31.50,215,515,340,575),(31.90,215,485,510,575),(32.15,205,440,490,540),(32.40,190,395,480,490),(32.55,190,395,480,490)],
 'agi':[(32.65,715,190,905,300),(32.90,715,190,905,300),(33.50,745,145,950,255),(34.10,750,140,960,262),(34.30,750,140,960,262)],
 'ag2':[(34.35,700,200,860,310),(34.50,700,200,860,310),(35.20,580,335,725,400),(35.90,600,310,725,372),(37.05,600,310,720,372)],
 'nec':[(35.00,330,120,440,160),(35.20,330,120,440,160),(35.90,335,125,440,162),(36.60,340,128,445,165),(37.05,340,128,445,165)],
 'lat':[(35.00,0,335,70,385),(35.20,0,335,70,385),(35.90,0,320,95,372),(36.30,0,315,100,375)],
}
THR={'veb':165,'mob':200,'agi':165,'ag2':150,'nec':165,'lat':165}
def rect(k,t):
    kf=G[k]
    if t<kf[0][0] or t>kf[-1][0]: return None
    for a,b in zip(kf,kf[1:]):
        if a[0]<=t<=b[0]:
            u=(t-a[0])/max(1e-6,b[0]-a[0])
            return [a[i]+(b[i]-a[i])*u for i in range(1,5)]
    return list(kf[-1][1:])
def ramp(k,t):
    kf=G[k]; t0,t1=kf[0][0],kf[-1][0]
    return float(np.clip(min((t-t0)/0.12,(t1-t)/0.12),0,1))
def apply(fr,t):
    out=fr
    for k in G:
        r=rect(k,t)
        if r is None: continue
        x0,y0,x1,y1=[int(round(v)) for v in r]; y0+=BY; y1+=BY
        x0=max(0,x0); x1=min(fr.shape[1],x1)
        reg=out[y0:y1,x0:x1]
        if reg.size==0: continue
        g=cv2.cvtColor(reg,cv2.COLOR_RGB2GRAY).astype(np.float32)
        loc=cv2.GaussianBlur(g,(0,0),9)
        if False:
            mn=reg.min(axis=2).astype(np.float32)
            m=((mn>228)&(g-loc>40)).astype(np.uint8)*255
            m=cv2.dilate(m,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5)))
        else:
            m=((g>THR[k])&(g-loc>28)).astype(np.uint8)*255
            m=cv2.dilate(m,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(9,9)))
        if k=='mob':  # keep gear icon: drop mask pixels that are not pure white
            pass
        pad=12
        big=cv2.copyMakeBorder(reg,pad,pad,pad,pad,cv2.BORDER_REPLICATE)
        mb=cv2.copyMakeBorder(m,pad,pad,pad,pad,cv2.BORDER_CONSTANT,value=0)
        inp=cv2.inpaint(np.ascontiguousarray(big),mb,6,cv2.INPAINT_TELEA)[pad:-pad,pad:-pad]
        a=ramp(k,t)
        soft=cv2.GaussianBlur(m,(0,0),2.0).astype(np.float32)/255.0*a
        new=reg.astype(np.float32)*(1-soft[...,None])+inp.astype(np.float32)*soft[...,None]
        if out is fr: out=fr.copy()
        out[y0:y1,x0:x1]=new.clip(0,255).astype(np.uint8)
    return out
