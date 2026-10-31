import cv2,numpy as np,subprocess,json,sys
W,H=1080,1920
def frames(src,t0,t1):
    n=int(round((t1-t0)*30))
    p=subprocess.Popen(['ffmpeg','-loglevel','error','-ss',str(t0),'-i',src,'-frames:v',str(n),'-f','rawvideo','-pix_fmt','gray','-'],stdout=subprocess.PIPE)
    out=[]
    while True:
        b=p.stdout.read(W*H)
        if len(b)<W*H: break
        out.append(np.frombuffer(b,np.uint8).reshape(H,W).copy())
    return out
def track(fr,t0,labels,R=45):
    """labels: dict id->(tref,x,y,w,h). returns id->list of (x,y,score) per frame"""
    res={}
    for k,(tr,x,y,w,h) in labels.items():
        ir=int(round((tr-t0)*30)); ir=min(max(ir,0),len(fr)-1)
        tpl=fr[ir][y:y+h,x:x+w]
        pos=[None]*len(fr); pos[ir]=(x,y,1.0)
        for rng in (range(ir+1,len(fr)),range(ir-1,-1,-1)):
            px,py=x,y
            for i in rng:
                x0=max(px-R,0);y0=max(py-R,0);x1=min(px+R+w,W);y1=min(py+R+h,H)
                m=cv2.matchTemplate(fr[i][y0:y1,x0:x1],tpl,cv2.TM_CCOEFF_NORMED)
                _,mx,_,loc=cv2.minMaxLoc(m)
                if mx>0.45: px,py=x0+loc[0],y0+loc[1]
                pos[i]=(px,py,float(mx))
        res[k]=pos
    return res
if __name__=='__main__':
    cfg=json.load(open(sys.argv[1])); t0,t1=cfg['t0'],cfg['t1']
    fr=frames(cfg['src'],t0,t1)
    labs={k:tuple(v) for k,v in cfg['labels'].items()}
    res=track(fr,t0,labs)
    json.dump({'t0':t0,'n':len(fr),'pos':res},open(sys.argv[2],'w'))
    for k,p in res.items():
        print(k,[ (i,p[i][0],p[i][1],round(p[i][2],2)) for i in range(0,len(p),15)])
