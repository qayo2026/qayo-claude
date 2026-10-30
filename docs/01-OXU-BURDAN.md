# 01 QAYO İNŞAAT — SON VƏZİYYƏT (30 oktyabr 2026)

**Əvvəl bunu oxu.** Canlı sayt (qayoconstruction.com) yeganə həqiqətdir; bu fayl onun xəritəsidir. Köhnə `00_SAHIB_BURADAN_BASLA.md` 20 oktyabr vəziyyətidir, köhnəlmiş ola bilər.

## Prinsip
- Hər layihə özü bir bazadır: kod, media, qeyd və son vəziyyət layihənin öz içindədir. Başqa AI bura girib birbaşa son versiyaya baxır; ayrıca mərkəz və ya başqa AI-dən asılılıq yoxdur.

## Canlı
- Sayt: https://qayoconstruction.com — Hatchable v677, hamısı sahibin təsdiqi ilə.

## Giriş videosu (üz qabığı)
- Zəncir: `pages/onlayn-satis.js` → `/qayo-intro-video/intro.js?v=14` → `player.html?v=14` → `qayo-insaat-azerbaycan-web.mp4?v=18`.
- Üz qabığı: yuxarıda QAYO İNŞAAT lockup, altında hərəkətli qlobus, nömrə/cədvəl yoxdur. Video özü toxunulmazdır.
- Videonu dəyişəndə `?v=` nömrələrini artır (telefon keşi).
- Eyni video ayrıca layihədə: QAYO İNŞAAT AZƏRBAYCAN VİDEO (qayo-insaat.hatchable.site), yükləmə düyməsi ilə.

## Link önizləmə şəkli (WhatsApp)
- Fayl: `public/og/qayo-link-onizleme-1200x630.jpg` (4 qrup pəncərəsi, nömrəsiz, 2 mərtəbəli əlaqə bloku).
- Meta: `pages/onlayn-satis.js` və `pages/catalog.js` (og:image, twitter:image), hazırda `?v=20261030c`. Şəkil dəyişəndə hərf/nömrə artır.

## GitHub (son nüsxə)
- `qayo2026/qayo-claude`, branch `video-synth-update`: `media/teqdimat-video/`, `media/insaat-azerbaycan/`, `media/link-onizleme/`.
- Paylaşım ölçüləri: Story 1080×1920 və Feed 1080×1350 (namizəddir, hələ canlı deyil).

## Qaydalar
- "Canlıya qoy" = GitHub son nüsxə + Hatchable deploy + canlı yoxlama. O deməmiş heç nə canlıya çıxmır; yeni iş namizəd qalır.
- Hər layihədə bir son versiya. Silmə yalnız dəqiq siyahı və sahibin təsdiqi ilə.
- QAYO AI MƏRKƏZ-ə yazma: hər layihə özü bir mərkəzdir.

## Açıq
- 45 köhnə faylın təmizliyi sahibin təsdiqini gözləyir (siyahı: QAYO_01_ikinci_temizlik_siyahisi.txt).
- Arxiv layihəsi (g0gpjf) Private edilməlidir (sahib edir).

## Səs
- Giriş videosu səssiz başlayır, ilk toxunuşda (barmaq qalxanda) səs açılır — brauzer qaydasıdır, aşmaq olmur.
- Vərəq çevirmə səsləri: `public/qayo-catalog-navigation.js` (WebAudio, 4 seçim); iPhone səssiz düyməsinə baxmasın deyə `navigator.audioSession.type="playback"`. Fayl dəyişəndə `?v=` artır (hazırda 8).
