# Dil və ölkə sistemi (KOSMOS videosu)
Videoda **dəyişə bilən iki ayrı şey** var; hər biri öz paketidir, bir-birindən asılı deyil.

## 1. Dil paketi — `tools/lang/<dil>.json`
Şəhər adları, qonşu adları, brend pill yazısı, **səs mətni**. Hazır: `az`, `en`, `ru`, `tr`.
İşə salmaq: `KOSMOS_LANG=ru python3 old_clean.py ...`
Yazılar kodla (text-fx) çəkilir, Inter şrifti 4 dili də dəstəkləyir (kiril, türk hərfləri yoxlanıb).
Uzun ad kənardan çıxmasın deyə mövqe pəncərəyə sıxılır.

## 2. Ölkə paketi — `tools/countries/<ölkə>.json`
Mərkəz (hub), şəhərlər (koordinatla), qonşular (koordinatla), xəritə mənbəyi (rayon/sərhəd faylları). Hazır: `az`.
**Vacib məhdudiyyət:** hazırkı video Gemini-nin Azərbaycan peyk kadrının üstünə yazı qoyur. Başqa ölkə (Moskva, Türkiyə...) üçün iki yol var:
- (a) ölkə üçün yeni xam kadr (Gemini) + eyni overlay,
- (b) tam kodla xəritə (`mapscene` / `oldmap_scene`), ölkə paketindən oxuyur — Gemini-dən asılı deyil.
Sistemin hədəfi (b)-dir ("xəritə real mənbədən, kodla").

## 3. Səs
Dil dəyişəndə **səs də dəyişir**. Gemini səsi yalnız Azərbaycan dilindədir. Hər dil üçün: təsdiqlənmiş mətn → tərcümə (insan yoxlayır) → öz səs mühərriki ilə səsləndirmə → musiqiyə yerləşdirmə. Bu, ayrıca səs bölməsidir.

## 4. Tərcümə qaydası
Adlar tərcümə cədvəlindən gəlir (avtomatik tərcümə yox), çünki coğrafi adlar rəsmi yazılışla olmalıdır. Yeni dil = yeni json faylı, kod dəyişmir.

## Əsas qayda: beynəlxalq standart (2026-10-24)
Sistem Azərbaycana görə yox, BEYNƏLXALQ qaydalara görə qurulur. Əsas (master) dil = ingilis; ad sistemləri, xidmət/məhsul adları və videodakı mətnlər beynəlxalq peşəkar terminlə təyin olunur (araşdırmaya əsasən). az/ru/tr yalnız tərcümə paketləridir (tools/lang/*.json). Marka adı (QAYO TEXNOLOGİYA) logo faylı kimi bütün dillərdə eyni qalır. Adlar hər dəfə yenidən müzakirə olunmur — paketdə təsdiqlənib, yalnız paket dəyişir.
Proqram qrupları (master): 01 WEB PLATFORMS · 02 MOBILE APPS · 03 DESKTOP SOFTWARE · 04 IoT & EMBEDDED SYSTEMS.
