import cv2,numpy as np,sys
Y0,Y1,X0=1056,1236,684
def fix(im):
    h,w=im.shape[:2]
    mir=im[:,::-1]
    m=np.zeros((h,w),np.float32); m[Y0:Y1,X0:]=1
    m=cv2.GaussianBlur(m,(0,0),7)
    m[:, :X0-30]=0
    m=m[...,None]
    return np.clip(im*(1-m)+mir*m,0,255).astype(np.uint8)
if __name__=='__main__':
    for f,o in ((sys.argv[1],sys.argv[2]),):
        cv2.imwrite(o,fix(cv2.imread(f)))
