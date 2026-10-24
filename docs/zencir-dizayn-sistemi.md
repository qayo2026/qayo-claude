# QAYO zənciri — vahid dizayn sistemi və "layihə tamamdır" meyarı
Konsept: 6 səhnə, 1 vizual dil (təbii görüntü + işıq). Hər halqa eyni sistemdən çıxır; baxan "hamısı bir əldən çıxıb" görməlidir.

## 1. Zəncir
01 Kosmos → 02 Texnologiya → 03 Dünya → 04 Azərbaycan → 05 Bakı → 06 İnşaat → 07 Kataloq (web, son).
Halqalar arasında **bir ortaq element** keçir: ağ-mavi işıq xətti (şüa / qövs). Əvvəlki halqa onunla bitir, növbəti onunla başlayır.

## 2. Vizual dil (referans: "Təbii görüntü + işıq" və "Təbii tonlar")
- **Fon/görüntü:** təbii tonlar (yer, dəniz, bulud, şəhər) — süni rəngli filtr yoxdur. Tünd göy fon: `#000818` / `#061327`.
- **İşıq:** yalnız ağ-mavi (ağ, `#5CE1FF` parıltısı). Qövslər, düyünlər, şüa — hamısı bu rəngdə.
- **Yazılar:** Inter Bold, ağ-mavi parıltı, kodla (text-fx), solğun olmaz. Şəhər/obyekt adları ağ-mavi.
- **Vurğu rəngləri (hər biri tək məqsədlə):** kəhrəba `#FFC46B` = yalnız sərhəd/qonşu kateqoriyası; qırmızı = yalnız QAYO loqosu. Başqa rəng yoxdur (biri sarı, biri qırmızı olmaz).
- **Lövhə (pill):** şüşə üslublu, "QAYO TEXNOLOGİYA", oxunaqlı, hər halqada eyni.
- **Format:** 1080×1920, 9:16, MP4, H.264, 30 FPS, AAC. Göstərmə: tam ekran video, ⋯ → Download, başqa heç nə.

## 3. Ortaq funksionallıq (hər layihədə eyni)
1. Dil paketi (`tools/lang/`) — dil dəyişir, kod dəyişmir.
2. Ölkə paketi (`tools/countries/`) — ölkə/şəhər dəyişir.
3. Qırılma radarı (`seam_radar.py`) — səs, musiqi, söz, görüntü.
4. Standart yoxlama `/api/video` (`ready`, ölçü, hash).
5. Kodun GitHub nüsxəsi (başqa yerə daşımaq üçün).
6. Səs mühərriki (öz sistemimiz) — Gemini səsindən asılılıq yoxdur.

## 4. "Layihə tamamdır" (Definition of Done) — 10 bənd
1. Görüntü təsdiqlənib (səsdən əvvəl).
2. Rəng sistemi yuxarıdakı paletə uyğundur.
3. Yazı/adlar kodla, düzgün yazılışla, canlı rəngdə.
4. Xəritə/coğrafi adlar real mənbədən.
5. Qırılma radarı: SƏS / MUSİQİ / SÖZ / GÖRÜNTÜ təmiz (radar + qulaq).
6. Söz təkrarı yoxdur, sözə calaq yoxdur.
7. Format standartına uyğundur (`ready: true`).
8. Əvvəlki və növbəti halqa ilə keçid (ortaq işıq xətti) oturur.
9. Kod və fayl GitHub-dadır, namizəd fayllar təmizlənib (bir son versiya).
10. Anar "Canlıya qoy" deyib, canlı link yoxlanıb.

## 5. Vəziyyət
| Halqa | Görüntü | Səs | Canlı |
|---|---|---|---|
| 01 KOSMOS | tamam (V37) | Gemini səsi, qırılma yoxdur; öz səs mühərriki hələ yox | V37 canlı |
| 02–07 | başlanmayıb (hər biri bu sistemlə) | — | — |

Qayda: DoD-dən keçməyən halqa tamam sayılmır və növbəti halqaya keçilmir.
