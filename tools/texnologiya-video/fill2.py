import numpy as np, cv2
from fill import band_rows
H,W=1920,1080
def sstep(x): x=np.clip(x,0,1); return x*x*(3-2*x)
def compose2(fr,band,S=1.2,L=28,amax=0.55,reach=380):
    y0,y1=band; y0=max(0,y0-4); y1=min(H-1,y1+4)
    F=np.median(fr,axis=1,keepdims=True).astype(np.float32)
    f32=fr.astype(np.float32)
    # captions residue only outside the band
    inband=np.zeros(H,np.float32); inband[y0:y1+1]=1
    D=np.clip(f32-F,0,255)*(1-inband).reshape(H,1,1)
    # zoomed band
    bh=y1-y0+1; cy=(y0+y1)/2.0
    zw=int(round(W*S)); zh=int(round(bh*S))
    z=cv2.resize(fr[y0:y1+1],(zw,zh),interpolation=cv2.INTER_CUBIC)
    x0=(zw-W)//2; z=z[:,x0:x0+W].astype(np.float32)
    ty=int(round(cy-zh/2.0))
    # navy base with soft edge glow extension
    top=z[:12].mean(0); bot=z[-12:].mean(0)
    def prof(p):
        p=cv2.GaussianBlur(p.reshape(1,W,3),(0,0),70).reshape(W,3)
        lum=p.mean(1,keepdims=True); return p*np.clip(90/np.maximum(lum,1),0.3,1.0)
    pt,pb=prof(top),prof(bot)
    yy=np.arange(H,dtype=np.float32).reshape(H,1,1)
    dt=np.clip(ty-yy,0,None); db=np.clip(yy-(ty+zh-1),0,None)
    at=amax*np.exp(-(dt/reach)**1.5)*(yy<ty+1); ab=amax*np.exp(-(db/reach)**1.5)*(yy>ty+zh-2)
    base=F+(pt.reshape(1,W,3)-F)*at*0.9
    base=base+(pb.reshape(1,W,3)-base)*ab*0.9
    # place zoomed band with vertical feather
    layer=np.zeros((H,W,3),np.float32); al=np.zeros(H,np.float32)
    a0=max(0,ty); a1=min(H,ty+zh)
    layer[a0:a1]=z[a0-ty:a1-ty]
    r=np.arange(zh,dtype=np.float32)
    f=np.minimum(sstep(r/L),sstep((zh-1-r)/L))
    al[a0:a1]=f[a0-ty:a1-ty]
    al=al.reshape(H,1,1)
    rng=np.random.default_rng(int(fr[::97,::97].sum())%100000)
    base=base+rng.normal(0,2.2,(H,W,1)).astype(np.float32)
    out=base*(1-al)+layer*al+D
    return np.clip(out,0,255).astype(np.uint8)
