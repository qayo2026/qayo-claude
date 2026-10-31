import sys, subprocess, numpy as np, fill
from scipy.signal import medfilt
src,dst=sys.argv[1],sys.argv[2]
W,H=1080,1920; sz=W*H*3
def reader():
    return subprocess.Popen(["ffmpeg","-v","error","-i",src,"-f","rawvideo","-pix_fmt","rgb24","-"],stdout=subprocess.PIPE)
# pass 1: band rows per frame
rd=reader(); B=[]
while True:
    b=rd.stdout.read(sz)
    if len(b)<sz: break
    fr=np.frombuffer(b,np.uint8).reshape(H,W,3)
    r=fill.band_rows(fr); B.append(r if r else (None,None))
rd.wait()
n=len(B); y0=np.array([b[0] if b[0] is not None else np.nan for b in B],float); y1=np.array([b[1] if b[1] is not None else np.nan for b in B],float)
for a in (y0,y1):
    m=np.isnan(a); a[m]=np.interp(np.nonzero(m)[0],np.nonzero(~m)[0],a[~m]) if m.any() else a[m]
y0=medfilt(y0,11); y1=medfilt(y1,11)
print("band rows range",y0.min(),y0.max(),y1.min(),y1.max())
rd=reader()
wr=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r","30","-i","-","-i",src,"-map","0:v","-map","1:a","-c:v","libx264","-crf","16","-preset","medium","-pix_fmt","yuv420p","-c:a","copy","-movflags","+faststart",dst],stdin=subprocess.PIPE)
i=0
while True:
    b=rd.stdout.read(sz)
    if len(b)<sz: break
    fr=np.frombuffer(b,np.uint8).reshape(H,W,3)
    o=fill.compose(fr,(int(y0[i]),int(y1[i])),amax=0.95,reach=800,dark=1.0)
    wr.stdin.write(o.tobytes()); i+=1
wr.stdin.close(); wr.wait(); print("frames",i)
