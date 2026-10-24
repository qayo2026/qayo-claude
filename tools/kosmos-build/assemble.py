"""KOSMOS sınaq videosu (səssiz): peyk -> parlayış -> bulud -> şüa Qafqaza -> kodla xəritə -> kodla loqo.
İstifadə: python3 assemble.py <iş_qovluğu> <çıxış.mp4> | python3 assemble.py <iş_qovluğu> --test 10,60,150"""
import os, sys, subprocess, cv2, numpy as np
HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,HERE); sys.path.insert(0,os.path.join(HERE,'..','az-map'))
from scenes import *
import mapscene
WORK=sys.argv[1]
WHITE_F=np.array((255,250,240),np.float32)
def rd(path): return cv2.imread(path)
def peyk(i): return rd(f'{WORK}/peyk/p_{i:04d}.png')
def v5(i): return rd(f'{WORK}/V5/v_{i:04d}.png')
# vaxt xətti
S1=127; S2_START=127; S2=12; S3_START=133; S3=36; S4_START=161; S4=180; S5_START=341; S5=84
TOTAL=S5_START+S5
def sc1(g):
    i=g+1; ox=60+80*ease_io(i/110.0)
    img=window_composite(peyk(i),ox,g)
    if i>122: k=(i-122)/5.0; img=img*(1-k)+WHITE_F*k
    return img
def sc2(g):
    j=g-S2_START; i=142+j
    img=window_composite(peyk(i),100,g)
    if j<5: k=1-(j+1)/6.0; img=img*(1-k)+WHITE_F*k
    return img
def sc3(g):
    j=g-S3_START; return window_composite(v5(1+j),100,g)
def sc4(g): return mapscene.render(g-S4_START).astype(np.float32)
def sc5(g): return logo_scene(g-S5_START).astype(np.float32)
def frame(g):
    parts=[]
    if g<S1: img=sc1(g)
    elif g<S3_START: img=sc2(g)
    else:
        img=None
    if g>=S3_START and g<S4_START:
        base=sc3(g)
        if g<S2_START+S2:   # S2/S3 qarışması (6 kadr)
            w=(g-S3_START+1)/7.0; base=sc2(g)*(1-w)+base*w
        img=base
    if g>=S4_START and g<S5_START:
        m=sc4(g)
        if g<S3_START+S3:   # S3/S4 qarışması (8 kadr)
            w=(g-S4_START+1)/9.0; m=sc3(g)*(1-w)+m*w
        img=m
    if g>=S5_START: img=sc5(g)
    return np.clip(img,0,255).astype(np.uint8)
if __name__=='__main__':
    if sys.argv[2]=='--test':
        os.makedirs(f'{WORK}/asm',exist_ok=True)
        for g in [int(x) for x in sys.argv[3].split(',')]: cv2.imwrite(f'{WORK}/asm/g_{g:04d}.png',frame(g))
    else:
        out=sys.argv[2]
        cmd=['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s','1080x1920','-r','30','-i','-',
             '-f','lavfi','-i','anullsrc=r=48000:cl=stereo','-t',f'{TOTAL/30.0:.3f}',
             '-c:v','libx264','-preset','slow','-crf','17','-pix_fmt','yuv420p','-r','30','-profile:v','high',
             '-c:a','aac','-b:a','128k','-movflags','+faststart',out]
        p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
        for g in range(TOTAL):
            p.stdin.write(frame(g).tobytes())
            if g%25==0: print('kadr',g,'/',TOTAL,flush=True)
        p.stdin.close(); p.wait(); print('hazır',out)
