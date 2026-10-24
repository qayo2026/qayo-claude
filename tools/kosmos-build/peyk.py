import sys, os, json, cv2, numpy as np
sys.path.insert(0,'/home/claude/qayo-claude/tools/text-fx')
from text_fx import text_sprite, fit_text, ease_out, ease_io, WHITE, CYAN, RED, FONT_BOLD
Q=json.load(open('quads.json'))
os.makedirs('peyk',exist_ok=True)
LAST_WING=int(sys.argv[1]) if len(sys.argv)>1 else 128
TOT=int(sys.argv[2]) if len(sys.argv)>2 else 174
WINGS={'L':('QAYO',(930,300),0.80,0.62),'R':('TEXNOLOGİYA',(700,300),0.88,0.40)}

def hudmask(im, excl):
    hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV)
    h,s,v=[hsv[...,k].astype(int) for k in range(3)]
    strict=((h>=74)&(h<=96)&(s>=60)&(v>=45)).astype(np.uint8)*255
    # kosmos (qaranlıq) zonada sərbəst eşik: yarımşəffaf HUD ləkələri
    dark=(cv2.GaussianBlur(hsv[...,2],(0,0),25)<46).astype(np.uint8)
    dark=cv2.erode(dark,np.ones((15,15),np.uint8))
    loose=(((h>=72)&(h<=100)&(s>=34)&(v>=34)).astype(np.uint8)*255)*dark
    m=cv2.bitwise_or(strict,loose)
    # Yer üzərindəki HUD lövhələri (sabit zonalar): yarımşəffaf yaşıl-mavi
    bl=cv2.GaussianBlur(im,(0,0),2); hb=cv2.cvtColor(bl,cv2.COLOR_BGR2HSV)
    roi=np.zeros(im.shape[:2],np.uint8)
    for (x0,y0,x1,y1) in ((1020,35,1250,150),(870,580,1160,705),(1130,215,1250,505)):
        roi[y0:y1,x0:x1]=1
    tl=(((hb[...,0]>=74)&(hb[...,0]<=102)&(hb[...,1]>=22)&(hb[...,2]>=30)).astype(np.uint8)*255)*roi
    m=cv2.bitwise_or(m,tl)
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
    m=cv2.dilate(m,np.ones((7,7),np.uint8))
    teal_in=((h>=76)&(h<=92)&(s>=110)&(v>=100)).astype(np.uint8)*255
    teal_in=cv2.dilate(teal_in,np.ones((5,5),np.uint8))
    m[excl>0]=0
    m=cv2.bitwise_or(m,np.where(excl>0,teal_in,0).astype(np.uint8))
    return m

def texture(text,size,fitw,fith,nshow,line_t):
    Tw,Th=size
    f=fit_text(text,int(Tw*fitw),0.04)
    a,fw=text_sprite(text,f,0.04,FONT_BOLD,n=None)
    # height limit
    if a.shape[0]>Th*fith:
        f=int(f*Th*fith/a.shape[0]); a,fw=text_sprite(text,f,0.04,FONT_BOLD,n=None)
    sp,_=text_sprite(text,f,0.04,FONT_BOLD,n=max(nshow,0))
    tex=np.zeros((Th,Tw),np.float32)
    x0=int((Tw-a.shape[1])/2); y0=int(Th*0.42-a.shape[0]/2)
    h_,w_=sp.shape
    tex[y0:y0+h_, x0:x0+w_]=np.maximum(tex[y0:y0+h_, x0:x0+w_],sp[:Th-y0,:Tw-x0])
    line=np.zeros((Th,Tw),np.float32)
    if line_t>0:
        lx0=x0+int(a.shape[1]*0.02); lx1=lx0+int((a.shape[1]*0.96)*line_t)
        ly=int(Th*0.78); cv2.rectangle(line,(lx0,ly),(max(lx1,lx0+1),ly+int(Th*0.045)),1.0,-1)
        line=cv2.GaussianBlur(line,(0,0),1.2)
    return tex,line

def process(i):
    im=cv2.imread(f'A/a_{i:04d}.png')
    if i<=LAST_WING:
        qs={k:np.array(Q[k][i-1],np.float32) for k in Q}
        excl=np.zeros(im.shape[:2],np.uint8)
        for q in qs.values():
            cv2.fillConvexPoly(excl,q.astype(np.int32),255)
        excl=cv2.dilate(excl,np.ones((9,9),np.uint8))
        m=hudmask(im,excl)
        im=cv2.inpaint(im,m,5,cv2.INPAINT_TELEA)
        # remove Gemini wing text
        tm=np.zeros(im.shape[:2],np.uint8)
        for q in qs.values():
            pm=np.zeros(im.shape[:2],np.uint8); cv2.fillConvexPoly(pm,q.astype(np.int32),255)
            pm=cv2.erode(pm,np.ones((7,7),np.uint8))
            b,g,r=[im[...,c].astype(int) for c in range(3)]
            t=(((np.minimum(np.minimum(b,g),r)>135)|((r>140)&(g<110)&(b<130)))&(pm>0)).astype(np.uint8)*255
            tm|=t
        tm=cv2.dilate(tm,np.ones((7,7),np.uint8))
        im=cv2.inpaint(im,tm,4,cv2.INPAINT_TELEA)
        f=im.astype(np.float32)
        for k,(text,size,fitw,fith) in WINGS.items():
            Tw,Th=size
            n=int(len(text)*ease_io((i-6)/22.0)+0.999) if i>=6 else 0
            lt=ease_out((i-24)/18.0)
            tex,line=texture(text,size,fitw,fith,n,lt)
            src=np.float32([[0,0],[0,Th],[Tw,Th],[Tw,0]])
            M=cv2.getPerspectiveTransform(src,qs[k])
            wt=cv2.warpPerspective(tex,M,(1280,720)); wl=cv2.warpPerspective(line,M,(1280,720))
            gl=cv2.GaussianBlur(wt,(0,0),6)*0.6; gll=cv2.GaussianBlur(wl,(0,0),5)*1.0
            for c,v in enumerate((CYAN[2],CYAN[1],CYAN[0])):
                f[...,c]=f[...,c]*(1-np.clip(gl,0,1)*0.55)+v*np.clip(gl,0,1)*0.55
            for c,v in enumerate((RED[2],RED[1],RED[0])):
                f[...,c]=f[...,c]*(1-np.clip(gll,0,1)*0.6)+v*np.clip(gll,0,1)*0.6
            for c,v in enumerate((255,255,255)):
                f[...,c]=f[...,c]*(1-np.clip(wt,0,1))+v*np.clip(wt,0,1)
            for c,v in enumerate((RED[2],RED[1],RED[0])):
                f[...,c]=f[...,c]*(1-np.clip(wl,0,1))+v*np.clip(wl,0,1)
        im=np.clip(f,0,255).astype(np.uint8)
    cv2.imwrite(f'peyk/p_{i:04d}.png',im)

if __name__=='__main__':
    rng=range(1,TOT+1) if len(sys.argv)<4 else [int(x) for x in sys.argv[3].split(',')]
    for i in rng: process(i)
