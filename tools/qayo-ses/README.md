# QAYO SƏS — öz səs sistemimiz

Məqsəd: səs→mətn, mətn→səs, səs kəs/calaq, vaxta oturt, qırılma radarı — kənar xidmətdən (Gemini, OpenAI) asılı olmadan, öz serverimizdə.

## Vəziyyət (2026-10-26)
- HAZIR və sınanıb (model tələb etmir): `qayo_ses/audio.py` (phrases, cut, splice, place, fit_tempo), `qayo_ses/radar.py` (klik, boşluq, kəsik, təkrar söz). Test: `PYTHONPATH=. python3 tests/test_audio.py`
- YAZILIB, hələ SINANMAYIB (modellər serverdə endirilməlidir): `stt.py` (faster-whisper, Azərbaycan), `tts.py` (Meta MMS azj-script_latin), `server.py` (FastAPI: /stt /tts /phrases /cut /splice /radar)
- GÖZLƏYİR: icra serveri seçimi (VPS / Claude self-hosted / Remote Control). Hatchable-da işləmir (64 MB, WebAssembly yoxdur) — Hatchable yalnız mərkəz (baza, fayl, növbə) olur və bu xidməti çağırır.

## Serverdə qaldırmaq
    export QAYO_KEY=<gizli açar>
    docker compose up -d --build        # ilk /stt və /tts çağırışında modellər endirilir
    curl localhost:8000/health

## Qaydalar (Anarın)
- Sözə calaq verilməz (təkrar söz radarı), boşluq lazımdırsa musiqiyə calaq.
- Öz diktor səsi sonra təlim ediləcək; /tts interfeysi dəyişməyəcək.
- Namizəd → "Canlıya qoy" deməmiş canlıya keçmir.
