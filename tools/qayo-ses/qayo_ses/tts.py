"""Mətn → səs (açıq Meta MMS Azərbaycan modeli). Sonra öz diktor səsimizlə əvəz olunur — interfeys eyni qalır."""
import os, numpy as np, wave
_m = None
def _get():
    global _m
    if _m is None:
        import torch
        from transformers import VitsModel, AutoTokenizer
        name = os.environ.get("QAYO_TTS_MODEL", "facebook/mms-tts-azj-script_latin")
        _m = (VitsModel.from_pretrained(name, cache_dir=os.environ.get("QAYO_MODELS", "/models")),
              AutoTokenizer.from_pretrained(name, cache_dir=os.environ.get("QAYO_MODELS", "/models")), torch)
    return _m

def speak(text, dst):
    model, tok, torch = _get()
    with torch.no_grad():
        wav = model(**tok(text, return_tensors="pt")).waveform[0].numpy()
    pcm = (np.clip(wav, -1, 1) * 32767).astype(np.int16)
    with wave.open(dst, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(model.config.sampling_rate); w.writeframes(pcm.tobytes())
    return dst
