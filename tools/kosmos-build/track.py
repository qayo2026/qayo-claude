import cv2, numpy as np, json
N=150
quads={'L':np.array([[155,404],[205,476],[452,368],[408,311]],np.float32),
       'R':np.array([[519,262],[560,322],[722,252],[680,208]],np.float32)}
out={k:[v.tolist()] for k,v in quads.items()}
prev=cv2.imread('A/a_0001.png'); pg=cv2.cvtColor(prev,cv2.COLOR_BGR2GRAY)
cur={k:v.copy() for k,v in quads.items()}
for i in range(2,N+1):
    im=cv2.imread(f'A/a_{i:04d}.png'); g=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
    for k in cur:
        mask=np.zeros(pg.shape,np.uint8); cv2.fillConvexPoly(mask,cur[k].astype(np.int32),255)
        mask=cv2.erode(mask,np.ones((5,5),np.uint8))
        p0=cv2.goodFeaturesToTrack(pg,300,0.005,4,mask=mask)
        if p0 is None or len(p0)<8: out[k].append(cur[k].tolist()); continue
        p1,st,_=cv2.calcOpticalFlowPyrLK(pg,g,p0,None,winSize=(21,21),maxLevel=3)
        ok=st.ravel()==1
        if ok.sum()<8: out[k].append(cur[k].tolist()); continue
        H,inl=cv2.findHomography(p0[ok],p1[ok],cv2.RANSAC,2.0)
        if H is None: out[k].append(cur[k].tolist()); continue
        cur[k]=cv2.perspectiveTransform(cur[k].reshape(-1,1,2),H).reshape(4,2)
        out[k].append(cur[k].tolist())
    pg=g
json.dump(out,open('quads.json','w'))
for n in (31,61,91,121,150):
    im=cv2.imread(f'A/a_{n:04d}.png')
    for k in out:
        q=np.array(out[k][n-1],np.int32); cv2.polylines(im,[q],True,(0,255,255) if k=='L' else (0,255,0),2)
    cv2.imwrite(f'q_{n}.png',cv2.resize(im,None,fx=0.5,fy=0.5))
a=[cv2.imread(f'q_{n}.png') for n in (31,61,91,121)]
cv2.imwrite('q_all.png',np.vstack([np.hstack(a[:2]),np.hstack(a[2:])]))
