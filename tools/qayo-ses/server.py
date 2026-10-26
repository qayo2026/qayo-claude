"""QAYO SƏS xidməti (FastAPI). Hamısı bir ünvanda: /stt /tts /phrases /cut /splice /radar. Hatchable bu ünvanı çağırır."""
import os, uuid, shutil, tempfile
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Header
from fastapi.responses import FileResponse
from qayo_ses import audio, radar
app = FastAPI(title="QAYO SƏS")
KEY = os.environ.get("QAYO_KEY", "")
T = tempfile.mkdtemp()

def _auth(k):
    if KEY and k != KEY: raise HTTPException(401, "açar səhvdir")

def _save(f):
    p = os.path.join(T, uuid.uuid4().hex + "_" + os.path.basename(f.filename or "a"))
    with open(p, "wb") as o: shutil.copyfileobj(f.file, o)
    return p

@app.get("/health")
def health(): return {"ok": True}

@app.post("/phrases")
def phrases(file: UploadFile = File(...), x_key: str = Header("")):
    _auth(x_key); p = _save(file)
    return {"duration": audio.duration(p), "phrases": audio.phrases(p)}

@app.post("/stt")
def stt(file: UploadFile = File(...), lang: str = Form("az"), x_key: str = Header("")):
    _auth(x_key); from qayo_ses import stt as S
    r = S.transcribe(_save(file), lang); r["repeats"] = radar.check_repeats(r["segments"]); return r

@app.post("/tts")
def tts(text: str = Form(...), x_key: str = Header("")):
    _auth(x_key); from qayo_ses import tts as TT
    return FileResponse(TT.speak(text, os.path.join(T, uuid.uuid4().hex + ".wav")), media_type="audio/wav")

@app.post("/cut")
def cut(file: UploadFile = File(...), start: float = Form(...), end: float = Form(...), x_key: str = Header("")):
    _auth(x_key)
    return FileResponse(audio.cut(_save(file), os.path.join(T, uuid.uuid4().hex + ".wav"), start, end), media_type="audio/wav")

@app.post("/splice")
def splice(files: list[UploadFile] = File(...), crossfade: float = Form(0.04), gap: float = Form(0.0), x_key: str = Header("")):
    _auth(x_key)
    return FileResponse(audio.splice([_save(f) for f in files], os.path.join(T, uuid.uuid4().hex + ".wav"), crossfade, gap), media_type="audio/wav")

@app.post("/radar")
def rad(file: UploadFile = File(...), x_key: str = Header("")):
    _auth(x_key); return radar.check_audio(_save(file))
