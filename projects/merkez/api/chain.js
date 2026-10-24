import { db } from 'hatchable';
export const access = 'public';
export const methods = ['GET'];
const RULES = [
  'Zəncir 7 halqadır: 1 KOSMOS, 2 TEX BREND, 3 DÜNYA, 4 SMART AZƏRBAYCAN, 5 SMART BAKU, 6 QAYO İNŞAAT, 7 KATALOK web son.',
  'İctimaiyyət BİR video və BİR fasiləsiz mətn görür; halqalar yalnız içəridəki bölgüdür.',
  'Bütün zəncir üçün BİR səs mənbəyi və BİR musiqi qatı; hər videonun öz (Gemini) səsi silinir.',
  'Keçidlərdə görüntü dəyişir, səs və musiqi kəsilmir.',
  'Fon və vurğu rəngləri ümumi palitradan çıxmır (1-5 tünd göy + qırmızı vurğu, 7 şirkət rəngləri).',
  'Hər halqada: video/layihə hazır, səs mətni təsdiqlənmiş, fon və vurğu rəngi, növbəti keçid təyin olunmalıdır.',
  'Zəncir yalnız bütün çatışmazlıqlar bağlananda göndərməyə hazır sayılır; Anar "Canlıya qoy" deməmiş heç nə yayımlanmır.'
];
export default async function (req, res) {
  const c = await db.query('SELECT pos, slug, name, kind, link, asset_status, voice_text, voice_ok, bg_color, accent_color, transition_next, note, updated_at FROM chain ORDER BY pos');
  const m = await db.query('SELECT key, value, note FROM chain_meta ORDER BY key');
  const links = c.rows.map(r => {
    const missing = [];
    if (r.asset_status !== 'hazır') missing.push('video/layihə hazır deyil (' + r.asset_status + ')');
    if (!r.voice_text) missing.push('səs mətni yoxdur');
    else if (!r.voice_ok) missing.push('səs mətni təsdiqlənməyib');
    if (!r.bg_color) missing.push('fon rəngi yoxdur');
    if (!r.accent_color) missing.push('vurğu rəngi yoxdur');
    if (r.pos < c.rows.length && !r.transition_next) missing.push('növbəti keçid təyin olunmayıb');
    return { ...r, missing };
  });
  const global = m.rows.map(r => ({ key: r.key, value: r.value, note: r.note, missing: !r.value }));
  const open = links.reduce((n, l) => n + l.missing.length, 0) + global.filter(g => g.missing).length;
  res.setHeader('Cache-Control', 'no-store');
  res.json({ title: 'QAYO ZƏNCİR 001', ready: open === 0, open_items: open, rules: RULES, global, links });
}