"""Gemini səsinin kəkələməsini (artıq 'ki' hecası) kəsmədən söndürür: yalnız danışıq zolağı (250–6000 Hz) həmin aralıqda azaldılır, musiqi və vaxt dəyişmir.
İstifadə: python3 voice_fix.py orijinal.mp4 çıxış.mp4 [a b]   (varsayılan 9.00 9.19)"""
import sys, subprocess, numpy as np, scipy.io.wavfile as W, scipy.signal as sg, tempfile, os
def _ramp(n,sr,a,b,r=0.015):
    g=np.zeros(n,np.float32); i0,i1,rr=int(a*sr),int(b*sr),int(r*sr); g[i0:i1]=1; g[i0-rr:i0]=np.linspace(0,1,rr); g[i1:i1+rr]=np.linspace(1,0,rr); return g
def fix(src,out,cut=(9.205,9.47),red=0.92,clar=(7.15,9.65),clar_gain=0.55):
    """cut: artıq 'ki' hecası (yalnız danışıq zolağı azaldılır); clar: aydınlıq üçün 2–4.5 kHz samit parlaqlığı."""
    t=tempfile.mktemp(suffix='.wav'); subprocess.run(['ffmpeg','-v','error','-y','-i',src,'-vn','-ac','2','-ar','48000',t],check=True)
    sr,x=W.read(t); x=x.astype(np.float32)/32768; os.remove(t); n=len(x)
    sp=sg.butter(4,[250/(sr/2),6000/(sr/2)],'band'); pr=sg.butter(4,[2000/(sr/2),4500/(sr/2)],'band')
    gc=_ramp(n,sr,*cut); gl=_ramp(n,sr,*clar,r=0.05); y=x.copy()
    for c in range(x.shape[1]):
        y[:,c]=x[:,c]-red*gc*sg.filtfilt(*sp,x[:,c])+clar_gain*gl*(1-gc)*sg.filtfilt(*pr,x[:,c])
    tw=tempfile.mktemp(suffix='.wav'); W.write(tw,sr,(np.clip(y,-1,1)*32767).astype(np.int16))
    subprocess.run(['ffmpeg','-v','error','-y','-i',src,'-i',tw,'-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','192k',out],check=True); os.remove(tw)
if __name__=='__main__':
    fix(sys.argv[1],sys.argv[2])
