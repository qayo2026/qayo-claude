import sys,subprocess,numpy as np
from PIL import Image,ImageDraw
t=float(sys.argv[1]); y0=int(sys.argv[2]); y1=int(sys.argv[3]); x0=int(sys.argv[4]); x1=int(sys.argv[5]); out=sys.argv[6]
src=sys.argv[7] if len(sys.argv)>7 else 'ext93.mp4'
subprocess.run(['ffmpeg','-y','-loglevel','error','-ss',str(t),'-i',src,'-frames:v','1','/tmp/_g.png'],check=True)
im=Image.open('/tmp/_g.png').convert('RGB').crop((x0,y0,x1,y1)); d=ImageDraw.Draw(im)
for x in range((x0//50+1)*50,x1,50):
    d.line([(x-x0,0),(x-x0,y1-y0)],fill=(255,255,0) if x%100==0 else (90,90,0),width=1)
    if x%100==0: d.text((x-x0+2,2),str(x),fill=(255,255,0))
for y in range((y0//50+1)*50,y1,50):
    d.line([(0,y-y0),(x1-x0,y-y0)],fill=(0,255,255) if y%100==0 else (0,90,90),width=1)
    if y%100==0: d.text((2,y-y0+2),str(y),fill=(0,255,255))
im.save(out)
