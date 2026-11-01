# QAYO FİHRİST — hər şeyin yeri (1–2 ildən sonra da tapmaq üçün)

Son yenilənmə: 2026-11-01. **Əvvəl bunu oxu.** Köhnə sənədlər: `docs/projects/README.md` (tarixçə).

## 1. Layihələr — cəmi 6 (hər biri ayrıdır, bir-biri ilə qarışmır)
Ölçülər hamısında eynidir: 9x16 (sayt, Story, Reels) · 4x5 (lent, Facebook, Instagram) · 16x9 (YouTube, LinkedIn)

| № | Hatchable layihəsi (ad) | slug / ünvan | Nədir |
|---|---|---|---|
| 1 | 01 — QAYO İNŞAAT: WEB SAYT + VİDEO | qayo-web-catalog · qayoconstruction.com | Əsas sayt + giriş videosu |
| 2 | 02 — QAYO İNŞAAT: MP4 VİDEO | qayo-insaat-video | İNŞAAT videosu, 3 ölçü, yükləmə |
| 3 | 03 — QAYO İNŞAAT: KATALOQ + QİYMƏT | qayo-insaat-onlayn | Sayta bağlı onlayn kataloq + qiymət sistemi |
| 4 | 04 — QAYO İNŞAAT: PDF B2B | qayo-insaat-pdf-b6d5 · catalog.qayoconstruction.com | Tam müstəqil B2B kataloq + "QAYO İNŞAAT Məhsul Kataloqu.pdf"; heç nəyə bağlı deyil |
| 5 | 05 — QAYO İNŞAAT: ŞƏKİLLƏR | qayo-insaat-sekiller | Postlar (Post 4x5, Post 9x16), sonra vizit kart, broşür |
| 6 | 06 — QAYO TEXNOLOGİYA | qayo-texnologiya-3 (domen sonra) | Ayrı brend, TEXNOLOGİYA videosu, 3 ölçü |

Bunlardan kənardakı hər şey (KOSMOS, LAB, Studio 2, MONEY MAP, Energy Pay, BRAND, WORLD SEARCH, "ARXİV" və s.) bu 6-ya aid deyil.
Hər video layihəsində `public/videos.json` var: hər faylın standart adı, ölçüsü, təyinatı, yolu. AI xidmətləri oradan oxuyur.

## 2. Video faylları (GitHub: `qayo2026/qayo-claude`)
- `media/insaat/QAYO İNŞAAT Video 9x16|4x5|16x9.mp4` (30 san. = 20 san. Dünya→Azərbaycan→Bakı + 10 san. onlayn satış)
- `media/texnologiya/QAYO TEXNOLOGİYA Video 9x16|4x5|16x9.mp4`
- Hatchable fayl yolları: İNŞAAT `/qayo-insaat-9x16.mp4`, `-4x5`, `-16x9`; TEXNOLOGİYA `/media/qayo-texnologiya-9x16.mp4`, `-4x5`, `-16x9`.
- Sayt giriş videosu: `public/qayo-intro-video/qayo-insaat-azerbaycan-web.mp4` (qayo-web-catalog), zəncir: onlayn-satis.js → intro.js?v=15 → player.html?v=15 → mp4?v=19. Videonu dəyişəndə `?v=` nömrələrini artır (telefon keşi).
- Link önizləmə şəkli: `media/og/qayo-link-onizleme-1200x630-20261101.jpg` (saytda `public/og/…`). Şəkli dəyişəndə YENİ fayl adı ver (WhatsApp keşləyir).

## 3. Standartlar
- Ölçülər: 9x16 (Story, Reels, sayt telefon) · 4x5 (Facebook/Instagram lenti) · 16x9 (YouTube, LinkedIn, X).
- Ad: `QAYO İNŞAAT Video 9x16`. Adda "v2", "30s", "_" yoxdur. Ad bir dəfə təyin olunur, dəyişmir.
- Gələcək videolarda fon ağ; mövcud texnologiya videosu tünd göy qalır.
- Şəkli məcburi zolağa salıb kəsmə; yazılar şəklin içinə girmir (16:9-da yuxarı/aşağı zolaq).
- Link önizləməsi: başlıq "QAYO İNŞAAT — BİRLİKDƏ İNŞA EDƏK", təsvir böyük hərflə.

## 3b. Paylaşım sırası
TEXNOLOGİYA videosu (ayrı) · sayt linki (qayoconstruction.com) · İNŞAAT videosu · qiymət cədvəli (catalog.qayoconstruction.com). Müştəriyə "PDF" yox, "qiymət cədvəli" deyilir. PDF adı: `QAYO İNŞAAT Qiymət Cədvəli.pdf`.

## 4. İş qaydası
- Yeni iş əvvəl **namizəd** olur, video faylı kimi göndərilir. "Canlıya qoy" deyəndən sonra: GitHub son nüsxə + Hatchable deploy + canlı yoxlama.
- Layihə silmək yalnız sahibin işidir (Claude silə bilmir). Silinməli köhnələr "ARXİV" adlıdır.
- Yeni layihə açılmır; mövcud layihənin yeni versiyası deploy olunur.

## 5. Açıq məsələlər
- TEXNOLOGİYA layihəsi hələ Private; domen alınanda "Open to web" + domen bağlanır.
- Köhnə İNŞAAT layihələri: video-teqdimat, qayo-insaat (AZƏRBAYCAN VİDEO) — köhnə 20 san. videonu saxlayır; qərar sahibindədir.
- 16:9 İNŞAAT: enli Gemini kadrları gələrsə yenidən qurulur (hazırda yanlar yumşaq fonla doldurulub).
- İSTİLİK/BORU önizləmə şəkli: kataloqdakı 16, 17 və 01, 04 şəkilləri istifadə olunub; orijinal fayllar gələrsə keyfiyyət artır.
