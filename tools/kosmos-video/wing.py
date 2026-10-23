import cv2,numpy as np,json,os,shutil
from PIL import Image,ImageDraw,ImageFont
Q=json.load(open('quads.json'))
FB='/usr/share/fonts/opentype/inter/Inter-Black.otf'
def tex(word,ratio,fill=0.9,cap=0.82):
    TW=1200; TH=int(round(TW*ratio)); S=2
    img=Image.new('L',(TW*S,TH*S),0); d=ImageDraw.Draw(img)
    capH=cap*TH*S; size=int(capH/0.727)
    f=ImageFont.truetype(FB,size)
    ws=[f.getlength(c) for c in word]; nat=sum(ws)
    target=fill*TW*S
    if nat>target:
        size=int(size*target/nat); f=ImageFont.truetype(FB,size); ws=[f.getlength(c) for c in word]; nat=sum(ws); capH=size*0.727
    tr=max(0,(target-nat)/(len(word)-1)) if len(word)>1 else 0
    tr=min(tr,size*0.55)
    tot=nat+tr*(len(word)-1); x=(TW*S-tot)/2
    top=(TH*S-capH)/2
    asc=f.getbbox('H')[1]  # top of H
    for c,w in zip(word,ws):
        d.text((x,top-asc),c,font=f,fill=255); x+=w+tr
    img=img.resize((TW,TH),Image.LANCZOS)
    return np.asarray(img).astype(np.float32)/255,TW,TH
def apply(im,Qd,word):
    TL,TR,BR,BL=np.float32(Qd)
    L=np.linalg.norm(TR-TL); h=(np.linalg.norm(TL-BL)+np.linalg.norm(TR-BR))/2
    if L<20: return im
    up=((TL-BL)+(TR-BR))/2
    # erase old text: only text pixels
    ax=((TR-TL)+(BR-BL))/2*0.07
    ex=np.float32([TL+up*0.35-ax,TR+up*0.35+ax,BR-up*0.05+ax,BL-up*0.05-ax])
    m=np.zeros(im.shape[:2],np.uint8); cv2.fillPoly(m,[ex.astype(np.int32)],255)
    bg=cv2.medianBlur(im,31)
    g=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY).astype(np.int32); gb=cv2.cvtColor(bg,cv2.COLOR_BGR2GRAY).astype(np.int32)
    i32=im.astype(np.int32); red=((i32[...,2]-i32[...,0])>8)&((i32[...,2]-i32[...,1])>25)
    tm=((np.abs(g-gb)>9)&(m>0)&(~red)).astype(np.uint8)
    tm=cv2.dilate(tm,np.ones((5,5),np.uint8))&(m>0).astype(np.uint8)&(~red).astype(np.uint8)
    out=im.copy(); out[tm>0]=cv2.GaussianBlur(bg,(0,0),1.0)[tm>0]
    im=out
    # new text box: scale up in height about centre
    c=(TL+TR+BR+BL)/4
    k=1.45
    bt=lambda P:(c+(P-c)*np.float32([1.0,1])) 
    TL2=TL+up*0.15; TR2=TR+up*0.15; BL2=BL+up*0.15; BR2=BR+up*0.15
    mid=lambda a,b:(a+b)/2
    cT=mid(TL2,TR2);cB=mid(BL2,BR2)
    ctr_l=mid(TL2,BL2); ctr_r=mid(TR2,BR2)
    TL3=ctr_l+(TL2-ctr_l)*k; BL3=ctr_l+(BL2-ctr_l)*k; TR3=ctr_r+(TR2-ctr_r)*k; BR3=ctr_r+(BR2-ctr_r)*k
    h3=h*k
    t,TW,TH=tex(word,h3/L,fill=0.86,cap=0.84)
    Hm=cv2.getPerspectiveTransform(np.float32([[0,0],[TW,0],[TW,TH],[0,TH]]),np.float32([TL3,TR3,BR3,BL3]))
    a=cv2.warpPerspective(t,Hm,(im.shape[1],im.shape[0]),flags=cv2.INTER_AREA)
    a=cv2.GaussianBlur(a,(0,0),0.7)[...,None]
    white=np.float32([245,245,248])
    return np.clip(im*(1-a)+white*a,0,255).astype(np.uint8)
def edit(i,im):
    band=im[657:1260].copy()
    for n,word in (('L','QAYO'),('R','TEXNOLOGİYA')):
        q=Q[n].get(str(i))
        if q: band=apply(band,q,word)
    im=im.copy(); im[657:1260]=band; return im
if __name__=='__main__':
    os.makedirs('out2w',exist_ok=True)
    import sys
    fr=[int(x) for x in sys.argv[1:]] or range(1,274)
    for i in fr:
        f='out2/f_%04d.png'%i
        im=cv2.imread(f)
        if i<=110: im=edit(i,im)
        cv2.imwrite('out2w/f_%04d.png'%i,im)
