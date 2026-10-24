# Video qırılma qaydaları (KOSMOS-dan çıxan dərslər)
Hər yeni video (Dünya, Azərbaycan, Smart Worker...) bu 8 maddədən keçməlidir. Alətlər: `tools/kosmos-build/`.

## SƏS / SÖZ
1. **Sözə calaq yoxdur.** Sözün içində heç nə kəsilmir, uzadılmır, təkrarlanmır. Boşluq lazımdırsa yalnız musiqi uzadılır.
2. **Söz sərhədi əvvəlcə tapılır.** Danışıq zolağında (300–3400 Hz) enerji + spektrogram ilə sözün son səsi (məs. "k" partlayışı) tapılır. Uzatma/keçid sözün son səsindən ən az 0,15 san sonra başlayır. (KOSMOS: "k" 9,55-də idi, uzatma 9,45-də başlamışdı → "yerdəyikk".)
3. **Təkrar yoxlaması dalğa ilə yox, spektrlə.** Dalğa korelyasiyası təkrar sözü tapmır; mel/spektrogram pəncərəsi ilə yoxlanır. Qısa (millisaniyə) kəkələmə də spektrogramda görünür.
4. **Gemini səsinin qalıq qüsuru** (artıq hecalar, kəkələmə) yalnız danışıq zolağını həmin aralıqda azaltmaqla (`voice_fix.py`) düzəlir, vaxt dəyişmir. Əsl həll: öz səs mühərrikimiz.

## MUSİQİ
5. **İki fərqli musiqi anı üst-üstə qarışdırılmır** (crossfade ilə calaq tonları bir-birinə qarışdırır). Boşluq üçün musiqi parçası `rubberband` ilə ton dəyişmədən yavaş uzadılır; heç bir calaq nöqtəsi qalmır.

## GÖRÜNTÜ
6. **Geri tullanma yoxdur.** Yavaşıma/ləngimə mövcud kadrdan davam edir, əvvəlki kadra qayıtmır. Ləngimə xəritə tam açılandan sonra, loqoya keçməzdən əvvəl 1–2 san.
7. **Sinxron:** video nə qədər uzanırsa, səs eyni qədər uzanır; loqo zərbəsi öz kadrında qalır.

## YOXLAMA
8. **Qırılma radarı** (`seam_radar.py`) hər namizəd üçün 4 ayrı başlıqda: SƏS, MUSİQİ, SÖZ, GÖRÜNTÜ. Radardan keçməyən fayl göndərilmir. Radar tapır, amma son qərarı insan qulağı verir (orijinalın öz zərbələri radara "qırılma" görünə bilər).

## Qalan zəif yer / növbəti addım
- Radar orijinalın öz zərbəsini calaqdan ayırmır → "orijinala nisbətən fərq" rejimi əlavə olunmalıdır.
- Radarda "söz sonu təhlükəsi" yoxlaması (uzatma sözün son səsinə yaxındırmı) əlavə olunmalıdır.
- Mərkəzi bazaya (QAYO LAB) yalnız "Canlıya qoy" sözündən sonra bağlanır.
