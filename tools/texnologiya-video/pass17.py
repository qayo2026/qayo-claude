import sys, subprocess, numpy as np, fill, fill2
from scipy.signal import medfilt
src,dst=sys.argv[1],sys.argv[2]; S0=float(sys.argv[3])
W,H=1080,1920; sz=W*H*3
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
S=1+(S0-1)*(1-sm(36.6,37.3,t))
print("bands done",n,flush=True)
ra=rd(src)
wr=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r","30","-i","-","-i",src,"-map","0:v","-map","1:a","-c:v","libx264","-crf","16","-preset","medium","-pix_fmt","yuv420p","-c:a","copy","-movflags","+faststart",dst],stdin=subprocess.PIPE)
for i in range(n):
    fr=np.frombuffer(ra.stdout.read(sz),np.uint8).reshape(H,W,3)
    wr.stdin.write(fill2.compose2(fr,(int(round(Y0[i])),int(round(Y1[i]))),S=float(S[i])).tobytes())
    if i%200==0: print(i,flush=True)
wr.stdin.close(); wr.wait(); print("done",flush=True)
