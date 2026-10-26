"""Səs qırılma radarı: kliklər, uzun boşluqlar, kəsilmiş son, təkrarlanan söz."""
import numpy as np, re
from .audio import load, phrases, duration

def check_audio(path, max_gap=1.2, click_jump=0.5):
    x, sr = load(path)
    issues = []
    d = np.abs(np.diff(x))
    for i in np.where(d > click_jump)[0][:20]:
        issues.append({"type": "klik", "t": round(i / sr, 3)})
    ph = phrases(path)
    for (a0, a1), (b0, b1) in zip(ph, ph[1:]):
        if b0 - a1 > max_gap: issues.append({"type": "uzun_boşluq", "t": a1, "uzunluq": round(b0 - a1, 2)})
    if ph and duration(path) - ph[-1][1] < 0.05:
        issues.append({"type": "son_kəsilib", "t": ph[-1][1]})
    if ph and ph[0][0] < 0.03:
        issues.append({"type": "başlanğıc_kəsilib", "t": ph[0][0]})
    return {"phrases": ph, "issues": issues}

def check_repeats(segments):
    """segments: [{'text':..., 'start':..., 'end':...}] — ardıcıl təkrarlanan söz/ifadə. Sözə calaq verilməməlidir."""
    words = []
    for s in segments:
        for w in re.findall(r"\w+", s["text"].lower()):
            words.append((w, s["start"]))
    out = []
    for (a, ta), (b, tb) in zip(words, words[1:]):
        if a == b and len(a) > 2: out.append({"type": "təkrar_söz", "söz": a, "t": round(tb, 2)})
    for n in (3, 2):
        for i in range(len(words) - 2 * n + 1):
            if [w for w, _ in words[i:i + n]] == [w for w, _ in words[i + n:i + 2 * n]]:
                out.append({"type": "təkrar_ifadə", "ifadə": " ".join(w for w, _ in words[i:i + n]), "t": round(words[i + n][1], 2)})
    return out
