"""Köhnə KOSMOS (12 san) xəritə kadrlarında Gemini sərhəd xəttinə real Azərbaycan konturunu oturdur (ECC affin izləmə).
İstifadə: python3 oldmap.py <kadrlar_qovluğu(o_%04d.png)> <ilk> <son> <overlay_test_qovluğu>"""
import sys, os, json, cv2, numpy as np
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(HERE,'..','az-map'))
import mapscene as M
Y0,Y1=500,1430
def contour_mask():
    azm=np.zeros((M.H,M.W),np.uint8)
    for f in M.AZ: M.draw_geom(azm,f['geometry'],fill=255)
    cs,_=cv2.findContours(azm,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    m=np.zeros((M.H,M.W),np.float32); cv2.drawContours(m,cs,-1,1.0,3,cv2.LINE_AA)
    return m
def bright(img):
    hsv=cv2.cvtColor(img,cv2.COLOR_BGR2HSV); m=((hsv[...,2]>205)&(hsv[...,1]<110)).astype(np.float32)
    m[:Y0]=0; m[Y1:]=0
    # çox böyük parlaq ləkələri (pill, şüa) at
    n,lab,st,_=cv2.connectedComponentsWithStats((m>0).astype(np.uint8),connectivity=8)
    for i in range(1,n):
        if st[i,cv2.CC_STAT_AREA]<12: m[lab==i]=0
    return m
def blur(m,s): return cv2.GaussianBlur(m,(0,0),s)
TPL=contour_mask()
def coarse(img_m,tpl):
    best=(-1,None)
    for s in np.arange(0.35,1.5,0.05):
        t=cv2.resize(blur(tpl,3),None,fx=s,fy=s)
        if t.shape[0]>=img_m.shape[0] or t.shape[1]>=img_m.shape[1]: continue
        r=cv2.matchTemplate(blur(img_m,3),t,cv2.TM_CCOEFF_NORMED); _,mx,_,loc=cv2.minMaxLoc(r)
        if mx>best[0]: best=(mx,(s,loc))
    return best
def to_warp(s,loc):  # tpl(x,y) -> img: s*x+loc
    return np.array([[s,0,loc[0]],[0,s,loc[1]]],np.float32)
def ecc(img_m,warp):
    tpl=blur(TPL,6); inp=blur(img_m,6)
    # ECC: warp xəritəsi şablondan giriş kadrına (WARP_INVERSE_MAP olmadan: giriş=warp(şablon))
    w=warp.copy()
    try:
        cc,w=cv2.findTransformECC(inp,tpl,w,cv2.MOTION_AFFINE,(cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_COUNT,60,1e-6),None,5)
    except cv2.error: return warp,0.0
    return w,cc
def apply(w,pt): return (w[0,0]*pt[0]+w[0,1]*pt[1]+w[0,2], w[1,0]*pt[0]+w[1,1]*pt[1]+w[1,2])
def track(frames_dir,a,b,seedf):
    res={}
    img=cv2.imread(f'{frames_dir}/o_{seedf:04d}.png'); m=bright(img)
    # əl ilə təxmini başlanğıc (kadr 240): miqyas ~0.88, Bakı (49.87,40.41) -> (830,898)
    bk=M.proj(49.87,40.41); s=0.88
    w0=np.array([[s,0,830-s*bk[0]],[0,s,898-s*bk[1]]],np.float32)
    w0,cc=ecc(m,w0); print('seed',seedf,'cc',round(cc,3),w0.round(3).tolist()); res[seedf]=(w0.tolist(),cc)
    for rng in (range(seedf+1,b+1),range(seedf-1,a-1,-1)):
        w=w0.copy()
        for f in rng:
            m=bright(cv2.imread(f'{frames_dir}/o_{f:04d}.png')); w,cc=ecc(m,w); res[f]=(w.tolist(),cc)
    return res
if __name__=='__main__':
    d=sys.argv[1]; a,b=int(sys.argv[2]),int(sys.argv[3]); out=sys.argv[4]; os.makedirs(out,exist_ok=True)
    seed=int(sys.argv[5]) if len(sys.argv)>5 else 225
    res=track(d,a,b,seed); json.dump({str(k):v for k,v in res.items()},open(f'{out}/track.json','w'))
    for f in range(a,b+1,10):
        img=cv2.imread(f'{d}/o_{f:04d}.png'); w=np.array(res[f][0],np.float32)
        warped=cv2.warpAffine(TPL,w,(1080,1920)); img[...,2]=np.clip(img[...,2]+warped*255,0,255)
        for c in M.CITIES:
            x,y=apply(w,c['p']); cv2.circle(img,(int(x),int(y)),6,(0,255,0),-1)
        cv2.imwrite(f'{out}/t_{f:04d}.png',img[460:1460]); print(f,round(res[f][1],3))
