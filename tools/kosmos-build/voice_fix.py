"""Gemini səsinin kəkələməsini (artıq 'ki' hecası) kəsmədən söndürür: yalnız danışıq zolağı (250–6000 Hz) həmin aralıqda azaldılır, musiqi və vaxt dəyişmir.
İstifadə: python3 voice_fix.py orijinal.mp4 çıxış.mp4 [a b]   (varsayılan 9.00 9.19)"""
import sys, subprocess, numpy as np, scipy.io.wavfile as W, scipy.signal as sg, tempfile, os
def fix(src,out,a=9.00,b=9.19,red=0.92,ramp=0.02):
    t=tempfile.mktemp(suffix='.wav'); subprocess.run(['ffmpeg','-v','error','-y','-i',src,'-vn','-ac','2','-ar','48000',t],check=True)
    sr,x=W.read(t); x=x.astype(np.float32)/32768; os.remove(t)
    bb,aa=sg.butter(4,[250/(sr/2),6000/(sr/2)],'band'); n=len(x); g=np.zeros(n,np.float32)
    i0,i1,r=int(a*sr),int(b*sr),int(ramp*sr); g[i0:i1]=1; g[i0-r:i0]=np.linspace(0,1,r); g[i1:i1+r]=np.linspace(1,0,r)
    y=x.copy()
    for c in range(x.shape[1]): y[:,c]=x[:,c]-red*g*sg.filtfilt(bb,aa,x[:,c])
    tw=tempfile.mktemp(suffix='.wav'); W.write(tw,sr,(np.clip(y,-1,1)*32767).astype(np.int16))
    subprocess.run(['ffmpeg','-v','error','-y','-i',src,'-i',tw,'-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','192k',out],check=True); os.remove(tw)
if __name__=='__main__':
    a=float(sys.argv[3]) if len(sys.argv)>3 else 9.00; b=float(sys.argv[4]) if len(sys.argv)>4 else 9.19
    fix(sys.argv[1],sys.argv[2],a,b)
