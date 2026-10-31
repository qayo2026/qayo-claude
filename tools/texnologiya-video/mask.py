import cv2, numpy as np
from PIL import Image
Y0,Y1=585,1065
im=np.array(Image.open('full_10.6.png').convert('RGB'))[Y0:Y1]
g=cv2.GaussianBlur(im[:,:,1].astype(np.float32),(0,0),2.0)
print('g percentiles',np.percentile(g,[50,80,90,95,99]))
thr=60
m=(g>thr).astype(np.uint8)
poly=np.zeros_like(m); poly[5:375,165:935]=1
m=m*poly
m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((7,7),np.uint8))
cv2.imwrite('mask.png',m*255)
prev=im.copy(); prev[m==0]=(prev[m==0]*0.25).astype(np.uint8)
Image.fromarray(np.concatenate([im,prev],0)).save('mask_prev.png')
np.save('mask.npy',m)
