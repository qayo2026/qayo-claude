"""Əl ilə açar kadrlarla (miqyas s, Bakı anker nöqtəsi) real konturu köhnə videonun Gemini xəritəsinə oturdur; aralıq kadrlar interpolyasiya."""
import sys, os, json, cv2, numpy as np
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(HERE,'..','az-map'))
import mapscene as M
from oldmap import TPL
BK=M.proj(49.87,40.41)
def load(p): return json.load(open(p))   # {"kadr":[s,bx,by],...}
def warp_for(keys,f):
    ks=sorted(keys,key=int); xs=[int(k) for k in ks]
    s=np.interp(f,xs,[keys[k][0] for k in ks]); sy=np.interp(f,xs,[keys[k][1] for k in ks]); bx=np.interp(f,xs,[keys[k][2] for k in ks]); by=np.interp(f,xs,[keys[k][3] for k in ks])
    return np.array([[s,0,bx-s*BK[0]],[0,sy,by-sy*BK[1]]],np.float32)
def apply(w,pt): return (w[0,0]*pt[0]+w[0,2], w[1,1]*pt[1]+w[1,2])
if __name__=='__main__':
    d,keysp,out=sys.argv[1:4]; frames=[int(x) for x in sys.argv[4].split(',')]; keys=load(keysp); os.makedirs(out,exist_ok=True)
    for f in frames:
        img=cv2.imread(f'{d}/o_{f:04d}.png'); w=warp_for(keys,f)
        wp=cv2.warpAffine(TPL,w,(1080,1920)); img[...,2]=np.clip(img[...,2]+wp*255,0,255)
        for c in M.CITIES:
            x,y=apply(w,c['p']); cv2.circle(img,(int(x),int(y)),5,(0,255,0),-1); cv2.putText(img,c['name'][:4],(int(x)+6,int(y)),0,0.5,(0,255,0),1)
        cv2.imwrite(f'{out}/f_{f:04d}.png',img[520:1440])
