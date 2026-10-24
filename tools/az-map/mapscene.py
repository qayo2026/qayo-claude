"""QAYO xəritə səhnəsi (şaquli 1080x1920, tək rəng). Verilənlər: Natural Earth (az-districts.geojson, neighbors.geojson).
Gemini xəritəsi istifadə olunmur; adlar cities.json-dan, düzgün Azərbaycan yazılışı ilə."""
import json, os, sys, math, cv2, numpy as np
HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,os.path.join(HERE,'..','text-fx'))
from text_fx import text_sprite, blend, glow, ease_out, ease_io, WHITE, CYAN, RED, FONT_BOLD
W,H=1080,1920
GROUND=(24,8,0)      # BGR #000818
CY=(255,225,92)      # BGR #5CE1FF
CYD=(168,127,31)     # BGR primary_dim #1F7FA8
LON0,LAT0,S=47.85,40.35,198.0
KX=math.cos(math.radians(LAT0))
def proj(lon,lat): return (540+(lon-LON0)*KX*S, 960-(lat-LAT0)*S)
def rings(geom):
    t=geom['type']; c=geom['coordinates']
    polys=[c] if t=='Polygon' else c
    for p in polys:
        yield [np.array([proj(x,y) for x,y in r],np.float32) for r in p]
def draw_geom(img,geom,fill=None,line=None,lw=1):
    for rs in rings(geom):
        outer=rs[0].astype(np.int32)
        if fill is not None:
            cv2.fillPoly(img,[outer],fill,cv2.LINE_AA)
            for hole in rs[1:]: cv2.fillPoly(img,[hole.astype(np.int32)],GROUND_F if isinstance(fill,tuple) else 0)
        if line is not None:
            cv2.polylines(img,[outer],True,line,lw,cv2.LINE_AA)
GROUND_F=GROUND
AZ=json.load(open(os.path.join(HERE,'az-districts.geojson')))['features']
NB=json.load(open(os.path.join(HERE,'neighbors.geojson')))['features']
CITIES=json.load(open(os.path.join(HERE,'cities.json')))
HUB=proj(47.75,40.42)
for c in CITIES: c['p']=proj(c['lon'],c['lat'])

def fbm(h,w,seed=3):
    r=np.random.RandomState(seed); out=np.zeros((h,w),np.float32); amp=1.0; tot=0
    for sc in (200,90,40,18):
        n=r.rand(h//sc+2,w//sc+2).astype(np.float32)
        out+=cv2.resize(n,(w,h),interpolation=cv2.INTER_CUBIC)*amp; tot+=amp; amp*=0.55
    return out/tot

def build_static():
    # fon: yumşaq radial
    yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
    d=np.sqrt(((xx-540)/700)**2+((yy-960)/1100)**2)
    base=np.zeros((H,W,3),np.float32)
    g=np.array(GROUND,np.float32); g2=np.array((52,22,4),np.float32)  # #041634
    k=np.clip(1-d,0,1)[...,None]**1.6
    base=g*(1-k)+g2*k
    # quru: qonşular + AZ
    land=np.zeros((H,W),np.uint8)
    for f in NB: draw_geom(land,f['geometry'],fill=255)
    azm=np.zeros((H,W),np.uint8)
    for f in AZ: draw_geom(azm,f['geometry'],fill=255)
    relief=fbm(H,W)
    relief=(relief-relief.mean())/ (relief.std()+1e-6)
    lm=(cv2.GaussianBlur(land,(0,0),1.2).astype(np.float32)/255)[...,None]
    am=(cv2.GaussianBlur(azm,(0,0),1.2).astype(np.float32)/255)[...,None]
    nb_col=np.array((36,17,6),np.float32)   # BGR ~ #061124
    az_col=np.array((70,34,10),np.float32)  # BGR ~ #0A2246
    rel=(1+0.16*relief)[...,None]
    img=base*(1-lm)+nb_col*rel*lm
    img=img*(1-am)+az_col*rel*am
    img=img.astype(np.uint8)
    # sərhədlər
    for f in NB: draw_geom(img,f['geometry'],line=tuple(int(c*0.95) for c in CYD),lw=1)
    return img

_STATIC=None
def static():
    global _STATIC
    if _STATIC is None:
        p=os.path.join('/tmp','qayo_map_static.npy')
        if os.path.exists(p): _STATIC=np.load(p)
        else: _STATIC=build_static(); np.save(p,_STATIC)
    return _STATIC

CENTROIDS=[]
for f in AZ:
    pts=np.concatenate([r[0] for r in rings(f['geometry'])]); CENTROIDS.append(pts.mean(0))
DIST=np.array([math.hypot(c[0]-HUB[0],c[1]-HUB[1]) for c in CENTROIDS])

def beam_layer(hy,flick,seed):
    L=np.zeros((H,W),np.float32)
    r=np.random.RandomState(seed)
    pts=[(HUB[0]+ (r.rand()-0.5)*6*(1-y/ max(hy,1))*0 + math.sin(y*0.03+seed)*5, y) for y in range(0,int(hy),14)]+[(HUB[0],hy)]
    pts=np.array(pts,np.int32)
    cv2.polylines(L,[pts.reshape(-1,1,2)],False,1.0,5,cv2.LINE_AA)
    return L*flick

def bez(p0,p1,t,bend):
    mx,my=(p0[0]+p1[0])/2,(p0[1]+p1[1])/2
    dx,dy=p1[0]-p0[0],p1[1]-p0[1]; n=math.hypot(dx,dy)+1e-6
    c=(mx-dy/n*bend*n,my+dx/n*bend*n)
    return ((1-t)**2*p0[0]+2*(1-t)*t*c[0]+t*t*p1[0],(1-t)**2*p0[1]+2*(1-t)*t*c[1]+t*t*p1[1])

def add(img,layer,color,amt=1.0):
    a=np.clip(layer,0,1)[...,None]*amt
    img[:]=np.clip(img+a*np.array(color,np.float32),0,255)

LABELS={}
def label_sprite(name,n):
    key=(name,n)
    if key not in LABELS: LABELS[key]=text_sprite(name,38,0.04,FONT_BOLD,n=n)[0]
    return LABELS[key]

def render(f, total=180, fade_out=8):
    img=static().astype(np.float32).copy()
    # rayonlar: dalğa ilə yanır
    R=1000*ease_out((f-12)/70.0) if f>=12 else -1
    lit=np.zeros((H,W),np.float32); edge=np.zeros((H,W),np.float32)
    for i,fe in enumerate(AZ):
        k=np.clip((R-DIST[i])/70.0,0,1) if R>=0 else 0
        if k<=0: continue
        steady=0.60
        pulse=max(0.0,1.0-abs((R-DIST[i])-35)/45.0)   # dalğa cəbhəsi
        a=min(1.0,steady*k+0.9*pulse)
        for rs in rings(fe['geometry']):
            cv2.fillPoly(lit,[rs[0].astype(np.int32)],a*0.45,cv2.LINE_AA)
            cv2.polylines(edge,[rs[0].astype(np.int32)],True,a,2 if pulse>0.2 else 1,cv2.LINE_AA)
    add(img,lit,CYD,0.7); add(img,edge,CY,0.85)
    add(img,cv2.GaussianBlur(edge,(0,0),5),CY,0.6)
    # dalğa halqası
    if R>0 and R<1000:
        ring=np.zeros((H,W),np.float32)
        cv2.circle(ring,(int(HUB[0]),int(HUB[1])),int(R),1.0,3,cv2.LINE_AA)
        a=1-R/1000
        add(img,ring*a,CY,0.9); add(img,cv2.GaussianBlur(ring,(0,0),9)*a,CY,1.0)
    # şəbəkə xətləri
    net=np.zeros((H,W),np.float32); thin=np.zeros((H,W),np.float32)
    order=sorted(range(len(CITIES)),key=lambda i: math.hypot(CITIES[i]['p'][0]-HUB[0],CITIES[i]['p'][1]-HUB[1]))
    prog={}
    for rank,i in enumerate(order):
        t0=34+rank*3; p=ease_out((f-t0)/26.0); prog[i]=p
        if p<=0: continue
        pts=[bez(HUB,CITIES[i]['p'],t/24.0*p,0.12) for t in range(25)]
        cv2.polylines(net,[np.array(pts,np.int32).reshape(-1,1,2)],False,1.0,3,cv2.LINE_AA)
    if f>=84:
        q=ease_out((f-84)/30.0)
        for i,j in ((1,0),(5,4),(5,6),(6,3),(6,7),(8,9),(10,11),(11,12),(7,8),(2,3),(13,5)):
            a,b=CITIES[i]['p'],CITIES[j]['p']
            e=(a[0]+(b[0]-a[0])*q,a[1]+(b[1]-a[1])*q)
            cv2.line(thin,(int(a[0]),int(a[1])),(int(e[0]),int(e[1])),1.0,1,cv2.LINE_AA)
    add(img,cv2.GaussianBlur(net,(0,0),7),CY,1.1); add(img,net,(255,250,230),0.95)
    add(img,thin,CY,0.55)
    # hub + şəhər nöqtələri
    pts=np.zeros((H,W),np.float32)
    if f>=12: cv2.circle(pts,(int(HUB[0]),int(HUB[1])),9,1.0,-1,cv2.LINE_AA)
    for i,c in enumerate(CITIES):
        if prog.get(i,0)>=0.98:
            cv2.circle(pts,(int(c['p'][0]),int(c['p'][1])),7 if c['name']!='Bakı' else 10,1.0,-1,cv2.LINE_AA)
            ph=((f*0.045+i*0.31)%1.0)
            ring=np.zeros((H,W),np.float32)
            cv2.circle(ring,(int(c['p'][0]),int(c['p'][1])),int(8+26*ph),1.0,1,cv2.LINE_AA)
            add(img,ring*(1-ph)*0.8,CY,0.9)
    add(img,cv2.GaussianBlur(pts,(0,0),8),CY,1.3); add(img,pts,(255,255,255),1.0)
    # şüa
    if f<46:
        hy=HUB[1]*ease_out(f/12.0) if f<12 else HUB[1]
        fl=0.85+0.15*math.sin(f*2.3)
        dec=1.0 if f<20 else max(0.0,1-(f-20)/26.0)
        bl=beam_layer(hy,fl*dec,f)
        add(img,cv2.GaussianBlur(bl,(0,0),16),CY,1.4*dec); add(img,cv2.GaussianBlur(bl,(0,0),4),CY,1.2*dec); add(img,bl,(255,255,255),1.0)
    # təsir partlayışı
    if 12<=f<34:
        k=(f-12)/22.0
        fr=np.zeros((H,W),np.float32)
        cv2.circle(fr,(int(HUB[0]),int(HUB[1])),int(14+110*ease_out(k)),1.0,-1,cv2.LINE_AA)
        add(img,cv2.GaussianBlur(fr,(0,0),46)*(1-k),(255,235,170),1.2)
        add(img,cv2.GaussianBlur(fr,(0,0),22)*(1-k)**2,(255,250,235),0.9)
    # yazılar (text-fx: hərf-hərf)
    for i,c in enumerate(CITIES):
        t0=34+order.index(i)*3+22
        if f<t0: continue
        n=int(len(c['name'])*ease_io((f-t0)/14.0)+0.999)
        sp=label_sprite(c['name'],min(n,len(c['name'])))
        full=label_sprite(c['name'],len(c['name']))
        y=c['p'][1]+c['dy']
        if c['side']=='r': x0=c['p'][0]+c['dx']
        elif c['side']=='l': x0=c['p'][0]-c['dx']-full.shape[1]
        else: x0=c['p'][0]-full.shape[1]/2
        cx_sp=x0+sp.shape[1]/2
        glow(img,sp,cx_sp,y,1.0,CYAN,sigma=6,strength=0.8); blend(img,sp,cx_sp,y,1.0,WHITE)
    # çərçivə künclər
    m=48; L=70
    fr=np.zeros((H,W),np.float32)
    for (x,y,sx,sy) in ((m,m,1,1),(W-m,m,-1,1),(m,H-m,1,-1),(W-m,H-m,-1,-1)):
        cv2.line(fr,(x,y),(x+sx*L,y),1.0,2,cv2.LINE_AA); cv2.line(fr,(x,y),(x,y+sy*L),1.0,2,cv2.LINE_AA)
    add(img,fr,CY,0.55)
    # vinyet və çıxış
    yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
    v=1-0.35*np.clip(np.sqrt(((xx-540)/760)**2+((yy-960)/1250)**2)-0.6,0,1)
    img*=v[...,None]
    if f>=total-fade_out:
        k=(f-(total-fade_out))/fade_out
        img=img*(1-k)+np.array(GROUND,np.float32)*k
    return np.clip(img,0,255).astype(np.uint8)

if __name__=='__main__':
    out=sys.argv[1]; os.makedirs(out,exist_ok=True)
    fr=[int(x) for x in sys.argv[2].split(',')] if len(sys.argv)>2 else range(180)
    for f in fr: cv2.imwrite(f'{out}/m_{f:04d}.png',render(f))
