import { db } from 'hatchable';
export const access = 'member';
export const methods = ['POST'];
const FIELDS = ['name', 'kind', 'link', 'asset_status', 'voice_text', 'voice_ok', 'bg_color', 'accent_color', 'transition_next', 'note'];
export default async function (req, res) {
  const b = req.body || {};
  if (b.meta_key) {
    await db.query('UPDATE chain_meta SET value=$2, updated_at=now() WHERE key=$1', [b.meta_key, b.value ?? null]);
    return res.json({ ok: true });
  }
  if (!b.slug) return res.status(400).json({ error: 'slug və ya meta_key lazımdır' });
  const sets = [], vals = [b.slug];
  for (const f of FIELDS) {
    if (Object.prototype.hasOwnProperty.call(b, f)) { vals.push(b[f]); sets.push(f + '=$' + vals.length); }
  }
  if (!sets.length) return res.status(400).json({ error: 'dəyişən sahə yoxdur' });
  const r = await db.query('UPDATE chain SET ' + sets.join(', ') + ', updated_at=now() WHERE slug=$1', vals);
  res.json({ ok: true, changes: r.rowCount ?? null });
}