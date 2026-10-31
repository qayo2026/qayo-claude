# QAYO TEXNOLOGİYA video — qurulma mənbəsi (final: V9.27)

Canlı: Hatchable `qayo-texnologiya` (proj_UoyMYEP2jTd1) → /media/qayo-texnologiya.mp4
GitHub nüsxəsi: media/texnologiya/qayo-texnologiya.mp4 (sha256 ad9577e8…6230c)

## Yenidən qurmaq
Mənbə: təmiz master `MASTER_V9.21.mp4` (altyazılı, fonsuz doldurulmamış). Repoda deyil (böyükdür).
    python3 -u pass18.py MASTER_V9.21.mp4 MASTER_V9.27.mp4 1.0
Əsas modul: fill2.compose2 (navy fon, zoom YOXDUR, dither σ2.2, L=28).
Eksportlar:
- 9:16 1080x1920: crf 23
- 4:5 1080x1350: crop 1080:1350:0:190
- Canlı (≤10 MB): -c:v libx264 -preset slow -b:v 1700k -maxrate 2100k -bufsize 4200k -pix_fmt yuv420p -c:a aac -b:a 112k -movflags +faststart

`archive/` — köhnə keçid skriptləri (pass3–16), yalnız tarix üçün; istifadə etmə.
Kadrı KƏSMƏ (crop/zoom yox) — geniş görüntü qaydası.
