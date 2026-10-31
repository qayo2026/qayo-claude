import sys, subprocess, numpy as np, ghost
src,dst=sys.argv[1],sys.argv[2]
W,H,FPS=1080,1920,30
rd=subprocess.Popen(["ffmpeg","-v","error","-i",src,"-f","rawvideo","-pix_fmt","rgb24","-"],stdout=subprocess.PIPE)
wr=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r","30","-i","-","-i",src,"-map","0:v","-map","1:a","-c:v","libx264","-crf","16","-preset","medium","-pix_fmt","yuv420p","-c:a","copy","-movflags","+faststart",dst],stdin=subprocess.PIPE)
n=0;sz=W*H*3
while True:
    b=rd.stdout.read(sz)
    if len(b)<sz: break
    fr=np.frombuffer(b,np.uint8).reshape(H,W,3)
    fr=ghost.apply(fr,n/FPS)
    wr.stdin.write(np.ascontiguousarray(fr).tobytes()); n+=1
wr.stdin.close(); wr.wait(); print("frames",n)
