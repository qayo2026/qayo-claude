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
    """Peyk görünüşlü, kodla qurulmuş fon: dəniz + relyef (hillshade) + işıqlar + parlaq ölkə sərhədi. Tək rəng ailəsi."""
    yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
    land=np.zeros((H,W),np.uint8)
    for f in NB: draw_geom(land,f['geometry'],fill=255)
    azm=np.zeros((H,W),np.uint8)
    for f in AZ: draw_geom(azm,f['geometry'],fill=255)
    land=np.maximum(land,azm)
    lm=(cv2.GaussianBlur(land,(0,0),1.3).astype(np.float32)/255)[...,None]
    am=(cv2.GaussianBlur(azm,(0,0),1.3).astype(np.float32)/255)[...,None]
    # dəniz: dərin -> sahil yaxınlığında dayaz
    dist=cv2.distanceTransform((land==0).astype(np.uint8),cv2.DIST_L2,5)
    shallow=np.exp(-dist/55.0)[...,None]
    deep=np.array(GROUND,np.float32); shal=np.array((84,48,8),np.float32)   # #083054
    wav=(0.5+0.5*np.sin(yy*0.045+fbm(H,W,7)*9))[...,None]
    sea=deep*(1-shallow*0.9)+shal*shallow*0.9
    sea=sea*(1+0.06*wav)
    # quru: relyef
    e=cv2.GaussianBlur(fbm(H,W,5),(0,0),3); e=(e-e.mean())/(e.std()+1e-6)
    e2=cv2.GaussianBlur(e,(0,0),2.0)
    gx=cv2.Sobel(e2,cv2.CV_32F,1,0,ksize=3); gy=cv2.Sobel(e2,cv2.CV_32F,0,1,ksize=3)
    shade=np.clip(-(gx*0.7+gy*0.7)*0.9,-1,1)[...,None]
    t=np.clip(0.5+0.22*e,0,1)[...,None]
    lo=np.array((52,30,10),np.float32); hi=np.array((118,84,36),np.float32)   # BGR #0A1E34 -> #245476
    landc=(lo*(1-t)+hi*t)*(1+0.55*shade)
    landc=np.where(am>0.5,landc*1.18+np.array((10,6,0),np.float32),landc)
    img=sea*(1-lm)+landc*lm
    # şəhər işıqları (Azərbaycan daxilində seyrək)
    r=np.random.RandomState(11); lights=np.zeros((H,W),np.float32)
    ys,xs=np.where(azm>0)
    for k in r.choice(len(ys),min(900,len(ys)),replace=False):
        cv2.circle(lights,(int(xs[k]),int(ys[k])),1,float(0.35+0.65*r.rand()),-1,cv2.LINE_AA)
    img=np.clip(img+cv2.GaussianBlur(lights,(0,0),1.1)[...,None]*np.array((200,235,255),np.float32)*0.55,0,255)
    img=img.astype(np.uint8)
    # qonşu sərhədləri
    for f in NB: draw_geom(img,f['geometry'],line=tuple(int(c*0.95) for c in CYD),lw=1)
    # ölkə kontur xətti: parlaq ağ-mavi
    cs,_=cv2.findContours(azm,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    ol=np.zeros((H,W),np.float32); cv2.drawContours(ol,cs,-1,1.0,3,cv2.LINE_AA)
    f32=img.astype(np.float32)
    f32+=cv2.GaussianBlur(ol,(0,0),7)[...,None]*np.array(CY,np.float32)*0.9
    f32+=ol[...,None]*np.array((255,250,235),np.float32)*0.95
    return np.clip(f32,0,255).astype(np.uint8)

_STATIC=None
def static():
    global _STATIC
    if _STATIC is None:
        p=os.path.join('/tmp','qayo_map_static_v2.npy')
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
    cv2.polylines(L,[pts.reshape(-1,1,2)],False,1.0,9,cv2.LINE_AA)
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
    # davamlı nazik şüa (lövhəyə qədər)
    if f>=46:
        th=np.zeros((H,W),np.float32); cv2.line(th,(int(HUB[0]),0),(int(HUB[0]),int(HUB[1])),1.0,2,cv2.LINE_AA)
        a=0.55*min(1.0,(f-46)/10.0)
        add(img,cv2.GaussianBlur(th,(0,0),6),CY,a*1.2); add(img,th,(255,250,235),a)
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
    # mərkəz lövhəsi: şüanın üstündə, QAYO TEXNOLOGİYA
    if f>=30:
        pk=ease_out((f-30)/10.0); cx,cy,pw,ph_=int(HUB[0]),600,560,88
        pm=np.zeros((H,W),np.float32)
        cv2.rectangle(pm,(cx-pw//2+ph_//2,cy-ph_//2),(cx+pw//2-ph_//2,cy+ph_//2),1.0,-1)
        cv2.circle(pm,(cx-pw//2+ph_//2,cy),ph_//2,1.0,-1,cv2.LINE_AA); cv2.circle(pm,(cx+pw//2-ph_//2,cy),ph_//2,1.0,-1,cv2.LINE_AA)
        pm=cv2.GaussianBlur(pm,(0,0),1.0)
        a=(pm*0.72*pk)[...,None]; img=img*(1-a)+np.array((38,17,4),np.float32)*a
        edge=np.zeros((H,W),np.float32)
        cv2.rectangle(edge,(cx-pw//2+ph_//2,cy-ph_//2),(cx+pw//2-ph_//2,cy+ph_//2),1.0,2,cv2.LINE_AA)
        cv2.ellipse(edge,(cx-pw//2+ph_//2,cy),(ph_//2,ph_//2),0,90,270,1.0,2,cv2.LINE_AA); cv2.ellipse(edge,(cx+pw//2-ph_//2,cy),(ph_//2,ph_//2),0,-90,90,1.0,2,cv2.LINE_AA)
        add(img,cv2.GaussianBlur(edge,(0,0),8),CY,1.0*pk); add(img,edge,CY,0.95*pk)
        tn=int(16*ease_io((f-40)/18.0)+0.999) if f>=40 else 0
        if tn>0:
            tsp=text_sprite('QAYO TEXNOLOGİYA',46,0.10,FONT_BOLD,n=min(tn,16))[0]
            tfu=text_sprite('QAYO TEXNOLOGİYA',46,0.10,FONT_BOLD,n=16)[0]
            tx=cx-tfu.shape[1]/2+tsp.shape[1]/2
            glow(img,tsp,tx,cy,1.0,CYAN,sigma=7,strength=0.9); blend(img,tsp,tx,cy,1.0,WHITE)
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
