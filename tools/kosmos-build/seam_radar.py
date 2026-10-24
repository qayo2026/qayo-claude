"""QIRILMA RADARI: videoda calaq/qırılma yerlərini 4 ayrı başlıq altında tapır.
İstifadə: python3 seam_radar.py video.mp4
  SƏS      — dalğa sıçrayışı/klik (calaq yeri)
  MUSİQİ   — aşağı tezlik (musiqi) zərfində kəskin sıçrayış / təkrar döngü
  SÖZ      — danışıq zolağında eyni parçanın təkrarı (söz iki dəfə)
  GÖRÜNTÜ  — kadr sıçrayışı (kəsik) və donma"""
import sys, subprocess, numpy as np, scipy.io.wavfile as W, scipy.signal as sg, cv2, tempfile, os
def load_audio(p):
    t=tempfile.mktemp(suffix='.wav'); subprocess.run(['ffmpeg','-v','error','-y','-i',p,'-vn','-ac','1','-ar','16000',t],check=True)
    sr,x=W.read(t); os.remove(t); return sr,x.astype(np.float32)/32768
def clusters(ts,gap=0.15):
    out=[]
    for t in sorted(ts):
        if out and t-out[-1][-1]<gap: out[-1].append(t)
        else: out.append([t])
    return [(c[0],c[-1]) for c in out]
def audio_clicks(sr,x):
    # xətti proqnoz qalığı: calaqda qalıq kəskin böyüyür
    r=x[2:]-2*x[1:-1]+x[:-2]; w=int(sr*0.004); e=np.sqrt(np.convolve(r**2,np.ones(w)/w,'same'))
    med=np.median(e)+1e-9; idx=np.where(e>max(12*med,0.02))[0]
    return clusters(idx/sr)
def music_jumps(sr,x):
    b,a=sg.butter(4,250/(sr/2),'low'); lo=sg.filtfilt(b,a,x); h=int(sr*0.05)
    env=np.array([np.sqrt((lo[i:i+h]**2).mean()) for i in range(0,len(lo)-h,h)])
    d=np.abs(np.diff(env)); thr=max(4*np.median(d)+1e-6,0.06)
    return [(i+1)*0.05 for i in range(len(d)) if d[i]>thr and env[i+1]>0.02 or d[i]>thr and env[i]>0.02]
def speech_repeats(sr,x):
    b,a=sg.butter(4,[300/(sr/2),3400/(sr/2)],'band'); sp=sg.filtfilt(b,a,x); win=int(sr*0.5); hop=int(sr*0.1); out=[]
    segs=[(i,sp[i:i+win]) for i in range(0,len(sp)-win,hop)]
    for i,s in segs:
        if np.sqrt((s**2).mean())<0.05: continue
        for j,s2 in segs:
            if j<=i+int(sr*0.7): continue
            if np.sqrt((s2**2).mean())<0.05: continue
            c=np.dot(s,s2)/(np.linalg.norm(s)*np.linalg.norm(s2)+1e-9)
            if c>0.7: out.append((i/sr,j/sr,float(c)))
    return out
def video_jumps(p):
    cap=cv2.VideoCapture(p); fps=cap.get(5); prev=None; d=[]
    while True:
        ok,f=cap.read()
        if not ok: break
        g=cv2.resize(cv2.cvtColor(f,cv2.COLOR_BGR2GRAY),(108,192)).astype(np.float32)
        d.append(0 if prev is None else float(np.abs(g-prev).mean())); prev=g
    d=np.array(d); med=np.median(d)+1e-6; k=5
    loc=np.array([np.median(d[max(0,i-k):i+k+1]) for i in range(len(d))])+0.3
    jumps=[i/fps for i in range(1,len(d)) if d[i]>4*loc[i]]
    fr=[]; run=0
    for i,v in enumerate(d):
        run=run+1 if v<0.02 else 0
        if run==int(fps*0.8): fr.append((i-run+1)/fps)
    return jumps,fr
def main(p):
    sr,x=load_audio(p); print('=== SƏS ==='); c=audio_clicks(sr,x)
    print('  təmiz' if not c else '\n'.join(f'  klik/calaq {a:.2f}s' for a,b in c))
    print('=== MUSİQİ ==='); m=clusters(music_jumps(sr,x),0.2)
    print('  təmiz' if not m else '\n'.join(f'  sıçrayış ~{a:.2f}s' for a,b in m))
    print('=== SÖZ ==='); r=speech_repeats(sr,x)
    print('  təmiz' if not r else '\n'.join(f'  təkrar: {a:.1f}s ≈ {b:.1f}s (uyğunluq {c:.2f})' for a,b,c in r[:6]))
    print('=== GÖRÜNTÜ ==='); j,fr=video_jumps(p)
    print('  təmiz' if not j and not fr else '\n'.join([f'  kəsik/sıçrayış {t:.2f}s' for t in j]+[f'  donma {t:.2f}s-dən' for t in fr]))
if __name__=='__main__': main(sys.argv[1])
