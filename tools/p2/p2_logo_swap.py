"""P2 / Peyk qlobus səhnəsi: Gemini-nin içinə yazdığı 'QAYO Texnologiya' + slogan əvəzinə RƏSMİ loqo (kodla).
Mətn pikseli təmizlənə bilmir (qlobus korlanır) -> həmin saniyələrdə buzlu şüşə lövhə + rəsmi loqo.
İstifadə: python3 p2_logo_swap.py <giriş.mp4> <çıxış.mp4>"""
import sys,os,subprocess,tempfile,math,glob
import numpy as np,cv2
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(HERE,'..','text-fx'))
from text_fx import *
SRC,DST=sys.argv[1],sys.argv[2]; FB='/usr/share/fonts/opentype/inter/Inter-Bold.otf'
FPS=24; TD=tempfile.mkdtemp(); subprocess.run(['ffmpeg','-loglevel','error','-y','-i',SRC,'-vf','fps=%d'%FPS,TD+'/f_%04d.png'],check=True)
files=sorted(glob.glob(TD+'/f_*.png')); H,W=cv2.imread(files[0]).shape[:2]
# rəsmi loqodan üfüqi xətt: QAYO + TEXNOLOGİYA, eyni hərf hündürlüyü
L=cv2.imread(os.path.join(HERE,'..','..','assets','logo','qayo-texnologiya-logo-beyaz.png'),cv2.IMREAD_UNCHANGED)[:,:,3].astype(np.float32)/255
def crop(a):
    r=np.where((a>0.05).any(1))[0]; c=np.where((a>0.05).any(0))[0]; return a[r[0]:r[-1]+1,c[0]:c[-1]+1]
def ext(a,c0,c1):
    cols=np.where((a>0.05).any(0))[0]; w=cols[-1]-cols[0]; x0=cols[0]+int(w*c0); x1=cols[0]+int(w*c1); r=np.where((a[:,x0:x1]>0.05).any(1))[0]; return r[0],r[-1]
q=crop(L[0:700]); t=crop(L[900:1221]); qr0,qr1=ext(q,0.42,0.62); tr0,tr1=ext(t,0.0,0.07)
CAP=96; gap=38
for _ in range(2):
    sq=CAP/(qr1-qr0+1); st=CAP/(tr1-tr0+1); w=q.shape[1]*sq+gap+t.shape[1]*st; CAP=CAP*min(1.0,W*0.78/w)
sq=CAP/(qr1-qr0+1); st=CAP/(tr1-tr0+1)
q2=cv2.resize(q,(int(q.shape[1]*sq),int(q.shape[0]*sq)),interpolation=cv2.INTER_AREA); t2=cv2.resize(t,(int(t.shape[1]*st),int(t.shape[0]*st)),interpolation=cv2.INTER_AREA)
qb=int(qr1*sq); tb=int(tr1*st); top=max(qb,tb); Hc=max(q2.shape[0]+top-qb,t2.shape[0]+top-tb)
LA=np.zeros((Hc,q2.shape[1]+gap+t2.shape[1]),np.float32); LA[top-qb:top-qb+q2.shape[0],:q2.shape[1]]=q2; LA[top-tb:top-tb+t2.shape[0],q2.shape[1]+gap:]=t2
SUB,_=text_sprite('SOFTWARE & INTELLIGENCE',30,0.16,FB)
def ease_out(x): x=min(1,max(0,x)); return 1-(1-x)**3
def plate_a(t): return ease_out((t-2.35)/0.4)*(1-ease_out((t-3.55)/0.3))
band=np.zeros((H,W),np.float32); y0,y1=int(0.31*H),int(0.69*H); band[y0:y1]=1; band=cv2.GaussianBlur(band,(0,0),22)
LCY=int(0.455*H); SCY=int(0.585*H)
for i,fp in enumerate(files):
    t_=i/FPS; pa=plate_a(t_)
    if pa<=0.001: continue
    im=cv2.imread(fp).astype(np.float32)
    bl=cv2.GaussianBlur(im,(0,0),26); tint=np.float32([70,38,12])
    m=(band*pa)[...,None]; plate=bl*0.5+tint*0.5; im=im*(1-m)+plate*m
    lo=pa*ease_out((t_-2.55)/0.5); sc=0.93+0.07*ease_out((t_-2.55)/0.9)
    if lo>0:
        a=LA*lo; glow(im,a,W/2,LCY,sc,WHITE,sigma=14,strength=0.8*lo); blend(im,a,W/2,LCY,sc,WHITE)
        so=pa*ease_out((t_-2.85)/0.4)
        if so>0: blend(im,SUB*so,W/2,SCY,1.0,CYAN)
    cv2.imwrite(fp,np.clip(im,0,255).astype(np.uint8))
subprocess.run(['ffmpeg','-loglevel','error','-y','-framerate',str(FPS),'-i',TD+'/f_%04d.png','-i',SRC,'-map','0:v','-map','1:a?','-c:v','libx264','-crf','17','-preset','slow','-pix_fmt','yuv420p','-c:a','copy','-movflags','+faststart','-shortest',DST],check=True)
print('OK',DST)
