// QAYO RADAR (layihə hazırlıq yoxlaması). İstifadə: GET /api/radar?project=kosmos|brand  (project=all hamısı)
// Hər layihə KOSMOS standartından keçməlidir: canlı, video, arxa kod (GitHub), versiya qaydası.
import { db } from 'hatchable';
export const access = 'public';
export const methods = ['GET'];

const GH = 'qayo2026/qayo-claude';
const MAX_BYTES = 10 * 1024 * 1024;
const PROJECTS = {
  kosmos: { dir: 'kosmos', name: 'KOSMOS', key: 'KOSMOS', site: 'https://qayo-kosmos.hatchable.site', media: '/media/qayo-kosmos-original.mp4', gh: 'media/qayo-kosmos-original.mp4', tools: 'tools/kosmos-video', api: '/api/video' },
  brand: { dir: 'brand', name: 'QAYO BRAND TEXNOLOGİYA', key: 'BRAND', site: 'https://qayo-brand.hatchable.site', media: '/media/qayo-brand-master.mp4', gh: 'media/qayo-brand-master.mp4', tools: 'tools/brand-video', api: '/api/video' }
};

function boxes(b, dv, s, e) {
  const out = []; let p = s;
  while (p + 8 <= e) {
    let size = dv.getUint32(p); const type = String.fromCharCode(b[p + 4], b[p + 5], b[p + 6], b[p + 7]); let hdr = 8;
    if (size === 1) { size = Number(dv.getBigUint64(p + 8)); hdr = 16; } else if (size === 0) size = e - p;
    if (size < hdr) break;
    out.push({ type, s: p + hdr, e: Math.min(p + size, e) }); p += size;
  }
  return out;
}
function measure(buf) {
  const b = new Uint8Array(buf), dv = new DataView(buf);
  const top = boxes(b, dv, 0, b.length);
  const moovI = top.findIndex(x => x.type === 'moov'), mdatI = top.findIndex(x => x.type === 'mdat');
  const moov = top[moovI];
  if (!moov) return { problems: ['moov yoxdur'], faststart: false, measured: null };
  const res = { tracks: [], duration: 0 };
  const kids = boxes(b, dv, moov.s, moov.e);
  const mvhd = kids.find(x => x.type === 'mvhd');
  if (mvhd) { const v = b[mvhd.s]; const ts = dv.getUint32(mvhd.s + (v === 1 ? 20 : 12)); const du = v === 1 ? Number(dv.getBigUint64(mvhd.s + 24)) : dv.getUint32(mvhd.s + 16); res.duration = ts ? du / ts : 0; }
  for (const t of kids.filter(x => x.type === 'trak')) {
    const tk = boxes(b, dv, t.s, t.e); const tr = { kind: '', samples: 0, w: 0, h: 0 };
    const tkhd = tk.find(x => x.type === 'tkhd');
    if (tkhd) { const v = b[tkhd.s]; const o = tkhd.s + (v === 1 ? 88 : 76); tr.w = Math.round(dv.getUint32(o) / 65536); tr.h = Math.round(dv.getUint32(o + 4) / 65536); const mo = tkhd.s + (v === 1 ? 52 : 40); if (Math.abs(dv.getInt32(mo + 4)) > Math.abs(dv.getInt32(mo))) { const x = tr.w; tr.w = tr.h; tr.h = x; } }
    const mdia = tk.find(x => x.type === 'mdia');
    if (mdia) {
      const md = boxes(b, dv, mdia.s, mdia.e);
      const hdlr = md.find(x => x.type === 'hdlr');
      if (hdlr) tr.kind = String.fromCharCode(b[hdlr.s + 8], b[hdlr.s + 9], b[hdlr.s + 10], b[hdlr.s + 11]);
      const mdhd = md.find(x => x.type === 'mdhd');
      if (mdhd) { const v = b[mdhd.s]; const ts = dv.getUint32(mdhd.s + (v === 1 ? 20 : 12)); const du = v === 1 ? Number(dv.getBigUint64(mdhd.s + 24)) : dv.getUint32(mdhd.s + 16); tr.dur = ts ? du / ts : 0; }
      const minf = md.find(x => x.type === 'minf');
      if (minf) { const stbl = boxes(b, dv, minf.s, minf.e).find(x => x.type === 'stbl'); if (stbl) { const sb = boxes(b, dv, stbl.s, stbl.e); const stsz = sb.find(x => x.type === 'stsz'); if (stsz) tr.samples = dv.getUint32(stsz.s + 8); const stsd = sb.find(x => x.type === 'stsd'); if (stsd) tr.codec = String.fromCharCode(b[stsd.s + 12], b[stsd.s + 13], b[stsd.s + 14], b[stsd.s + 15]); } }
    }
    res.tracks.push(tr);
  }
  const v = res.tracks.find(t => t.kind === 'vide'), a = res.tracks.find(t => t.kind === 'soun');
  const W = v ? v.w : 0, H = v ? v.h : 0, fps = v && v.dur ? v.samples / v.dur : 0;
  const m = { size: W + 'x' + H, fps: Math.round(fps * 100) / 100, video: v ? (v.codec === 'avc1' || v.codec === 'avc3' ? 'H.264' : v.codec) : null, audio: a ? (a.codec === 'mp4a' ? 'AAC' : a.codec) : null, duration_s: Math.round(res.duration * 10) / 10 };
  const problems = [];
  if (W !== 1080 || H !== 1920) problems.push('ölçü ' + m.size + ' (lazım 1080x1920)');
  if (Math.abs(fps - 30) >= 0.5) problems.push('FPS ' + m.fps + ' (lazım 30)');
  if (m.video !== 'H.264') problems.push('video kodek ' + m.video);
  if (m.audio !== 'AAC') problems.push('səs ' + (m.audio || 'yoxdur'));
  return { measured: m, problems, faststart: mdatI < 0 || moovI < mdatI };
}
const hex = async buf => [...new Uint8Array(await crypto.subtle.digest('SHA-256', buf))].map(x => x.toString(16).padStart(2, '0')).join('');
const get = async (url, opt) => { try { return await fetch(url, opt); } catch (e) { return null; } };

async function run(p) {
  const checks = []; // {group, name, ok, detail}
  const add = (group, name, ok, detail) => checks.push({ group, name, ok: !!ok, detail: detail || '' });
  // ---- CANLI
  const sr = await get(p.site);
  const html = sr && sr.ok ? await sr.text() : '';
  add('CANLI', 'səhifə açılır', sr && sr.ok, sr ? 'HTTP ' + sr.status : 'əlçatmaz');
  add('CANLI', 'səhifə master videoya bağlıdır', html.includes(p.media), p.media);
  // ---- VİDEO
  const mr = await get(p.site + p.media);
  let sha = null, ms = null;
  if (mr && mr.ok) {
    const buf = await mr.arrayBuffer();
    sha = await hex(buf); ms = measure(buf);
    add('VİDEO', 'fayl endirilir, tip video/mp4', (mr.headers.get('content-type') || '').includes('video/mp4'), mr.headers.get('content-type') || '');
    add('VİDEO', 'ölçü ≤ 10 MB (Hatchable limiti)', buf.byteLength <= MAX_BYTES, (buf.byteLength / 1048576).toFixed(2) + ' MB');
    add('VİDEO', 'standart 1080×1920 · 30 fps · H.264 · AAC', ms.problems.length === 0, ms.problems.length ? ms.problems.join('; ') : JSON.stringify(ms.measured));
    add('VİDEO', 'faststart (iPhone-da qara ekran olmasın)', ms.faststart, ms.faststart ? 'moov əvvəldədir' : 'moov sondadır');
  } else add('VİDEO', 'fayl endirilir', false, mr ? 'HTTP ' + mr.status : 'əlçatmaz');
  // ---- SERVER (öz yoxlama funksiyası)
  const ar = await get(p.site + p.api);
  let aj = null;
  if (ar && ar.ok) { try { aj = await ar.json(); } catch (e) {} }
  add('SERVER', p.api + ' funksiyası var', !!aj, ar ? 'HTTP ' + ar.status : 'əlçatmaz');
  if (aj) {
    add('SERVER', p.api + ' ready=true', aj.ready === true, (aj.problems || []).join('; '));
    add('SERVER', 'funksiyanın hash-ı faylla eynidir', sha && aj.file_sha256 === sha, '');
  }
  // ---- ARXA KOD (GitHub)
  const gr = await get('https://raw.githubusercontent.com/' + GH + '/main/' + p.gh);
  if (gr && gr.ok) {
    const gsha = await hex(await gr.arrayBuffer());
    add('ARXA KOD', 'GitHub nüsxəsi canlı fayl ilə eynidir', sha && gsha === sha, 'GitHub ' + gsha.slice(0, 8) + ' · canlı ' + (sha || '?').slice(0, 8));
  } else add('ARXA KOD', 'GitHub nüsxəsi var', false, gr ? 'HTTP ' + gr.status : 'əlçatmaz');
  const tr = await get('https://api.github.com/repos/' + GH + '/contents/' + p.tools, { headers: { 'User-Agent': 'qayo-radar', Accept: 'application/vnd.github+json' } });
  add('ARXA KOD', 'hazırlanma skriptləri GitHub-dadır (' + p.tools + ')', tr && tr.ok, tr ? 'HTTP ' + tr.status : 'əlçatmaz');
  // layihenin oz kodu GitHub-dadir (sabah basqa yere dasimaq ucun)
  const cr = await get('https://api.github.com/repos/' + GH + '/git/trees/main?recursive=1', { headers: { 'User-Agent': 'qayo-radar', Accept: 'application/vnd.github+json' } });
  let paths = [];
  if (cr && cr.ok) { try { paths = (await cr.json()).tree.map(x => x.path); } catch (e) {} }
  const need = ['api/video.js', 'lib/mp4.js', 'public/index.html', 'hatchable.toml'];
  const miss = need.filter(f => !paths.includes('projects/' + p.dir + '/' + f));
  add('ARXA KOD', 'layihe kodu GitHub-dadir (projects/' + p.dir + ')', cr && cr.ok && miss.length === 0, miss.length ? 'yoxdur: ' + miss.join(', ') : need.length + ' fayl');
  const ir = await get('https://raw.githubusercontent.com/' + GH + '/main/projects/' + p.dir + '/public/index.html');
  // host canli HTML-e oz elaveni qoyur, ona gore tam hash yox, esas hisse (body) mueyyen olunur
  const gh = ir && ir.ok ? await ir.text() : '';
  const bodyOf = s => { const i = s.indexOf('<body'); const j = s.lastIndexOf('</body>'); return i >= 0 && j > i ? s.slice(i, j).replace(/\s+/g, '') : null; };
  const gb = bodyOf(gh), lb = bodyOf(html);
  add('ARXA KOD', 'GitHub-daki sehife kodu canli sehife ile eynidir', !!gb && !!lb && lb.includes(gb.slice(gb.indexOf('>') + 1)), gb ? (lb ? 'govde ' + gb.length + ' simvol' : 'canli govde tapilmadi') : 'GitHub nusxesi yoxdur');
  const nr = await get('https://api.github.com/repos/' + GH + '/contents/media/namized', { headers: { 'User-Agent': 'qayo-radar', Accept: 'application/vnd.github+json' } });
  let left = [];
  if (nr && nr.ok) { try { left = (await nr.json()).map(x => x.name).filter(n => n.toLowerCase().includes(p.key.toLowerCase())); } catch (e) {} }
  add('ARXA KOD', 'GitHub-da namizəd qalığı yoxdur', left.length === 0, left.join(', '));
  // ---- VERSİYA (mərkəzi baza)
  const rows = (await db.query("SELECT label,status,where_it_is FROM versions WHERE project = $1 AND status <> 'silindi'", [p.key])).rows;
  const son = rows.filter(r => r.status === 'son'), nam = rows.filter(r => r.status !== 'son');
  add('VERSİYA', 'bazada yalnız bir SON versiya var', son.length === 1, son.length + ' son');
  add('VERSİYA', 'namizəd/qaralama qalığı yoxdur', nam.length === 0, nam.map(r => r.label).join(', '));
  add('VERSİYA', 'SON qeydi canlı hash-a uyğundur', son.length === 1 && sha && (son[0].where_it_is || '').includes(sha.slice(0, 8)), son[0] ? son[0].where_it_is : '');
  const jr = (await db.query("SELECT count(*)::int n FROM journal WHERE project = $1", [p.key])).rows[0].n;
  add('VERSİYA', 'jurnalda qeyd var', jr > 0, jr + ' qeyd');
  const fails = checks.filter(c => !c.ok);
  return { project: p.name, passed: fails.length === 0, total: checks.length, failed: fails.length, checks };
}

export default async function (req, res) {
  const q = (req.query && req.query.project) || 'all';
  const list = q === 'all' ? Object.keys(PROJECTS) : [q];
  const out = [];
  for (const k of list) {
    if (!PROJECTS[k]) return res.status(404).json({ error: 'layihə yoxdur', available: Object.keys(PROJECTS) });
    out.push(await run(PROJECTS[k]));
  }
  res.setHeader('Cache-Control', 'no-store');
  return res.json({
    radar: 'QAYO RADAR v1',
    rule: 'Layihə yalnız passed=true olanda hazırdır. Qalmayanda növbəti layihəyə keçilmir.',
    all_passed: out.every(o => o.passed),
    results: out
  });
}