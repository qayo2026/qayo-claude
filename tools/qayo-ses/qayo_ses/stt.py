"""Səs → mətn (açıq Whisper, öz serverimizdə). Model ilk işə düşəndə endirilir."""
import os
_model = None
def _get():
    global _model
    if _model is None:
        from faster_whisper import WhisperModel
        _model = WhisperModel(os.environ.get("QAYO_STT_MODEL", "medium"),
                              device=os.environ.get("QAYO_DEVICE", "cpu"),
                              compute_type=os.environ.get("QAYO_COMPUTE", "int8"),
                              download_root=os.environ.get("QAYO_MODELS", "/models"))
    return _model

def transcribe(path, lang="az"):
    segs, info = _get().transcribe(path, language=lang, word_timestamps=True, vad_filter=True)
    out = []
    for s in segs:
        out.append({"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip(),
                    "words": [{"w": w.word.strip(), "start": round(w.start, 2), "end": round(w.end, 2)} for w in (s.words or [])]})
    return {"language": info.language, "segments": out, "text": " ".join(x["text"] for x in out)}
