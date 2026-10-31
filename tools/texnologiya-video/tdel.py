import cv2,numpy as np
X0,X1,Y0,Y1=210,870,535,670
def remove(fr,thr=7,dil=25):
    reg=fr[Y0:Y1,X0:X1]
    g=cv2.cvtColor(reg,cv2.COLOR_RGB2GRAY).astype(np.float32)
    gs=cv2.GaussianBlur(g,(0,0),2)
    # background level: heavy median
    bg=cv2.medianBlur(np.clip(gs,0,255).astype(np.uint8),61).astype(np.float32)
    m=((gs-bg)>thr).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,_=cv2.connectedComponentsWithStats(m,8)
    keep=np.zeros_like(m)
    for i in range(1,n):
        if st[i,cv2.CC_STAT_AREA]>=60 and st[i,cv2.CC_STAT_HEIGHT]>=8: keep[lab==i]=1
    if keep.sum()==0: return fr
    mk=cv2.dilate(keep,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(dil,dil)))
    # smooth fill: inpaint at 1/4 resolution then upscale
    sm=cv2.resize(reg,(reg.shape[1]//4,reg.shape[0]//4),interpolation=cv2.INTER_AREA)
    mm=cv2.resize(mk,(sm.shape[1],sm.shape[0]),interpolation=cv2.INTER_NEAREST)
    mm=cv2.dilate(mm,np.ones((3,3),np.uint8))*255
    fill=cv2.inpaint(sm,mm,5,cv2.INPAINT_TELEA)
    fill=cv2.GaussianBlur(cv2.resize(fill,(reg.shape[1],reg.shape[0]),interpolation=cv2.INTER_CUBIC),(0,0),3)
    soft=cv2.GaussianBlur(mk.astype(np.float32),(0,0),6)
    soft=np.clip(soft*1.6,0,1)
    res=reg*(1-soft[...,None])+fill*soft[...,None]
    out=fr.copy(); out[Y0:Y1,X0:X1]=np.clip(res,0,255).astype(np.uint8); return out
