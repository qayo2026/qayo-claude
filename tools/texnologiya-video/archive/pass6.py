import sys,subprocess,numpy as np,cv2
import overlay as OV
from PIL import Image,ImageFont,ImageDraw
SRC,OUT=sys.argv[1],sys.argv[2]
TMIN=float(sys.argv[3]) if len(sys.argv)>3 else 0; TMAX=float(sys.argv[4]) if len(sys.argv)>4 else 99
W,H,FPS=1080,1920,30
def smooth(a,b,x): u=np.clip((x-a)/(b-a),0,1); return u*u*(3-2*u)
# title removal box (full-frame coords)
BX0,BX1,BY0,BY1=250,830,550,700
IN0,IN1=99.0,99.5
OUT0,OUT1=99.2,99.5
def remove_title(fr):
    M=70
    crop=fr[BY0-M:BY1+M,BX0-M:BX1+M]
    er=cv2.erode(crop,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(91,91)))
    bl=cv2.GaussianBlur(er,(0,0),18)[M:-M,M:-M].astype(np.float32)
    box=fr[BY0:BY1,BX0:BX1].astype(np.float32)
    # keep original thin streaks/HUD that are darker than the fill? no: use fill, then re-add faint streaks
    streak=np.clip(box-cv2.GaussianBlur(box,(0,0),4)-6,0,40)*0.6
    ys=np.arange(BY1-BY0,dtype=np.float32); xs=np.arange(BX1-BX0,dtype=np.float32)
    fe=(np.minimum(smooth(0,35,ys),smooth(0,35,BY1-BY0-1-ys))[:,None]*np.minimum(smooth(0,35,xs),smooth(0,35,BX1-BX0-1-xs))[None,:])[...,None]
    # match the fill's tone to the ring just outside the box (median) so no rectangle shows
    def ring(a,b):
        return np.median(np.concatenate([a[:, :12].reshape(-1,3), a[:, -12:].reshape(-1,3), a[:12].reshape(-1,3), a[-12:].reshape(-1,3)]),axis=0)
    delta=ring(box,None)-ring(bl,None)
    res=np.clip(bl+delta,0,255)
    return np.clip(res*fe+box*(1-fe),0,255).astype(np.uint8)
TY0,TY1=240,540; TH=TY1-TY0
TYH0,TYH1=1120,1420; THH=TYH1-TYH0
DY=-880
FONT='/usr/share/fonts/opentype/inter/Inter-SemiBold.otf'
# (text,size,yc,t_start,spread,track,t_fade_start,t_fade_end)
LINES=[("DÜNYAYA AÇILIN",68,1230+DY,17.95,0.9,6,20.60,20.90),
 ("YENİ BİZNES İMKANLARINI",50,1215+DY,22.00,1.3,5,27.00,27.25),
 ("KƏŞF EDİN,",50,1285+DY,23.40,0.45,5,27.00,27.25),
 ("FÜRSƏTLƏRİ QAÇIRMAYIN",50,1355+DY,24.60,1.0,5,27.00,27.25)]
chars=[]
for text,size,yc,t0,spread,track,f0,f1 in LINES:
    f=ImageFont.truetype(FONT,size)
    widths=[f.getlength(c) for c in text]
    total=sum(widths)+track*(len(text)-1); x=(W-total)/2; n=len(text)
    for i,c in enumerate(text):
        if c!=' ':
            im=Image.new('L',(W,TH),0); ImageDraw.Draw(im).text((x,yc-TY0),c,font=f,fill=255,anchor='lm')
            chars.append((np.asarray(im,np.float32)/255,t0+spread*i/max(1,n-1),f0,f1))
        x+=widths[i]+track
HOLD=[("QAYO TEXNOLOGİYA",68,1215,10.50,1.25,6),("QLOBAL ŞƏBƏKƏMİZLƏ",50,1300,12.30,0.95,5),("HƏR YERDƏYİK.",50,1365,13.70,0.85,5)]
H0,H1,HG=16.80,17.10,14.60   # hold fade out; start taking over at HG
hchars=[]
for text,size,yc,t0,spread,track in HOLD:
    f=ImageFont.truetype(FONT,size)
    widths=[f.getlength(c) for c in text]
    total=sum(widths)+track*(len(text)-1); x=(W-total)/2; n=len(text)
    for i,c in enumerate(text):
        if c!=' ':
            im=Image.new('L',(W,THH),0); ImageDraw.Draw(im).text((x,yc-TYH0),c,font=f,fill=255,anchor='lm')
            hchars.append((np.asarray(im,np.float32)/255,t0+spread*i/max(1,n-1)))
        x+=widths[i]+track
def hold_layer(t):
    a=np.zeros((THH,W),np.float32)
    for m,ts in hchars:
        k=float(smooth(ts,ts+0.22,t))*(1-float(smooth(H0,H1,t)))
        if k>0: a=np.maximum(a,m*k)
    return a
def text_layer(t):
    a=np.zeros((TH,W),np.float32)
    for m,ts,f0,f1 in chars:
        k=float(smooth(ts,ts+0.22,t))*(1-float(smooth(f0,f1,t)))
        if k>0: a=np.maximum(a,m*k)
    return a

def blank_top(fr,t):
    a_t=float(smooth(14.7,15.0,t))*(1-float(smooth(22.07,22.2,t)))
    if a_t<=0: return fr
    y0,y1=520,722
    ys=np.arange(y0,y1,dtype=np.float32)
    k=float(smooth(17.85,18.05,t))        # 0 = globe scene, 1 = flat map scene
    e0=690*(1-k)+650*k; e1=716*(1-k)+674*k
    ay=1-smooth(e0,e1,ys)
    bgc=np.median(fr[y0:y0+12],axis=(0,1)).astype(np.float32)
    reg=fr[y0:y1].astype(np.float32)
    a=(ay*a_t)[:,None,None]
    fr[y0:y1]=np.clip(reg*(1-a)+bgc*a,0,255).astype(np.uint8)
    return fr
dec=subprocess.Popen(['ffmpeg','-v','error','-i',SRC,'-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
enc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
 '-i',SRC,'-map','0:v','-map','1:a','-c:v','libx264','-preset','medium','-crf','15','-pix_fmt','yuv420p','-c:a','copy',OUT],stdin=subprocess.PIPE)
fs=W*H*3;i=0
while True:
    buf=dec.stdout.read(fs)
    if len(buf)<fs: break
    t=i/FPS; fr=np.frombuffer(buf,np.uint8).reshape(H,W,3).copy()
    fr=blank_top(fr,t)
    fr=OV.apply(fr,i)
    if IN0<=t<OUT1:
        w=float(smooth(IN0,IN0+0.15,t))*(1-float(smooth(OUT0,OUT1,t)))
        if w>0:
            clean=remove_title(fr)
            fr[BY0:BY1,BX0:BX1]=(clean*w+fr[BY0:BY1,BX0:BX1]*(1-w)).astype(np.uint8)
    if HG<=t<H1:
        reg=fr[TYH0:TYH1].astype(np.float32)
        bg=np.concatenate([reg[:,:50],reg[:,-50:]],axis=1).mean(axis=1,keepdims=True)
        reg=np.repeat(bg,W,axis=1)
        ah=hold_layer(t); gl=cv2.GaussianBlur(ah,(0,0),9)
        reg=reg+gl[...,None]*np.array([60,170,255],np.float32)*0.55
        reg=reg*(1-ah[...,None])+ah[...,None]*np.array([235,248,255],np.float32)
        fr[TYH0:TYH1]=np.clip(reg,0,255).astype(np.uint8)
    a=text_layer(t)
    if a.max()>0:
        gl=cv2.GaussianBlur(a,(0,0),9)
        reg=fr[TY0:TY1].astype(np.float32)
        reg=reg+gl[...,None]*np.array([60,170,255],np.float32)*0.55
        reg=reg*(1-a[...,None])+a[...,None]*np.array([235,248,255],np.float32)
        fr[TY0:TY1]=np.clip(reg,0,255).astype(np.uint8)
    enc.stdin.write(fr.tobytes()); i+=1
enc.stdin.close(); enc.wait(); print('frames',i)
