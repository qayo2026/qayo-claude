import json,numpy as np,cv2
from PIL import Image,ImageDraw,ImageFont
W,H=1080,1920
FONT='/usr/share/fonts/opentype/inter/Inter-SemiBold.otf'
_fc={}
def font(sz):
    sz=max(7,int(round(sz*2))/2)
    if sz not in _fc: _fc[sz]=ImageFont.truetype(FONT,sz)
    return _fc[sz]
def sm(a,b,x):
    u=min(max((x-a)/(b-a),0),1); return u*u*(3-2*u)
J=json.load(open('trO.json')); T0=J['t0']; REF=J['ref']
def smoothed(arr,k=2):
    a=np.array([v[:4] for v in arr],np.float32); o=a.copy()
    for i in range(len(a)):
        lo,hi=max(0,i-k),min(len(a),i+k+1); o[i]=a[lo:hi].mean(0)
    return o
TAB={k:smoothed(v) for k,v in J['res'].items()}
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
    L=NODE[k]; sc=w/REF[k][2]
    im=Image.new('L',(X1-X0,Y1-Y0),0); d=ImageDraw.Draw(im)
    if k=='NC':
        s1=18*sc; s2=fit([L[1]],w+6,9.6*sc)
        d.text(((X1-X0)/2,(Y1-Y0)/2-s1*0.45),L[0],font=font(s1),fill=255,anchor='mm')
        d.text(((X1-X0)/2,(Y1-Y0)/2+s1*0.55),L[1],font=font(s2),fill=255,anchor='mm')
    else:
        sz=fit(L,(w+4),15.5*sc); f=font(sz)
        lh=sz*1.25; ty=(Y1-Y0)/2-lh*len(L)/2
        for i,l in enumerate(L):
            d.text(((X1-X0)/2,ty+lh*i+lh/2),l,font=f,fill=255,anchor='mm')
    t=(np.asarray(im).astype(np.float32)/255)[...,None]*a
    reg=reg*(1-t)+np.array([236,248,255],np.float32)*t
    fr[Y0:Y1,X0:X1]=np.clip(reg,0,255).astype(np.uint8)
def side(fr,k,r,a):
    x,y,w,h=[int(round(v)) for v in r[:4]]
    L=SIDE[k]; sc=w/REF[k][2]
    P=8
    sz=fit(L,w-2,(25 if k=='SR' else 22 if k in('SA','SB','SU') else 21)*sc); f=font(sz)
    tw=max(f.getlength(l) for l in L); lh=sz*1.32
    bw=int(tw+2*P+4); bh=int(lh*len(L)+2*P-2)
    bx=x-P+ (0 if k=='SA' else -2); by=int(y+h/2-bh/2)
    bx=min(bx,W-bw-4)
    im=Image.new('RGBA',(bw,bh),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.rounded_rectangle([0,0,bw-1,bh-1],radius=5,fill=(14,32,50,255),outline=(96,150,188,255),width=1)
    for i,l in enumerate(L):
        d.text((P+2,P-1+lh*i+lh/2),l,font=f,fill=(236,248,255,255),anchor='lm')
    arr=np.asarray(im).astype(np.float32)
    x0,y0=max(bx,0),max(by,0); x1,y1=min(bx+bw,W),min(by+bh,H)
    if x1<=x0: return
    sub=arr[y0-by:y1-by,x0-bx:x1-bx]; al=sub[...,3:4]/255*a
    reg=fr[y0:y1,x0:x1].astype(np.float32)
    fr[y0:y1,x0:x1]=(reg*(1-al)+sub[...,:3]*al).astype(np.uint8)
def title(fr,r,a):
    x,y,w,h=[int(round(v)) for v in r[:4]]
    P=9
    X0,Y0,X1,Y1=x-P,y-P,x+w+P,y+h+P
    reg=fr[Y0:Y1,X0:X1]
    bl=cv2.medianBlur(reg,41)
    bl=cv2.GaussianBlur(bl,(0,0),3)
    m=np.zeros((Y1-Y0,X1-X0),np.float32); m[4:-4,4:-4]=1; m=cv2.GaussianBlur(m,(0,0),2.5)[...,None]*a
    reg=reg.astype(np.float32)*(1-m)+bl.astype(np.float32)*m
    txt='QAYO TEXNOLOGİYA'
    sc=w/REF['TT'][2]
    sz=fit([txt],w-8,54*sc)
    f=font(sz)
    im=Image.new('L',(X1-X0,Y1-Y0),0); d=ImageDraw.Draw(im)
    d.text(((X1-X0)/2,(Y1-Y0)/2+3),txt,font=f,fill=255,anchor='mm',stroke_width=1,stroke_fill=255)
    t=(np.asarray(im).astype(np.float32)/255)[...,None]*a
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
