from PIL import Image, ImageDraw, ImageFilter
SS=8
def mark_mask():
    W,H=(520+30)*SS,(520+30)*SS
    off=15
    def P(pts): return [((x+off)*SS,(y+off)*SS) for x,y in pts]
    m=Image.new("L",(W,H),0);d=ImageDraw.Draw(m)
    cx,cy,R,r=308,299,204,122
    d.ellipse([(cx-R+off)*SS,(cy-R+off)*SS,(cx+R+off)*SS,(cy+R+off)*SS],fill=255)
    d.ellipse([(cx-r+off)*SS,(cy-r+off)*SS,(cx+r+off)*SS,(cy+r+off)*SS],fill=0)
    d.polygon(P([(217,393),(100,560),(100,640),(468,640),(293,324)]),fill=0)
    d.polygon(P([(315,288),(293,324),(393,505),(431,505),(437,497),(426,478),(426,469),(468,426),(440,400),(380,392)]),fill=255)
    d.polygon(P([(271,376),(201,503),(343,503)]),fill=255)
    m=m.filter(ImageFilter.GaussianBlur(3.2*SS))  # soften corners
    import numpy as np
    a=np.array(m).astype(float)/255;a=np.clip((a-0.5)*10+0.5,0,1)
    m=Image.fromarray((a*255).astype("uint8"))
    bbox=((104-6+off)*SS,(95-6+off)*SS,(512+7+off)*SS,(506+7+off)*SS)
    return m.crop(bbox)
RED=(200,38,45)
def icon(S,ratio,mark):
    T=S*4;mw,mh=mark.size;k=ratio*T/max(mw,mh)
    mm=mark.resize((int(mw*k),int(mh*k)),Image.LANCZOS)
    b=Image.new("RGB",(T,T),RED);b.paste((255,255,255),((T-mm.size[0])//2,(T-mm.size[1])//2),mm)
    return b.resize((S,S),Image.LANCZOS)
if __name__=="__main__":
    mk=mark_mask()
    i=icon(1024,0.58,mk);i.save("V-ikon-1024.png")
    for n,s in [("qayo-pwa-192.png",192),("qayo-pwa-512.png",512),("qayo-apple-touch-180.png",180)]: icon(s,0.58,mk).save("V-"+n)
    icon(512,0.42,mk).save("V-qayo-pwa-maskable-512.png")
    p=i.resize((400,400),Image.LANCZOS);k=Image.new("L",(400,400),0);ImageDraw.Draw(k).rounded_rectangle((0,0,399,399),90,fill=255)
    sh=Image.new("RGB",(460,460),(238,240,244));sh.paste(p,(30,30),k);sh.save("V-onizleme.png")
