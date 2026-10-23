import cv2,numpy as np,os
from PIL import Image,ImageDraw,ImageFont
W,H=1080,1920
TITLE='QAYO TEXNOLOGİYA'
BODY=['RƏQƏMSAL TEXNOLOGİYALARLA','BİZNES ƏLAQƏLƏRİNİZİ','GENİŞLƏNDİRİN']
fb=ImageFont.truetype('/usr/share/fonts/opentype/inter/Inter-Bold.otf',60*2)
fs=ImageFont.truetype('/usr/share/fonts/opentype/inter/Inter-SemiBold.otf',44*2)
PX,PW,BOT=100,880,1246
pad=30; lh=54
ph=pad+72+10+lh*len(BODY)+pad-6
py=BOT-ph
print('panel',PX,py,PW,ph,'widths',[fs.getlength(l)/2 for l in BODY],fb.getlength(TITLE)/2)
S=2
sp=Image.new('RGBA',(PW*S,ph*S),(0,0,0,0))
d=ImageDraw.Draw(sp)
d.rounded_rectangle([0,0,PW*S-1,ph*S-1],radius=28*S,fill=(10,21,48,240),outline=(47,123,255,255),width=3*S)
# left red bar clipped to panel shape
bar=Image.new('L',sp.size,0);ImageDraw.Draw(bar).rounded_rectangle([0,0,PW*S-1,ph*S-1],radius=28*S,fill=255)
barm=Image.new('L',sp.size,0);ImageDraw.Draw(barm).rectangle([0,0,14*S,ph*S],fill=255)
from PIL import ImageChops
m=ImageChops.multiply(bar,barm)
red=Image.new('RGBA',sp.size,(229,57,53,255));sp.paste(red,(0,0),m)
tx=14+pad
d.text((tx*S,(pad-6)*S),TITLE,font=fb,fill=(255,255,255,255))
for i,l in enumerate(BODY):
    d.text((tx*S,(pad+72+10+i*lh-6)*S),l,font=fs,fill=(255,255,255,255))
sp=sp.resize((PW,ph),Image.LANCZOS)
spa=np.asarray(sp).astype(np.float32)
sprite_rgb=spa[:,:,:3][:,:,::-1];sprite_a=spa[:,:,3:]/255.0
ease=lambda t:1-(1-min(max(t,0),1))**3
T_IN=5.9;N=273
os.makedirs('out2',exist_ok=True)
mask=np.zeros((H,W),np.uint8);mask[1066:1228,700:1080]=255
for i in range(1,N+1):
    t=(i-1)/30
    im=cv2.imread(f'src/s_{i:04d}.png')
    if t>=T_IN-0.2:
        im=cv2.inpaint(im,mask,5,cv2.INPAINT_TELEA)
    if False:
        p=ease((t-T_IN)/0.4);dy=int(round((1-p)*60));a=p
        y0=py+dy;h2=min(ph,H-y0)
        reg=im[y0:y0+h2,PX:PX+PW].astype(np.float32)
        sa=sprite_a[:h2]*a
        im[y0:y0+h2,PX:PX+PW]=np.clip(reg*(1-sa)+sprite_rgb[:h2]*sa,0,255).astype(np.uint8)
    cv2.imwrite(f'out2/f_{i:04d}.png',im)
print('done')
