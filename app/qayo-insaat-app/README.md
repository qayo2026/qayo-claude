# QAYO İNŞAAT — mobil tətbiq qabığı

Bir kod, iki mağaza: `com.qayoconstruction.insaat` (iPhone/iPad + Android + Huawei APK).
Qabıq saytı (qayoconstruction.com/catalog) açır, məhsul və qiymət saytdan oxunur — mağazaya yenidən göndərmək lazım deyil.

## Qaydalar
1. Ad: QAYO İNŞAAT (hər mağazada eyni).
2. Sayt dəyişəndə tətbiq avtomatik yenilənir.
3. Apple üçün qabıqda real telefon funksiyaları da olmalıdır (paylaş, WhatsApp, bildiriş) — növbəti mərhələ.

## Hazırlıq (developer hesabı açılandan sonra)
- Android: `npm i && npm run android` → Android Studio ilə `.aab` (Google Play Console-a yüklənir).
- iPhone: `npm i && npm run ios` → Mac yoxdursa bulud build (Codemagic/EAS) ilə `.ipa`, App Store Connect-ə yüklənir.
- İkon: 1024×1024 PNG (App Store), adaptiv ikon (Android) — ikon seçiləndən sonra əlavə olunur.

## Status
Qabıq hazırdır, mağaza hesabları gözlənilir. Canlı sayta toxunmur.
