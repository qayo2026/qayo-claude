"""P2 / Peyk qlobus səhnəsi: Gemini-nin içinə yazdığı 'QAYO Texnologiya' + slogan əvəzinə Peykin RƏSMİ QAYO loqosu (kodla).
Mətn pikseli təmizlənə bilmir (qlobus korlanır) -> həmin saniyələrdə buzlu şüşə lövhə + rəsmi loqo.
İstifadə: python3 p2_logo_swap.py <giriş.mp4> <çıxış.mp4>"""
import sys,os,subprocess,tempfile,glob
import numpy as np,cv2,math
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(HERE,'..','text-fx'))
from text_fx import *
SRC,DST=sys.argv[1],sys.argv[2]; FB='/usr/share/fonts/opentype/inter/Inter-Bold.otf'
FPS=24; TD=tempfile.mkdtemp(); subprocess.run(['ffmpeg','-loglevel','error','-y','-i',SRC,'-vf','fps=%d'%FPS,TD+'/f_%04d.png'],check=True)
files=sorted(glob.glob(TD+'/f_*.png')); H,W=cv2.imread(files[0]).shape[:2]
# Peyk loqosu: yalnız rəsmi QAYO (assets/logo/qayo-logo-beyaz.png)
Lq=cv2.imread(os.path.join(HERE,'..','..','assets','logo','qayo-logo-beyaz.png'),cv2.IMREAD_UNCHANGED)[:,:,3].astype(np.float32)/255
def crop(a):
    r=np.where((a>0.05).any(1))[0]; c=np.where((a>0.05).any(0))[0]; return a[r[0]:r[-1]+1,c[0]:c[-1]+1]
Lq=crop(Lq); LWD=int(W*0.23); LA=cv2.resize(Lq,(LWD,int(Lq.shape[0]*LWD/Lq.shape[1])),interpolation=cv2.INTER_AREA)
SUB=None

def ease_out(x): x=min(1,max(0,x)); return 1-(1-x)**3
# ---- fırlanan HUD halqası (Kosmos loqo üslubu): kodla çəkilir
CX_,CY_=W//2,int(0.5*H); RS=H*0.43/300.0
def rc(r): return int(r*RS)
def arc(l,r,a0,a1,th,v=1.0):
    cv2.ellipse(l,(CX_,CY_),(rc(r),rc(r)),0,a0,a1,v,max(1,int(th*RS)),cv2.LINE_AA)
def ticks(l,r,n,ln,ang,v=0.8,every=1):
    for k in range(0,n,every):
        a=math.radians(ang+360.0*k/n); c,s=math.cos(a),math.sin(a)
        cv2.line(l,(int(CX_+c*rc(r)),int(CY_+s*rc(r))),(int(CX_+c*rc(r+ln)),int(CY_+s*rc(r+ln))),v,1,cv2.LINE_AA)
def ring_layers(t):
    u=max(0.0,t-2.35); spin=3.2*(1-ease_out(u/1.0)); a=t*28
    cy_=np.zeros((H,W),np.float32); bl_=np.zeros((H,W),np.float32)
    arc(cy_,300,0,360,1.6,0.7); ticks(cy_,300,90,9,-a*0.4+spin*40,0.7)
    for st in (20,150,260): arc(bl_,272,st+a,st+a+70,13,1.0)
    arc(cy_,272,0,360,1.4,0.35)
    arc(cy_,244,0,360,2.2,0.8)
    for st in (30,200): 
        arc(cy_,226,st-a*0.7,st-a*0.7+110,3.0,1.0)
        for e in (st-a*0.7,st-a*0.7+110): 
            q=math.radians(e); cv2.circle(cy_,(int(CX_+math.cos(q)*rc(226)),int(CY_+math.sin(q)*rc(226))),max(3,rc(5)),1.0,-1,cv2.LINE_AA)
    ticks(cy_,198,72,8,a*0.5-spin*30,0.6)
    arc(cy_,176,40+a*0.3,240+a*0.3,1.8,0.8)
    # sağdakı pilləli blok
    for j in range(9):
        r0=250+j*5; arc(bl_,r0,-14+j*0.4,-14+4+j*0.9,3.0,0.9)
    return cy_,bl_

def plate_a(t): return ease_out((t-2.35)/0.4)*(1-ease_out((t-3.8)/0.3))
band=np.zeros((H,W),np.float32); y0,y1=int(0.32*H),int(0.68*H); band[y0:y1]=1; band=cv2.GaussianBlur(band,(0,0),22)
LCY=int(0.5*H); SCY=int(0.585*H)
for i,fp in enumerate(files):
    t_=i/FPS; pa=plate_a(t_)
    if pa<=0.001: continue
    im=cv2.imread(fp).astype(np.float32)
    bl=cv2.GaussianBlur(im,(0,0),26); tint=np.float32([70,38,12])
    m=(band*pa)[...,None]; plate=bl*0.5+tint*0.5; im=im*(1-m)+plate*m
    lo=ease_out((t_-2.5)/0.5)*(1-ease_out((t_-3.55)/0.3)); sc=0.93+0.07*ease_out((t_-2.5)/0.9)
    if lo>0:
        cyl,bll=ring_layers(t_)
        # halqanın içində tünd disk
        dk=np.zeros((H,W),np.float32); cv2.circle(dk,(CX_,CY_),rc(205),1.0,-1,cv2.LINE_AA); dk=cv2.GaussianBlur(dk,(0,0),6)*0.45*lo
        im=im*(1-dk[...,None])
        gl=cv2.GaussianBlur(cyl,(0,0),7)+cv2.GaussianBlur(bll,(0,0),9)*0.8; P=np.float32([245,216,88]); D=np.float32([255,125,25])
        im=np.clip(im+(P*(cyl*0.9+gl*0.9)[...,None]+D*(bll*0.95+gl*0.4)[...,None])*lo,0,255)
        a=LA*lo; glow(im,a,W/2,CY_,sc,WHITE,sigma=12,strength=0.7*lo); blend(im,a,W/2,CY_,sc,WHITE)
    cv2.imwrite(fp,np.clip(im,0,255).astype(np.uint8))
subprocess.run(['ffmpeg','-loglevel','error','-y','-framerate',str(FPS),'-i',TD+'/f_%04d.png','-i',SRC,'-map','0:v','-map','1:a?','-c:v','libx264','-crf','17','-preset','slow','-pix_fmt','yuv420p','-c:a','copy','-movflags','+faststart','-shortest',DST],check=True)
print('OK',DST)
