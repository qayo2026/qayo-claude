import json,numpy as np
from labels import *
TA=json.load(open('trA.json')); TS=json.load(open('tr_ts.json')); T1=json.load(open('trC1.json')); T2=json.load(open('trC2.json'))
cA=json.load(open('cfgA.json'))['labels']; c1=json.load(open('cfgC1.json'))['labels']; c2=json.load(open('cfgC2.json'))['labels']
FA0=540; FS0=705; FC0=723
def ramp(a,b,t): return sm(a,b,t)
SPEC={ # id:(text,code,start,fade_in,end0,end1,kind)
 'a_US':('UNITED STATES','US',18.6,0.15,22.05,22.2),'a_FR':('FRANCE','FR',18.6,0.15,22.05,22.2),
 'a_DE':('GERMANY','DE',18.6,0.15,22.05,22.2),'a_RU':('RUSSIA','RU',18.6,0.15,22.05,22.2),
 'a_BR':('BRAZIL','BR',18.6,0.15,22.05,22.2),
 'g_AZ':('AZERBAIJAN','AZ',22.2,0.1,27.30,27.58),'g_DE':('GERMANY','DE',22.5,0.1,27.30,27.58),
 'g_FR':('FRANCE','FR',22.5,0.1,27.30,27.58),'g_US':('UNITED STATES','US',24.0,0.1,27.30,27.58),
 'g_BR':('BRAZIL','BR',24.03,0.1,27.30,27.58),'g_NG':('NIGERIA','NG',24.1,0.1,27.30,27.58)}
def rawpos(k,f):
    t=f/30
    if k[0]=='a':
        n={'a_US':'US','a_FR':'FR1','a_DE':'DE1','a_RU':'RU1','a_BR':'BR'}[k]
        x,y,s=TA['pos'][n][min(max(f-FA0,0),TA['n']-1)]; _,_,_,w,h=cA[n]; return x,y,w,h
    n=k[2:]
    if n in('FR','DE','AZ') and t<24.0:
        arr=TS['res']['B_'+n]; v=arr[min(max(f-FS0,0),len(arr)-1)]; return v[0],v[1],v[2],v[3]
    if t<24.6:
        arr=TS['res']['C_'+n]; v=arr[min(max(f-FS0,0),len(arr)-1)]; return v[0],v[1],v[2],v[3]
    if t<25.8:
        p=T1['pos'][n][min(f-FC0,T1['n']-1)]; _,_,_,w,h=c1[n]; return p[0],p[1],w,h
    p=T2['pos'][n][min(f-FC0,T2['n']-1)]; _,_,_,w,h=c2[n]; return p[0],p[1],w,h
# smoothed tables
TAB={}
for k,sp in SPEC.items():
    f0=int(sp[2]*30)-3; f1=int(sp[5]*30)+3
    arr=np.array([rawpos(k,f) for f in range(f0,f1)],float)
    ker=np.ones(5)/5; pad=np.pad(arr,((2,2),(0,0)),mode='edge')
    sm_=np.stack([np.convolve(pad[:,j],ker,mode='valid') for j in range(4)],1)
    TAB[k]=(f0,sm_)
def alpha(sp,t): return ramp(sp[2],sp[2]+sp[3],t)*(1-ramp(sp[4],sp[5],t))
def apply(fr,f):
    t=f/30
    order=sorted(SPEC,key=lambda k:(0 if k=='g_AZ' else 1))
    for k in order:
        sp=SPEC[k]; a=alpha(sp,t)
        if a<=0.01: continue
        f0,arr=TAB[k]; 
        if not(f0<=f<f0+len(arr)): continue
        x,y,w,h=arr[f-f0]; P=6 if k[0]=='a' else int(min(8,max(3,round(0.18*h))))
        bx,by,bw,bh=int(round(x-P)),int(round(y-P)),int(round(w+2*P)),int(round(h+2*P))
        stacked=(k=='a_BR'); hi=(k=='g_AZ')
        lab=render(sp[0],sp[1],bw,bh,stacked=stacked,hi=hi)
        if lab.size[0]>bw and k in('g_US',): bx=bx+bw-lab.size[0]   # right anchored
        arrl=np.asarray(lab).astype(np.float32); lw,lh=lab.size
        x0,y0=max(bx,0),max(by,0); x1,y1=min(bx+lw,W),min(by+lh,H)
        if x1<=x0 or y1<=y0: continue
        sub=arrl[y0-by:y1-by,x0-bx:x1-bx]; al=sub[...,3:4]/255*a
        reg=fr[y0:y1,x0:x1].astype(np.float32)
        fr[y0:y1,x0:x1]=(reg*(1-al)+sub[...,:3]*al).astype(np.uint8)
    return fr
if __name__=='__main__':
    import sys,subprocess
    from PIL import Image
    ts=[float(x) for x in sys.argv[2:]]
    out=[]
    for t in ts:
        subprocess.run(['ffmpeg','-y','-loglevel','error','-ss',str(t),'-i','ext93.mp4','-frames:v','1','/tmp/_o.png'],check=True)
        fr=np.array(Image.open('/tmp/_o.png').convert('RGB'))
        fr=apply(fr,int(round(t*30)))
        out.append(Image.fromarray(fr[560:1130]))
    w,h=out[0].size
    n=len(out); cols=2; rows=(n+1)//2
    s=Image.new('RGB',(w*cols//2*1,h*rows//2*1))
    s=Image.new('RGB',(w//2*cols,h//2*rows))
    for i,im in enumerate(out): s.paste(im.resize((w//2,h//2)),((i%cols)*(w//2),(i//cols)*(h//2)))
    s.save(sys.argv[1])
