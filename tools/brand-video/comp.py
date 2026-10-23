import cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont
src=cv2.imread('/mnt/user-data/attachments/a6aa69b0-1996-5cb8-8d20-d22e27e0cece/81a171c8-image.jpg')
FD='/usr/share/fonts/opentype/inter/Inter-%s.otf'
S=2
mk=np.zeros(src.shape[:2],np.uint8); mk[6:32,930:1130]=255; src=cv2.inpaint(src,mk,5,cv2.INPAINT_TELEA)
big=cv2.resize(src,None,fx=S,fy=S,interpolation=cv2.INTER_CUBIC)   # work at 2x original
H0,W0=src.shape[:2]
pil=Image.fromarray(cv2.cvtColor(big,cv2.COLOR_BGR2RGB)); d=ImageDraw.Draw(pil)
def tc(cx,cy,t,f,fill,tr=0):
    w=sum(d.textlength(c,font=f) for c in t)+tr*S*(len(t)-1); x=cx*S-w/2
    for c in t: d.text((x,cy*S),c,font=f,fill=fill,anchor='lm'); x+=d.textlength(c,font=f)+tr*S
pills={'mobile':((495,125,685,178),['MOBİL','TƏTBİQLƏR']),'web':((115,287,322,358),['WEB','PLATFORMALAR']),
 'desk':((858,287,1068,358),['KOMPYUTER','PROQRAMLARI']),'iot':((78,727,308,800),['AĞILLI CİHAZ','SİSTEMLƏRİ']),
 'api':((880,727,1105,800),['SERVER VƏ API','SİSTEMLƏRİ']),'ai':((467,877,713,943),['AVTOMATLAŞDIRMA'])}
bg=(4,17,40)
for k,((x0,y0,x1,y1),L) in pills.items():
    d.rectangle([(x0+14)*S,(y0+9)*S,(x1-14)*S,(y1-9)*S],fill=bg)
    f=ImageFont.truetype(FD%'Bold',int((21 if len(L)==2 else 19)*S)); cx=(x0+x1)/2; cy=(y0+y1)/2
    if len(L)==2:
        tc(cx,cy-13,L[0],f,(255,255,255),.8); tc(cx,cy+13,L[1],f,(255,255,255),.8)
    else: tc(cx,cy,L[0],f,(255,255,255),.8)
arr=cv2.cvtColor(np.array(pil),cv2.COLOR_RGB2BGR)
# center: replace AUTOMATION COMPANY
x0,y0,x1,y1=420*S,590*S,760*S,626*S
roi=arr[y0:y1,x0:x1]; g=cv2.cvtColor(roi,cv2.COLOR_BGR2GRAY)
m=((g>110)).astype(np.uint8)*255; m=cv2.dilate(m,np.ones((9,9),np.uint8))
arr[y0:y1,x0:x1]=cv2.inpaint(roi,m,6,cv2.INPAINT_TELEA)
pil=Image.fromarray(cv2.cvtColor(arr,cv2.COLOR_BGR2RGB)); d=ImageDraw.Draw(pil)
L=Image.new('RGBA',pil.size,(0,0,0,0)); dl=ImageDraw.Draw(L); d=dl
tc(590,608,'TEXNOLOGİYA',ImageFont.truetype(FD%'Bold',int(26*S)),(255,255,255,255),4)
la=np.array(L).astype(np.float32); m=la[...,3:4]/255.
base=cv2.cvtColor(np.array(pil.convert('RGB')),cv2.COLOR_RGB2BGR).astype(np.float32)
gl=cv2.GaussianBlur(la[...,2::-1]*m,(0,0),7*S)
txt=la[...,[2,1,0]]
base=base*(1-m)+txt*m+gl*.6
base=np.clip(base,0,255).astype(np.uint8)
# portrait canvas 1080x1920
sc=1080/ (W0*S)
img=cv2.resize(base,(1080,int(H0*S*sc)),interpolation=cv2.INTER_AREA)
h=img.shape[0]; y0=(1920-h)//2
canvas=np.zeros((1920,1080,3),np.float32)
rowt=cv2.GaussianBlur(img[:12].mean(0,keepdims=True),(0,0),60).mean(1,keepdims=True)*0+np.median(img[:8].reshape(-1,3),0)
rowb=np.median(img[-8:].reshape(-1,3),0)
for y in range(y0):
    canvas[y]=rowt*(0.6+0.4*y/y0)
for y in range(1920-y0-h):
    canvas[y0+h+y]=rowb*(1-0.4*y/max(1,(1920-y0-h)))
ramp=np.ones((h,1,1),np.float32); n=26
r=np.linspace(0,1,n)**1.5; ramp[:n,0,0]=r; ramp[-n:,0,0]=r[::-1]
bgc=canvas[y0:y0+h].copy(); bgc[:]=np.where(np.arange(h)[:,None,None]<h//2,rowt,rowb)
canvas[y0:y0+h]=img*ramp+bgc*(1-ramp)
cv2.imwrite('orig_still.png',np.clip(canvas,0,255).astype(np.uint8))
print(y0,h)
