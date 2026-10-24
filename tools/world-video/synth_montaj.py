"""QAYO TEXNOLOGİYA montajı (15 s): A ofis (Gemini xam kadr) → B düz xəritə (kodla) → C qlobus (kodla).
Xəritə, qövslər, çiplər, logo, yazılar — hamısı kodla. İstifadə: python3 synth_montaj.py <çıxış_qovluğu> <ofis_kadrları_qovluğu> [kadr,...]"""
import sys, os, math
HERE=os.path.dirname(os.path.abspath(__file__)); OUTD=sys.argv[1]; OFD=sys.argv[2]; sys.argv=[sys.argv[0],OUTD]+sys.argv[3:]
sys.path.insert(0,HERE)
import synth_kod as K
from synth_kod import *
os.makedirs(OUTD,exist_ok=True)
DURM=15.0; BY=600
# ofis kadrları
OFF=[cv2.imread(os.path.join(OFD,f)) for f in sorted(os.listdir(OFD)) if f.endswith('.png')]
OH=OFF[0].shape[0]
vm=np.ones((OH,W),np.float32); fade=np.minimum(1,np.linspace(0,1,50)); vm[:50]*=fade[:,None]; vm[-50:]*=fade[::-1][:,None]; vm[:,:30]*=np.linspace(0,1,30)[None]; vm[:,-30:]*=np.linspace(1,0,30)[None]
def shotA_old(t):
    img=K.bg.copy(); a=ease_out(t/0.5); f=OFF[min(int(t*30),len(OFF)-1)].astype(np.float32)
    m=(vm*a)[...,None]; img[BY:BY+OH]=img[BY:BY+OH]*(1-m)+f*m; MCA_=[(110,700),(970,700),(110,1010),(970,1010)]; K.MC[:]=MCA_; K.TA=lambda k:0.5+0.35*k; K.draw_mods(img,t); return img

# --- V15: acıq rəng, adlar dairələrin içində, rəqəmsiz ---
CW,CH=910,570
SRC=np.float32([[0,0],[CW,0],[CW,CH],[0,CH]]); DST=np.float32([[98,180],[1002,170],[1002,744],[78,748]])
PM=cv2.getPerspectiveTransform(SRC,DST)
NIGHT=cv2.imread(os.path.join(K.HERE,'..','..','assets','earth','earth-night.jpg')).astype(np.float32)
MAPC=cv2.resize(NIGHT,(CW,CH),interpolation=cv2.INTER_AREA)*np.float32([1.9,1.6,1.25])+np.float32([34,18,6])
HUBC=(CW//2,268); NODE=[(125,100),(785,100),(125,470),(785,470),(455,482)]; NR=76
NAVY=np.float32([60,30,8]); WHT=np.float32([252,246,236])
NLINES=[['WEB','PLATFORMS'],['MOBILE','APPS'],['DESKTOP','SOFTWARE'],['IoT &','EMBEDDED','SYSTEMS'],['AUTOMATION &','CONTROL','SYSTEMS']]
def _ts(txt,mw):
    tx,_=K.text_sprite(txt,17,0.04,K.FB); h,w=tx.shape
    if w>mw: tx=cv2.resize(tx,(mw,int(h*mw/w)),interpolation=cv2.INTER_AREA)
    return tx
NTXT=[[_ts(t,118) for t in L if t] for L in NLINES]
LQ=cv2.imread(os.path.join(K.HERE,'..','..','assets','logo','qayo-texnologiya-logo-qara.png'),cv2.IMREAD_UNCHANGED)
LOGOC=cv2.resize(LQ[:,:,3],(124,int(LQ.shape[0]*124/LQ.shape[1])),interpolation=cv2.INTER_AREA).astype(np.float32)/255
ew=np.ones((CH,CW),np.float32); ew[:,:10]*=np.linspace(0,1,10)[None]; ew[:,-10:]*=np.linspace(1,0,10)[None]; ew[:10]*=np.linspace(0,1,10)[:,None]; ew[-10:]*=np.linspace(1,0,10)[:,None]
def stamp(c,al,cx,cy,col,o=1.0):
    h,w=al.shape; x0=cx-w//2; y0=cy-h//2; a=al[...,None]*o; c[y0:y0+h,x0:x0+w]=c[y0:y0+h,x0:x0+w]*(1-a)+col*a
def netcanvas(t):
    c=MAPC.copy(); lay=np.zeros((CH,CW),np.float32); P=np.float32(K.PRIM)
    ta=[0.9+0.4*k for k in range(5)]
    for k,(nx,ny) in enumerate(NODE):
        p=ease_out((t-ta[k]+0.3)/0.5)
        if p>0:
            e=(int(HUBC[0]+(nx-HUBC[0])*p),int(HUBC[1]+(ny-HUBC[1])*p)); cv2.line(lay,HUBC,e,1.0,4,cv2.LINE_AA)
            ph=(t*0.55+k*0.27)%1.0
            if p>=1: cv2.circle(lay,(int(HUBC[0]+(nx-HUBC[0])*ph),int(HUBC[1]+(ny-HUBC[1])*ph)),7,1.5,-1,cv2.LINE_AA)
    for a_,b_ in [(0,1),(1,3),(3,4),(4,2),(2,0)]:
        q=min(ease_out((t-ta[max(a_,b_)]-0.3)/0.6),1.0)
        if q>0:
            A=NODE[a_];B=NODE[b_]; cv2.line(lay,A,(int(A[0]+(B[0]-A[0])*q),int(A[1]+(B[1]-A[1])*q)),0.6,3,cv2.LINE_AA)
    for j in range(3):
        q=((t*0.5+j/3.0)%1.0); cv2.circle(lay,HUBC,int(70+90*q),float((1-q)*0.7),2,cv2.LINE_AA)
    bl=cv2.GaussianBlur(lay,(0,0),8); bs=cv2.GaussianBlur(lay,(0,0),2.5)
    c=np.clip(c+P*np.clip(bl*1.4+bs*0.9+lay*0.9,0,1.5)[...,None]*0.95+255*np.clip(lay-0.9,0,1)[...,None]*0.5,0,255)
    ph_=ease_out((t-0.25)/0.5)
    if ph_>0:
        hh=np.zeros((CH,CW),np.float32); cv2.circle(hh,HUBC,92,1.0,-1,cv2.LINE_AA); hh=cv2.GaussianBlur(hh,(0,0),22)*ph_*(0.8+0.2*math.sin(t*3))
        c=np.clip(c+P*hh[...,None]*0.9,0,255); r=int(84*ph_)
        cv2.circle(c,HUBC,r,tuple(float(v) for v in WHT),-1,cv2.LINE_AA); cv2.circle(c,HUBC,r,tuple(float(v) for v in P),4,cv2.LINE_AA)
        if ph_>0.6: stamp(c,LOGOC,HUBC[0],HUBC[1],NAVY)
    for k,(nx,ny) in enumerate(NODE):
        o=ease_out((t-ta[k])/0.4)
        if o<=0: continue
        hh=np.zeros((CH,CW),np.float32); cv2.circle(hh,(nx,ny),NR+6,1.0,-1,cv2.LINE_AA); hh=cv2.GaussianBlur(hh,(0,0),14)*o*(0.75+0.25*math.sin((t-ta[k])*3))
        c=np.clip(c+P*hh[...,None]*0.9,0,255)
        r=int(NR*(0.6+0.4*o)); cv2.circle(c,(nx,ny),r,tuple(float(v) for v in WHT),-1,cv2.LINE_AA); cv2.circle(c,(nx,ny),r,tuple(float(v) for v in P),4,cv2.LINE_AA)
        if o<0.6: continue
        tmp=np.zeros((150,150,3),np.uint8); K.icon(tmp,K.ICON[k],75,75,t-ta[k],1.0); m=cv2.resize(tmp.max(axis=2),(42,42),interpolation=cv2.INTER_CUBIC).astype(np.float32)/255
        L=NTXT[k]; th=sum(x.shape[0]+7 for x in L)-7; stamp(c,np.clip(m*1.3,0,1),nx,ny-52,np.float32([150,70,10])); y=ny+10-th//2+(4 if len(L)==2 else 0)
        for tx in L:
            stamp(c,tx,nx,y+tx.shape[0]//2,NAVY); y+=tx.shape[0]+6
    return c
ZM=2.0; RY0,RH=100,1100; RXC=498; REGY=470
xs_=np.arange(W,dtype=np.float32); fx=np.clip(np.minimum((xs_-10)/110,(1030-xs_)/40),0.05,1.0); fy=np.ones(RH,np.float32); fy[:70]=np.linspace(0,1,70); fy[-110:]=np.linspace(1,0,110); vmR=fy[:,None]*fx[None]; vmR[:150,860:]*=np.linspace(1,0.08,W-860)[None,:]*np.linspace(0.08,1,150)[::-1][:,None]**0+0.0
_cache={}
def offz(i):
    if i not in _cache:
        _cache[i]=cv2.resize(OFF[i],(int(W*ZM),int(OH*ZM)),interpolation=cv2.INTER_CUBIC)[RY0:RY0+RH,RXC:RXC+W].astype(np.float32)
        if len(_cache)>8: _cache.pop(next(iter(_cache)))
    return _cache[i]
def shotA(t):
    img=K.bg.copy(); a=ease_out(t/0.5); i=min(OFF_N-1,36+int(t/5.0*(OFF_N-37))); z=offz(i); sa=ease_out((t-0.2)/0.6)
    wc=cv2.warpPerspective(netcanvas(t),PM,(W,RH)); wm=cv2.warpPerspective(ew*sa,PM,(W,RH))[...,None]
    r=z*(1-wm)+wc*wm; m=(vmR*a)[...,None]; img[REGY:REGY+RH]=img[REGY:REGY+RH]*(1-m)+r*m
    return img
OFF_N=len(OFF)
# düz xəritə
MW_,MH_,MY0=1080,540,633
MAP=cv2.resize(K.TEX,(MW_,MH_),interpolation=cv2.INTER_AREA)*np.float32([1.0,0.92,0.80])*0.80
mm=np.ones((MH_,MW_),np.float32); mm[:40]*=np.linspace(0,1,40)[:,None]; mm[-40:]*=np.linspace(1,0,40)[:,None]; mm[:,:25]*=np.linspace(0,1,25)[None]; mm[:,-25:]*=np.linspace(1,0,25)[None]
for gx_ in range(0,MW_,90): MAP[:,gx_]=np.clip(MAP[:,gx_]+np.float32([40,30,8]),0,255)
for gy_ in range(0,MH_,90): MAP[gy_,:]=np.clip(MAP[gy_,:]+np.float32([40,30,8]),0,255)
def mp(lon,lat): return (lon+180)/360*MW_, MY0+(90-lat)/180*MH_
B_ARC0,B_STEP,B_GROW=0.8,0.4,0.4; B_FIN=B_ARC0+8*B_STEP+B_GROW+0.15
def bez(a,b,n=40):
    d=math.hypot(b[0]-a[0],b[1]-a[1]); c=((a[0]+b[0])/2,(a[1]+b[1])/2-0.35*d); return [((1-u)**2*a[0]+2*u*(1-u)*c[0]+u*u*b[0],(1-u)**2*a[1]+2*u*(1-u)*c[1]+u*u*b[1]) for u in [i/n for i in range(n+1)]]
Y0L,HL=MY0-170,MH_+200
def draw_panel(img,po):
    if po>0: a=K.panel[:,:,3:4]/255*po; img[:]=img*(1-a)+K.panel[:,:,[2,1,0]]*a
def chip_pop(img,k,tk,t):
    u=(t-tk)/0.35
    if u<=0: return
    x,y=chip_pos(k); o=ease_out(u); fl=max(0.0,1-(t-tk-0.35)/0.6)*0.6; sc=K.chips[k].copy()
    if fl>0: sc[:,:,:3]=np.clip(sc[:,:,:3]+np.float32([20,70,95])*fl,0,255)
    blit(img,sc,x+int((1-o)*-40),y,o)
def shotB(t):
    tb=t-5.2; img=K.bg.copy(); a=ease_out(tb/0.5)
    m=(mm*a)[...,None]; img[MY0:MY0+MH_]=img[MY0:MY0+MH_]*(1-m)+MAP*m
    lay=np.zeros((HL,W),np.float32); head=np.zeros((HL,W),np.float32); hub=mp(*K.HUB)
    for k in range(1,len(COUNTRIES)):
        t0=B_ARC0+(k-1)*B_STEP; p=(tb-t0)/B_GROW
        if p<=0: continue
        pts=bez(hub,mp(COUNTRIES[k][3],COUNTRIES[k][4])); m_=max(1,int(len(pts)*min(1.0,ease_out(p))))
        age=tb-t0-B_GROW; f=1.0 if p<1 else (max(0.28,1-0.72*min(1.0,age/0.6)) if tb<B_FIN else 0.28+0.72*ease_out((tb-B_FIN)/0.6))
        for i in range(1,m_): cv2.line(lay,(int(pts[i-1][0]),int(pts[i-1][1]-Y0L)),(int(pts[i][0]),int(pts[i][1]-Y0L)),f,3,cv2.LINE_AA)
        e=(int(pts[min(m_,len(pts)-1)][0]),int(pts[min(m_,len(pts)-1)][1]-Y0L)); cv2.circle(head,e,7 if p>=1 else 5,1.0,-1,cv2.LINE_AA)
        if p>=1 and 0<age<1.2: cv2.circle(lay,e,int(8+30*ease_out(age/1.2)),float(1-age/1.2),2,cv2.LINE_AA)
        if tb>=B_FIN:
            ph=((tb-B_FIN)*0.7+k*0.173)%1.0; q=pts[int(ph*(len(pts)-1))]; cv2.circle(head,(int(q[0]),int(q[1]-Y0L)),5,1.0,-1,cv2.LINE_AA)
    c=(int(hub[0]),int(hub[1]-Y0L)); cv2.circle(head,c,9,1.0,-1,cv2.LINE_AA)
    for j in range(3):
        q=((tb*0.8+j/3.0)%1.0); cv2.circle(lay,c,int(10+70*q),float((1-q)*0.9),2,cv2.LINE_AA)
    bl=cv2.GaussianBlur(lay,(0,0),9); bs=cv2.GaussianBlur(lay,(0,0),3); hb=cv2.GaussianBlur(head,(0,0),8)
    al=np.clip(bl*1.6+bs*1.0+lay,0,1.4)[...,None]; reg=img[Y0L:Y0L+HL]; pr=np.float32(PRIM)
    reg[:]=np.clip(reg+pr*al*0.9+255*np.clip(lay*0.9+head+hb*0.6,0,1)[...,None]*0.7,0,255)
    draw_panel(img,ease_out((tb-0.3)/0.5))
    for k in range(len(COUNTRIES)): chip_pop(img,k,0.6 if k==0 else B_ARC0+(k-1)*B_STEP+B_GROW,tb)
    return img
def shotC(t):
    tl=4.2+(t-10.0)*1.9; K.TA=lambda k:1e9; img=K.bg.copy(); g=K.globe(tl); ox,oy=CX-S//2,CY-S//2
    reg=img[oy:oy+S,ox:ox+S]; reg[:]=reg+g; K.draw_arcs(reg,tl); draw_panel(img,1.0)
    for k in range(len(COUNTRIES)): x,y=chip_pos(k); blit(img,K.chips[k],x,y,1.0)
    return img
def lerp(a,b,w): return a*(1-w)+b*w
def compose_m(i):
    t=i/FPS
    if t<5.0: out=shotA(t)
    elif t<5.5: out=lerp(shotA(t),shotB(t),ease_io((t-5.0)/0.5))
    elif t<9.7: out=shotB(t)
    elif t<10.2: out=lerp(shotB(t),shotC(t),ease_io((t-9.7)/0.5))
    else: out=shotC(t)
    K.draw_head(out,t)
    out*=min(1.0,max(0.0,(DURM-t)/0.5))*ease_out(t/0.4)
    return np.clip(out,0,255).astype(np.uint8)
if __name__=='__main__':
    only=[int(x) for x in sys.argv[2].split(',')] if len(sys.argv)>2 else range(int(DURM*FPS))
    for i in only: cv2.imwrite('%s/f_%04d.png'%(OUTD,i),compose_m(i))
