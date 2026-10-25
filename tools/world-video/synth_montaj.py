"""QAYO TEXNOLOGİYA montajı (15 s): A ofis (Gemini xam kadr) → B düz xəritə (kodla) → C qlobus (kodla).
Xəritə, qövslər, çiplər, logo, yazılar — hamısı kodla. İstifadə: python3 synth_montaj.py <çıxış_qovluğu> <ofis_kadrları_qovluğu> [kadr,...]"""
import sys, os, math
HERE=os.path.dirname(os.path.abspath(__file__)); OUTD=sys.argv[1]; OFD=sys.argv[2]; sys.argv=[sys.argv[0],OUTD]+sys.argv[3:]
sys.path.insert(0,HERE)
import synth_kod as K
from PIL import Image, ImageDraw
from synth_kod import *
os.makedirs(OUTD,exist_ok=True)
DURM=16.6; BY=600
# --- başlıq: rəsmi loqonun öz piksellərindən üfüqi xətt (QAYO + TEXNOLOGİYA) ---
_L=cv2.imread(os.path.join(K.HERE,'..','..','assets','logo','qayo-texnologiya-logo-beyaz.png'),cv2.IMREAD_UNCHANGED)[:,:,3].astype(np.float32)/255
def _crop(a):
    r=np.where((a>0.05).any(1))[0]; c=np.where((a>0.05).any(0))[0]; return a[r[0]:r[-1]+1,c[0]:c[-1]+1]
_qa=_L[0:700]; _ta=_L[900:1221]
def _ext(a,c0,c1):
    cols=np.where((a>0.05).any(0))[0]; w=cols[-1]-cols[0]; x0=cols[0]+int(w*c0); x1=cols[0]+int(w*c1); r=np.where((a[:,x0:x1]>0.05).any(1))[0]; return r[0],r[-1]
_q=_crop(_qa); _t=_crop(_ta)
qr0,qr1=_ext(_q,0.42,0.62); tr0,tr1=_ext(_t,0.0,0.07)   # A/Y və T hərflərinin hündürlüyü
CAP=88
for _it in range(2):
    _sq=CAP/(qr1-qr0+1); _st=CAP/(tr1-tr0+1); _w=_q.shape[1]*_sq+34+_t.shape[1]*_st; CAP=CAP*min(1.0,980/_w)
_sq=CAP/(qr1-qr0+1); _st=CAP/(tr1-tr0+1)
_q2=cv2.resize(_q,(int(_q.shape[1]*_sq),int(_q.shape[0]*_sq)),interpolation=cv2.INTER_AREA); _t2=cv2.resize(_t,(int(_t.shape[1]*_st),int(_t.shape[0]*_st)),interpolation=cv2.INTER_AREA)
_gap=34; qb=int(qr1*_sq); tb_=int(tr1*_st); top=max(qb,tb_)
_Hc=max(_q2.shape[0]+(top-qb),_t2.shape[0]+(top-tb_)); _cv=np.zeros((_Hc,_q2.shape[1]+_gap+_t2.shape[1]),np.float32)
_cv[top-qb:top-qb+_q2.shape[0],:_q2.shape[1]]=_q2; _cv[top-tb_:top-tb_+_t2.shape[0],_q2.shape[1]+_gap:]=_t2
K.LA=_cv; K.LW=_cv.shape[1]; K.LH=_cv.shape[0]; K.LCY=215
K.spr[:]=[(a_,b_,c_,d_,e_,352,g_) for (a_,b_,c_,d_,e_,f_,g_) in K.spr]

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
HUBC=(CW//2,268); NODE=[(128,104),(782,104),(128,446),(782,446),(455,470)]; NR=90
NAVY=np.float32([60,30,8]); WHT=np.float32([252,246,236])
NLINES=[['WEB','PLATFORMS'],['MOBILE','APPS'],['DESKTOP','SOFTWARE'],['IoT &','EMBEDDED','SYSTEMS'],['AUTOMATION &','CONTROL','SYSTEMS']]
def _ts(txt,mw):
    tx,_=K.text_sprite(txt,22,0.05,K.FB); h,w=tx.shape
    if w>mw: tx=cv2.resize(tx,(mw,int(h*mw/w)),interpolation=cv2.INTER_AREA)
    return tx
NTXT=[[_ts(t,136) for t in L if t] for L in NLINES]
LQ=cv2.imread(os.path.join(K.HERE,'..','..','assets','logo','qayo-texnologiya-logo-beyaz.png'),cv2.IMREAD_UNCHANGED)
LOGOC=cv2.resize(LQ[:,:,3],(150,int(LQ.shape[0]*150/LQ.shape[1])),interpolation=cv2.INTER_AREA).astype(np.float32)/255
ew=np.ones((CH,CW),np.float32); ew[:,:10]*=np.linspace(0,1,10)[None]; ew[:,-10:]*=np.linspace(1,0,10)[None]; ew[:10]*=np.linspace(0,1,10)[:,None]; ew[-10:]*=np.linspace(1,0,10)[:,None]
def stamp(c,al,cx,cy,col,o=1.0):
    h,w=al.shape; x0=cx-w//2; y0=cy-h//2; a=al[...,None]*o; c[y0:y0+h,x0:x0+w]=c[y0:y0+h,x0:x0+w]*(1-a)+col*a

def glass(c,cx,cy,r,t,k,o=1.0):
    R=r+4; sz=2*R+1; y,x=np.mgrid[-R:R+1,-R:R+1].astype(np.float32); d=np.sqrt(x*x+y*y)/r
    mask=np.clip((1.0-d)*r/1.5,0,1)
    u=np.clip((y/r+1)/2,0,1)[...,None]
    col=np.float32([120,64,20])*(1-u)+np.float32([46,20,4])*u
    P=np.float32(K.PRIM)
    inner=np.clip((d-0.72)/0.28,0,1)[...,None]**2; col=col+P*inner*0.35
    ol=np.clip(1-np.abs(d-0.955)/0.045,0,1)[...,None]; col=col*(1-ol)+P*ol*1.0+255*ol*0.25
    sx,sy=(x+0.0*r)/(0.62*r),(y+0.66*r)/(0.20*r); sp=np.exp(-(sx*sx+sy*sy)*1.8)[...,None]*np.clip(1.2-d,0,1)[...,None]
    col=col+(255-col)*np.clip(sp*0.22,0,1)
    sw=((t*0.45+k*0.23)%1.7)-0.35; uu=(x+y)/(2.0*r)*0.5+0.5
    gl=np.exp(-((uu-sw)/0.05)**2)*np.clip(1.1-d,0,1); col=col+(255-col)*gl[...,None]*0.18
    x0,y0=cx-R,cy-R; a=(mask*o*0.93)[...,None]
    h,w=c.shape[:2]; xa,ya=max(0,x0),max(0,y0); xb,yb=min(w,x0+sz),min(h,y0+sz)
    c[ya:yb,xa:xb]=c[ya:yb,xa:xb]*(1-a[ya-y0:yb-y0,xa-x0:xb-x0])+np.clip(col,0,255)[ya-y0:yb-y0,xa-x0:xb-x0]*a[ya-y0:yb-y0,xa-x0:xb-x0]

# --- mərkəz loqosu üçün elektron axını ---
_lm=(LOGOC>0.5).astype(np.uint8); _lc,_=cv2.findContours(_lm,cv2.RETR_LIST,cv2.CHAIN_APPROX_NONE); LCON=[c[:,0,:] for c in _lc if len(c)>25]
_rl=np.random.RandomState(5); LEL=[]
for ci,c in enumerate(LCON):
    for j in range(2 if len(c)>90 else 1): LEL.append((ci,_rl.rand(),(0.08+0.12*_rl.rand())*(1 if _rl.rand()<0.5 else -1)))
def logo_fx(c,t,o):
    lh,lw=LOGOC.shape; x0=HUBC[0]-lw//2; y0=HUBC[1]-lh//2; lay=np.zeros((CH,CW),np.float32)
    for ci,ph,sp in LEL:
        cc=LCON[ci]; n=len(cc)
        for tr in range(8):
            idx=int(((ph+sp*t)*n-tr*(1 if sp>0 else -1)*1.5)%n); x,y=cc[idx]
            cv2.circle(lay,(int(x0+x),int(y0+y)),2 if tr==0 else 1,float(1.0-tr/8.0),-1,cv2.LINE_AA)
    bl=cv2.GaussianBlur(lay,(0,0),3.5); bs=cv2.GaussianBlur(lay,(0,0),1.2); al=np.clip(bl*1.5+bs*0.8+lay,0,1.3)[...,None]
    c[:]=np.clip(c+np.float32(K.PRIM)*al*0.9*o+255*np.clip(lay,0,1)[...,None]*0.6*o,0,255)
def netcanvas(t):
    c=MAPC.copy(); lay=np.zeros((CH,CW),np.float32); P=np.float32(K.PRIM)
    ta=[0.9+0.4*k for k in range(5)]
    for k,(nx,ny) in enumerate(NODE):
        p=ease_out((t-ta[k]+0.3)/0.5)
        if p>0:
            e=(int(HUBC[0]+(nx-HUBC[0])*p),int(HUBC[1]+(ny-HUBC[1])*p)); cv2.line(lay,HUBC,e,1.0,4,cv2.LINE_AA)
            if p>=1:
                for jj in range(3):
                    ph=(t*0.5+k*0.27+jj/3.0)%1.0; cv2.circle(lay,(int(HUBC[0]+(nx-HUBC[0])*ph),int(HUBC[1]+(ny-HUBC[1])*ph)),8,1.6,-1,cv2.LINE_AA)
    for a_,b_ in [(0,1),(1,3),(3,4),(4,2),(2,0)]:
        q=min(ease_out((t-ta[max(a_,b_)]-0.3)/0.6),1.0)
        if q>0:
            A=NODE[a_];B=NODE[b_]; cv2.line(lay,A,(int(A[0]+(B[0]-A[0])*q),int(A[1]+(B[1]-A[1])*q)),0.6,3,cv2.LINE_AA)
    for j in range(3):
        q=((t*0.5+j/3.0)%1.0); cv2.circle(lay,HUBC,int(70+90*q),float((1-q)*0.7),2,cv2.LINE_AA)
    bl=cv2.GaussianBlur(lay,(0,0),8); bs=cv2.GaussianBlur(lay,(0,0),2.5)
    c=np.clip(c+P*np.clip(bl*0.6+bs*0.45+lay*0.55,0,1.1)[...,None]*0.8+255*np.clip(lay-0.9,0,1)[...,None]*0.18,0,255)
    ph_=ease_out((t-0.25)/0.5)
    if ph_>0:
        hh=np.zeros((CH,CW),np.float32); cv2.circle(hh,HUBC,92,1.0,-1,cv2.LINE_AA); hh=cv2.GaussianBlur(hh,(0,0),22)*ph_*(0.8+0.2*math.sin(t*3))
        c=np.clip(c+P*hh[...,None]*0.35,0,255); r=int(98*ph_)
        glass(c,HUBC[0],HUBC[1],r,t,9)
        for j in range(6):
            an=t*0.8+j*math.pi/3; cv2.circle(c,(int(HUBC[0]+126*math.cos(an)),int(HUBC[1]+126*math.sin(an))),4,tuple(float(v) for v in WHT),-1,cv2.LINE_AA)
        if ph_>0.6: stamp(c,LOGOC,HUBC[0],HUBC[1],WHT); logo_fx(c,t,1.0)
    for k,(nx,ny) in enumerate(NODE):
        o=ease_out((t-ta[k])/0.4)
        if o<=0: continue
        hh=np.zeros((CH,CW),np.float32); cv2.circle(hh,(nx,ny),NR+6,1.0,-1,cv2.LINE_AA); hh=cv2.GaussianBlur(hh,(0,0),14)*o*(0.75+0.25*math.sin((t-ta[k])*3))
        c=np.clip(c+P*hh[...,None]*0.3,0,255)
        shd=np.zeros((CH,CW),np.float32); cv2.circle(shd,(nx+5,ny+int(5*math.sin(t*1.7+k*1.3))+20),NR-4,1.0,-1,cv2.LINE_AA); shd=cv2.GaussianBlur(shd,(0,0),13)*o; c=c*(1-0.6*shd)[...,None]
        r=int(NR*(0.6+0.4*o))+int(2*math.sin(t*2.1+k)); ny=ny+int(5*math.sin(t*1.7+k*1.3)); glass(c,nx,ny,r,t,k,o)
        if o<0.6: continue
        tmp=np.zeros((150,150,3),np.uint8); K.icon(tmp,K.ICON[k],75,75,t-ta[k],1.0); m=cv2.resize(tmp.max(axis=2),(54,54),interpolation=cv2.INTER_CUBIC).astype(np.float32)/255
        L=NTXT[k]; th=sum(x.shape[0]+7 for x in L)-7; stamp(c,np.clip(m*1.3,0,1),nx,ny-58,np.float32(K.PRIM)); y=ny+10-th//2+(4 if len(L)==2 else 0)
        for tx in L:
            stamp(c,tx,nx,y+tx.shape[0]//2,WHT); y+=tx.shape[0]+5
    return c
ZM=2.0; RY0,RH=100,1100; RXC=498; REGY=470
xs_=np.arange(W,dtype=np.float32); fx=np.clip(np.minimum((xs_-10)/110,(1030-xs_)/40),0.05,1.0); fy=np.ones(RH,np.float32); fy[:70]=np.linspace(0,1,70); fy[-110:]=np.linspace(1,0,110); vmR=fy[:,None]*fx[None]; vmR[:150,860:]*=np.linspace(1,0.08,W-860)[None,:]*np.linspace(0.08,1,150)[::-1][:,None]**0+0.0
_cache={}
HM=np.ones((RH,W),np.float32); HM[20:230,925:]=0.12; HM[360:480,985:]=0.1; HM=cv2.GaussianBlur(HM,(0,0),14)[...,None]
def offz(i):
    if i not in _cache:
        _cache[i]=cv2.resize(OFF[i],(int(W*ZM),int(OH*ZM)),interpolation=cv2.INTER_CUBIC)[RY0:RY0+RH,RXC:RXC+W].astype(np.float32)*HM
        if len(_cache)>8: _cache.pop(next(iter(_cache)))
    return _cache[i]
def shotA(t):
    img=K.bg.copy(); a=1.0; i=min(OFF_N-1,36+int(t/5.0*(OFF_N-37))); z=offz(i); sa=1.0
    wc=cv2.warpPerspective(netcanvas(t+0.8),PM,(W,RH)); wm=cv2.warpPerspective(ew*sa,PM,(W,RH))[...,None]
    r=z*(1-wm)+wc*wm; m=(vmR*a)[...,None]; img[REGY:REGY+RH]=img[REGY:REGY+RH]*(1-m)+r*m
    return img
OFF_N=len(OFF)
# düz xəritə (daha böyük, ölkələr birbaşa üstündə)
LON0,LATT=-25.0,76.0; PXD=1080/175.0; MW_=1080; MH_=int(118*PXD); MY0=740
_m=cv2.resize(K.TEX,(int(360*PXD),int(180*PXD)),interpolation=cv2.INTER_AREA); _x0=int((LON0+180)*PXD); _y0=int((90-LATT)*PXD)
MAP=_m[_y0:_y0+MH_,_x0:_x0+MW_].copy()*np.float32([1.05,0.86,0.68])*0.8+np.float32([22,8,0])
mm=np.ones((MH_,MW_),np.float32); mm[:40]*=np.linspace(0,1,40)[:,None]; mm[-40:]*=np.linspace(1,0,40)[:,None]; mm[:,:25]*=np.linspace(0,1,25)[None]; mm[:,-25:]*=np.linspace(1,0,25)[None]
for gx_ in range(0,MW_,int(PXD*20)): MAP[:,gx_]=np.clip(MAP[:,gx_]+np.float32([40,30,8]),0,255)
for gy_ in range(0,MH_,int(PXD*20)): MAP[gy_,:]=np.clip(MAP[gy_,:]+np.float32([40,30,8]),0,255)
def mp(lon,lat): return (lon-LON0)*PXD, MY0+(LATT-lat)*PXD
MSET=[6,16,18,10,7,8,17,11,9]; GSET=[0,5,12,13,3,2,1,15,4]; K.ARCSET=[5,12,13,3,2,1,15,4]; K.ARCSTEP=0.9
B_ARC0,B_STEP,B_GROW=0.7,0.4,0.35; B_FIN=B_ARC0+9*B_STEP+B_GROW+0.15
def bez(a,b,n=40):
    d=math.hypot(b[0]-a[0],b[1]-a[1]); c=((a[0]+b[0])/2,(a[1]+b[1])/2-0.35*d); return [((1-u)**2*a[0]+2*u*(1-u)*c[0]+u*u*b[0],(1-u)**2*a[1]+2*u*(1-u)*c[1]+u*u*b[1]) for u in [i/n for i in range(n+1)]]
Y0L,HL=MY0-200,MH_+300
# kiçik ölkə çipləri (bayraq + ad)
def mini_chip(k):
    c=K.COUNTRIES[k]; tx,_=K.text_sprite(K.NAMES[c[0]],24,0.03,K.FB); th,tw=tx.shape; fl=K.flag(c[2],30); fh,fw=fl.shape[:2]
    w=12+fw+10+tw+16; h=46; im=Image.new('RGBA',(w,h),(0,0,0,0)); ImageDraw.Draw(im).rounded_rectangle([0,0,w-1,h-1],radius=h//2,fill=(6,19,39,232),outline=(88,216,245,255),width=2)
    sc=np.asarray(im).astype(np.float32).copy(); y0=(h-fh)//2; a=fl[:,:,3:4]/255
    sc[y0:y0+fh,12:12+fw,:3]=sc[y0:y0+fh,12:12+fw,:3]*(1-a)+fl[:,:,:3]*a; sc[y0:y0+fh,12:12+fw,3:4]=np.maximum(sc[y0:y0+fh,12:12+fw,3:4],fl[:,:,3:4])
    ty=(h-th)//2; tx0=12+fw+10; aa=tx[...,None]; sc[ty:ty+th,tx0:tx0+tw,:3]=sc[ty:ty+th,tx0:tx0+tw,:3]*(1-aa)+255*aa; sc[ty:ty+th,tx0:tx0+tw,3:4]=np.maximum(sc[ty:ty+th,tx0:tx0+tw,3:4],aa*255)
    return sc
MCH=[mini_chip(k) for k in range(len(K.COUNTRIES))]
OFFS={6:(50,-72),7:(-5,95),8:(55,90),9:(-45,-90),10:(120,40),11:(-60,-90),16:(85,-72),17:(-100,55),18:(-75,70)}
OFFG={0:(115,-60),5:(-10,85),12:(70,55),13:(-30,-75),3:(-170,-20),2:(30,-115),1:(-150,50),15:(-70,115),4:(55,75)}
def put_label(img,k,px,py,o,fl=0.0,offs=None):
    if o<=0: return
    sc=MCH[k].copy()
    if fl>0: sc[:,:,:3]=np.clip(sc[:,:,:3]+np.float32([20,70,95])*fl,0,255)
    h,w=sc.shape[:2]; ox,oy=(offs or OFFS).get(k,(0,70)); cx,cy=int(px+ox),int(py+oy); cx=min(max(cx,w//2+8),W-w//2-8)
    ex=cx-w//2 if px<cx-w//2 else (cx+w//2 if px>cx+w//2 else px); ey=cy+h//2 if py>cy+h//2 else (cy-h//2 if py<cy-h//2 else py)
    ex=int(min(max(px,cx-w//2+20),cx+w//2-20)) if abs(px-cx)<w//2+20 else ex
    cv2.line(img,(int(px),int(py)),(int(ex),int(ey)),(245,216,88),2,cv2.LINE_AA)
    blit(img,sc,cx-w//2,cy-h//2,o)
def chip_pop(img,k,tk,t):
    u=(t-tk)/0.35
    if u<=0: return
    x,y=mp(K.COUNTRIES[k][3],K.COUNTRIES[k][4]); put_label(img,k,x,y,ease_out(u),max(0.0,1-(t-tk-0.35)/0.6)*0.6)
def shotB(t):
    tb=t-5.2; img=K.bg.copy(); a=ease_out(tb/0.5)
    m=(mm*a)[...,None]; img[MY0:MY0+MH_]=img[MY0:MY0+MH_]*(1-m)+MAP*m
    lay=np.zeros((HL,W),np.float32); head=np.zeros((HL,W),np.float32); hub=mp(*K.HUB)
    for ki,k in enumerate(MSET):
        t0=B_ARC0+ki*B_STEP; p=(tb-t0)/B_GROW
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
    for ki,k in enumerate(MSET): chip_pop(img,k,B_ARC0+ki*B_STEP+B_GROW,tb)
    return img
def shotC(t):
    tl=4.2+(t-10.0)*1.9; K.TA=lambda k:1e9; img=K.bg.copy(); g=K.globe(tl); ox,oy=CX-S//2,CY-S//2
    reg=img[oy:oy+S,ox:ox+S]; reg[:]=reg+g; K.draw_arcs(reg,tl)
    for k in GSET:
        x,y,v=K.proj(COUNTRIES[k][3],COUNTRIES[k][4],tl)
        cs=math.sin(K.PHI0)*math.sin(math.radians(COUNTRIES[k][4]))+math.cos(K.PHI0)*math.cos(math.radians(COUNTRIES[k][4]))*math.cos(math.radians(COUNTRIES[k][3]-K.lam0(tl))); fd=min(1.0,max(0.0,(cs-0.12)/0.25))
        lf=1-ease_io(min(max((t-14.0)/0.5,0.0),1.0))
        if v and fd>0 and lf>0: put_label(img,k,x,y,lf*fd*ease_out((tl-(0.6 if k==0 else T_ARC0+K.ARCSET.index(k)*K.ARCSTEP+T_GROW))/0.35),offs=OFFG)
    return img
def lerp(a,b,w): return a*(1-w)+b*w
# --- final: qlobusa yaxınlaşma + Gemini fragmenti (QAYO Texnologiya) ---
ENDF=[cv2.imread(os.path.join(os.environ.get('ENDF_DIR','.'),'c_%03d.png'%n)).astype(np.float32) for n in range(1,23)]
_fm=np.ones((608,1080),np.float32); _t=np.linspace(0,1,150); _b=np.linspace(1,0,170); _fm[:150]*=(0.5-0.5*np.cos(np.pi*_t))[:,None]; _fm[-170:]*=(0.5-0.5*np.cos(np.pi*_b))[:,None]
_xm=np.ones(1080,np.float32); _xm[:40]=np.linspace(0.55,1,40); _xm[-40:]=np.linspace(1,0.55,40); _fm*=_xm[None]
def zoomC(t):
    img=shotC(t); u=ease_io(min(max((t-14.2)/0.8,0.0),1.0)); z=1+1.0*u
    if z<=1.0001: return img
    M=np.float32([[z,0,540*(1-z)],[0,z,1090*(1-z)]]); return cv2.warpAffine(img,M,(W,H),flags=cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE)
def shotD(t):
    img=K.bg.copy(); n=min(21,max(0,int((t-14.7)*30))); f=ENDF[n]; hold=max(0.0,t-15.4)/1.2; z=1+0.05*min(hold,1.0)
    if z>1.0001:
        M=np.float32([[z,0,540*(1-z)],[0,z,304*(1-z)]]); f=cv2.warpAffine(f,M,(1080,608),flags=cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE)
    y0=1090-304; m=_fm[...,None]; img[y0:y0+608]=img[y0:y0+608]*(1-m)+f*m
    return img

# --- başlıq üçün elektron effekti: hərflərin kənarı boyunca axan elektronlar + işıq zolağı ---
HY0,HY1=140,420
_h0=np.zeros_like(K.bg); K.draw_head(_h0,20.0); _hm=(_h0[HY0:HY1].max(axis=2)>170).astype(np.uint8)
_cs,_=cv2.findContours(_hm,cv2.RETR_LIST,cv2.CHAIN_APPROX_NONE); HCON=[c[:,0,:] for c in _cs if len(c)>40]
_rg=np.random.RandomState(11); HEL=[]
for ci,c in enumerate(HCON):
    for j in range(2 if len(c)>150 else 1): HEL.append((ci,_rg.rand(),(0.06+0.10*_rg.rand())*(1 if _rg.rand()<0.5 else -1)))
HMASK=cv2.GaussianBlur(_hm.astype(np.float32),(0,0),1.2)
def head_fx(img,t):
    lay=np.zeros((HY1-HY0,W),np.float32)
    for ci,ph,sp in HEL:
        c=HCON[ci]; n=len(c)
        for tr in range(9):
            idx=int(((ph+sp*t)*n-tr*(1 if sp>0 else -1)*2.0)%n); x,y=c[idx]
            cv2.circle(lay,(int(x),int(y)),3 if tr==0 else 2,float(1.0-tr/9.0),-1,cv2.LINE_AA)
    bx=((t*0.42)%2.2)*W*1.5-W*0.4; xs=np.arange(W,dtype=np.float32); band=np.exp(-((xs-bx)/110.0)**2)[None,:]
    bl=cv2.GaussianBlur(lay,(0,0),5); bs=cv2.GaussianBlur(lay,(0,0),1.6)
    al=np.clip(bl*1.4+bs*0.8+lay,0,1.3)[...,None]; P=np.float32(K.PRIM); reg=img[HY0:HY1]
    reg[:]=np.clip(reg+P*al*0.9+255*np.clip(lay,0,1)[...,None]*0.6+0,0,255)

# --- başlıq: elektron saplarından toxunma (weave) ---
HEAD_IMG=np.zeros_like(K.bg); K.draw_head(HEAD_IMG,20.0); HEAD_IMG=HEAD_IMG[HY0:HY1].copy()
_hh=HY1-HY0; _yy,_xx=np.mgrid[0:_hh,0:W].astype(np.float32); _HT=((_yy%6)<2.0); _VT=((_xx%6)<2.0)
_ed=cv2.GaussianBlur(cv2.morphologyEx(_hm,cv2.MORPH_GRADIENT,np.ones((3,3),np.uint8)).astype(np.float32),(0,0),1.1)
_hmb=_hm>0
def head_weave(img,t):
    p=min(max((t-0.15)/2.0,0.0),1.0); dly=np.where(_yy>170,0.30,0.0).astype(np.float32)
    hx=((p*1.45-dly)*1.35-0.35*(_yy/_hh))*W; Hv=_HT&(_xx<hx)
    qv=np.clip(p*1.45-dly-0.30*(_xx/W),0,1); vy=_hh*(1-qv); Vv=_VT&(_yy>vy)
    s=min(max((p-0.72)/0.28,0.0),1.0); s=s*s*(3-2*s)
    alpha=np.maximum((Hv|Vv).astype(np.float32),s)
    reg=img[HY0:HY1]; ol=np.clip(0.30+0.7*p,0,1)
    reg[:]=np.clip(reg+HEAD_IMG*alpha[...,None]+np.float32(K.PRIM)*(_ed*ol*0.9)[...,None]*(1-0.6*s),0,255)
    if p<1.0:
        lay=np.zeros((_hh,W),np.float32)
        for y in range(1,_hh,6):
            x=int(np.clip(hx[y,0],0,W-1))
            for dx in (0,-6,-12):
                xx_=x+dx
                if 0<=xx_<W and _hmb[y,xx_]: cv2.circle(lay,(xx_,y),3 if dx==0 else 2,1.0-abs(dx)/16.0,-1,cv2.LINE_AA)
        for x in range(1,W,6):
            yy_=int(vy[0,x])
            if 0<=yy_<_hh and _hmb[yy_,x]: cv2.circle(lay,(x,yy_),3,1.0,-1,cv2.LINE_AA)
        bl=cv2.GaussianBlur(lay,(0,0),4); reg[:]=np.clip(reg+np.float32(K.PRIM)*np.clip(bl*1.6+lay,0,1.3)[...,None]*0.9+255*np.clip(lay,0,1)[...,None]*0.6,0,255)
def compose_m(i):
    t=i/FPS
    if t<5.0: out=shotA(t)
    elif t<5.5: out=lerp(shotA(t),shotB(t),ease_io((t-5.0)/0.5))
    elif t<9.7: out=shotB(t)
    elif t<10.2: out=lerp(shotB(t),shotC(t),ease_io((t-9.7)/0.5))
    elif t<14.7: out=zoomC(t)
    elif t<15.1: out=lerp(zoomC(min(t,15.0)),shotD(t),ease_io((t-14.7)/0.4))
    else: out=shotD(t)
    hd=out.copy(); head_weave(hd,t); head_fx(hd,t) if t>2.0 else None; h=1-ease_io(min(max((t-14.6)/0.5,0.0),1.0)); out=lerp(out,hd,h)
    
    return np.clip(out,0,255).astype(np.uint8)
if __name__=='__main__':
    only=[int(x) for x in sys.argv[2].split(',')] if len(sys.argv)>2 else range(int(DURM*FPS))
    for i in only: cv2.imwrite('%s/f_%04d.png'%(OUTD,i),compose_m(i))
