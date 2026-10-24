"""Orijinal 12 san KOSMOS üçün kosmetik təmizlik (səs, kadr sırası, rəng toxunulmaz):
1) xəritə kadrlarında sağ-aşağı Gemini iz ləkəsini doldurur; 2) peyk qanadlarına yumşaq işıq (açma).
İstifadə: python3 old_clean.py <orijinal.mp4> <çıxış.mp4> [--test f1,f2,...]"""
import sys, os, subprocess, cv2, numpy as np, tempfile, shutil
SRC,OUT=sys.argv[1],sys.argv[2]
SM_A,SM_B=175,284           # ləkə kadrları (1-əsaslı)
KEY=[(1,210,920),(30,230,930),(60,240,920),(90,230,760),(108,230,700)]
def wing_params(i):
    xs=[k[0] for k in KEY]; cx=np.interp(i,xs,[k[1] for k in KEY]); cy=np.interp(i,xs,[k[2] for k in KEY])
    amt=1.0 if i<=95 else max(0.0,1-(i-95)/15.0)
    return cx,cy,amt
_yy,_xx=None,None
def wing_lift(img,i):
    cx,cy,amt=wing_params(i)
    if amt<=0: return img
    global _yy,_xx
    if _yy is None: _yy,_xx=np.mgrid[0:1920,0:1080].astype(np.float32)
    d=np.sqrt(((_xx-cx)/270.0)**2+((_yy-cy)/240.0)**2)
    m=np.clip(1.25-d,0,1)**1.3*amt
    f=img.astype(np.float32)/255.0
    g=np.power(f,0.88)*1.04                      # açma
    lum=f.max(axis=2,keepdims=True); hi=np.clip((lum-0.45)/0.4,0,1)
    bloom=cv2.GaussianBlur(f*hi,(0,0),14)*0.15    # yumşaq işıq
    out=f*(1-m[...,None])+np.clip(g+bloom,0,1)*m[...,None]
    return (out*255).astype(np.uint8)
def _ss(t): t=np.clip(t,0,1); return t*t*(3-2*t)
_fade=None
def smear_fix(img):
    """Sağ-aşağı Gemini izini tünd fona (#000818) yumşaq söndürür; kənar diaqonal və hamar."""
    global _fade
    H,W=img.shape[:2]
    if _fade is None:
        yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
        _fade=(_ss((xx-540)/280.0)*_ss((yy-950)/230.0))[...,None]
    g=np.array((24,8,0),np.float32)
    return np.clip(img.astype(np.float32)*(1-_fade)+g*_fade,0,255).astype(np.uint8)
def proc(img,i):
    img=wing_lift(img,i)
    if SM_A<=i<=SM_B: img=smear_fix(img)
    return img
if __name__=='__main__':
    tmp=tempfile.mkdtemp(); subprocess.run(['ffmpeg','-v','error','-i',SRC,'-vf','fps=30',f'{tmp}/f_%04d.png'],check=True)
    n=len(os.listdir(tmp))
    if len(sys.argv)>3 and sys.argv[3]=='--test':
        os.makedirs(OUT,exist_ok=True)
        for i in [int(x) for x in sys.argv[4].split(',')]: cv2.imwrite(f'{OUT}/c_{i:04d}.png',proc(cv2.imread(f'{tmp}/f_{i:04d}.png'),i))
    else:
        cmd=['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s','1080x1920','-r','30','-i','-','-i',SRC,
             '-map','0:v','-map','1:a','-c:v','libx264','-preset','slow','-crf','17','-pix_fmt','yuv420p','-r','30','-c:a','copy','-shortest','-movflags','+faststart',OUT]
        p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
        for i in range(1,n+1):
            p.stdin.write(proc(cv2.imread(f'{tmp}/f_{i:04d}.png'),i).tobytes())
        p.stdin.close(); p.wait(); print('hazır',OUT)
    shutil.rmtree(tmp)
