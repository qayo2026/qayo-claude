import cv2,numpy as np,json
QL=np.float32([[40,376],[186,292],[196,310],[48,393]])
QR=np.float32([[302,216],[402,161],[409,172],[310,230]])
def gray(i): return cv2.cvtColor(cv2.imread('src/s_%04d.png'%i)[657:1260],cv2.COLOR_BGR2GRAY)
def expand(Q,k):
    # expand quad outward perpendicular (height) by k*h each side and 0.0 along
    TL,TR,BR,BL=Q
    up=(TL-BL+TR-BR)/2; 
    return np.float32([TL+up*k,TR+up*k,BR-up*k,BL-up*k])
def track(Q0,start,end,step):
    G={}
    Q=Q0.copy(); res={start:Q.copy()}; i=start
    prev=gray(i)
    while i!=end:
        j=i+step; cur=gray(j)
        m=np.zeros(prev.shape,np.uint8); cv2.fillPoly(m,[expand(Q,1.2).astype(np.int32)],255)
        p0=cv2.goodFeaturesToTrack(prev,200,0.01,4,mask=m)
        if p0 is None or len(p0)<8: print('lost',j); break
        p1,st,err=cv2.calcOpticalFlowPyrLK(prev,cur,p0,None,winSize=(15,15),maxLevel=3)
        ok=st.ravel()==1
        if ok.sum()<8: print('lost',j); break
        H,inl=cv2.findHomography(p0[ok],p1[ok],cv2.RANSAC,1.5)
        if H is None or inl.sum()<8: print('lost',j,inl.sum() if inl is not None else 0); break
        Q=cv2.perspectiveTransform(Q.reshape(-1,1,2),H).reshape(-1,2)
        res[j]=Q.copy(); prev=cur; i=j
    return res
out={}
for name,Q in (('L',QL),('R',QR)):
    f=track(Q,30,115,1); b=track(Q,30,1,-1)
    r={**b,**f}; out[name]={str(k):v.tolist() for k,v in r.items()}
    print(name,min(r),max(r))
json.dump(out,open('quads.json','w'))
