import cv2,numpy as np,math,os,sys
from PIL import Image,ImageDraw,ImageFont
W,H=1080,1920; S=2
back=cv2.imread('back.png')[...,::-1].astype(np.float32)
back0=cv2.imread('back0.png')[...,::-1].astype(np.float32)
import math as _m
MODC=[(300,0),(60,1),(240,2),(120,3)]
MODPOS=[(540+415*_m.sin(_m.radians(a)),930-505*_m.cos(_m.radians(a))) for a,_ in MODC]
MODT=[1.3,1.8,2.3,2.8]
DIFF=back-back0
trgb=np.load('t_rgb.npy').astype(np.float32); tm=np.load('t_m.npy').astype(np.float32)[...,None]
land=cv2.imread('land.png',0)
CX,CY,R=540,930,330
X0,Y0,X1,Y1=140,530,940,1330   # ROI
RW,RH=X1-X0,Y1-Y0
# globe dot grid
pts=[]
step=2.0
for la in np.arange(-88,88.1,step):
    n=max(8,int(360/step*math.cos(math.radians(la))))
    for k in range(n): pts.append((-180+360*k/n+ (step/2 if int((la+90)/step)%2 else 0),la))
P=np.array(pts); LON=np.radians(P[:,0]); LAT=np.radians(P[:,1])
isl=land[((90-P[:,1])/180*1023).astype(int).clip(0,1023),(((P[:,0]+180)/360*2047).astype(int)%2048)]>0
V=np.stack([np.cos(LAT)*np.sin(LON),np.sin(LAT),np.cos(LAT)*np.cos(LON)],1)  # x east,y north,z toward lon0
def ll(lon,lat):
    lo,la=math.radians(lon),math.radians(lat); return np.array([math.cos(la)*math.sin(lo),math.sin(la),math.cos(la)*math.cos(lo)])
def view(v,front_lon,tilt=math.radians(22)):
    a=-math.radians(front_lon); c,s=math.cos(a),math.sin(a)
    x=v[...,0]*c+v[...,2]*s; z=-v[...,0]*s+v[...,2]*c; y=v[...,1]
    ct,st=math.cos(tilt),math.sin(tilt)
    y2=y*ct-z*st; z2=y*st+z*ct
    return np.stack([x,y2,z2],-1)
CIT=[('Bakı',49.9,40.4),('Berlin',13.4,52.5),('Qahirə',31.2,30.0),('Dubay',55.3,25.2),('Mumbay',72.8,19.1),('Sinqapur',103.8,1.35),
     ('İstanbul',28.9,41.0),('London',-0.1,51.5),('Nyu-York',-74.0,40.7),('Tokio',139.7,35.7),('Sidney',151.2,-33.9),('Moskva',37.6,55.8)]
COLS=[(255,70,90),(255,70,90),(60,230,120),(255,200,60),(255,90,200),(255,170,60),(160,120,255),(255,120,60),(90,200,255),(255,100,160),(120,255,200),(255,230,90)]
FD='/usr/share/fonts/opentype/inter/Inter-Bold.otf'
FONT=ImageFont.truetype(FD,20)
def sc(p): return (CX+R*p[0]-X0, CY-R*p[1]-Y0)
def frame(t):
    fl=-15+ (80+15)*(t/7.5)      # front longitude: Atlantic -> Asia
    vv=view(V,fl); front=vv[:,2]>0.03
    lay=np.zeros((RH*S,RW*S,3),np.float32)
    x=(CX+R*vv[front,0]-X0)*S; y=(CY-R*vv[front,1]-Y0)*S; z=vv[front,2]; ld=isl[front]
    fres=(1-z)**1.4
    for xx,yy,zz,fr,l in zip(x,y,z,fres,ld):
        if l:
            a=min(1.4,0.55+1.0*fr+0.3*zz); r=max(1,int((1.9+2.0*fr+0.8*zz)*S/2))
            cv2.circle(lay,(int(xx),int(yy)),r,(a*140,a*230,a*255),-1,cv2.LINE_AA)
        else:
            a=0.10+0.25*fr; r=max(1,int(1.2*S/2+0.5))
            cv2.circle(lay,(int(xx),int(yy)),r,(a*100,a*190,a*255),-1,cv2.LINE_AA)
    # arcs from Baku
    hub=ll(CIT[0][1],CIT[0][2]); labels=[]
    for i in range(1,len(CIT)):
        tgt=ll(CIT[i][1],CIT[i][2]); om=math.acos(np.clip(hub@tgt,-1,1))
        t0=3.0+0.2*i; p=np.clip((t-t0)/1.1,0,1)
        seg=[]
        for s_ in np.linspace(0,1,60):
            q=(math.sin((1-s_)*om)*hub+math.sin(s_*om)*tgt)/math.sin(om)
            q=q*(1+0.38*math.sin(math.pi*s_)*(om/2.2+0.25))
            seg.append(q)
        seg=view(np.array(seg),fl)
        n=int(p*59)
        for k in range(n):
            if seg[k,2]<0.0 or seg[k+1,2]<0.0: continue
            a=0.35+0.65*k/59; 
            cv2.line(lay,tuple(np.int32(np.array(sc(seg[k]))*S)),tuple(np.int32(np.array(sc(seg[k+1]))*S)),(70*a,190*a,255*a),int(2.2*S),cv2.LINE_AA)
        if p>0:
            j=n if p<1 else int((((t-t0)*0.5+i*.11)%1.0)*59)
            for k in range(max(0,j-8),j):
                if seg[k,2]<0 or seg[k+1,2]<0: continue
                a=1-(j-k)/8
                cv2.line(lay,tuple(np.int32(np.array(sc(seg[k]))*S)),tuple(np.int32(np.array(sc(seg[k+1]))*S)),(255*a,255*a,255*a),int(3.2*S),cv2.LINE_AA)
    # markers
    for i,(nm,lo,la) in enumerate(CIT):
        pv=view(ll(lo,la),fl)
        if pv[2]<0.08: continue
        xx,yy=sc(pv); col=COLS[i]; appear=1 if i==0 else np.clip((t-(3.0+0.2*i)-0.9)/0.4,0,1)
        if i==0: appear=np.clip((t-0.4)/0.4,0,1)
        if appear<=0: continue
        pu=((t*1.0)+i*.23)%1.0
        cv2.circle(lay,(int(xx*S),int(yy*S)),int((7+4*(i==0))*S/1.2),tuple(float(c) for c in col),-1,cv2.LINE_AA)
        cv2.circle(lay,(int(xx*S),int(yy*S)),int((10+34*pu)*S/1.2),tuple(float(c*(1-pu)) for c in col),int(2*S),cv2.LINE_AA)
        labels.append((nm,xx,yy,appear))
    g=cv2.GaussianBlur(lay,(0,0),5*S)*1.2+cv2.GaussianBlur(lay,(0,0),16*S)*0.8
    lay=lay+g
    roi=cv2.resize(lay,(RW,RH),interpolation=cv2.INTER_AREA)
    f=back0.copy()
    for (mx,my),mt in zip(MODPOS,MODT):
        p=np.clip((t-mt)/0.6,0,1)
        if p<=0: continue
        e=1-(1-p)**3; sc_=0.55+0.45*e
        bx0,by0,bx1,by1=int(mx-175),int(my-75),int(mx+175),int(my+185)
        bx0=max(0,bx0);bx1=min(W,bx1);by0=max(0,by0);by1=min(H,by1)
        patch=DIFF[by0:by1,bx0:bx1]
        M=cv2.getRotationMatrix2D((mx-bx0,my-by0+40),0,sc_)
        wp=cv2.warpAffine(patch,M,(bx1-bx0,by1-by0),flags=cv2.INTER_LINEAR)
        f[by0:by1,bx0:bx1]+=wp*e
        # flash ring
        if p<1:
            fl=np.zeros((H,W,3),np.float32)
            cv2.circle(fl,(int(mx),int(my)),int(60+60*p),(120*(1-p),230*(1-p),255*(1-p)),3,cv2.LINE_AA)
            f+=fl+cv2.GaussianBlur(fl,(0,0),8)*1.5
    f[Y0:Y1,X0:X1]+=roi*1.0
    # labels (PIL)
    pil=Image.fromarray(np.clip(f,0,255).astype(np.uint8)); d=ImageDraw.Draw(pil,'RGBA')
    placed=[]
    for nm,xx,yy,ap in labels:
        gx,gy=xx+X0,yy+Y0
        if any(abs(gx-a)<95 and abs(gy-b)<38 for a,b in placed): continue
        placed.append((gx,gy))
        if abs(gx-CX)<270 and CY-120<gy<CY+200: continue
        w=d.textlength(nm,font=FONT)+22
        d.rounded_rectangle([gx-w/2,gy-48,gx+w/2,gy-18],radius=10,fill=(236,240,248,int(235*ap)))
        d.text((gx,gy-33),nm,font=FONT,fill=(20,30,50,int(255*ap)),anchor='mm')
    f=np.array(pil).astype(np.float32)
    # text layer with fade/scale-in
    ta=np.clip((t-0.3)/0.9,0,1); ta=ta*ta*(3-2*ta)
    pulse=1+0.05*math.sin(t*2.4)
    f=f*(1-tm*ta)+trgb*ta*pulse
    tt='QAYO TEXNOLOGİYA'; ft=ImageFont.truetype('/usr/share/fonts/opentype/inter/Inter-Black.otf',70*S)
    Lr=Image.new('RGBA',(W*S,260*S),(0,0,0,0)); dl=ImageDraw.Draw(Lr)
    tr=7*S; wd=sum(dl.textlength(c,font=ft) for c in tt)+tr*(len(tt)-1); x=(W*S-wd)/2
    for k,c in enumerate(tt):
        st=0.5+0.07*k; p=np.clip((t-st)/0.5,0,1); e=1-(1-p)**3
        cw=dl.textlength(c,font=ft)
        if p>0:
            Lc=Image.new('RGBA',Lr.size,(0,0,0,0)); ImageDraw.Draw(Lc).text((x,130*S+(1-e)*40*S),c,font=ft,fill=(255,255,255,int(255*e)),anchor='lm')
            Lr=Image.alpha_composite(Lr,Lc)
        x+=cw+tr
    la=np.array(Lr).astype(np.float32); ma=la[...,3:4]/255.
    la=cv2.resize(la,(W,260),interpolation=cv2.INTER_AREA); ma=cv2.resize(ma[...,0],(W,260),interpolation=cv2.INTER_AREA)[...,None]
    glw=cv2.GaussianBlur(la[...,:3]*ma,(0,0),14)*1.2*np.array([.55,.85,1.0],np.float32)+cv2.GaussianBlur(la[...,:3]*ma,(0,0),4)*.5
    YT=215
    f[YT:YT+260]=f[YT:YT+260]*(1-ma)+la[...,:3]*ma+glw
    f*=min(1,t/0.4)
    f=np.clip(f,0,255).astype(np.uint8)
    zz=1+0.03*t/7.5
    Mx=cv2.getRotationMatrix2D((W/2,H/2),0,zz)
    return cv2.warpAffine(f,Mx,(W,H),flags=cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE)
if __name__=='__main__':
    os.makedirs('af2',exist_ok=True)
    if len(sys.argv)>1:
        for t in map(float,sys.argv[1:]): cv2.imwrite('p_%.1f.png'%t,frame(t)[...,::-1])
    else:
        for i in range(225): cv2.imwrite('af2/a_%04d.png'%i,frame(i/30.0)[...,::-1])
