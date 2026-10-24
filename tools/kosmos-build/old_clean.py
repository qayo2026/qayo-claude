"""Orijinal 12 san KOSMOS üçün kosmetik təmizlik (səs, kadr sırası, rəng toxunulmaz):
1) xəritə kadrlarında sağ-aşağı Gemini iz ləkəsini doldurur; 2) peyk qanadlarına yumşaq işıq (açma).
İstifadə: python3 old_clean.py <orijinal.mp4> <çıxış.mp4> [--test f1,f2,...]"""
import sys, os, subprocess, json, cv2, numpy as np, tempfile, shutil
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE); sys.path.insert(0,os.path.join(HERE,'..','az-map')); sys.path.insert(0,os.path.join(HERE,'..','text-fx'))
import oldfit as OF, mapscene as MS
from text_fx import text_sprite, blend, glow, ease_io, WHITE, CYAN, FONT_BOLD
KEYS=json.load(open(os.path.join(HERE,'old-keys.json')))
NAMES=['Bakı','Şəki','Gəncə','Naxçıvan','Lənkəran','Xaçmaz']
LAB_A,LAB_B=225,280
AMBER=(255,196,107)   # 'sərhəd qonşuları' kateqoriyasının ayrıca rəngi (#FFC46B); şəhər/rayon adları ağ-mavi qalır
NEI=[('Rusiya',47.3,42.0),('Gürcüstan',44.6,41.7),('Ermənistan',44.95,40.15),('İran',47.3,38.3),('Xəzər dənizi',50.45,40.9)]
SRC,OUT=sys.argv[1],sys.argv[2]
SM_A,SM_B=175,284           # ləkə kadrları (1-əsaslı)
KEY=[(1,210,920),(30,230,930),(60,240,920),(90,230,760),(108,230,700)]
def wing_params(i):
    xs=[k[0] for k in KEY]; cx=np.interp(i,xs,[k[1] for k in KEY]); cy=np.interp(i,xs,[k[2] for k in KEY])
    amt=1.0 if i<=95 else max(0.0,1-(i-95)/15.0)
    return cx,cy,amt
_yy,_xx=None,None
def wing_lift(img,i):
    """Qanad panellərinə işıq: rəng maskası (bənövşəyi-mavi panel) + hərəkətli parıltı zolağı + yumşaq xarici işıq."""
    cx,cy,amt=wing_params(i)
    if amt<=0: return img
    global _yy,_xx
    if _yy is None: _yy,_xx=np.mgrid[0:1920,0:1080].astype(np.float32)
    d=np.sqrt(((_xx-cx)/340.0)**2+((_yy-cy)/310.0)**2)
    roi=np.clip(1.15-d,0,1)
    hsv=cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
    Hh,Ss,Vv=hsv[...,0],hsv[...,1],hsv[...,2]
    m=((Hh>=108)&(Hh<=135)&(Ss>45)&(Vv>70)).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((9,9),np.uint8))
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
    M=cv2.GaussianBlur(m.astype(np.float32),(0,0),1.6)*(roi>0.05)*np.clip(roi*1.6,0,1)
    f=img.astype(np.float32)
    pulse=0.5+0.5*np.sin(i*0.22)
    # hərəkətli parıltı zolağı (diaqonal)
    t=(_xx*0.6-_yy*0.8)
    band=np.exp(-((t-(-150+ (i%120)*8.0))/55.0)**2)
    light=np.array((255,238,205),np.float32)      # BGR: soyuq ağ-mavi
    lift=(0.13+0.07*pulse+0.38*band)[...,None]
    out=f+M[...,None]*lift*light*0.55*amt
    out=f*(1-M[...,None]*0.0)+(out-f)+ (f*M[...,None]*0.10*amt)   # panel parlaqlığı
    glow=cv2.GaussianBlur(M,(0,0),16)[...,None]*np.array((255,215,120),np.float32)*(0.22+0.10*pulse)*amt
    return np.clip(out+glow,0,255).astype(np.uint8)
def _ss(t): t=np.clip(t,0,1); return t*t*(3-2*t)
_fade=None
def smear_fix(img):
    """Sağ-aşağı Gemini izini tünd fona (#000818) yumşaq söndürür; kənar diaqonal və hamar."""
    global _fade
    H,W=img.shape[:2]
    if _fade is None:
        yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
        _fade=(_ss((xx-540)/280.0)*_ss((yy-950)/230.0))[...,None]
    g=np.array((24,8,0),np.float32)
    return np.clip(img.astype(np.float32)*(1-_fade)+g*_fade,0,255).astype(np.uint8)
def pill_text(img,i):
    """Gemini-nin bulanıq lövhə yazısını silir, yerinə kəskin text-fx 'QAYO TEXNOLOGİYA' yazır."""
    if not (222<=i<=281): return img
    w=OF.warp_for(KEYS,i); s=float(w[0,0]); hx,hy=OF.apply(w,MS.HUB)
    pw=335*s; ph=84*s; cx=hx-41*s; cy=hy-35*s
    x0,x1,y0,y1=int(cx-pw/2+ph*0.25),int(cx+pw/2+ph*0.02),int(cy-ph*0.32),int(cy+ph*0.32)
    reg=img[y0:y1,x0:x1]
    g=cv2.cvtColor(reg,cv2.COLOR_BGR2GRAY).astype(np.float32); bg=cv2.GaussianBlur(g,(0,0),9)
    tm=((g>bg+14)|(g>205)).astype(np.uint8)*255; tm=cv2.dilate(tm,np.ones((5,5),np.uint8))
    full=img.copy(); full[y0:y1,x0:x1]=cv2.inpaint(reg,tm,5,cv2.INPAINT_TELEA)
    f=full.astype(np.float32)
    nn=17; tf=text_sprite('QAYO TEXNOLOGİYA',40,0.10,FONT_BOLD,n=nn)[0]
    sc=(pw*0.80)/tf.shape[1]
    sp=cv2.resize(tf,None,fx=sc,fy=sc,interpolation=cv2.INTER_AREA) if tf.ndim==2 else cv2.resize(tf,None,fx=sc,fy=sc,interpolation=cv2.INTER_AREA)
    a=min(1.0,(i-222)/6.0)*(1.0 if i<277 else max(0.0,(281-i)/4.0))
    glow(f,sp,cx,cy,a,CYAN,sigma=6,strength=0.6); blend(f,sp,cx,cy,a,WHITE)
    out=np.clip(f,0,255)
    # keçid: 222-227 aralığında köhnə mətnlə qarışıq
    k=min(1.0,(i-222)/6.0)
    return np.clip(img.astype(np.float32)*(1-k)+out*k,0,255).astype(np.uint8) if False else out.astype(np.uint8)
def labels(img,i):
    if not (LAB_A<=i<=LAB_B): return img
    w=OF.warp_for(KEYS,i); f=img.astype(np.float32)
    for k,c in enumerate(c for n in NAMES for c in MS.CITIES if c['name']==n):
        t0=LAB_A+2+k*2; p=ease_io((i-t0)/14.0)
        if p<=0: continue
        fade=1.0 if i<LAB_B-4 else max(0.0,(LAB_B-i)/4.0)
        nn=len(c['name']); n=min(nn,int(nn*p+0.999))
        if c['name']=='Lənkəran': c=dict(c,side='l',dx=16,dy=4)
        if c['name']=='Gəncə': c=dict(c,side='l',dx=30,dy=14)
        sp=text_sprite(c['name'],30,0.04,FONT_BOLD,n=n)[0]; full=text_sprite(c['name'],30,0.04,FONT_BOLD,n=nn)[0]
        px,py=OF.apply(w,c['p']); y=py+c['dy']
        if c['side']=='r': x0=px+c['dx']
        elif c['side']=='l': x0=px-c['dx']-full.shape[1]
        else: x0=px-full.shape[1]/2
        cx=x0+sp.shape[1]/2
        glow(f,sp,cx,y,fade,CYAN,sigma=5,strength=0.7); blend(f,sp,cx,y,fade,WHITE)
    for k,(nm,lon,lat) in enumerate(NEI):
        t0=LAB_A+2+(len(NAMES)+k)*2; p=ease_io((i-t0)/14.0)
        if p<=0: continue
        fade=(1.0 if i<LAB_B-4 else max(0.0,(LAB_B-i)/4.0))*0.92
        nn=len(nm); n=min(nn,int(nn*p+0.999))
        sp=text_sprite(nm,25,0.07,FONT_BOLD,n=n)[0]; full=text_sprite(nm,25,0.07,FONT_BOLD,n=nn)[0]
        px,py=OF.apply(w,MS.proj(lon,lat)); cx=px-full.shape[1]/2+sp.shape[1]/2
        glow(f,sp,cx,py,fade,AMBER,sigma=5,strength=0.55); blend(f,sp,cx,py,fade,AMBER)
    return np.clip(f,0,255).astype(np.uint8)
SC_A,SC_B=190,300
WIN_Y0,WIN_Y1=506,1410
_scene=None
def scene_frame(img,i):
    """Azərbaycan parlayır hissəsi: referans stilində kodla xəritə (oldmap_scene). Qanad/şüa/səs/loqo toxunulmazdır."""
    global _scene
    if _scene is None:
        import oldmap_scene as _o; _scene=_o
    t=i-SC_A
    ours=_scene.render(t) if t<100 else _scene.render(99)
    old=img[WIN_Y0:WIN_Y1].astype(np.float32)
    g=np.array((24,8,0),np.float32)
    if i<=SC_A+6:
        w=(i-SC_A+1)/7.0; win=old*(1-w)+ours*w
    elif i<276:
        win=ours
    else:
        d=float(np.clip(1-(i-277)/8.0,0,1))
        base=ours*d+g*(1-d)
        bl=float(np.clip((i-281)/10.0,0,1)); bl=bl*bl*(3-2*bl)
        win=base*(1-bl)+old*bl
    out=img.astype(np.float32); out[WIN_Y0:WIN_Y1]=win
    return np.clip(out,0,255).astype(np.uint8)
_DL=None
def _dist_layer():
    global _DL
    if _DL is None:
        ln=np.zeros((1920,1080),np.uint8); fill=np.zeros((1920,1080),np.uint8)
        for ft in MS.AZ:
            MS.draw_geom(ln,ft['geometry'],line=255,lw=1); MS.draw_geom(fill,ft['geometry'],fill=255)
        _DL=(ln,fill)
    return _DL
def districts(img,i):
    """Rayon xətləri: köhnə xəritənin üstünə, ölkə daxilində, solğun."""
    if not (LAB_A-4<=i<=LAB_B): return img
    p=_ss((i-(LAB_A-4))/14.0)*(1.0 if i<LAB_B-4 else max(0.0,(LAB_B-i)/4.0))
    if p<=0: return img
    w=OF.warp_for(KEYS,i); ln,fill=_dist_layer()
    L=cv2.warpAffine(ln,w,(1080,1920)).astype(np.float32)/255
    F=cv2.warpAffine(fill,w,(1080,1920)); F=cv2.erode(F,np.ones((3,3),np.uint8),iterations=7).astype(np.float32)/255
    m=cv2.GaussianBlur(F,(0,0),3)*np.clip(L*1.6,0,1)*0.55*p
    f=img.astype(np.float32); col=np.array(CYAN[::-1],np.float32)
    f=f*(1-m[...,None])+col*m[...,None]
    return np.clip(f,0,255).astype(np.uint8)
def proc(img,i):
    img=wing_lift(img,i)
    if SM_A<=i<=SM_B: img=smear_fix(img)
    img=pill_text(img,i)
    img=districts(img,i)
    return labels(img,i)
if __name__=='__main__':
    tmp=tempfile.mkdtemp(); subprocess.run(['ffmpeg','-v','error','-i',SRC,'-vf','fps=30',f'{tmp}/f_%04d.png'],check=True)
    n=len(os.listdir(tmp))
    if len(sys.argv)>3 and sys.argv[3]=='--test':
        os.makedirs(OUT,exist_ok=True)
        for i in [int(x) for x in sys.argv[4].split(',')]: cv2.imwrite(f'{OUT}/c_{i:04d}.png',proc(cv2.imread(f'{tmp}/f_{i:04d}.png'),i))
    else:
        HOLD_AT,HOLD_N=276,27      # xəritə tam açılandan sonra ~2 san nəfəs (kadr 276-da, çox yavaş sürüşmə)
        # Səs: heç bir iki musiqi anı üst-üstə qarışdırılmır. Söz bitəndən (9.45) logo zərbəsinə (10.75) qədər
        # musiqi parçası tembri/ucalığı pozmadan YAVAŞ uzadılır (atempo) — calaq, qarışma, təkrar yoxdur.
        T0,T1=9.45,10.75; E=HOLD_N/30.0; XF=0.02; tempo=(T1-T0)/(T1-T0+E+2*XF)
        aud=(f"[1:a]asplit=3[a0][a1][a2];[a0]atrim=0:{T0},asetpts=PTS-STARTPTS[x0];"
             f"[a1]atrim={T0}:{T1},asetpts=PTS-STARTPTS,rubberband=tempo={tempo:.5f}:pitch=1:transients=smooth:detector=soft:window=long[m];[a2]atrim={T1},asetpts=PTS-STARTPTS[x2];"
             f"[x0][m]acrossfade=d={XF}[p];[p][x2]acrossfade=d={XF}[aout]")
        cmd=['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s','1080x1920','-r','30','-i','-','-i',os.environ.get('KOSMOS_AUDIO',SRC),
             '-filter_complex',aud,'-map','0:v','-map','[aout]','-c:v','libx264','-preset','slow','-crf','17','-pix_fmt','yuv420p','-r','30','-c:a','aac','-b:a','192k','-shortest','-movflags','+faststart',OUT]
        p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
        cache={}
        def P(i):
            if i not in cache:
                cache[i]=proc(cv2.imread(f'{tmp}/f_{i:04d}.png'),i).astype(np.float32)
                while len(cache)>8: cache.pop(next(iter(cache)))
            return cache[i]
        for k in range(1,n+HOLD_N+1):
            S0=HOLD_AT-6
            if k<=S0: fr=P(k)
            elif k<=HOLD_AT+HOLD_N:       # 270→276 çox yavaş sürüşmə (geri tullanma yox)
                u=(k-S0)/(HOLD_N+6); src=S0+6*ease_io(u); lo=int(src); fr_=src-lo
                fr=P(lo)*(1-fr_)+P(min(lo+1,HOLD_AT))*fr_ if lo<HOLD_AT else P(HOLD_AT)
            else: fr=P(k-HOLD_N)
            p.stdin.write(np.clip(fr,0,255).astype(np.uint8).tobytes())
        p.stdin.close(); p.wait(); print('hazır',OUT)
    shutil.rmtree(tmp)
