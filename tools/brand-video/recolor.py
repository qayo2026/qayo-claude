"""Brend videosunu KOSMOS rəng sisteminə gətirir (palette.json): əsas = #58D8F5 (cyan), fon = tünd göy, marka qırmızısı yalnız yazı altındakı xətt.
İstifadə: python3 recolor.py giriş.mp4 çıxış.mp4 [--test saniyə,saniyə]"""
import sys, cv2, numpy as np, subprocess, os, tempfile
H_CY=96                     # #58D8F5 → OpenCV hue ≈ 96
def grade(bgr):
    hsv=cv2.cvtColor(bgr,cv2.COLOR_BGR2HSV).astype(np.float32); h,s,v=hsv[...,0],hsv[...,1],hsv[...,2]
    sat=(s>70)&(v>60)
    blue=sat&(h>=100)&(h<=128)                  # kral göyü → cyan-a çək
    h[blue]=h[blue]+(H_CY-h[blue])*0.8; s[blue]*=0.88
    other=sat&~((h>=85)&(h<=128))               # çəhrayı/bənövşəyi/narıncı/yaşıl nöqtələr → cyan-ağ
    h[other]=H_CY; s[other]*=0.45; v[other]=np.minimum(255,v[other]*1.08)
    hsv[...,0]=h; hsv[...,1]=np.clip(s,0,255); hsv[...,2]=np.clip(v,0,255)
    out=cv2.cvtColor(hsv.astype(np.uint8),cv2.COLOR_HSV2BGR)
    # marka qırmızısı xətti (yazı altı) toxunulmaz
    y0,y1,x0,x1=925,1000,320,840; red=(bgr[y0:y1,x0:x1,2]>170)&(bgr[y0:y1,x0:x1,1]<110)
    out[y0:y1,x0:x1][red]=bgr[y0:y1,x0:x1][red]
    return out
if __name__=='__main__':
    src,dst=sys.argv[1],sys.argv[2]; cap=cv2.VideoCapture(src); fps=cap.get(5)
    if len(sys.argv)>3 and sys.argv[3]=='--test':
        os.makedirs(dst,exist_ok=True)
        for t in [float(x) for x in sys.argv[4].split(',')]:
            cap.set(cv2.CAP_PROP_POS_FRAMES,int(t*fps)); ok,f=cap.read(); cv2.imwrite(f'{dst}/r_{t}.png',np.hstack([f,grade(f)]))
    else:
        p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s','1080x1920','-r',str(fps),'-i','-','-i',src,'-map','0:v','-map','1:a','-c:v','libx264','-preset','slow','-crf','17','-pix_fmt','yuv420p','-c:a','copy','-shortest','-movflags','+faststart',dst],stdin=subprocess.PIPE)
        while True:
            ok,f=cap.read()
            if not ok: break
            p.stdin.write(grade(f).tobytes())
        p.stdin.close(); p.wait()
