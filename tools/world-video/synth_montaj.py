"""QAYO TEXNOLOGİYA montajı (15 s): A ofis (Gemini xam kadr) → B düz xəritə (kodla) → C qlobus (kodla).
Xəritə, qövslər, çiplər, logo, yazılar — hamısı kodla. İstifadə: python3 synth_montaj.py <çıxış_qovluğu> <ofis_kadrları_qovluğu> [kadr,...]"""
import sys, os, math
HERE=os.path.dirname(os.path.abspath(__file__)); OUTD=sys.argv[1]; OFD=sys.argv[2]; sys.argv=[sys.argv[0],OUTD]+sys.argv[3:]
sys.path.insert(0,HERE)
import synth_kod as K
from synth_kod import *
os.makedirs(OUTD,exist_ok=True)
DURM=15.0; BY=600
# ofis kadrları
OFF=[cv2.imread(os.path.join(OFD,f)) for f in sorted(os.listdir(OFD)) if f.endswith('.png')]
OH=OFF[0].shape[0]
vm=np.ones((OH,W),np.float32); fade=np.minimum(1,np.linspace(0,1,50)); vm[:50]*=fade[:,None]; vm[-50:]*=fade[::-1][:,None]; vm[:,:30]*=np.linspace(0,1,30)[None]; vm[:,-30:]*=np.linspace(1,0,30)[None]
def shotA_old(t):
    img=K.bg.copy(); a=ease_out(t/0.5); f=OFF[min(int(t*30),len(OFF)-1)].astype(np.float32)
    m=(vm*a)[...,None]; img[BY:BY+OH]=img[BY:BY+OH]*(1-m)+f*m; MCA_=[(110,700),(970,700),(110,1010),(970,1010)]; K.MC[:]=MCA_; K.TA=lambda k:0.5+0.35*k; K.draw_mods(img,t); return img

# --- V13: monitorun ekraninda QAYO halqa/hub sebekesi ---
CW,CH=880,540
SRC=np.float32([[0,0],[CW,0],[CW,CH],[0,CH]]); DST=np.float32([[150,48],[1022,30],[1010,566],[138,552]])
PM=cv2.getPerspectiveTransform(SRC,DST)
MAPC=cv2.resize(K.TEX,(CW,CH),interpolation=cv2.INTER_AREA); g_=cv2.cvtColor(MAPC.astype(np.uint8),cv2.COLOR_BGR2GRAY).astype(np.float32)
MAPC=(g_[...,None]*np.float32([1.0,0.82,0.45])*1.05)
dots=np.zeros((CH,CW),np.float32); dots[::6,::6]=1.0; MAPC=MAPC*(0.35+0.65*dots[...,None])
HUBC=(CW//2,CH//2+6); NODE=[(185,92),(695,92),(185,350),(695,350)]; NR=56
LOGOC=cv2.resize(K.LOGO[:,:,3],(150,int(K.LOGO.shape[0]*150/K.LOGO.shape[1])),interpolation=cv2.INTER_AREA).astype(np.float32)/255
LABC=[cv2.resize(l,(int(l.shape[1]*1.08),int(l.shape[0]*1.08)),interpolation=cv2.INTER_AREA) for l in K.mod_lab]
ew=np.ones((CH,CW),np.float32); ew[:,:30]*=np.linspace(0,1,30)[None]; ew[:,-30:]*=np.linspace(1,0,30)[None]; ew[:30]*=np.linspace(0,1,30)[:,None]; ew[-30:]*=np.linspace(1,0,30)[:,None]
def netcanvas(t):
    c=MAPC.copy(); lay=np.zeros((CH,CW),np.float32); P=np.float32(K.PRIM)
    ta=[0.9+0.45*k for k in range(4)]
    for k,(nx,ny) in enumerate(NODE):
        p=ease_out((t-ta[k]+0.3)/0.5)
        if p>0:
            e=(int(HUBC[0]+(nx-HUBC[0])*p),int(HUBC[1]+(ny-HUBC[1])*p)); cv2.line(lay,HUBC,e,1.0,3,cv2.LINE_AA)
            ph=(t*0.55+k*0.27)%1.0
            if p>=1: cv2.circle(lay,(int(HUBC[0]+(nx-HUBC[0])*ph),int(HUBC[1]+(ny-HUBC[1])*ph)),6,1.5,-1,cv2.LINE_AA)
    for a_,b_,j in [(0,1,0),(1,3,1),(3,2,2),(2,0,3)]:
        q=min(ease_out((t-ta[max(a_,b_)]-0.3)/0.6),1.0)
        if q>0:
            A=NODE[a_];B=NODE[b_]; cv2.line(lay,A,(int(A[0]+(B[0]-A[0])*q),int(A[1]+(B[1]-A[1])*q)),0.55,2,cv2.LINE_AA)
    for j in range(3):
        q=((t*0.5+j/3.0)%1.0); cv2.circle(lay,HUBC,int(60+90*q),float((1-q)*0.7),2,cv2.LINE_AA)
    bl=cv2.GaussianBlur(lay,(0,0),8); bs=cv2.GaussianBlur(lay,(0,0),2.5)
    c=np.clip(c+P*np.clip(bl*1.5+bs*0.9+lay*0.8,0,1.4)[...,None]*0.95+255*np.clip(lay-0.9,0,1)[...,None]*0.5,0,255)
    ph_=ease_out((t-0.25)/0.5)
    if ph_>0:
        hh=np.zeros((CH,CW),np.float32); cv2.circle(hh,HUBC,100,1.0,-1,cv2.LINE_AA); hh=cv2.GaussianBlur(hh,(0,0),22)*ph_*(0.8+0.2*math.sin(t*3))
        c=np.clip(c+P*hh[...,None]*0.9,0,255)
        cv2.circle(c,HUBC,int(100*ph_),(39,19,6),-1,cv2.LINE_AA); cv2.circle(c,HUBC,int(100*ph_),tuple(int(v) for v in P),3,cv2.LINE_AA)
        if ph_>0.6: blend(c,LOGOC,HUBC[0],HUBC[1],1.0,WHITE)
    for k,(nx,ny) in enumerate(NODE):
        o=ease_out((t-ta[k])/0.4)
        if o<=0: continue
        hh=np.zeros((CH,CW),np.float32); cv2.circle(hh,(nx,ny),NR+8,1.0,-1,cv2.LINE_AA); hh=cv2.GaussianBlur(hh,(0,0),14)*o*(0.75+0.25*math.sin((t-ta[k])*3))
        c=np.clip(c+P*hh[...,None]*0.9,0,255)
        r=int(NR*(0.6+0.4*o)); cv2.circle(c,(nx,ny),r,(39,19,6),-1,cv2.LINE_AA); cv2.circle(c,(nx,ny),r,tuple(int(v*o) for v in P),3,cv2.LINE_AA)
        tmp=np.zeros((150,150,3),np.uint8); K.icon(tmp,K.ICON[k],75,75,t-ta[k],1.0); tmp=cv2.resize(tmp,(116,116),interpolation=cv2.INTER_CUBIC).astype(np.float32)*o
        y0=ny-58;x0=nx-58; c[y0:y0+116,x0:x0+116]=np.maximum(c[y0:y0+116,x0:x0+116],tmp)
        l=LABC[k]; blit(c,l,nx-l.shape[1]//2,ny+NR+8,o)
    return c
ZM=1.3; H2=int(OH*ZM); Y2=BY+OH+40-H2; XC=(int(W*ZM)-W)//2
vm2=cv2.resize(vm,(W,H2)); 
def shotA(t):
    img=K.bg.copy(); a=ease_out(t/0.5); f=OFF[min(int(t*30),len(OFF)-1)].astype(np.float32); sa=ease_out((t-0.2)/0.6)
    c=netcanvas(t); wc=cv2.warpPerspective(c,PM,(W,OH)); wm=cv2.warpPerspective(ew*0.93*sa,PM,(W,OH))[...,None]
    r=f*(1-wm)+wc*wm; z=cv2.resize(r,(int(W*ZM),H2),interpolation=cv2.INTER_CUBIC)[:,XC:XC+W]
    m=(vm2*a)[...,None]; img[Y2:Y2+H2]=img[Y2:Y2+H2]*(1-m)+z*m
    return img
# düz xəritə
MW_,MH_,MY0=1080,540,633
MAP=cv2.resize(K.TEX,(MW_,MH_),interpolation=cv2.INTER_AREA)*np.float32([1.0,0.92,0.80])*0.80
mm=np.ones((MH_,MW_),np.float32); mm[:40]*=np.linspace(0,1,40)[:,None]; mm[-40:]*=np.linspace(1,0,40)[:,None]; mm[:,:25]*=np.linspace(0,1,25)[None]; mm[:,-25:]*=np.linspace(1,0,25)[None]
for gx_ in range(0,MW_,90): MAP[:,gx_]=np.clip(MAP[:,gx_]+np.float32([40,30,8]),0,255)
for gy_ in range(0,MH_,90): MAP[gy_,:]=np.clip(MAP[gy_,:]+np.float32([40,30,8]),0,255)
def mp(lon,lat): return (lon+180)/360*MW_, MY0+(90-lat)/180*MH_
B_ARC0,B_STEP,B_GROW=0.8,0.4,0.4; B_FIN=B_ARC0+8*B_STEP+B_GROW+0.15
def bez(a,b,n=40):
    d=math.hypot(b[0]-a[0],b[1]-a[1]); c=((a[0]+b[0])/2,(a[1]+b[1])/2-0.35*d); return [((1-u)**2*a[0]+2*u*(1-u)*c[0]+u*u*b[0],(1-u)**2*a[1]+2*u*(1-u)*c[1]+u*u*b[1]) for u in [i/n for i in range(n+1)]]
Y0L,HL=MY0-170,MH_+200
def draw_panel(img,po):
    if po>0: a=K.panel[:,:,3:4]/255*po; img[:]=img*(1-a)+K.panel[:,:,[2,1,0]]*a
def chip_pop(img,k,tk,t):
    u=(t-tk)/0.35
    if u<=0: return
    x,y=chip_pos(k); o=ease_out(u); fl=max(0.0,1-(t-tk-0.35)/0.6)*0.6; sc=K.chips[k].copy()
    if fl>0: sc[:,:,:3]=np.clip(sc[:,:,:3]+np.float32([20,70,95])*fl,0,255)
    blit(img,sc,x+int((1-o)*-40),y,o)
def shotB(t):
    tb=t-5.2; img=K.bg.copy(); a=ease_out(tb/0.5)
    m=(mm*a)[...,None]; img[MY0:MY0+MH_]=img[MY0:MY0+MH_]*(1-m)+MAP*m
    lay=np.zeros((HL,W),np.float32); head=np.zeros((HL,W),np.float32); hub=mp(*K.HUB)
    for k in range(1,len(COUNTRIES)):
        t0=B_ARC0+(k-1)*B_STEP; p=(tb-t0)/B_GROW
        if p<=0: continue
        pts=bez(hub,mp(COUNTRIES[k][3],COUNTRIES[k][4])); m_=max(1,int(len(pts)*min(1.0,ease_out(p))))
        age=tb-t0-B_GROW; f=1.0 if p<1 else (max(0.28,1-0.72*min(1.0,age/0.6)) if tb<B_FIN else 0.28+0.72*ease_out((tb-B_FIN)/0.6))
        for i in range(1,m_): cv2.line(lay,(int(pts[i-1][0]),int(pts[i-1][1]-Y0L)),(int(pts[i][0]),int(pts[i][1]-Y0L)),f,3,cv2.LINE_AA)
        e=(int(pts[min(m_,len(pts)-1)][0]),int(pts[min(m_,len(pts)-1)][1]-Y0L)); cv2.circle(head,e,7 if p>=1 else 5,1.0,-1,cv2.LINE_AA)
        if p>=1 and 0<age<1.2: cv2.circle(lay,e,int(8+30*ease_out(age/1.2)),float(1-age/1.2),2,cv2.LINE_AA)
        if tb>=B_FIN:
            ph=((tb-B_FIN)*0.7+k*0.173)%1.0; q=pts[int(ph*(len(pts)-1))]; cv2.circle(head,(int(q[0]),int(q[1]-Y0L)),5,1.0,-1,cv2.LINE_AA)
    c=(int(hub[0]),int(hub[1]-Y0L)); cv2.circle(head,c,9,1.0,-1,cv2.LINE_AA)
    for j in range(3):
        q=((tb*0.8+j/3.0)%1.0); cv2.circle(lay,c,int(10+70*q),float((1-q)*0.9),2,cv2.LINE_AA)
    bl=cv2.GaussianBlur(lay,(0,0),9); bs=cv2.GaussianBlur(lay,(0,0),3); hb=cv2.GaussianBlur(head,(0,0),8)
    al=np.clip(bl*1.6+bs*1.0+lay,0,1.4)[...,None]; reg=img[Y0L:Y0L+HL]; pr=np.float32(PRIM)
    reg[:]=np.clip(reg+pr*al*0.9+255*np.clip(lay*0.9+head+hb*0.6,0,1)[...,None]*0.7,0,255)
    draw_panel(img,ease_out((tb-0.3)/0.5))
    for k in range(len(COUNTRIES)): chip_pop(img,k,0.6 if k==0 else B_ARC0+(k-1)*B_STEP+B_GROW,tb)
    return img
def shotC(t):
    tl=4.2+(t-10.0)*1.9; K.TA=lambda k:1e9; img=K.bg.copy(); g=K.globe(tl); ox,oy=CX-S//2,CY-S//2
    reg=img[oy:oy+S,ox:ox+S]; reg[:]=reg+g; K.draw_arcs(reg,tl); draw_panel(img,1.0)
    for k in range(len(COUNTRIES)): x,y=chip_pos(k); blit(img,K.chips[k],x,y,1.0)
    return img
def lerp(a,b,w): return a*(1-w)+b*w
def compose_m(i):
    t=i/FPS
    if t<5.0: out=shotA(t)
    elif t<5.5: out=lerp(shotA(t),shotB(t),ease_io((t-5.0)/0.5))
    elif t<9.7: out=shotB(t)
    elif t<10.2: out=lerp(shotB(t),shotC(t),ease_io((t-9.7)/0.5))
    else: out=shotC(t)
    K.draw_head(out,t)
    out*=min(1.0,max(0.0,(DURM-t)/0.5))*ease_out(t/0.4)
    return np.clip(out,0,255).astype(np.uint8)
if __name__=='__main__':
    only=[int(x) for x in sys.argv[2].split(',')] if len(sys.argv)>2 else range(int(DURM*FPS))
    for i in only: cv2.imwrite('%s/f_%04d.png'%(OUTD,i),compose_m(i))
