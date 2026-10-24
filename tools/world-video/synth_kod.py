"""QAYO DÜNYA + TEXNOLOGİYA (kodla qlobus): açıq mənbə NASA Blue Marble teksturası + deck.gl üslubunda qövslər.
Gemini yoxdur. Azərbaycandan (hub) ölkələrə qövslər yayılır, ölkə çipləri aşağıda yığılır, ətrafda 4 proqram modulu.
İstifadə: python3 synth_kod.py <çıxış_qovluğu> [kadr,...]   Dil: KOSMOS_LANG=az|en|ru|tr"""
import sys, os, json, math, cv2, numpy as np
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(HERE,'..','text-fx'))
from text_fx import *
from PIL import Image, ImageDraw, ImageFont
W,H,FPS,DUR=1080,1920,30,10.0
OUT=sys.argv[1] if len(sys.argv)>1 else 'fr'; os.makedirs(OUT,exist_ok=True)
FB='/usr/share/fonts/opentype/inter/Inter-Bold.otf'; FBL='/usr/share/fonts/opentype/inter/Inter-Black.otf'; EMO='/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf'
PRIM=(245,216,88)  # BGR #58D8F5
LANG=os.environ.get('KOSMOS_LANG','az'); PACK=json.load(open(os.path.join(HERE,'..','lang',LANG+'.json')))
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
def arc_pts(a,b,n=70):
    va,vb=vec(*a),vec(*b); ang=math.acos(np.clip(np.dot(va,vb),-1,1)); pts=[]
    for i in range(n+1):
        s=i/n; v=(math.sin((1-s)*ang)*va+math.sin(s*ang)*vb)/max(math.sin(ang),1e-6); v/=np.linalg.norm(v)
        lon=math.degrees(math.atan2(v[1],v[0])); lat=math.degrees(math.asin(np.clip(v[2],-1,1))); r=1+(0.10+0.22*ang/math.pi)*math.sin(math.pi*s); pts.append((lon,lat,r))
    return pts
T_ARC0,T_STEP,T_GROW=1.3,0.55,0.9
def land_t(k): return T_ARC0+k*T_STEP+T_GROW
def draw_arcs(img,t):
    lay=np.zeros((S,S),np.float32); head=np.zeros((S,S),np.float32); ox,oy=CX-S//2,CY-S//2
    for k in range(1,len(COUNTRIES)):
        t0=T_ARC0+(k-1)*T_STEP; p=(t-t0)/T_GROW
        if p<=0: continue
        pts=arc_pts(HUB,(COUNTRIES[k][3],COUNTRIES[k][4])); m=int(len(pts)*min(1.0,ease_out(p)))
        sp=[proj(l,a,t,r) for l,a,r in pts[:max(m,1)]]
        for i in range(1,len(sp)):
            if sp[i][2] and sp[i-1][2]:
                cv2.line(lay,(int(sp[i-1][0]-ox),int(sp[i-1][1]-oy)),(int(sp[i][0]-ox),int(sp[i][1]-oy)),1.0,3,cv2.LINE_AA)
        if 0<p<1.6:
            j=int((len(pts)-1)*min(1.0,((t-t0)*0.9)%1.0*1.0)) if False else int((len(pts)-1)*min(1.0,ease_out(min(p,1.0))))
            if sp and sp[min(j,len(sp)-1)][2]: cv2.circle(head,(int(sp[min(j,len(sp)-1)][0]-ox),int(sp[min(j,len(sp)-1)][1]-oy)),5,1.0,-1,cv2.LINE_AA)
        if m>=len(pts)-1 and sp[-1][2]:
            e=(int(sp[-1][0]-ox),int(sp[-1][1]-oy)); pu=(t-t0-T_GROW)
            cv2.circle(head,e,7,1.0,-1,cv2.LINE_AA)
            if 0<pu<1.4: cv2.circle(lay,e,int(8+30*ease_out(pu/1.4)),float(1-pu/1.4),2,cv2.LINE_AA)
        elif sp and sp[-1][2]: cv2.circle(head,(int(sp[-1][0]-ox),int(sp[-1][1]-oy)),6,1.0,-1,cv2.LINE_AA)
    hx,hy,hv=proj(HUB[0],HUB[1],t)
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
MODS=PACK.get('modules',[['WEB','PLATFORMALAR'],['KOMPYUTER','PROQRAMLARI'],['AĞILLI CİHAZ','SİSTEMLƏRİ'],['MOBİL','TƏTBİQLƏR']]); SIDES=[('L',0),('R',0),('L',1),('R',1)]
MW,MH=300,116; VY0,VH=440,790; MY=[VY0+10,VY0+VH-MH-10]; mod_sp=[]
for a_,b_ in MODS:
    sc=Image.new('RGBA',(MW,MH),(0,0,0,0)); ImageDraw.Draw(sc).rounded_rectangle([0,0,MW-1,MH-1],radius=18,fill=(6,19,39,225),outline=(88,216,245,255),width=3); sc=np.asarray(sc).astype(np.float32)
    for j,tt in enumerate((a_,b_)):
        tx,_=text_sprite(tt,27,0.05,FB); th,tw=tx.shape
        if tw>MW-30: tx=cv2.resize(tx,(MW-30,th),interpolation=cv2.INTER_AREA); tw=MW-30
        y0=14+j*46; x0=(MW-tw)//2; sc[y0:y0+th,x0:x0+tw,:3]=sc[y0:y0+th,x0:x0+tw,:3]*(1-tx[...,None])+255*tx[...,None]; sc[y0:y0+th,x0:x0+tw,3:4]=np.maximum(sc[y0:y0+th,x0:x0+tw,3:4],tx[...,None]*255)
    mod_sp.append(sc)
def blit(img,sc,x,y,o):
    h,w=sc.shape[:2]; xs,xe=max(0,x),min(W,x+w)
    if xe<=xs: return
    s0=xs-x; a=sc[:,s0:s0+xe-xs,3:4]/255*o; img[y:y+h,xs:xe]=img[y:y+h,xs:xe]*(1-a)+sc[:,s0:s0+xe-xs,[2,1,0]]*a
def draw_mods(img,t):
    for k,(side,row) in enumerate(SIDES):
        o=ease_out((t-(0.9+k*0.25))/0.4)
        if o<=0: continue
        x=30 if side=='L' else W-30-MW; x+=int((1-o)*(-80 if side=='L' else 80)); blit(img,mod_sp[k],x,MY[row],o)
HEAD=[(PACK.get('world',{}).get('brand','QAYO'),150,0.06,FBL,WHITE,168,0.0),(T('title','QAYO TEXNOLOGİYA'),40,0.04,FB,WHITE,300,0.5),
      (T('sub1','RƏQƏMSAL BİZNES PLATFORMASI'),30,0.12,FB,CYAN,362,0.9),(T('sub2','SİSTEMLƏR · DATA · BİZNES PAKETLƏRİ'),26,0.14,FB,CYAN,410,1.2)]
spr=[]
for t_,s,tr,f,col,y,st in HEAD:
    full,_=text_sprite(t_,s,tr,f)
    if full.shape[1]>W-60: s=int(s*(W-60)/full.shape[1]); full,_=text_sprite(t_,s,tr,f)
    spr.append((t_,s,tr,f,col,y,st))
def draw_head(img,t):
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
    po=ease_out((t-1.0)/0.5)
    if po>0: a=panel[:,:,3:4]/255*po; img[:]=img*(1-a)+panel[:,:,[2,1,0]]*a
    for k in range(len(COUNTRIES)):
        tk=0.7 if k==0 else land_t(k)-0.25; o=ease_out((t-tk)/0.35)
        if o<=0: continue
        x,y=chip_pos(k); y+=int((1-o)*-60); fl=max(0.0,1-(t-tk)/0.5)*0.55; sc=chips[k]; h,w=sc.shape[:2]; a=sc[:,:,3:4]/255*o
        col=np.clip(sc[:,:,[2,1,0]]+np.float32([90,70,20])*fl,0,255); img[y:y+h,x:x+w]=img[y:y+h,x:x+w]*(1-a)+col*a
    draw_mods(img,t); draw_head(img,t)
    img*=ease_out(t/0.4)
    return np.clip(img,0,255).astype(np.uint8)
if __name__=='__main__':
    only=[int(x) for x in sys.argv[2].split(',')] if len(sys.argv)>2 else range(int(DUR*FPS))
    for i in only: cv2.imwrite('%s/f_%04d.png'%(OUT,i),compose(i))
