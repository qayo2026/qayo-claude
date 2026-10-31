import json,numpy as np,cv2
from PIL import Image,ImageDraw,ImageFont
W,H=1080,1920
FONT='/usr/share/fonts/opentype/inter/Inter-SemiBold.otf'
_fc={}
def font(sz):
    sz=max(7,int(round(sz*2))/2)
    if sz not in _fc: _fc[sz]=ImageFont.truetype(FONT,sz)
    return _fc[sz]

SS=4
def ss_gray(w,h,fx,fy,draw):
    """draw(d,K,ox,oy): K=scale factor; returns float mask w*h in [0,1] placed with fractional offset (fx,fy)"""
    im=Image.new('L',(w*SS,h*SS),0); d=ImageDraw.Draw(im)
    draw(d,SS,int(round(fx*SS)),int(round(fy*SS)))
    a=np.asarray(im).astype(np.float32)/255
    return cv2.resize(a,(w,h),interpolation=cv2.INTER_AREA)
def sm(a,b,x):
    u=min(max((x-a)/(b-a),0),1); return u*u*(3-2*u)
J=json.load(open('trO.json')); T0=J['t0']; REF=J['ref']
def smoothed(arr,k=2):
    a=np.array([v[:4] for v in arr],np.float32); o=a.copy()
    for i in range(len(a)):
        lo,hi=max(0,i-k),min(len(a),i+k+1); o[i]=a[lo:hi].mean(0)
    return o
def polysm(arr,deg=4):
    a=np.array([v[:4] for v in arr],np.float64); n=len(a)
    # outlier clip with running median, then low-order polynomial over the whole scene
    from scipy.signal import medfilt
    b=np.stack([medfilt(a[:,j],9) for j in range(4)],1)
    bad=np.abs(a-b)>2.5; a=np.where(bad,b,a)
    t=np.linspace(-1,1,n); o=np.empty_like(a)
    for j in range(4): o[:,j]=np.polyval(np.polyfit(t,a[:,j],deg),t)
    return o.astype(np.float32)
TAB={k:polysm(v) for k,v in J['res'].items()}
MEDW={k:float(np.median(v[:,2])) for k,v in TAB.items()}
def shift(img,dx,dy):
    M=np.float32([[1,0,dx],[0,1,dy]])
    return cv2.warpAffine(img,M,(img.shape[1],img.shape[0]),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT,borderValue=0)
NODE={'N2':('MOBİL','TƏTBİQLƏR'),'N3':('AĞILLI','CİHAZ'),'N4':('İDARƏETMƏ','SİSTEMİ'),'NC':('QAYO','TEXNOLOGİYA'),'NV':('VEB','PLATFORMA')}
SIDE={'SR':('AĞILLI CİHAZ','SİSTEMLƏRİ'),'SA':('AVTOMATLAŞDIRMA VƏ','İDARƏETMƏ SİSTEMLƏRİ'),'SV':('VEB PLATFORMALAR',),'SM':('MOBİL TƏTBİQLƏR',),'SB':('BİZNES VƏ MÜŞTƏRİ','İDARƏETMƏSİ'),'SU':('MASAÜSTÜ PROQRAM','TƏMİNATI')}
TITLE=True
DELAY={'SV':0.0,'SM':0.1,'SR':0.2,'SA':0.3,'SB':0.4,'SU':0.5,'NV':0.6,'N2':0.7,'N3':0.8,'N4':0.9,'NC':1.0}
def fit(lines,maxw,maxsz):
    sz=maxsz
    while sz>7 and max(font(sz).getlength(l) for l in lines)>maxw: sz-=0.5
    return sz
def node(fr,k,r,a):
    x,y,w,h,_=r if len(r)==5 else (*r,1)
    x,y,w,h=int(round(r[0])),int(round(r[1])),int(round(r[2])),int(round(r[3]))
    P=5
    X0,Y0,X1,Y1=x-P,y-P,x+w+P,y+h+P
    if k=='NC': X0-=4; X1+=4; Y1+=11; Y0-=1
    ring=np.concatenate([fr[Y0-5:Y0,X0:X1].reshape(-1,3),fr[Y1:Y1+5,X0:X1].reshape(-1,3),fr[Y0:Y1,X0-5:X0].reshape(-1,3),fr[Y0:Y1,X1:X1+5].reshape(-1,3)])
    bg=np.median(ring,axis=0).astype(np.float32)
    reg=fr[Y0:Y1,X0:X1].astype(np.float32)
    m=np.zeros((Y1-Y0,X1-X0),np.float32); m[3:-3,3:-3]=1; m=cv2.GaussianBlur(m,(0,0),2.2)[...,None]*a
    reg=reg*(1-m)+bg*m
    L=NODE[k]; sc=MEDW[k]/REF[k][2]
    fx=r[0]-x; fy=r[1]-y
    bw_,bh_=X1-X0,Y1-Y0
    if k=='NC':
        s1=18*sc; s2=fit([L[1]],MEDW[k]+6,9.6*sc)
        def dr(d,K,ox,oy):
            d.text((bw_/2*K+ox,(bh_/2-s1*0.45)*K+oy),L[0],font=font(s1*K),fill=255,anchor='mm')
            d.text((bw_/2*K+ox,(bh_/2+s1*0.55)*K+oy),L[1],font=font(s2*K),fill=255,anchor='mm')
    else:
        sz=fit(L,(MEDW[k]+4),15.5*sc); lh=sz*1.25; ty=bh_/2-lh*len(L)/2
        def dr(d,K,ox,oy):
            for i,l in enumerate(L):
                d.text((bw_/2*K+ox,(ty+lh*i+lh/2)*K+oy),l,font=font(sz*K),fill=255,anchor='mm')
    t=ss_gray(bw_,bh_,fx,fy,dr)[...,None]*a
    reg=reg*(1-t)+np.array([236,248,255],np.float32)*t
    fr[Y0:Y1,X0:X1]=np.clip(reg,0,255).astype(np.uint8)
def side(fr,k,r,a):
    xf,yf,wf,hf=[float(v) for v in r[:4]]
    w=MEDW[k]
    L=SIDE[k]; sc=w/REF[k][2]
    P=8
    sz=fit(L,w-2,(25 if k=='SR' else 22 if k in('SA','SB','SU') else 21)*sc); f=font(sz)
    tw=max(f.getlength(l) for l in L); lh=sz*1.32
    bw=int(tw+2*P+4); bh=int(lh*len(L)+2*P-2)
    bxf=xf-P+ (0 if k=='SA' else -2); byf=yf+hf/2-bh/2
    bxf=min(bxf,W-bw-4)
    bx=int(np.floor(bxf)); by=int(np.floor(byf)); fx=bxf-bx; fy=byf-by
    def mk(fill):
        def dr(d,K,ox,oy):
            if fill=='box':
                d.rounded_rectangle([ox,oy,ox+bw*K-1,oy+bh*K-1],radius=5*K,fill=255)
            elif fill=='bord':
                d.rounded_rectangle([ox,oy,ox+bw*K-1,oy+bh*K-1],radius=5*K,outline=255,width=K)
            else:
                for i,l in enumerate(L):
                    d.text((ox+(P+2)*K,oy+(P-1+lh*i+lh/2)*K),l,font=font(sz*K),fill=255,anchor='lm')
        return dr
    PADN=2
    wB,hB=bw+2*PADN,bh+2*PADN
    def place(dr):
        def d2(d,K,ox,oy): dr(d,K,ox+PADN*K,oy+PADN*K)
        return ss_gray(wB,hB,fx,fy,d2)
    mbox=place(mk('box')); mbord=place(mk('bord')); mtxt=place(mk('txt'))
    rgb=np.zeros((hB,wB,3),np.float32); rgb[:]=(14,32,50)
    rgb=rgb*(1-mbord[...,None])+np.array((96,150,188),np.float32)*mbord[...,None]
    rgb=rgb*(1-mtxt[...,None])+np.array((236,248,255),np.float32)*mtxt[...,None]
    arr=np.dstack([rgb,np.clip(mbox+mbord,0,1)[...,None]*255])
    bx-=PADN; by-=PADN; bw,bh=wB,hB
    x0,y0=max(bx,0),max(by,0); x1,y1=min(bx+bw,W),min(by+bh,H)
    if x1<=x0: return
    sub=arr[y0-by:y1-by,x0-bx:x1-bx]; al=sub[...,3:4]/255*a
    reg=fr[y0:y1,x0:x1].astype(np.float32)
    fr[y0:y1,x0:x1]=(reg*(1-al)+sub[...,:3]*al).astype(np.uint8)
def title(fr,r,a):
    x,y,w,h=[int(round(v)) for v in r[:4]]
    fx=r[0]-x; fy=r[1]-y
    P=9
    X0,Y0,X1,Y1=x-P,y-P,x+w+P,y+h+P
    reg=fr[Y0:Y1,X0:X1]
    bl=cv2.medianBlur(reg,41)
    bl=cv2.GaussianBlur(bl,(0,0),3)
    m=np.zeros((Y1-Y0,X1-X0),np.float32); m[4:-4,4:-4]=1; m=cv2.GaussianBlur(m,(0,0),2.5)[...,None]*a
    reg=reg.astype(np.float32)*(1-m)+bl.astype(np.float32)*m
    txt='QAYO TEXNOLOGİYA'
    sc=MEDW['TT']/REF['TT'][2]
    sz=fit([txt],MEDW['TT']-8,54*sc)
    bw_,bh_=X1-X0,Y1-Y0
    def dr(d,K,ox,oy):
        d.text((bw_/2*K+ox,(bh_/2+3)*K+oy),txt,font=font(sz*K),fill=255,anchor='mm',stroke_width=K,stroke_fill=255)
    t=ss_gray(bw_,bh_,fx,fy,dr)[...,None]*a
    reg=reg*(1-t)+np.array([10,24,44],np.float32)*t
    fr[Y0:Y1,X0:X1]=np.clip(reg,0,255).astype(np.uint8)
def apply(fr,f):
    t=f/30
    if t<37.05: return fr
    a=sm(37.08,37.32,t)
    i=f-int(round(T0*30))
    if a<=0.01 or i<0: return fr
    if i<len(TAB['TT']): title(fr,TAB['TT'][i],a)
    for k in NODE:
        ak=a*sm(37.25+DELAY[k]*0.5,37.5+DELAY[k]*0.5,t)
        if i<len(TAB[k]) and ak>0.01: node(fr,k,TAB[k][i],ak)
    for k in SIDE:
        ak=a*sm(37.25+DELAY[k]*0.5,37.5+DELAY[k]*0.5,t)
        if i<len(TAB[k]) and ak>0.01: side(fr,k,TAB[k][i],ak)
    return fr
if __name__=='__main__':
    import sys,subprocess
    out=[]
    for t in [37.3,38.0,39.4]:
        subprocess.run(['ffmpeg','-y','-loglevel','error','-ss',str(t),'-i','ext93.mp4','-frames:v','1','/tmp/_o.png'],check=True)
        fr=np.array(Image.open('/tmp/_o.png').convert('RGB')); fr=apply(fr,int(round(t*30)))
        out.append(fr[560:1000])
    Image.fromarray(np.vstack(out)).save('cmp/off_test.png')
