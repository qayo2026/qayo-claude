"""QAYO DÜNYA + TEXNOLOGİYA (kodla qlobus): açıq mənbə NASA Blue Marble teksturası + deck.gl üslubunda qövslər.
Gemini yoxdur. Azərbaycandan (hub) ölkələrə qövslər yayılır, ölkə çipləri aşağıda yığılır, ətrafda 4 proqram modulu.
İstifadə: python3 synth_kod.py <çıxış_qovluğu> [kadr,...]   Dil: KOSMOS_LANG=az|en|ru|tr"""
import sys, os, json, math, cv2, numpy as np
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(HERE,'..','text-fx'))
from text_fx import *
from PIL import Image, ImageDraw, ImageFont
W,H,FPS,DUR=1080,1920,30,15.0
OUT=sys.argv[1] if len(sys.argv)>1 else 'fr'; os.makedirs(OUT,exist_ok=True)
FB='/usr/share/fonts/opentype/inter/Inter-Bold.otf'; FBL='/usr/share/fonts/opentype/inter/Inter-Black.otf'; EMO='/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf'
PRIM=(245,216,88)  # BGR #58D8F5
LANG=os.environ.get('KOSMOS_LANG','en'); PACK=json.load(open(os.path.join(HERE,'..','lang',LANG+'.json')))
def T(key,default): return PACK.get('world',{}).get(key,default)
# ---------- fon
BGT,BGB=np.float32([4,18,40]),np.float32([2,9,24]); yy=np.linspace(0,1,H)[:,None,None]
bg=((BGT*(1-yy)+BGB*yy)*np.ones((1,W,1),np.float32))[:,:,::-1].copy(); rng=np.random.RandomState(7)
for _ in range(140): cv2.circle(bg,(rng.randint(0,W),rng.randint(0,H)),1,(170,150,100),-1)
# ---------- ölkələr: (id, ad, bayraq, lon, lat)
COUNTRIES=[('az','AZƏRBAYCAN','🇦🇿',49.87,40.41),('tr','TÜRKİYƏ','🇹🇷',32.85,39.93),('de','ALMANİYA','🇩🇪',13.4,52.52),('fr','FRANSA','🇫🇷',2.35,48.86),
 ('ae','BƏƏ','🇦🇪',54.37,24.45),('us','ABŞ','🇺🇸',-77.04,38.9),('gb','BÖYÜK BRİTANİYA','🇬🇧',-0.13,51.5),('in','HİNDİSTAN','🇮🇳',77.2,28.6),
 ('cn','ÇİN','🇨🇳',116.4,39.9),('jp','YAPONİYA','🇯🇵',139.7,35.7)]
NAMES={c[0]:T(c[0],c[1]) for c in COUNTRIES}
HUB=(COUNTRIES[0][3],COUNTRIES[0][4])
# ---------- qlobus
TEX=cv2.imread(os.path.join(HERE,'..','..','assets','earth','earth-blue-marble.jpg')).astype(np.float32)
NIGHT=cv2.imread(os.path.join(HERE,'..','..','assets','earth','earth-night.jpg')).astype(np.float32)
TH,TW=TEX.shape[:2]; R=370; CX,CY=540,830; PAD=150; S=2*(R+PAD)
gx,gy=np.meshgrid(np.arange(S)-S/2,np.arange(S)-S/2); NX=gx/R; NY=-gy/R; D2=NX**2+NY**2; INS=D2<1.0; NZ=np.sqrt(np.clip(1-D2,0,1)); DD=np.sqrt(D2)
PHI0=math.radians(22)
# atmosfer
atm=np.zeros((S,S),np.float32); out=(DD>=1)&(DD<1.25); atm[out]=np.exp(-((DD[out]-1)/0.045)); atm_in=(1-NZ)**3*INS
SUN=np.array([0.95,0.15,0.30]); SUN/=np.linalg.norm(SUN); DAY=np.clip((NX*SUN[0]+NY*SUN[1]+NZ*SUN[2])*1.4+0.18,0,1)*INS
LIGHT=np.clip(0.30+0.85*NZ**0.55,0,1.15)*INS
def lam0(t): return 78-40*ease_io(t/DUR)
def globe(t):
    l0=math.radians(lam0(t)); lat=np.arcsin(np.clip(NY*math.cos(PHI0)+NZ*math.sin(PHI0),-1,1)); lon=l0+np.arctan2(NX,NZ*math.cos(PHI0)-NY*math.sin(PHI0))
    u=((np.degrees(lon)+180)%360)/360*(TW-1); v=(90-np.degrees(lat))/180*(TH-1)
    img=cv2.remap(TEX,u.astype(np.float32),v.astype(np.float32),cv2.INTER_LINEAR)
    nt=cv2.remap(NIGHT,u.astype(np.float32),v.astype(np.float32),cv2.INTER_LINEAR)
    nt=np.clip(nt*np.float32([0.55,1.25,1.9]),0,255)
    img=img*np.float32([1.05,0.98,0.88])*LIGHT[...,None]*(0.22+0.78*DAY[...,None])+nt*((1-DAY)**1.5)[...,None]*0.9
    img*=INS[...,None]
    pr=np.float32(PRIM); a=atm[...,None]*1.1; img=img+pr*a*0.9+pr*(atm_in[...,None]*0.55)
    return np.clip(img,0,255)
def proj(lon,lat,t,r=1.0):
    l0=math.radians(lam0(t)); la=math.radians(lat); dl=math.radians(lon)-l0
    X=math.cos(la)*math.sin(dl); Y=math.sin(la); Z=math.cos(la)*math.cos(dl)
    ny=Y*math.cos(PHI0)-Z*math.sin(PHI0); nz=Y*math.sin(PHI0)+Z*math.cos(PHI0); nx=X
    vis=(nz>0) or ((nx*nx+ny*ny)*r*r>1.0)
    return CX+R*r*nx, CY-R*r*ny, vis
def vec(lon,lat):
    la,lo=math.radians(lat),math.radians(lon); return np.array([math.cos(la)*math.cos(lo),math.cos(la)*math.sin(lo),math.sin(la)])
def arc_pts_(a,b,n=70):
    va,vb=vec(*a),vec(*b); ang=math.acos(np.clip(np.dot(va,vb),-1,1)); pts=[]
    for i in range(n+1):
        s=i/n; v=(math.sin((1-s)*ang)*va+math.sin(s*ang)*vb)/max(math.sin(ang),1e-6); v/=np.linalg.norm(v)
        lon=math.degrees(math.atan2(v[1],v[0])); lat=math.degrees(math.asin(np.clip(v[2],-1,1))); r=1+(0.10+0.22*ang/math.pi)*math.sin(math.pi*s); pts.append((lon,lat,r))
    return pts
T_ARC0,T_STEP,T_GROW=4.6,0.9,0.7
T_FIN=4.6+8*0.9+0.7+0.4
_APC={}
def arc_pts(a,b,n=70):
    key=(a,b)
    if key not in _APC: _APC[key]=arc_pts_(a,b,n)
    return _APC[key]
def TA(k): return 0.9+k*0.9
T_PANEL=4.0
def land_t(k): return T_ARC0+k*T_STEP+T_GROW
def draw_arcs(img,t):
    lay=np.zeros((S,S),np.float32); head=np.zeros((S,S),np.float32); ox,oy=CX-S//2,CY-S//2
    for k in range(1,len(COUNTRIES)):
        t0=T_ARC0+(k-1)*T_STEP; p=(t-t0)/T_GROW
        if p<=0: continue
        pts=arc_pts(HUB,(COUNTRIES[k][3],COUNTRIES[k][4])); m=int(len(pts)*min(1.0,ease_out(p)))
        age=t-t0-T_GROW; f=1.0 if p<1 else (max(0.28,1-0.72*min(1.0,age/0.8)) if t<T_FIN else 0.28+0.72*ease_out((t-T_FIN)/0.8))
        sp=[proj(l,a,t,r) for l,a,r in pts[:max(m,1)]]
        for i in range(1,len(sp)):
            if sp[i][2] and sp[i-1][2]:
                cv2.line(lay,(int(sp[i-1][0]-ox),int(sp[i-1][1]-oy)),(int(sp[i][0]-ox),int(sp[i][1]-oy)),f,3,cv2.LINE_AA)
        if 0<p<1.6:
            j=int((len(pts)-1)*min(1.0,((t-t0)*0.9)%1.0*1.0)) if False else int((len(pts)-1)*min(1.0,ease_out(min(p,1.0))))
            if sp and sp[min(j,len(sp)-1)][2]: cv2.circle(head,(int(sp[min(j,len(sp)-1)][0]-ox),int(sp[min(j,len(sp)-1)][1]-oy)),5,1.0,-1,cv2.LINE_AA)
        if m>=len(pts)-1 and sp[-1][2]:
            e=(int(sp[-1][0]-ox),int(sp[-1][1]-oy)); pu=(t-t0-T_GROW)
            cv2.circle(head,e,7,1.0,-1,cv2.LINE_AA)
            if 0<pu<1.4: cv2.circle(lay,e,int(8+30*ease_out(pu/1.4)),float(1-pu/1.4),2,cv2.LINE_AA)
        elif sp and sp[-1][2]: cv2.circle(head,(int(sp[-1][0]-ox),int(sp[-1][1]-oy)),6,1.0,-1,cv2.LINE_AA)
        if t>=T_FIN:
            ph=((t-T_FIN)*0.55+k*0.173)%1.0; q=pts[int(ph*(len(pts)-1))]; qx,qy,qv=proj(q[0],q[1],t,q[2])
            if qv: cv2.circle(head,(int(qx-ox),int(qy-oy)),5,1.0,-1,cv2.LINE_AA)
    hx,hy,hv=proj(HUB[0],HUB[1],t)
    for k in range(4):
        tk=t-TA(k)-0.3
        if tk<=0: continue
        sx,sy=MC[k]; row=SIDES[k][1]
        ctl=((sx+hx)/2,(sy+hy)/2+(-90 if row==0 else 90)); n=30; bz=[]
        for i in range(n+1):
            u=i/n; bz.append(((1-u)**2*sx+2*u*(1-u)*ctl[0]+u*u*hx,(1-u)**2*sy+2*u*(1-u)*ctl[1]+u*u*hy))
        g=ease_out(tk/0.7); m=max(1,int(n*g))
        for i in range(1,m+1): cv2.line(lay,(int(bz[i-1][0]-ox),int(bz[i-1][1]-oy)),(int(bz[i][0]-ox),int(bz[i][1]-oy)),0.55,2,cv2.LINE_AA)
        if tk>0.8:
            ph=((tk-0.8)/1.1)%1.0; b=bz[int(ph*n)]; cv2.circle(head,(int(b[0]-ox),int(b[1]-oy)),5,1.0,-1,cv2.LINE_AA)
    if hv:
        c=(int(hx-ox),int(hy-oy)); cv2.circle(head,c,9,1.0,-1,cv2.LINE_AA)
        for j in range(3):
            q=((t*0.8+j/3.0)%1.0); cv2.circle(lay,c,int(10+70*q),float((1-q)*0.9),2,cv2.LINE_AA)
    bl=cv2.GaussianBlur(lay,(0,0),9); bs=cv2.GaussianBlur(lay,(0,0),3); hb=cv2.GaussianBlur(head,(0,0),8)
    a=np.clip(bl*1.6+bs*1.0+lay,0,1.4)[...,None]; pr=np.float32(PRIM)
    img[:]=np.clip(img+pr*a*0.9+255*np.clip(lay*0.9+head+hb*0.6,0,1)[...,None]*0.7,0,255)
# ---------- çiplər, panel, modullar, başlıq (synth_birlesik ilə eyni)
def flag(e,h=34):
    im=Image.new('RGBA',(136,128),(0,0,0,0)); ImageDraw.Draw(im).text((0,0),e,font=ImageFont.truetype(EMO,109),embedded_color=True)
    im=im.crop(im.getbbox()); return np.asarray(im.resize((int(im.width*h/im.height),h),Image.LANCZOS)).astype(np.float32)
CW,CH,GX,GY=490,66,12,14; PX0,PY0=30,1290; chips=[]
for i,c in enumerate(COUNTRIES):
    sc=Image.new('RGBA',(CW,CH),(0,0,0,0)); ImageDraw.Draw(sc).rounded_rectangle([0,0,CW-1,CH-1],radius=CH//2,fill=(6,19,39,235),outline=(88,216,245,255),width=2)
    sc=np.asarray(sc).astype(np.float32); fl=flag(c[2],40); fh,fw=fl.shape[:2]; y0=(CH-fh)//2; a=fl[:,:,3:4]/255
    sc[y0:y0+fh,18:18+fw,:3]=sc[y0:y0+fh,18:18+fw,:3]*(1-a)+fl[:,:,:3]*a; sc[y0:y0+fh,18:18+fw,3:4]=np.maximum(sc[y0:y0+fh,18:18+fw,3:4],fl[:,:,3:4])
    tx,_=text_sprite(NAMES[c[0]],33,0.02,FB); th,tw=tx.shape; tx0=18+fw+14; av=CW-tx0-14
    if tw>av: tx=cv2.resize(tx,(av,th),interpolation=cv2.INTER_AREA); tw=av
    ty=(CH-th)//2; sc[ty:ty+th,tx0:tx0+tw,:3]=sc[ty:ty+th,tx0:tx0+tw,:3]*(1-tx[...,None])+255*tx[...,None]; sc[ty:ty+th,tx0:tx0+tw,3:4]=np.maximum(sc[ty:ty+th,tx0:tx0+tw,3:4],tx[...,None]*255)
    chips.append(sc)
def chip_pos(i): r,c=divmod(i,2); return PX0+14+c*(CW+GX),PY0+20+r*(CH+GY)
pm=Image.new('RGBA',(W,H),(0,0,0,0)); ImageDraw.Draw(pm).rounded_rectangle([PX0,PY0,W-PX0,PY0+450],radius=36,fill=(3,14,38,170),outline=(88,216,245,255),width=3); panel=np.asarray(pm).astype(np.float32)
MODS=PACK.get('modules',[['WEB','PLATFORMALAR'],['MOBİL','TƏTBİQLƏR'],['KOMPYUTER','PROQRAMLARI'],['AĞILLI CİHAZ','SİSTEMLƏRİ']]); ICON=[0,3,1,2,4]; SIDES=[('L',0),('R',0),('L',1),('R',1)]
BR=78; MC=[(125,575),(955,575),(125,1105),(955,1105)]; mod_lab=[]
bd=Image.new('RGBA',(2*BR+6,2*BR+6),(0,0,0,0)); ImageDraw.Draw(bd).ellipse([2,2,2*BR+3,2*BR+3],fill=(6,19,39,245),outline=(120,230,255,255),width=4); badge=np.asarray(bd).astype(np.float32)
HS=2*BR+160; hl=np.zeros((HS,HS),np.float32); cv2.circle(hl,(HS//2,HS//2),BR+2,1.0,5,cv2.LINE_AA); halo=np.clip(cv2.GaussianBlur(hl,(0,0),14)*3.2+cv2.GaussianBlur(hl,(0,0),5)*1.2,0,1.3)
LWB=250
for n_,(a_,b_) in enumerate(MODS):
    pl=Image.new('RGBA',(LWB,100),(0,0,0,0)); ImageDraw.Draw(pl).rounded_rectangle([14,0,LWB-15,95],radius=18,fill=(4,16,36,215),outline=(88,216,245,150),width=2); sc=np.asarray(pl).astype(np.float32).copy()
    nt_,_=text_sprite('%02d'%(n_+1),22,0.12,FB); nh,nw=nt_.shape; nx=(LWB-nw)//2; aa=nt_[...,None]; sc[0:nh,nx:nx+nw,:3]=sc[0:nh,nx:nx+nw,:3]*(1-aa)+np.float32([88,216,245])*aa; sc[0:nh,nx:nx+nw,3]=np.maximum(sc[0:nh,nx:nx+nw,3],nt_*255)
    for j,tt in enumerate((a_,b_)):
        if not tt: continue
        tx,_=text_sprite(tt,24,0.06,FB); th,tw=tx.shape
        if tw>LWB-44: tx=cv2.resize(tx,(LWB-44,th),interpolation=cv2.INTER_AREA); tw=LWB-44
        y0=30+j*31; x0=(LWB-tw)//2; aa=tx[...,None]; sc[y0:y0+th,x0:x0+tw,:3]=sc[y0:y0+th,x0:x0+tw,:3]*(1-aa)+255*aa; sc[y0:y0+th,x0:x0+tw,3]=np.maximum(sc[y0:y0+th,x0:x0+tw,3],tx*255)
    mod_lab.append(sc)
def blit(img,sc,x,y,o):
    h,w=sc.shape[:2]; xs,xe=max(0,x),min(W,x+w); ys,ye=max(0,y),min(H,y+h)
    if xe<=xs or ye<=ys: return
    s0=xs-x; r0=ys-y; a=sc[r0:r0+ye-ys,s0:s0+xe-xs,3:4]/255*o; img[ys:ye,xs:xe]=img[ys:ye,xs:xe]*(1-a)+sc[r0:r0+ye-ys,s0:s0+xe-xs,[2,1,0]]*a
def icon(img,k,cx,cy,tt,a):
    C=tuple(int(c*a) for c in PRIM); Wc=tuple(int(255*a*0.9) for _ in range(3)); L=cv2.LINE_AA
    if k==0:
        cv2.rectangle(img,(cx-30,cy-22),(cx+30,cy+22),C,2,L); cv2.line(img,(cx-30,cy-12),(cx+30,cy-12),C,2,L)
        for d in range(3): cv2.circle(img,(cx-23+d*7,cy-17),2,Wc,-1,L)
        for j in range(3):
            w=int(8+34*(0.5+0.5*math.sin(tt*2.2+j*1.7))); cv2.line(img,(cx-24,cy-3+j*9),(cx-24+w,cy-3+j*9),Wc,3,L)
    elif k==1:
        for j,Ln in enumerate((38,26,44,20)):
            pr=min(1.0,max(0.0,(tt*1.2-j*0.4)%2.4)); x2=int(cx-30+Ln*pr); cv2.line(img,(cx-30,cy-20+j*13),(x2,cy-20+j*13),C if j%2 else Wc,3,L)
            if 0<pr<1 and int(tt*4)%2==0: cv2.rectangle(img,(x2+2,cy-23+j*13),(x2+5,cy-17+j*13),Wc,-1)
    elif k==2:
        cv2.rectangle(img,(cx-14,cy-14),(cx+14,cy+14),Wc,2,L); cv2.rectangle(img,(cx-6,cy-6),(cx+6,cy+6),C,-1)
        for d in (-8,0,8):
            cv2.line(img,(cx+d,cy-14),(cx+d,cy-21),C,2,L); cv2.line(img,(cx+d,cy+14),(cx+d,cy+21),C,2,L); cv2.line(img,(cx-14,cy+d),(cx-21,cy+d),C,2,L); cv2.line(img,(cx+14,cy+d),(cx+21,cy+d),C,2,L)
        q=(tt*1.1)%1.0; cv2.circle(img,(cx,cy),int(24+14*q),tuple(int(c*a*(1-q)) for c in PRIM),2,L)
    elif k==4:
        cv2.circle(img,(cx,cy),16,Wc,2,L); cv2.circle(img,(cx,cy),6,C,-1,L)
        for j in range(8):
            an=tt*0.9+j*math.pi/4; cv2.line(img,(cx+int(16*math.cos(an)),cy+int(16*math.sin(an))),(cx+int(25*math.cos(an)),cy+int(25*math.sin(an))),C,5,L)
    else:
        cv2.rectangle(img,(cx-15,cy-27),(cx+15,cy+27),Wc,2,L); cv2.circle(img,(cx,cy+22),2,C,-1,L)
        for j in range(4):
            y=cy-21+((j*12+tt*14)%48)
            if cy-21<=y<=cy+16: cv2.line(img,(cx-10,int(y)),(cx+10 if j%2 else cx+4,int(y)),C,3,L)
def draw_mods(img,t):
    for k,(side,row) in enumerate(SIDES):
        o=ease_out((t-TA(k))/0.4)
        if o<=0: continue
        cx,cy=MC[k]; cx+=int((1-o)*(-90 if side=='L' else 90)); tt=t-TA(k); pul=0.75+0.25*math.sin(tt*3.0)
        hx0,hy0=cx-HS//2,cy-HS//2; xs,xe=max(0,hx0),min(W,hx0+HS); ys,ye=max(0,hy0),min(H,hy0+HS)
        hh=halo[ys-hy0:ye-hy0,xs-hx0:xe-hx0,None]*o*pul; img[ys:ye,xs:xe]=np.clip(img[ys:ye,xs:xe]+np.float32(PRIM)*hh*0.95,0,255)
        blit(img,badge,cx-BR-3,cy-BR-3,o)
        tmp=np.zeros((150,150,3),np.uint8); icon(tmp,ICON[k],75,75,tt,1.0); tmp=cv2.resize(tmp,(210,210),interpolation=cv2.INTER_CUBIC); ic=tmp.astype(np.float32)*o
        ys2,xs2=cy-105,cx-105; xa,xb=max(0,xs2),min(W,xs2+210)
        if xb>xa: img[ys2:ys2+210,xa:xb]=np.maximum(img[ys2:ys2+210,xa:xb],ic[:,xa-xs2:xb-xs2])
        lab=mod_lab[k]; blit(img,lab,cx-LWB//2,cy+BR+14,o)
LOGO=cv2.imread(os.path.join(HERE,'..','..','assets','logo','qayo-texnologiya-logo-beyaz.png'),cv2.IMREAD_UNCHANGED)
LW=420; LH=int(LOGO.shape[0]*LW/LOGO.shape[1]); LA=cv2.resize(LOGO[:,:,3].astype(np.float32)/255,(LW,LH),interpolation=cv2.INTER_AREA); LCY=100+LH//2
HEAD=[(T('sub1','SOFTWARE & INTELLIGENCE'),36,0.16,FB,CYAN,372,0.9)]
spr=[]
for t_,s,tr,f,col,y,st in HEAD:
    full,_=text_sprite(t_,s,tr,f)
    if full.shape[1]>W-60: s=int(s*(W-60)/full.shape[1]); full,_=text_sprite(t_,s,tr,f)
    spr.append((t_,s,tr,f,col,y,st))
def draw_head(img,t):
    pw=ease_io((t-0.15)/1.0)
    if pw>0:
        a=LA.copy(); a[:,int(LW*pw):]=0; glow(img,a,W/2,LCY,1.0,WHITE,sigma=14,strength=0.8); blend(img,a,W/2,LCY,1.0,WHITE)
    for t_,s,tr,f,col,y,st in spr:
        k=t-st
        if k<0: continue
        n=min(len(t_),int(len(t_)*ease_io(k/0.7)+0.999)); sp,_=text_sprite(t_,s,tr,f,n=n); full,_=text_sprite(t_,s,tr,f)
        cx=W/2-full.shape[1]/2+sp.shape[1]/2; glow(img,sp,cx,y,1.0,col,sigma=10 if s>100 else 6,strength=0.9 if s>100 else 0.6); blend(img,sp,cx,y,1.0,col)
def compose(i):
    t=i/FPS; img=bg.copy()
    g=globe(t); gi=min(1.0,ease_out(t/0.8)); ox,oy=CX-S//2,CY-S//2
    reg=img[oy:oy+S,ox:ox+S]; ml=np.clip((INS*1.0+atm*0.0),0,1)[...,None]
    # qlobus + atmosfer qatı birlikdə (additive atmosfer kənarda)
    reg[:]=reg+(g*gi)*1.0
    draw_arcs(reg,t)
    po=ease_out((t-T_PANEL)/0.5)
    if po>0: a=panel[:,:,3:4]/255*po; img[:]=img*(1-a)+panel[:,:,[2,1,0]]*a
    for k in range(len(COUNTRIES)):
        tk=T_PANEL+0.4 if k==0 else land_t(k)
        u=(t-tk)/0.35
        if u<=0: continue
        x,y=chip_pos(k); o=ease_out(u); fl=max(0.0,1-(t-tk-0.35)/0.6)*0.6
        sc=chips[k].copy()
        if fl>0: sc[:,:,:3]=np.clip(sc[:,:,:3]+np.float32([20,70,95])*fl,0,255)
        blit(img,sc,x+int((1-o)*-40),y,o)
    draw_mods(img,t); draw_head(img,t)
    img*=ease_out(t/0.4)
    return np.clip(img,0,255).astype(np.uint8)
if __name__=='__main__':
    only=[int(x) for x in sys.argv[2].split(',')] if len(sys.argv)>2 else range(int(DUR*FPS))
    for i in only: cv2.imwrite('%s/f_%04d.png'%(OUT,i),compose(i))
