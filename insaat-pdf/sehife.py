# Paylaşım səhifəsini (index.html) və önbaxış şəklini (og.jpg) mənbədən (menba.json) qurur.
import json, os, subprocess, html
from urllib.parse import quote
from PIL import Image
os.chdir(os.path.dirname(os.path.abspath(__file__)))
M=json.load(open('menba.json',encoding='utf-8')); N=M['nomreler']; ad=M['pdf']['musteri_adi']
os.makedirs('cixis_sehife',exist_ok=True)
for f in os.listdir('cixis_sehife'): os.remove('cixis_sehife/'+f)
import shutil; shutil.copy(M['pdf']['kapak']['sekil'],'cixis_sehife/og.jpg')
E_=html.escape
page=f'''<!doctype html>
<html lang="az"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E_(M['marka'])} Qiymət Cədvəli</title>
<meta name="description" content="Qiymət cədvəli. Məhsullar və sifariş: {E_(M['sayt_gorunen'])}">
<meta property="og:type" content="website">
<meta property="og:title" content="{E_(M['marka'])} Qiymət Cədvəli">
<meta property="og:description" content="Qiymət cədvəli. Sifariş: {E_(N[0]['gorunen'])} · {E_(N[1]['gorunen'])}">
<meta property="og:image" content="https://qayo-insaat-pdf-b6d5.hatchable.site/og.jpg">
<style>
:root{{--bg:#eef3fb;--fg:#17375f;--blue:#0b4b9f;--red:#e30613;--green:#0f7a3d;--card:#fff;--line:#cfdded}}
@media (prefers-color-scheme:dark){{:root:not([data-theme=light]){{--bg:#0d1b2e;--fg:#e8eef8;--card:#14263f;--line:#27405f}}}}
body{{margin:0;background:var(--bg);color:var(--fg);font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif}}
main{{max-width:520px;margin:0 auto;padding:24px max(16px,env(safe-area-inset-right)) 40px max(16px,env(safe-area-inset-left));display:flex;flex-direction:column;gap:14px}}
img{{width:100%;height:150px;object-fit:contain;border-radius:14px;background:#fff;border:1px solid var(--line)}}
a.b{{display:flex;align-items:center;justify-content:center;min-height:54px;border-radius:28px;color:#fff;font-weight:800;font-size:16px;text-decoration:none;text-align:center;padding:0 16px}}
.r{{background:var(--red)}}.g{{background:var(--green)}}.u{{background:var(--card);color:var(--blue)!important;border:2px solid var(--blue)}}
.row{{display:grid;grid-template-columns:1fr 1fr;gap:10px}}
@media(max-width:380px){{.row{{grid-template-columns:1fr}}}}
</style></head><body><main>
<img src="og.jpg" alt="{E_(M['marka'])}" width="1200" height="630">
<a class="b r" href="{quote(ad)}" download="{E_(ad)}">Qiymət cədvəli</a>
<a class="b r" href="{E_(M['sayt'])}">Məhsullar və sifariş → {E_(M['sayt_gorunen'])}</a>
<div class="row">
<a class="b g" href="{E_(N[0]['wa'])}">WhatsApp {E_(N[0]['gorunen'])}</a>
<a class="b g" href="{E_(N[1]['wa'])}">WhatsApp {E_(N[1]['gorunen'])}</a>
</div></main></body></html>'''
open('cixis_sehife/index.html','w',encoding='utf-8').write(page); print('sehife quruldu')
