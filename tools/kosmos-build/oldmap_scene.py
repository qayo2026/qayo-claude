"""KOSMOS (köhnə 12 san) üçün 'Azərbaycan parlayır' hissəsi: perspektivli kodla xəritə (real Natural Earth verilənləri).
Stil: tünd relyef, qızılı ölkə sərhədi, nazik rayon xətləri, şəbəkə, qövslər, düzgün adlar. Gemini xəritəsi istifadə olunmur.
render(t) -> (904,1080,3) float32 BGR pəncərə kadrı (t: 0-dan, 30 fps)."""
import sys, os, math, json, cv2, numpy as np
HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,os.path.join(HERE,'..','az-map')); sys.path.insert(0,os.path.join(HERE,'..','text-fx'))
import mapscene as M
from text_fx import text_sprite, blend, glow, ease_out, ease_io, WHITE, CYAN, FONT_BOLD
WW,WH=1080,904
X0,Y0,X1,Y1=-420,300,1500,1650           # xəritə fəzası (mapscene.proj koordinatları) -> layer
LW,LH=X1-X0,Y1-Y0
K=1.5
GROUND=np.array((24,8,0),np.float32)
GOLD=(107,196,255); GOLD_RGB=(255,196,107); CY_BGR=(255,225,92)
NEI=[('Rusiya',47.3,42.0),('Gürcüstan',44.6,41.7),('Ermənistan',44.95,40.15),('İran',47.3,38.3),('Xəzər dənizi',50.45,40.9)]
LABEL_CITIES=['Bakı','Şəki','Gəncə','Naxçıvan','Lənkəran','Xaçmaz']
CACHE='/tmp/qayo_oldscene_static_v1.npz'

def L(pt,k=1.0): return ((pt[0]-X0)*k,(pt[1]-Y0)*k)
def poly_layer(geom,k):
    for rs in M.rings(geom):
        yield [np.array([L(p,k) for p in r],np.float32) for r in rs]
def fill_geom(img,geom,val,k):
    for rs in poly_layer(geom,k): cv2.fillPoly(img,[rs[0].astype(np.int32)],val,cv2.LINE_AA)
def line_geom(img,geom,val,k,lw=1):
    for rs in poly_layer(geom,k): cv2.polylines(img,[rs[0].astype(np.int32)],True,val,lw,cv2.LINE_AA)

def fbm(h,w,seed):
    r=np.random.RandomState(seed); out=np.zeros((h,w),np.float32); amp=1.0; tot=0
    for sc in (260,120,56,26,12):
        n=r.rand(h//sc+2,w//sc+2).astype(np.float32)
        out+=cv2.resize(n,(w,h),interpolation=cv2.INTER_CUBIC)*amp; tot+=amp; amp*=0.58
    return out/tot

def build_static():
    h,w=int(LH*K),int(LW*K)
    land=np.zeros((h,w),np.uint8); azm=np.zeros((h,w),np.uint8)
    for f in M.NB: fill_geom(land,f['geometry'],255,K)
    for f in M.AZ: fill_geom(azm,f['geometry'],255,K)
    land=np.maximum(land,azm)
    lm=(cv2.GaussianBlur(land,(0,0),1.5).astype(np.float32)/255)[...,None]
    am=(cv2.GaussianBlur(azm,(0,0),1.5).astype(np.float32)/255)[...,None]
    dist=cv2.distanceTransform((land==0).astype(np.uint8),cv2.DIST_L2,5)
    shallow=np.exp(-dist/(60.0*K))[...,None]
    sea=GROUND*(1-shallow*0.85)+np.array((70,40,10),np.float32)*shallow*0.85
    e=cv2.GaussianBlur(fbm(h,w,5),(0,0),2.0*K); e=(e-e.mean())/(e.std()+1e-6)
    e2=cv2.GaussianBlur(e,(0,0),2.2*K)
    gx=cv2.Sobel(e2,cv2.CV_32F,1,0,ksize=3); gy=cv2.Sobel(e2,cv2.CV_32F,0,1,ksize=3)
    shade=np.clip(-(gx*0.6+gy*0.8)*1.4,-1,1)[...,None]
    t=np.clip(0.5+0.24*e,0,1)[...,None]
    lo=np.array((28,19,10),np.float32); hi=np.array((60,48,30),np.float32)      # BGR, tünd peyk relyefi
    landc=(lo*(1-t)+hi*t)*(1+0.65*shade)
    landc=np.where(am>0.5,landc*1.22+np.array((8,5,0),np.float32),landc)
    img=sea*(1-lm)+landc*lm
    # şəhər işıqları
    r=np.random.RandomState(11); lights=np.zeros((h,w),np.float32)
    ys,xs=np.where(azm>0)
    for k in r.choice(len(ys),min(1500,len(ys)),replace=False):
        cv2.circle(lights,(int(xs[k]),int(ys[k])),1,float(0.3+0.7*r.rand()),-1,cv2.LINE_AA)
    img+=cv2.GaussianBlur(lights,(0,0),1.2)[...,None]*np.array((190,225,255),np.float32)*0.5
    img=np.clip(img,0,255).astype(np.uint8)
    # qonşu ölkə sərhədləri (zəif)
    for f in M.NB: line_geom(img,f['geometry'],(120,90,60),K,1)
    # rayon xətləri: solğun mavi
    lay=np.zeros((h,w),np.float32)
    for f in M.AZ: line_geom(lay,f['geometry'],1.0,K,1)
    lay=cv2.GaussianBlur(lay,(0,0),0.6)
    f32=img.astype(np.float32)+lay[...,None]*np.array((235,200,150),np.float32)*0.55
    # şəbəkə (xəritə fəzasında): xətlər və düyünlər
    g=np.zeros((h,w),np.float32); step=90
    for gx_ in range(int(math.ceil(X0/step))*step,X1,step): cv2.line(g,(int((gx_-X0)*K),0),(int((gx_-X0)*K),h),1.0,1,cv2.LINE_AA)
    for gy_ in range(int(math.ceil(Y0/step))*step,Y1,step): cv2.line(g,(0,int((gy_-Y0)*K)),(w,int((gy_-Y0)*K)),1.0,1,cv2.LINE_AA)
    f32+=g[...,None]*np.array((200,150,90),np.float32)*0.16
    rr=np.random.RandomState(4)
    for gx_ in range(int(math.ceil(X0/step))*step,X1,step):
        for gy_ in range(int(math.ceil(Y0/step))*step,Y1,step):
            if rr.rand()<0.16: cv2.circle(f32,(int((gx_-X0)*K),int((gy_-Y0)*K)),3,(255,230,170),-1,cv2.LINE_AA)
    # ölkə sərhədi (qızılı) ayrıca layer
    cs,_=cv2.findContours(azm,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    ol=np.zeros((h,w),np.float32); cv2.drawContours(ol,cs,-1,1.0,int(3*K),cv2.LINE_AA)
    return np.clip(f32,0,255).astype(np.uint8),ol.astype(np.float32)

def static():
    if os.path.exists(CACHE):
        d=np.load(CACHE); return d['b'],d['o']
    b,o=build_static(); np.savez(CACHE,b=b,o=o); return b,o

# ---------------------------------------------------------------- kamera
def homography(u):
    """u in [0,1]: yavaş yaxınlaşma və yan sürüşmə. Çıxış: H (layer 1x koordinatlarından pəncərəyə)."""
    z=1.0+0.10*u
    hw=640/z; hh=560/z
    def quad(c):
        cx,cy=c
        return np.float32([[cx-hw*1.65,cy-hh*1.12],[cx+hw*1.65,cy-hh*1.12],[cx+hw*1.0,cy+hh*0.95],[cx-hw*1.0,cy+hh*0.95]])
    dst=np.float32([[0,0],[WW,0],[WW,WH],[0,WH]])
    hub=np.array(L(M.HUB),np.float32)
    target=np.array([540+10*u,390-8*u],np.float32)
    c=np.array(L((540,940)),np.float32)
    for _ in range(6):
        src=quad(c)
        H=cv2.getPerspectiveTransform(src,dst)
        p=cv2.perspectiveTransform(target.reshape(1,1,2),np.linalg.inv(H).astype(np.float64)).reshape(2)
        c=c+(hub-p)
    return H,quad(c)
def proj_pt(H,pt):
    p=cv2.perspectiveTransform(np.array([[L(pt)]],np.float32),H.astype(np.float32)).reshape(2)
    return float(p[0]),float(p[1])

# ---------------------------------------------------------------- dinamika
DISTD=np.array([math.hypot(c[0]-M.HUB[0],c[1]-M.HUB[1]) for c in M.CENTROIDS])
_D=None
def hubdist(k):
    global _D
    h,w=int(LH*k),int(LW*k)
    yy,xx=np.mgrid[0:h,0:w].astype(np.float32)
    hx,hy=L(M.HUB,k)
    return np.sqrt((xx-hx)**2+(yy-hy)**2)/k
def addc(img,layer,color,amt=1.0):
    img+= np.clip(layer,0,1)[...,None]*np.array(color,np.float32)*amt
def bez2(p0,p2,t,lift):
    c=((p0[0]+p2[0])/2,(p0[1]+p2[1])/2-lift)
    return ((1-t)**2*p0[0]+2*(1-t)*t*c[0]+t*t*p2[0],(1-t)**2*p0[1]+2*(1-t)*t*c[1]+t*t*p2[1])

_ST=None; _D1=None; _D15=None
HOLD=36           # zərbə anı: şüa dəyib dağılır (≈1.2 san), sonra xəritə açılır
def reveal_clock(tv): return 11.0 if tv<HOLD else 12.0+(tv-HOLD)*1.8
def render(tv,total=100):
    global _ST,_D1,_D15
    if _ST is None:
        _ST=static(); _D1=hubdist(1.0); _D15=hubdist(K)
    base,outl=_ST
    t=reveal_clock(tv)
    u=min(1.0,tv/float(total))
    H,_=homography(u)
    HK=(H@np.diag([1/K,1/K,1.0])).astype(np.float64)
    win=cv2.warpPerspective(cv2.GaussianBlur(base,(0,0),0.7),HK,(WW,WH),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE).astype(np.float32)
    # dalğa
    R=1400*ease_out((t-12)/62.0) if t>=12 else -1.0
    # qızılı sərhəd: dalğa ilə açılır
    reveal=np.clip((R-_D15)/60.0,0,1) if R>0 else np.zeros_like(outl)
    ol=outl*reveal
    if R<=0 and tv>=4: ol=outl*0.38*min(1.0,(tv-4)/8.0)
    olw=cv2.warpPerspective(ol,HK,(WW,WH),flags=cv2.INTER_LINEAR)
    glowl=cv2.GaussianBlur(olw,(0,0),9)
    addc(win,glowl,GOLD,1.25); addc(win,olw,(200,235,255),0.16); addc(win,olw,GOLD,1.0)
    # rayonlar: dalğa ilə yanır
    lit=np.zeros((int(LH),int(LW)),np.float32); edge=np.zeros_like(lit)
    if R>0:
        for i,fe in enumerate(M.AZ):
            kk=np.clip((R-DISTD[i])/80.0,0,1)
            if kk<=0: continue
            pulse=max(0.0,1.0-abs((R-DISTD[i])-40)/55.0)
            a=min(1.0,0.5*kk+0.9*pulse)
            for rs in poly_layer(fe['geometry'],1.0):
                cv2.fillPoly(lit,[rs[0].astype(np.int32)],a*0.30,cv2.LINE_AA)
                cv2.polylines(edge,[rs[0].astype(np.int32)],True,a,1,cv2.LINE_AA)
    H32=H.astype(np.float64)
    litw=cv2.warpPerspective(lit,H32,(WW,WH)); edgew=cv2.warpPerspective(edge,H32,(WW,WH))
    addc(win,litw,(190,150,90),0.9); addc(win,edgew,(255,225,150),0.8); addc(win,cv2.GaussianBlur(edgew,(0,0),4),CY_BGR,0.45)
    # dalğa halqası (yer müstəvisində)
    if 0<R<1300:
        ring=np.zeros((int(LH),int(LW)),np.float32); hx,hy=L(M.HUB)
        cv2.circle(ring,(int(hx),int(hy)),int(R),1.0,3,cv2.LINE_AA)
        rw=cv2.warpPerspective(ring,H32,(WW,WH)); a=max(0.0,1-R/1300.0)
        addc(win,cv2.GaussianBlur(rw,(0,0),6),CY_BGR,1.0*a); addc(win,rw,(255,250,235),0.8*a)
    hx_,hy_=proj_pt(H,M.HUB)
    # qövslər
    cities=M.CITIES; pts=[proj_pt(H,c['lonlat']) if 'lonlat' in c else proj_pt(H,c['p']) for c in cities]
    order=sorted(range(len(cities)),key=lambda i: math.hypot(cities[i]['p'][0]-M.HUB[0],cities[i]['p'][1]-M.HUB[1]))
    arcs=np.zeros((WH,WW),np.float32); arcs_t=np.zeros((WH,WW),np.float32); dots=np.zeros((WH,WW),np.float32)
    prog={}
    for rank,i in enumerate(order):
        t0=26+rank*3; p=ease_out((t-t0)/28.0); prog[i]=p
        if p<=0: continue
        dist=math.hypot(pts[i][0]-hx_,pts[i][1]-hy_); lift=0.30*dist+14
        seg=[bez2((hx_,hy_),pts[i],s/28.0*p,lift) for s in range(29)]
        cv2.polylines(arcs,[np.array(seg,np.int32).reshape(-1,1,2)],False,1.0,2,cv2.LINE_AA)
        if p>=0.98:
            q=((t*0.025+i*0.173)%1.0); dx,dy=bez2((hx_,hy_),pts[i],q,lift)
            cv2.circle(dots,(int(dx),int(dy)),3,1.0,-1,cv2.LINE_AA)
    if t>=72:
        qq=ease_out((t-72)/24.0)
        for i,j in ((1,0),(5,4),(5,6),(6,3),(6,7),(8,9),(10,11),(11,12),(7,8),(2,3),(13,5)):
            a=pts[i]; b=pts[j]; dist=math.hypot(b[0]-a[0],b[1]-a[1]); lift=0.22*dist+8
            seg=[bez2(a,b,s/20.0*qq,lift) for s in range(21)]
            cv2.polylines(arcs_t,[np.array(seg,np.int32).reshape(-1,1,2)],False,1.0,1,cv2.LINE_AA)
    addc(win,cv2.GaussianBlur(arcs,(0,0),7),CY_BGR,1.1); addc(win,arcs,(255,250,235),0.95); addc(win,arcs_t,CY_BGR,0.5)
    addc(win,cv2.GaussianBlur(dots,(0,0),4),CY_BGR,1.0); addc(win,dots,(255,255,255),1.0)
    # düyünlər
    nd=np.zeros((WH,WW),np.float32); rg=np.zeros((WH,WW),np.float32)
    if t>=12: cv2.ellipse(nd,(int(hx_),int(hy_)),(10,6),0,0,360,1.0,-1,cv2.LINE_AA)
    for i,c in enumerate(cities):
        if prog.get(i,0)>=0.98:
            x,y=pts[i]; r0=9 if c['name']=='Bakı' else 6
            cv2.ellipse(nd,(int(x),int(y)),(r0,max(3,int(r0*0.65))),0,0,360,1.0,-1,cv2.LINE_AA)
            ph=((t*0.045+i*0.31)%1.0)
            cv2.ellipse(rg,(int(x),int(y)),(int(8+26*ph),int(max(3,(8+26*ph)*0.6))),0,0,360,1.0,1,cv2.LINE_AA)
            addc(win,rg*(1-ph)*0.8,CY_BGR,0.9); rg[:]=0
    addc(win,cv2.GaussianBlur(nd,(0,0),7),CY_BGR,1.3); addc(win,nd,(255,255,255),1.0)
    # şüa və zərbə (tv = real kadr zamanı; hub-da dağılma ≈1.2 san)
    if tv<56:
        by=hy_*ease_out(tv/6.0) if tv<6 else hy_
        dec=1.0 if tv<36 else max(0.0,1-(tv-36)/20.0); fl=0.85+0.15*math.sin(tv*2.3)
        bl=np.zeros((WH,WW),np.float32)
        ptsb=[(hx_+math.sin(y*0.03+tv)*4,y) for y in range(-10,int(by),10)]+[(hx_,by)]
        cv2.polylines(bl,[np.array(ptsb,np.int32).reshape(-1,1,2)],False,1.0,8,cv2.LINE_AA)
        bl*=fl*dec
        addc(win,cv2.GaussianBlur(bl,(0,0),16),CY_BGR,1.4*dec); addc(win,cv2.GaussianBlur(bl,(0,0),4),CY_BGR,1.2*dec); addc(win,bl,(255,255,255),1.0)
    if 4<=tv<58:
        k=(tv-4)/54.0; kk=ease_out(min(1.0,k*1.6)); fr=np.zeros((WH,WW),np.float32)
        cv2.ellipse(fr,(int(hx_),int(hy_)),(int(20+190*kk),int(12+112*kk)),0,0,360,1.0,-1,cv2.LINE_AA)
        fade=max(0.0,1-k)
        addc(win,cv2.GaussianBlur(fr,(0,0),46)*fade,(255,235,170),1.3); addc(win,cv2.GaussianBlur(fr,(0,0),22)*fade**2,(255,250,235),1.0)
        # zərbə dalğaları (yer müstəvisində ellips)
        sw=np.zeros((WH,WW),np.float32)
        for j in range(3):
            kj=(tv-4-j*7)/34.0
            if 0<kj<1:
                rx=40+520*ease_out(kj); cv2.ellipse(sw,(int(hx_),int(hy_)),(int(rx),int(rx*0.58)),0,0,360,1.0,3,cv2.LINE_AA)
                addc(win,cv2.GaussianBlur(sw,(0,0),6)*(1-kj),CY_BGR,1.1); addc(win,sw*(1-kj),(255,250,235),0.9); sw[:]=0
        # qığılcımlar (dağılan şüa)
        rs=np.random.RandomState(7); spk=np.zeros((WH,WW),np.float32)
        for q in range(46):
            ang=rs.rand()*2*math.pi; sp=0.55+rs.rand()*0.9; t0=4+rs.rand()*6
            kq=(tv-t0)/30.0
            if kq<=0 or kq>=1: continue
            d0=30*sp+330*sp*ease_out(kq); d1=max(0,d0-26-40*sp)
            p0=(hx_+math.cos(ang)*d1,hy_+math.sin(ang)*d1*0.58); p1=(hx_+math.cos(ang)*d0,hy_+math.sin(ang)*d0*0.58)
            cv2.line(spk,(int(p0[0]),int(p0[1])),(int(p1[0]),int(p1[1])),float(1-kq),2,cv2.LINE_AA)
        addc(win,cv2.GaussianBlur(spk,(0,0),3),CY_BGR,1.0); addc(win,spk,(255,252,240),1.0)
    # lövhə QAYO TEXNOLOGİYA
    if t>=26:
        pk=ease_out((t-26)/10.0); cx,cy,pw,ph_=int(hx_-30),int(hy_-50),340,58
        pm=np.zeros((WH,WW),np.float32)
        cv2.rectangle(pm,(cx-pw//2+ph_//2,cy-ph_//2),(cx+pw//2-ph_//2,cy+ph_//2),1.0,-1)
        cv2.circle(pm,(cx-pw//2+ph_//2,cy),ph_//2,1.0,-1,cv2.LINE_AA); cv2.circle(pm,(cx+pw//2-ph_//2,cy),ph_//2,1.0,-1,cv2.LINE_AA)
        a=(cv2.GaussianBlur(pm,(0,0),1.0)*0.55*pk)[...,None]; win=win*(1-a)+np.array((70,44,20),np.float32)*a
        edge=np.zeros((WH,WW),np.float32)
        cv2.rectangle(edge,(cx-pw//2+ph_//2,cy-ph_//2),(cx+pw//2-ph_//2,cy+ph_//2),1.0,2,cv2.LINE_AA)
        cv2.ellipse(edge,(cx-pw//2+ph_//2,cy),(ph_//2,ph_//2),0,90,270,1.0,2,cv2.LINE_AA); cv2.ellipse(edge,(cx+pw//2-ph_//2,cy),(ph_//2,ph_//2),0,-90,90,1.0,2,cv2.LINE_AA)
        addc(win,cv2.GaussianBlur(edge,(0,0),7),CY_BGR,0.9*pk); addc(win,edge,(255,240,200),0.9*pk)
        nn=17
        if t>=34:
            n=min(nn,int(nn*ease_io((t-34)/16.0)+0.999))
            tf=text_sprite('QAYO TEXNOLOGİYA',40,0.10,FONT_BOLD,n=nn)[0]; sc=(pw*0.74)/tf.shape[1]
            tsp=text_sprite('QAYO TEXNOLOGİYA',40,0.10,FONT_BOLD,n=n)[0]; tsp=cv2.resize(tsp,None,fx=sc,fy=sc,interpolation=cv2.INTER_AREA)
            tx=cx-(tf.shape[1]*sc)/2+tsp.shape[1]/2
            glow(win,tsp,tx,cy,1.0,CYAN,sigma=6,strength=0.7); blend(win,tsp,tx,cy,1.0,WHITE)
    # adlar: şəhər/rayon (ağ-mavi), qonşular (kəhrəba)
    k0=0
    for nm in LABEL_CITIES:
        c=next(c for c in cities if c['name']==nm); i=cities.index(c)
        t0=40+k0*3; k0+=1; p=ease_io((t-t0)/14.0)
        if p<=0: continue
        side,dx,dy=c['side'],c['dx'],c['dy']
        if nm=='Lənkəran': side,dx,dy='l',16,4
        if nm=='Gəncə': side,dx,dy='l',46,22
        nn=len(nm); n=min(nn,int(nn*p+0.999))
        sp=text_sprite(nm,32,0.04,FONT_BOLD,n=n)[0]; full=text_sprite(nm,32,0.04,FONT_BOLD,n=nn)[0]
        x,y=pts[i]; y+=dy*0.8
        if side=='r': x0=x+dx*0.9
        elif side=='l': x0=x-dx*0.9-full.shape[1]
        else: x0=x-full.shape[1]/2
        cxs=x0+sp.shape[1]/2
        glow(win,sp,cxs,y,1.0,CYAN,sigma=5,strength=0.7); blend(win,sp,cxs,y,1.0,WHITE)
    for k,(nm,lon,lat) in enumerate(NEI):
        t0=40+(len(LABEL_CITIES)+k)*3; p=ease_io((t-t0)/14.0)
        if p<=0: continue
        nn=len(nm); n=min(nn,int(nn*p+0.999))
        sp=text_sprite(nm,27,0.07,FONT_BOLD,n=n)[0]; full=text_sprite(nm,27,0.07,FONT_BOLD,n=nn)[0]
        x,y=proj_pt(H,M.proj(lon,lat)); cxs=x-full.shape[1]/2+sp.shape[1]/2
        glow(win,sp,cxs,y,0.9,GOLD_RGB,sigma=5,strength=0.55); blend(win,sp,cxs,y,0.92,GOLD_RGB)
    # küncə mötərizələr + vinyet
    m_=34; Ls=50; fr=np.zeros((WH,WW),np.float32)
    for (x,y,sx,sy) in ((m_,m_,1,1),(WW-m_,m_,-1,1),(m_,WH-m_,1,-1),(WW-m_,WH-m_,-1,-1)):
        cv2.line(fr,(x,y),(x+sx*Ls,y),1.0,2,cv2.LINE_AA); cv2.line(fr,(x,y),(x,y+sy*Ls),1.0,2,cv2.LINE_AA)
    addc(win,fr,CY_BGR,0.45)
    yy,xx=np.mgrid[0:WH,0:WW].astype(np.float32)
    v=1-0.30*np.clip(np.sqrt(((xx-540)/700)**2+((yy-452)/620)**2)-0.7,0,1)
    return np.clip(win*v[...,None],0,255)

if __name__=='__main__':
    out=sys.argv[1]; os.makedirs(out,exist_ok=True)
    for f in [int(x) for x in sys.argv[2].split(',')]: cv2.imwrite(f'{out}/s_{f:03d}.png',render(f).astype(np.uint8))
