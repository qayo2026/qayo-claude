import cv2,numpy as np,glob,os,shutil,sys
ZX=1.0;ZY=1.5; Y0,Y1=657,1260
def tall(im):
    bg=np.median(im[40:120,:].reshape(-1,3),0)
    out=np.empty_like(im); out[:]=bg
    band=im[Y0:Y1]
    h=Y1-Y0; big=cv2.resize(band,None,fx=ZX,fy=ZY,interpolation=cv2.INTER_CUBIC)
    bh,bw=big.shape[:2]; x0=(bw-1080)//2
    big=big[:,x0:x0+1080]
    cy=(Y0+Y1)//2; ty=cy-bh//2
    out[ty:ty+bh]=big
    return out
os.makedirs('out8',exist_ok=True)
for f in sorted(glob.glob('out2w/*.png')):
    cv2.imwrite('out8/'+os.path.basename(f),tall(cv2.imread(f)))
last=tall(cv2.imread('out2w/f_0273.png')).astype(np.float32)
fs=sorted(glob.glob('tail2f/*.png')); N=30; end=cv2.imread(fs[N]).astype(np.float32)
shutil.rmtree('tail8',ignore_errors=True); os.makedirs('tail8')
for k in range(len(fs)):
    if k<N:
        a=k/N;a=a*a*(3-2*a); cv2.imwrite('tail8/t_%04d.png'%(k+1),np.clip(last*(1-a)+end*a,0,255).astype(np.uint8))
    else: shutil.copy(fs[k],'tail8/t_%04d.png'%(k+1))
