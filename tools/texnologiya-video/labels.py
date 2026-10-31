import json,numpy as np,cv2,math
from PIL import Image,ImageDraw,ImageFont
FONT='/usr/share/fonts/opentype/inter/Inter-SemiBold.otf'
W,H=1080,1920
def sm(a,b,x):
    u=min(max((x-a)/(b-a),0),1); return u*u*(3-2*u)
# ---------- flags (RGBA, drawn at 6x then downscaled) ----------
def star(d,cx,cy,r,fill,pts=5,inner=0.382,rot=-90):
    P=[]
    for i in range(pts*2):
        rr=r if i%2==0 else r*inner
        a=math.radians(rot+i*180/pts); P.append((cx+rr*math.cos(a),cy+rr*math.sin(a)))
    d.polygon(P,fill=fill)
def flag(code,fw,fh):
    S=6; w,h=fw*S,fh*S; im=Image.new('RGB',(w,h),(255,255,255)); d=ImageDraw.Draw(im)
    if code=='DE':
        for i,c in enumerate([(0,0,0),(221,0,0),(255,206,0)]): d.rectangle([0,i*h/3,w,(i+1)*h/3],fill=c)
    elif code=='FR':
        for i,c in enumerate([(0,85,164),(255,255,255),(239,65,53)]): d.rectangle([i*w/3,0,(i+1)*w/3,h],fill=c)
    elif code=='RU':
        for i,c in enumerate([(255,255,255),(0,57,166),(213,43,30)]): d.rectangle([0,i*h/3,w,(i+1)*h/3],fill=c)
    elif code=='NG':
        for i,c in enumerate([(0,135,81),(255,255,255),(0,135,81)]): d.rectangle([i*w/3,0,(i+1)*w/3,h],fill=c)
    elif code=='US':
        for i in range(13): d.rectangle([0,i*h/13,w,(i+1)*h/13],fill=(178,34,52) if i%2==0 else (255,255,255))
        d.rectangle([0,0,w*0.42,h*7/13],fill=(60,59,110))
        for r in range(4):
            for c in range(5):
                cx=w*0.42*(c+0.7)/5.4+w*0.0; cy=h*7/13*(r+0.7)/4.4
                d.ellipse([cx-S*0.7,cy-S*0.7,cx+S*0.7,cy+S*0.7],fill=(255,255,255))
    elif code=='BR':
        d.rectangle([0,0,w,h],fill=(0,155,58)); d.polygon([(w*0.5,h*0.1),(w*0.92,h*0.5),(w*0.5,h*0.9),(w*0.08,h*0.5)],fill=(254,223,0))
        d.ellipse([w*0.5-h*0.27,h*0.5-h*0.27,w*0.5+h*0.27,h*0.5+h*0.27],fill=(0,39,118))
    elif code=='AZ':
        for i,c in enumerate([(0,181,226),(239,51,64),(80,158,47)]): d.rectangle([0,i*h/3,w,(i+1)*h/3],fill=c)
        cx,cy=w*0.47,h*0.5; r=h*0.17
        d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=(255,255,255)); r2=r*0.8; d.ellipse([cx-r2+r*0.35,cy-r2,cx+r2+r*0.35,cy+r2],fill=(239,51,64))
        star(d,w*0.57,cy,h*0.11,(255,255,255),pts=8,inner=0.5,rot=-90)
    im=im.resize((fw,fh),Image.LANCZOS)
    return im
# ---------- label renderer ----------
_fc={}
def font(sz):
    sz=max(7,int(round(sz)))
    if sz not in _fc: _fc[sz]=ImageFont.truetype(FONT,sz)
    return _fc[sz]
def render(text,code,bw,bh,min_w=0,stacked=False,hi=False):
    """returns RGBA image of box (bw x bh)"""
    ts=bh*(0.46 if not hi else 0.44)
    if stacked: ts=bh*0.26
    f=font(ts); tw=f.getlength(text)
    fh=int(round(bh*(0.5 if not stacked else 0.38))); fw=int(round(fh*1.5))
    pad=max(5,int(bh*0.22))
    need=pad+fw+int(bh*0.2)+int(tw)+pad if not stacked else int(max(tw,fw))+2*pad
    bw=max(bw,need)
    im=Image.new('RGBA',(bw,bh),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.rounded_rectangle([0,0,bw-1,bh-1],radius=3,fill=(14,32,50,255),outline=(96,150,188,255),width=1)
    if hi: d.rounded_rectangle([1,1,bw-2,bh-2],radius=3,outline=(60,200,255,255),width=1)
    fl=flag(code,fw,fh)
    if not stacked:
        cy=bh*(0.57 if hi else 0.5); fy=int(cy-fh/2); im.paste(fl,(pad,fy)); 
        d.text((pad+fw+int(bh*0.2),cy),text,font=f,fill=(238,246,255,255),anchor='lm')
    else:
        d.text((bw/2,bh*0.30),text,font=f,fill=(238,246,255,255),anchor='mm')
        im.paste(fl,((bw-fw)//2,int(bh*0.55)))
    return im
