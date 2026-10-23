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

export function parseMp4(buf) {
  const b = new Uint8Array(buf), dv = new DataView(buf);
  const top = boxes(b, dv, 0, b.length);
  const moov = top.find(x => x.type === 'moov');
  if (!moov) return { error: 'moov yoxdur' };
  const ft = top.find(x => x.type === 'ftyp');
  const res = { tracks: [], duration: 0, brand: ft ? String.fromCharCode(b[ft.s], b[ft.s + 1], b[ft.s + 2], b[ft.s + 3]) : '' };
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
  return res;
}

export function measure(buf) {
  const info = parseMp4(buf);
  if (info.error) return { ready: false, problems: [info.error] };
  const v = info.tracks.find(t => t.kind === 'vide'), a = info.tracks.find(t => t.kind === 'soun');
  const W = v ? v.w : 0, H = v ? v.h : 0;
  const fps = v && v.dur ? v.samples / v.dur : 0;
  const m = { size: W + 'x' + H, fps: Math.round(fps * 100) / 100, video: v ? (v.codec === 'avc1' || v.codec === 'avc3' ? 'H.264' : v.codec) : null, audio: a ? (a.codec === 'mp4a' ? 'AAC' : a.codec) : null, duration_s: Math.round(info.duration * 10) / 10 };
  const problems = [];
  if (W !== 1080 || H !== 1920) problems.push('olcu ' + m.size + ' (lazim 1080x1920)');
  if (Math.abs(fps - 30) >= 0.5) problems.push('FPS ' + m.fps + ' (lazim 30)');
  if (m.video !== 'H.264') problems.push('video kodek ' + m.video);
  if (m.audio !== 'AAC') problems.push('ses ' + (m.audio || 'yoxdur'));
  return { measured: m, ready: problems.length === 0, problems };
}