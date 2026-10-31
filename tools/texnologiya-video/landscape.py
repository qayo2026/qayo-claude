# 16:9 (1920x1080) eksport: görüntü zolağı kəsilmədən, yazılar şəklin üstünə qaldırılır.
# python3 -u landscape.py MASTER_V9.21.mp4 out.mp4 [frame_index_for_test]
import sys, subprocess, numpy as np, cv2, fill
from scipy.signal import medfilt
src,dst=sys.argv[1],sys.argv[2]; test=[int(x) for x in sys.argv[3:]]
W,H=1080,1920; sz=W*H*3; OW,OH=1920,1080
def rd(p): return subprocess.Popen(["ffmpeg","-v","error","-i",p,"-f","rawvideo","-pix_fmt","rgb24","-"],stdout=subprocess.PIPE)
r=rd(src); B=[]
while True:
    b=r.stdout.read(sz)
    if len(b)<sz: break
    q=fill.band_rows(np.frombuffer(b,np.uint8).reshape(H,W,3)); B.append(q if q else (None,None))
r.wait(); n=len(B)
y0=np.array([b[0] if b[0] is not None else np.nan for b in B],float); y1=np.array([b[1] if b[1] is not None else np.nan for b in B],float)
for a in (y0,y1):
    m=np.isnan(a)
    if m.any(): a[m]=np.interp(np.nonzero(m)[0],np.nonzero(~m)[0],a[~m])
y0=medfilt(y0,11); y1=medfilt(y1,11)
def sm(a,b,x):
    u=np.clip((x-a)/(b-a),0,1); return u*u*(3-2*u)
t=np.arange(n)/30
w=np.maximum.reduce([np.minimum(sm(30.15,30.45,t),1-sm(32.35,32.65,t)),1-sm(0.75,1.05,t)])
Y0=(1-w)*y0+w*407; Y1=(1-w)*y1+w*1184
# zolaq hündürlüyünü sabit saxla (ən çox rast gələn) ki, görüntü hoppanmasın
bh_med=float(np.median(Y1-Y0))
print("bands",n,"median band h",bh_med,flush=True)
def groups(rows):
    g=[];
    if len(rows)==0: return g
    s=p=rows[0]
    for i in rows[1:]:
        if i-p>40: g.append((s,p)); s=i
        p=i
    g.append((s,p)); return g
def build(fr,Y0i,Y1i):
    a=max(0,int(round(Y0i))-4); b=min(H-1,int(round(Y1i))+4)
    bh=b-a+1
    s=min(OW/W,OH/bh)
    pw=int(round(W*s)); ph=int(round(bh*s))
    pic=cv2.resize(fr[a:b+1],(pw,ph),interpolation=cv2.INTER_CUBIC).astype(np.float32)
    F=np.median(fr,axis=1,keepdims=True).astype(np.float32)
    navy=F[a:b+1].mean((0,1)) if False else np.array([4,10,28],np.float32)
    canvas=np.empty((OH,OW,3),np.float32); canvas[:]=navy
    # yanlar: kənar sütunların yumşaq davamı
    x0=(OW-pw)//2; y_off=(OH-ph)//2
    if x0>0:
        L=np.repeat(pic[:,:1],x0,1); R=np.repeat(pic[:,-1:],OW-pw-x0,1)
        ext=np.concatenate([L,pic,R],1)
        ext=cv2.GaussianBlur(ext,(0,0),40)
        lum=ext.mean(2,keepdims=True); ext=ext*np.clip(70/np.maximum(lum,1),0.3,1.0)
        canvas[y_off:y_off+ph]=navy*0.5+ext*0.5
    # şəkil + üfüqi lələk
    fe=40; xw=np.ones(pw,np.float32)
    if x0>0:
        ramp=np.linspace(0,1,fe,dtype=np.float32); xw[:fe]=ramp; xw[-fe:]=ramp[::-1]
    reg=canvas[y_off:y_off+ph,x0:x0+pw]
    canvas[y_off:y_off+ph,x0:x0+pw]=reg*(1-xw.reshape(1,-1,1))+pic*xw.reshape(1,-1,1)
    # zolaqdan kənardakı yazılar
    f32=fr.astype(np.float32); D=np.clip(f32-F,0,255)
    D[a:b+1]=0
    rows=np.nonzero(D.max(axis=(1,2))>45)[0]
    for (g0,g1) in groups(rows):
        blk=D[g0:g1+1]
        cols=np.nonzero(blk.max(axis=(0,2))>45)[0]
        c0=max(0,cols[0]-14); c1=min(W-1,cols[-1]+14)
        blk=blk[:,c0:c1+1]
        cs=1.15; bw=int(blk.shape[1]*cs); bhh=int(blk.shape[0]*cs)
        blk=cv2.resize(blk,(bw,bhh),interpolation=cv2.INTER_CUBIC)
        top_group = g1 < a
        yy=36 if top_group else OH-36-bhh
        xx=(OW-bw)//2
        # oxunaqlıq üçün yumşaq tünd zolaq
        gr=np.zeros((OH,1,1),np.float32)
        c=yy+bhh/2; yv=np.arange(OH,dtype=np.float32)
        gr[:,0,0]=np.exp(-((yv-c)/(bhh*1.1+30))**2)*0.55
        canvas*= (1-gr)
        canvas[yy:yy+bhh,xx:xx+bw]+=blk
    return np.clip(canvas,0,255).astype(np.uint8)
ra=rd(src)
if test:
    import imageio
    for i in range(n):
        fr=np.frombuffer(ra.stdout.read(sz),np.uint8).reshape(H,W,3)
        if i in test:
            cv2.imwrite(f"/tmp/land_{i}.png",cv2.cvtColor(build(fr,Y0[i],Y1[i]),cv2.COLOR_RGB2BGR))
        if i>max(test): break
    sys.exit()
wr=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{OW}x{OH}","-r","30","-i","-","-i",src,"-map","0:v","-map","1:a","-c:v","libx264","-crf","20","-preset","medium","-pix_fmt","yuv420p","-c:a","copy","-movflags","+faststart",dst],stdin=subprocess.PIPE)
for i in range(n):
    fr=np.frombuffer(ra.stdout.read(sz),np.uint8).reshape(H,W,3)
    wr.stdin.write(build(fr,Y0[i],Y1[i]).tobytes())
    if i%200==0: print(i,flush=True)
wr.stdin.close(); wr.wait(); print("done",flush=True)
