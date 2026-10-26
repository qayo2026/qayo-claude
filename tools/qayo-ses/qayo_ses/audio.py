"""ffmpeg əsaslı səs əməliyyatları (model tələb etmir, hər yerdə işləyir)."""
import subprocess, json, numpy as np
from scipy.signal import butter, sosfilt

SR = 16000

def _run(cmd):
    r = subprocess.run(cmd, capture_output=True)
    if r.returncode: raise RuntimeError(r.stderr.decode()[-500:])
    return r.stdout

def load(path, sr=SR):
    """Fayl (səs və ya video) -> mono float32 massiv."""
    raw = _run(["ffmpeg", "-v", "error", "-i", path, "-vn", "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"])
    return np.frombuffer(raw, np.float32), sr

def duration(path):
    out = _run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", path])
    return float(json.loads(out)["format"]["duration"])

def phrases(path, min_gap=0.18, min_len=0.25, thresh=0.12):
    """Cümlə/söz bloklarının vaxtları (ASR olmadan, nitq zolağı enerjisi ilə). [(başlama, son), ...]"""
    x, sr = load(path)
    sos = butter(4, [250, 3500], "bandpass", fs=sr, output="sos")
    e = np.abs(sosfilt(sos, x))
    hop = int(0.02 * sr)
    env = np.array([e[i:i + hop].mean() for i in range(0, len(e) - hop, hop)])
    env = np.convolve(env, np.ones(5) / 5, "same")
    on = env > max(env.max() * thresh, 1e-4)
    out, start, last = [], None, None
    for i, v in enumerate(on):
        t = i * 0.02
        if v:
            if start is None: start = t
            last = t
        elif start is not None and t - last >= min_gap:
            if last - start >= min_len: out.append((round(start, 2), round(last + 0.02, 2)))
            start = None
    if start is not None and last - start >= min_len: out.append((round(start, 2), round(last + 0.02, 2)))
    return out

def cut(src, dst, start, end, fade=0.02):
    """[start,end] hissəsini kəs; kliksiz olsun deyə kiçik fade."""
    d = end - start
    _run(["ffmpeg", "-v", "error", "-y", "-ss", f"{start}", "-t", f"{d}", "-i", src,
          "-af", f"afade=t=in:d={fade},afade=t=out:st={max(d - fade, 0)}:d={fade}", dst])
    return dst

def splice(parts, dst, crossfade=0.04, gap=0.0):
    """Səs parçalarını calaq: qısa crossfade (klik olmasın). gap>0 -> aralarına sakitlik."""
    if len(parts) == 1:
        _run(["ffmpeg", "-v", "error", "-y", "-i", parts[0], dst]); return dst
    cmd = ["ffmpeg", "-v", "error", "-y"]
    for p in parts: cmd += ["-i", p]
    fc, prev = [], "[0:a]"
    for i in range(1, len(parts)):
        src = f"[{i}:a]"
        if gap > 0:
            fc.append(f"aevalsrc=0:d={gap}[g{i}]"); fc.append(f"{prev}[g{i}]concat=n=2:v=0:a=1[s{i}]"); prev = f"[s{i}]"
        fc.append(f"{prev}{src}acrossfade=d={crossfade}[a{i}]"); prev = f"[a{i}]"
    _run(cmd + ["-filter_complex", ";".join(fc), "-map", prev, dst])
    return dst

def place(src, dst, at, total):
    """Səsi tam videonun vaxt oxuna yerləşdir: 'at' saniyədə başlasın, ümumi müddət total olsun."""
    _run(["ffmpeg", "-v", "error", "-y", "-i", src, "-af",
          f"adelay={int(at * 1000)}|{int(at * 1000)},apad=whole_dur={total}", "-t", f"{total}", dst])
    return dst

def fit_tempo(src, dst, target_sec):
    """Səsi müddətə sığdır (sürəti dəyiş, tonu saxla). 0.8–1.25 hüdudundan kənar xəbərdarlıq."""
    d = duration(src); r = d / target_sec
    if not 0.5 <= r <= 2.0: raise ValueError(f"sürət nisbəti {r:.2f} çox böyükdür")
    _run(["ffmpeg", "-v", "error", "-y", "-i", src, "-af", f"atempo={r:.4f}", dst])
    return dst, r
