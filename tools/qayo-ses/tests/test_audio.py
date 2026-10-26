import subprocess, os, tempfile
from qayo_ses import audio, radar
d = tempfile.mkdtemp()
def tone(name, f, dur):
    p = os.path.join(d, name)
    subprocess.run(["ffmpeg","-v","error","-y","-f","lavfi","-i",f"sine=frequency={f}:duration={dur}","-af","volume=0.5",p],check=True); return p
a, b = tone("a.wav",440,1.0), tone("b.wav",660,1.5)
j = audio.splice([a,b], os.path.join(d,"j.wav"), crossfade=0.04, gap=0.3)
dur = audio.duration(j); assert 2.7 < dur < 2.9, dur
c = audio.cut(j, os.path.join(d,"c.wav"), 0.5, 1.5); assert abs(audio.duration(c)-1.0) < 0.05
p = audio.place(a, os.path.join(d,"p.wav"), 2.0, 5.0); assert abs(audio.duration(p)-5.0) < 0.05
r = radar.check_audio(j); assert len(r["phrases"]) >= 2, r
assert radar.check_repeats([{"text":"qayo qayo inşaat","start":0,"end":1}])
print("OK", r["phrases"])
