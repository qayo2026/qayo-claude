"""KOSMOS quruluşu: HUD zolaqları, pəncərə, loqo səhnəsi. Hamısı kodla, tək palitra (text-fx rəngləri)."""
import os, sys, math, cv2, numpy as np
HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,os.path.join(HERE,'..','text-fx'))
from text_fx import *
W,H=1080,1920
GROUND=np.array((24,8,0),np.float32)     # BGR #000818
CYB=(255,225,92); CYD=(168,127,31)       # BGR #5CE1FF, #1F7FA8
REDB=(84,59,255)
LOGO='/home/claude/qayo-claude/assets/logo/qayo-texnologiya-logo-beyaz.png'

_GB={}
def ground_bg(cy=960):
    if cy in _GB: return _GB[cy].copy()
    yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
    d=np.sqrt(((xx-540)/760)**2+((yy-cy)/1100)**2)
    k=np.clip(1-d,0,1)[...,None]**1.7
    _GB[cy]=GROUND*(1-k)+np.array((52,22,4),np.float32)*k
    return _GB[cy].copy()

def add(img,layer,color,amt=1.0):
    img[:]=np.clip(img+np.clip(layer,0,1)[...,None]*amt*np.array(color,np.float32),0,255)

def arc(layer,c,r,a0,a1,th,val=1.0):
    cv2.ellipse(layer,(int(c[0]),int(c[1])),(int(r),int(r)),0,a0,a1,val,int(th),cv2.LINE_AA)

def ring_hud(img,c,R,t,alpha=1.0,prog=1.0):
    """Halqa HUD: R = xarici radius. t = saniyə (fırlanma). prog 0..1 = çəkilmə."""
    s=R/420.0
    L1=np.zeros((H,W),np.float32); L2=np.zeros((H,W),np.float32); L3=np.zeros((H,W),np.float32)
    # xarici işarələr
    for k in range(120):
        a=math.radians(k*3+t*4); big=(k%5==0)
        r0=R; r1=R+(16 if big else 8)*s
        if k/120.0>prog: break
        cv2.line(L3,(int(c[0]+r0*math.cos(a)),int(c[1]+r0*math.sin(a))),(int(c[0]+r1*math.cos(a)),int(c[1]+r1*math.sin(a))),1.0,1,cv2.LINE_AA)
    # qalın qövslər
    for a0,a1,w,rr,sp in ((-100,-30,16,385,18),(15,70,10,385,-14),(160,235,16,385,12),(250,300,8,385,-10)):
        o=t*sp
        arc(L1,c,rr*s,a0+o,a0+o+(a1-a0)*prog,max(2,w*s))
    arc(L2,c,350*s,0,360*prog,max(1,2*s))
    for k in range(30):
        a=k*12-t*8
        if k/30.0>prog: break
        arc(L2,c,315*s,a,a+8,max(1,3*s))
    # alt qövs + nöqtələr
    arc(L2,c,285*s,205,205+130*prog,max(1,4*s))
    for ang in (205,335):
        if prog>0.98:
            cv2.circle(L1,(int(c[0]+285*s*math.cos(math.radians(ang))),int(c[1]+285*s*math.sin(math.radians(ang)))),int(max(3,7*s)),1.0,-1,cv2.LINE_AA)
    # sağ blok sırası
    for k in range(10):
        if k/10.0>prog: break
        a=20+k*3.6
        arc(L1,c,372*s,a,a+2.4,max(2,22*s),1.0-k*0.07)
    for L,amt in ((L3,0.5),(L2,0.75),(L1,1.0)):
        add(img,cv2.GaussianBlur(L,(0,0),6*s+1),CYB,1.0*alpha*amt)
        add(img,L,CYB,alpha*amt)

def band_top(img,g):
    ring_hud(img,(540,330),290,g/30.0,alpha=0.6)
def band_bottom(img,g):
    t=g/30.0; L=np.zeros((H,W),np.float32); Lg=np.zeros((H,W),np.float32)
    # dalğa
    xs=np.arange(60,1021,6)
    ys=1560+22*np.sin(xs*0.02+t*3.1)+14*np.sin(xs*0.047-t*2.2)+8*np.sin(xs*0.11+t*5)
    cv2.polylines(L,[np.stack([xs,ys],1).astype(np.int32).reshape(-1,1,2)],False,1.0,2,cv2.LINE_AA)
    # bərabərləşdirici zolaqlar
    r=np.random.RandomState(7)
    for k in range(36):
        x=84+k*26; ph=r.rand()*6.28
        hgt=20+int(46*(0.5+0.5*math.sin(t*3.2+ph)*math.sin(t*1.3+k*0.4)))
        cv2.rectangle(Lg,(x,1680-hgt),(x+12,1680),1.0,-1)
    # xətlər
    for y in (1480,1740):
        cv2.line(L,(60,y),(1020,y),0.5,1,cv2.LINE_AA)
    add(img,cv2.GaussianBlur(L,(0,0),5),CYB,0.5); add(img,L,CYB,0.5)
    add(img,Lg,CYB,0.42)

def window_composite(src,ox,g,alpha=1.0,wy=660,wh=600,sy=120,bands=True):
    """src: 1280x720 BGR. Pəncərə: x=[ox,ox+1080], y=[sy,sy+wh]. Zolaqlar: bizim HUD."""
    img=ground_bg()
    if bands: band_top(img,g); band_bottom(img,g)
    crop=src[sy:sy+wh,int(ox):int(ox)+1080].astype(np.float32)
    m=np.ones((wh,1),np.float32)
    f=70
    ramp=np.linspace(0,1,f,dtype=np.float32)[:,None]
    m[:f]=ramp; m[-f:]=ramp[::-1]
    m=m*alpha
    reg=img[wy:wy+wh]
    img[wy:wy+wh]=reg*(1-m[...,None])+crop*m[...,None]
    return img

def split_logo(width=440):
    logo=logo_alpha(LOGO,width); LH=logo.shape[0]
    rows=(logo>0.2).sum(1)>0; gaps=np.where(~rows)[0]
    split=int(gaps[(gaps>LH*0.35)&(gaps<LH*0.65)].mean())
    return logo[:split].copy(),logo[split:].copy(),LH,split
_LOGO=None
def logo_scene(f,total=84):
    global _LOGO
    if _LOGO is None: _LOGO=split_logo()
    q_a,t_a,LH,split=_LOGO
    img=ground_bg()
    t=f/30.0
    p=ease_out(f/34.0)
    ring_hud(img,(540,960),400,t+2,alpha=min(1.0,f/10.0+0.2),prog=p)
    top=960-LH/2
    qo=ease_out(f/14.0)
    if qo>0:
        sp=scaled(q_a,0.88+0.12*qo)
        glow(img,sp,540,top+q_a.shape[0]/2,qo,(90,190,255),sigma=14,strength=0.8)
        blend(img,sp,540,top+q_a.shape[0]/2,qo,WHITE)
    to=ease_out((f-12)/18.0)
    if to>0:
        cy=top+split+t_a.shape[0]/2+(1-to)*14
        glow(img,t_a,540,cy,to,(90,190,255),sigma=9,strength=0.7); blend(img,t_a,540,cy,to,WHITE)
    lo=ease_out((f-30)/14.0)
    if lo>0:
        Lw=int(300*lo); y=int(top+LH+34)
        l2=np.ones((6,max(Lw,1)),np.float32)
        glow(img,l2,540-150+Lw/2,y,1.0,RED,sigma=6,strength=1.0); blend(img,l2,540-150+Lw/2,y,1.0,RED)
    return np.clip(img,0,255).astype(np.uint8)
