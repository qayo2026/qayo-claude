// QAYO BRAND TEXNOLOGİYA: vahid menbe. Her AI musteri ucun link ve yukleme melumatini buradan goturmelidir.
import { measure } from 'lib/mp4.js';
export const access = 'public';
export const methods = ['GET'];

const SITE = 'https://qayo-brand.hatchable.site';
const FILE = SITE + '/media/qayo-brand-master.mp4';
// tesdiqlenmis master (lib/internal/brand-master-manifest.json ile eyni olmalidir)
const EXPECTED_SHA = 'ea09f6219d4a695a4d49a1e78e5f46938e693649fad75a95855cf9e25b5607f8';

export default async function (req, res) {
  let size = null, sha256 = null, check = { ready: false, problems: ['fayl oxunmadi'] };
  try {
    const r = await fetch(FILE);
    if (r.ok) {
      const buf = await r.arrayBuffer();
      size = buf.byteLength;
      const d = await crypto.subtle.digest('SHA-256', buf);
      sha256 = [...new Uint8Array(d)].map(x => x.toString(16).padStart(2, '0')).join('');
      check = measure(buf);
      if (sha256 !== EXPECTED_SHA) { check.ready = false; check.problems = (check.problems || []).concat('hash tesdiqlenmis master ile uygun deyil'); }
    }
  } catch (e) {}
  res.setHeader('Cache-Control', 'public, max-age=60');
  return res.json({
    name: 'QAYO BRAND TEXNOLOGİYA',
    send_to_customer: SITE,
    video_file: FILE,
    download: 'Səhifədə ⋯ → Download',
    file_size_bytes: size,
    file_sha256: sha256,
    expected_sha256: EXPECTED_SHA,
    ready: check.ready,
    problems: check.problems,
    measured: check.measured || null,
    standard: { size: '1080x1920', aspect: '9:16', format: 'MP4', video: 'H.264', fps: 30, audio: 'AAC' },
    rules_for_ai: [
      'Müştəriyə yalnız send_to_customer linkini ver.',
      'ready=false isə müştəriyə göndərmə, Anara problems siyahısını de.',
      'Videonu yükləyib yenidən göndərmə, çünki sıxıla bilər.',
      'Linki, hash-i və standartları dəyişdirmə, yalnız bu cavabdan götür.'
    ]
  });
}