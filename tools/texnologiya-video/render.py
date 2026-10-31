import cv2, numpy as np, subprocess, sys, math
from PIL import Image
SRC='../dm/final2.mp4'; OUT=sys.argv[1] if len(sys.argv)>1 else 'v91_raw.mp4'
T0,T1=11.0,15.2
TE=11.22   # impact moment (effects start)
W,H,FPS=1080,1920,30
Y0,Y1=540,1085; RH=Y1-Y0; OFF=585-Y0
IMX,IMY=506,695-Y0     # impact point (region coords)
BEAMX=510

# ---- base frames (clean map loop) 10.50..10.93 from original
def grab(t0,n):
    p=subprocess.run(['ffmpeg','-v','error','-ss',str(t0),'-i',SRC,'-frames:v',str(n),'-f','rawvideo','-pix_fmt','rgb24','-'],capture_output=True).stdout
    a=np.frombuffer(p,np.uint8).reshape(-1,H,W,3)
    return a[:,Y0:Y1].copy()
base=grab(10.50,7)
base_loop=list(base)+list(base[-2:0:-1])
# ---- land mask
im=base[2]
g=cv2.GaussianBlur(im[:,:,1].astype(np.float32),(0,0),2.0)
m=(g>60).astype(np.uint8)
poly=np.zeros_like(m); poly[OFF+5:OFF+375,165:878]=1; poly[OFF+195:OFF+245,780:878]=0
m=m*poly
m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((7,7),np.uint8))
n,lab,st,_=cv2.connectedComponentsWithStats(m)
for i in range(1,n):
    if st[i,cv2.CC_STAT_AREA]<500: m[lab==i]=0
mask=cv2.GaussianBlur(m.astype(np.float32),(0,0),1.5)
# bright points (city lights)
lum=im.astype(np.float32).sum(2)/3
lights=np.clip((cv2.GaussianBlur(lum,(0,0),1.0)-cv2.GaussianBlur(lum,(0,0),6.0)-25)/60,0,1)*mask
# ---- distance from impact (slightly squashed vertically for perspective)
yy,xx=np.mgrid[0:RH,0:W].astype(np.float32)
D=np.sqrt((xx-IMX)**2+((yy-IMY)*1.25)**2)
# ---- hubs (full-image coords) snapped to land
hubs=[(255,690),(350,715),(330,640),(300,765),(400,830),(365,905),(335,812),(520,745),(490,790),(590,810),(565,885),
 (620,745),(640,650),(760,640),(680,715),(690,770),(760,725),(810,715),(745,790),(770,830),(775,895),(800,890),(535,650),(430,610),(840,925),(560,690),(470,700),(660,690)]
ys,xs=np.where(m>0)
def snap(x,y):
    yy_=y-Y0
    d=(xs-x)**2+(ys-yy_)**2
    i=d.argmin(); return float(xs[i]),float(ys[i])
H_=[snap(x,y) for x,y in hubs]
H_=[h for h in H_ if (h[0]-IMX)**2+(h[1]-IMY)**2>40**2]
hub_d=[math.hypot(h[0]-IMX,(h[1]-IMY)*1.25) for h in H_]
order=np.argsort(hub_d)
RMAX=620.0; WAVE_T=2.6     # seconds for wave to reach RMAX
def ease(u): u=min(max(u,0),1); return 1-(1-u)**2.2
def smooth(a,b,x): u=np.clip((x-a)/(b-a),0,1); return u*u*(3-2*u)
CY=np.array([255,170,40],np.float32)/255  # BGR cyan-blue
def bez(p0,p1,t):
    mx,my=(p0[0]+p1[0])/2,(p0[1]+p1[1])/2
    dist=math.hypot(p1[0]-p0[0],p1[1]-p0[1])
    c=(mx,my-0.28*dist)
    x=(1-t)**2*p0[0]+2*(1-t)*t*c[0]+t*t*p1[0]
    y=(1-t)**2*p0[1]+2*(1-t)*t*c[1]+t*t*p1[1]
    return x,y
def frame_fx(tau,fi,orig):
    b=base_loop[fi%len(base_loop)].astype(np.float32)/255
    if tau<0: tau=-1.0
    r=RMAX*ease(max(tau,0)/WAVE_T) if tau>=0 else -1000.0
    # wave front lights the land
    lit=smooth(-14,14,r-D)*mask
    age=np.clip((r-D)/RMAX,0,1)
    steady=0.85+0.12*np.sin(tau*3.1+D*0.02)
    ring=np.exp(-((D-r)/9.0)**2)*(1.0 if r<RMAX else 0)*np.clip(1.2-tau/WAVE_T,0.0,1.0)
    halo=np.exp(-((D-r)/55.0)**2)*np.clip(1.1-tau/WAVE_T,0,1)
    glow=lit*steady
    add=np.zeros((RH,W,3),np.float32)
    add+=glow[...,None]*np.array([0.55,0.40,0.10],np.float32)*1.0       # BGR-ish in RGB order below
    # we work in RGB: light cyan-blue
    add=np.zeros((RH,W,3),np.float32)
    add[...,0]+=glow*0.04; add[...,1]+=glow*0.20; add[...,2]+=glow*0.32
    # white-hot front along land + overall ring
    front=np.exp(-((D-r)/16.0)**2)*mask*np.clip(1.2-tau/WAVE_T,0,1)
    add+=front[...,None]*np.array([0.45,0.80,1.0],np.float32)*0.7
    add+=ring[...,None]*np.array([0.30,0.70,1.0],np.float32)*0.40
    add+=halo[...,None]*np.array([0.04,0.14,0.30],np.float32)*0.45
    # city lights pulse
    add+=(lights*lit*(0.5+0.5*np.sin(tau*5+xx*0.07)))[...,None]*np.array([0.9,0.8,0.5],np.float32)*0.6
    # impact flash
    fl=np.exp(-(((xx-IMX)**2+(yy-IMY)**2)/(2*(26+90*min(tau,1.0))**2)))*np.clip(1.5-tau*1.4,0,1)*(1.0 if tau>=0 else 0.0)
    add+=fl[...,None]*np.array([0.8,0.95,1.0],np.float32)*0.9
    # ---- arcs
    layer=np.zeros((RH,W,3),np.uint8)
    pulse=np.zeros((RH,W,3),np.uint8)
    for k in order:
        hx,hy=H_[k]
        appear=hub_d[k]/RMAX*WAVE_T*0.88     # when the wave reaches the hub
        a=(tau-appear)/0.9
        if a<=0: continue
        a=min(a,1.0); a=1-(1-a)**2
        n=48; ts=np.linspace(0,a,max(2,int(n*a)+1))
        pts=np.array([bez((IMX,IMY),(hx,hy),t) for t in ts],np.float32)
        cv2.polylines(layer,[pts.astype(np.int32)],False,(120,205,255),1,cv2.LINE_AA)
        if a>=1:
            # traveling pulse
            ph=((tau*0.8+k*0.137)%1.0)
            px,py=bez((IMX,IMY),(hx,hy),ph)
            cv2.circle(pulse,(int(px),int(py)),4,(235,250,255),-1,cv2.LINE_AA)
            rr=int(5+9*((tau*1.3+k*0.2)%1.0))
            cv2.circle(pulse,(int(hx),int(hy)),rr,(110,200,255),1,cv2.LINE_AA)
            cv2.circle(pulse,(int(hx),int(hy)),3,(255,255,255),-1,cv2.LINE_AA)
    L=layer.astype(np.float32)/255; P=pulse.astype(np.float32)/255
    bl=cv2.GaussianBlur(L,(0,0),6)
    out=b+add+L*0.80+bl*0.9+P*0.9+cv2.GaussianBlur(P,(0,0),5)*0.7
    out=np.clip(out,0,1)
    out8=(out*255).astype(np.uint8)
    # beam column from original down to impact
    bx0,bx1=BEAMX-22,BEAMX+22
    ys_=np.arange(RH)[:,None]
    wy=np.clip((IMY-8-ys_)/20.0,0,1)       # 1 above impact, fades just before
    wx=np.exp(-((np.arange(bx0,bx1)-BEAMX)/14.0)**2)[None,:]
    wgt=(wy*wx)[...,None]
    seg=out8[:,bx0:bx1].astype(np.float32); o=orig[:,bx0:bx1].astype(np.float32)
    out8[:,bx0:bx1]=(seg*(1-wgt)+np.maximum(o,seg)*wgt).astype(np.uint8)
    return out8


# ---- on-screen text synced with the voice (below the map, open, uppercase)
from PIL import ImageFont, ImageDraw
TY0,TY1=1120,1400; TH=TY1-TY0
FONT='/usr/share/fonts/opentype/inter/Inter-SemiBold.otf'
LINES=[("QAYO TEXNOLOGİYA",68,1215,10.50,1.25,6),("QLOBAL ŞƏBƏKƏMİZLƏ",50,1300,12.30,0.95,5),("HƏR YERDƏYİK.",50,1365,13.70,0.85,5)]
chars=[]   # (mask float HxW, t_start)
for text,size,yc,t0,spread,track in LINES:
    f=ImageFont.truetype(FONT,size)
    widths=[f.getlength(c) for c in text]
    total=sum(widths)+track*(len(text)-1)
    x=(W-total)/2
    n=len(text)
    for i,c in enumerate(text):
        if c!=' ':
            im=Image.new('L',(W,TH),0); d=ImageDraw.Draw(im)
            d.text((x,yc-TY0),c,font=f,fill=255,anchor='lm')
            chars.append((np.asarray(im,np.float32)/255,t0+spread*i/max(1,n-1)))
        x+=widths[i]+track
def text_layer(t):
    a=np.zeros((TH,W),np.float32)
    fade=1.0-float(smooth(14.72,14.98,t))
    for m,ts in chars:
        k=float(smooth(ts,ts+0.22,t))
        if k>0: a=np.maximum(a,m*k)
    return a*fade

dec=subprocess.Popen(['ffmpeg','-v','error','-i',SRC,'-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
enc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
   '-i',SRC,'-map','0:v','-map','1:a','-c:v','libx264','-preset','medium','-crf','15','-pix_fmt','yuv420p','-c:a','copy',OUT],stdin=subprocess.PIPE)
fs=W*H*3; i=0
while True:
    buf=dec.stdout.read(fs)
    if len(buf)<fs: break
    t=i/FPS
    fr=np.frombuffer(buf,np.uint8).reshape(H,W,3).copy()
    if T0<=t<T1:
        tau=t-TE
        mine=frame_fx(tau,i,fr[Y0:Y1])
        o=fr[Y0:Y1].astype(np.float32)
        a=float(smooth(14.90,15.12,t)); w=1.0-a
        # feather top/bottom edges of the replaced band into the original
        ys_=np.arange(RH,dtype=np.float32)
        fe=np.minimum(smooth(0,30,ys_),smooth(0,30,RH-1-ys_))[:,None,None]
        k=w*fe
        fr[Y0:Y1]=(mine.astype(np.float32)*k+o*(1-k)).astype(np.uint8)
    if 10.45<=t<15.0:
        a=text_layer(t)
        if a.max()>0:
            gl=cv2.GaussianBlur(a,(0,0),9)
            reg=fr[TY0:TY1].astype(np.float32)
            col=np.array([235,248,255],np.float32); gcol=np.array([60,170,255],np.float32)
            reg=reg+gl[...,None]*gcol*0.55
            reg=reg*(1-a[...,None])+a[...,None]*col
            fr[TY0:TY1]=np.clip(reg,0,255).astype(np.uint8)
    enc.stdin.write(fr.tobytes()); i+=1
enc.stdin.close(); enc.wait()
print('frames',i)
