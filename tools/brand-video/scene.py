import numpy as np, cv2, math
from PIL import Image, ImageDraw, ImageFont
W,H=1080,1920; S=2
FD='/usr/share/fonts/opentype/inter/Inter-%s.otf'
def F(w,s): return ImageFont.truetype(FD%w,int(s*S))
CX,CY=540,930; RX,RY=415,505; NR=60
CY_=(92,225,255); RED=(255,59,84)
MODS=[(60,'KOMPYUTER\nPROQRAMLARI','monitor'),(120,'MOBİL\nTƏTBİQLƏR','phone'),
      (240,'AĞILLI CİHAZ\nSİSTEMLƏRİ','device'),(300,'WEB\nPLATFORMALAR','web')]
def glow(img,s,k):
    b=cv2.GaussianBlur(img,(0,0),s*S); return img+k*b
def bg():
    y,x=np.mgrid[0:H*S,0:W*S].astype(np.float32); d=np.hypot((x-CX*S)/(W*S*.75),(y-CY*S)/(H*S*.55))
    t=np.clip(1-d,0,1)**1.6
    im=np.zeros((H*S,W*S,3),np.float32)
    im[...,0]=2+4*t; im[...,1]=6+16*t; im[...,2]=16+48*t  # RGB
    rng=np.random.default_rng(3)
    for _ in range(260):
        px,py=rng.integers(0,W*S),rng.integers(0,H*S); r=rng.choice([1,2,3]); v=rng.uniform(80,200)
        cv2.circle(im,(int(px),int(py)),r,(v*.5,v*.85,v),-1,cv2.LINE_AA)
    return im
def globe(rot):
    R=318
    lay=np.zeros((H*S,W*S,3),np.float32)
    pts=[]
    nlat=64
    for i in range(1,nlat):
        lat=math.pi*(i/nlat-.5); r=math.cos(lat); n=max(6,int(2*math.pi*r*74/ (math.pi) *1.0))
        for j in range(n):
            lon=2*math.pi*j/n+rot*(1+0.0); pts.append((lon,lat))
    for lon,lat in pts:
        x,y,z=math.cos(lat)*math.sin(lon),math.sin(lat),math.cos(lat)*math.cos(lon)
        if z<=0.02: continue
        lo=math.atan2(x,z)
        la=lat
        land=(math.sin(3*(lon-rot)+1)+math.sin(4*la+2*(lon-rot))+math.cos(5*(lon-rot)-3*la)*.7+math.sin(7*la+(lon-rot)))>-0.3
        fres=(1-z)**1.6
        a=(0.50+0.9*fres+0.3*z)*(1 if land else .30)
        px,py=(CX+R*x)*S,(CY-R*y)*S
        rad=max(1,int((2.4+1.8*fres*2+1.2*z)*S/2))
        v=min(1.6,a)
        cv2.circle(lay,(int(px),int(py)),rad,(v*170,v*235,v*255),-1,cv2.LINE_AA)
    return lay,R
def icon(d,kind,cx,cy,col):
    w=int(3.2*S); P=lambda a,b:(int((cx+a)*S),int((cy+b)*S))
    if kind=='phone':
        d.rounded_rectangle([P(-13,-26),P(13,26)],radius=7*S,outline=col,width=w); d.line([P(-4,19),P(4,19)],fill=col,width=w)
    elif kind=='monitor':
        d.rounded_rectangle([P(-27,-20),P(27,10)],radius=4*S,outline=col,width=w); d.line([P(0,10),P(0,22)],fill=col,width=w); d.line([P(-12,23),P(12,23)],fill=col,width=w)
    elif kind=='server':
        for k in(-22,-4,14):
            d.rounded_rectangle([P(-24,k),P(24,k+14)],radius=3*S,outline=col,width=w); d.ellipse([P(14,k+4),P(18,k+8)],fill=col)
    elif kind=='gear':
        d.ellipse([P(-10,-10),P(10,10)],outline=col,width=w)
        for a in range(0,360,45):
            r1,r2=17,26; ca,sa=math.cos(math.radians(a)),math.sin(math.radians(a))
            d.line([P(r1*ca,r1*sa),P(r2*ca,r2*sa)],fill=col,width=int(w*1.8))
        d.ellipse([P(-18,-18),P(18,18)],outline=col,width=w)
    elif kind=='device':
        d.rounded_rectangle([P(-12,-8),P(12,28)],radius=4*S,outline=col,width=w)
        for r in(10,18,26): d.arc([P(-r,-12-r),P(r,-12+r)],225,315,fill=col,width=w)
    elif kind=='web':
        d.ellipse([P(-24,-24),P(24,24)],outline=col,width=w); d.ellipse([P(-10,-24),P(10,24)],outline=col,width=w)
        d.line([P(-24,0),P(24,0)],fill=col,width=w); d.line([P(0,-24),P(0,24)],fill=col,width=w)
def textc(d,txt,cx,cy,font,fill,track=0):
    w=sum(d.textlength(ch,font=font) for ch in txt)+track*S*(len(txt)-1); x=cx*S-w/2
    for ch in txt:
        d.text((x,cy*S),ch,font=font,fill=fill,anchor='lm'); x+=d.textlength(ch,font=font)+track*S
def render(rot=0.9, mode='all', skip_mods=False):
    im=bg(); R=318
    if mode=='all':
        g,R=globe(rot); im+=0.8*g+0.7*cv2.GaussianBlur(g,(0,0),5*S)+0.3*cv2.GaussianBlur(g,(0,0),22*S)
    # globe rim
    rim=np.zeros_like(im); cv2.circle(rim,(CX*S,CY*S),R*S,(40,120,230),int(2*S),cv2.LINE_AA)
    # orbits
    orb=np.zeros_like(im)
    for k,(rx,ry,a) in enumerate([(RX,RY,1),(RX+22,RY+22,.55),(RX-24,RY-26,.5)]):
        cv2.ellipse(orb,(CX*S,CY*S),(rx*S,ry*S),0,0,360,(a*50,a*170,a*255),int((2 if k==0 else 1.4)*S),cv2.LINE_AA)
    rng=np.random.default_rng(11); sp=np.zeros_like(im)
    for _ in range(140):
        t=rng.uniform(0,6.283); k=rng.uniform(-30,30)
        x=CX+(RX+k)*math.sin(t)*rng.uniform(.9,1.05); y=CY-(RY+k)*math.cos(t)*rng.uniform(.9,1.05)
        r=rng.choice([2,3,4]); v=rng.uniform(.6,1.0)
        cv2.circle(sp,(int(x*S),int(y*S)),int(r*S/2+1),(v*150,v*230,v*255),-1,cv2.LINE_AA)
    for t in (0.5,1.9,3.3,4.4,5.5):
        x=CX+RX*math.sin(t); y=CY-RY*math.cos(t); cv2.circle(sp,(int(x*S),int(y*S)),int(6*S),(255,255,255),-1,cv2.LINE_AA)
    im+=rim+orb+sp+1.2*cv2.GaussianBlur(sp,(0,0),7*S)
    im=glow(im,10,.7)
    pil=Image.fromarray(np.clip(im,0,255).astype(np.uint8)).convert('RGBA'); L=Image.new('RGBA',pil.size,(0,0,0,0)); d=ImageDraw.Draw(L)
    for a,lab,kind in ([] if skip_mods else MODS):
        x=CX+RX*math.sin(math.radians(a)); y=CY-RY*math.cos(math.radians(a))
        d.ellipse([(x-NR)*S,(y-NR)*S,(x+NR)*S,(y+NR)*S],fill=(6,24,60,235),outline=(70,200,255,255),width=int(3.5*S))
        d.ellipse([(x-NR+8)*S,(y-NR+8)*S,(x+NR-8)*S,(y+NR-8)*S],outline=(40,140,230,150),width=int(1.5*S))
        icon(d,kind,x,y,(235,248,255,255))
        lines=lab.split('\n'); ph=34*len(lines)+26; pw=max(d.textlength(l,font=F('Bold',26)) for l in lines)/S+44; py=y+NR+14
        d.rounded_rectangle([(x-pw/2)*S,py*S,(x+pw/2)*S,(py+ph)*S],radius=14*S,fill=(6,24,60,235),outline=(70,200,255,255),width=int(2.4*S))
        for i,l in enumerate(lines): textc(d,l,x,py+13+17+34*i,F('Bold',26),(240,250,255,255),.6)
    lay=L; hl=np.array(lay).astype(np.float32)[...,:3]*(np.array(lay)[...,3:4]/255.)
    base=np.array(pil.convert('RGB')).astype(np.float32); a=np.array(lay)[...,3:4]/255.
    base=base*(1-a)+np.array(lay)[...,:3]*a
    base=glow(base,8,.35)
    if mode=='back':
        return cv2.resize(np.clip(base,0,255).astype(np.uint8),(W,H),interpolation=cv2.INTER_AREA)
    # central text
    pil=Image.fromarray(np.clip(base,0,255).astype(np.uint8)).convert('RGBA')
    T_=Image.new('RGBA',pil.size,(0,0,0,0)); d=ImageDraw.Draw(T_)
    textc(d,'SOFTWARE & INTELLIGENCE',CX,CY-6,F('Bold',34),(255,255,255,255),3.5)
    d.line([(CX-200)*S,(CY+34)*S,(CX+200)*S,(CY+34)*S],fill=RED+(255,),width=int(4*S))
    ta=np.array(T_).astype(np.float32); m=ta[...,3:4]/255.
    base=np.array(pil.convert('RGB')).astype(np.float32)
    gl=cv2.GaussianBlur(ta[...,:3]*m,(0,0),14*S)+cv2.GaussianBlur(ta[...,:3]*m,(0,0),4*S)*.6
    if mode=='text':
        al=np.clip(m+np.clip(gl.mean(2,keepdims=True)/255*.6,0,1),0,1)
        rgb=ta[...,:3]*m+gl*.45
        return cv2.resize(rgb,(W,H),interpolation=cv2.INTER_AREA),cv2.resize(m[...,0],(W,H),interpolation=cv2.INTER_AREA)
    base=base*(1-m)+ta[...,:3]*m+gl*.45
    out=cv2.resize(np.clip(base,0,255).astype(np.uint8),(W,H),interpolation=cv2.INTER_AREA)
    return out
if __name__=='__main__':
    Image.fromarray(render()).save('still.png')
