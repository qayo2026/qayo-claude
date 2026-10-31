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
url=quote(ad)
page=f'''<!doctype html>
<html lang="az"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E_(M['marka'])} Qiymət Cədvəli</title>
<meta name="description" content="Qiymət cədvəli. Sifariş: {E_(N[0]['gorunen'])} · {E_(N[1]['gorunen'])}">
<meta property="og:type" content="website">
<meta property="og:title" content="{E_(M['marka'])} Qiymət Cədvəli">
<meta property="og:description" content="Qiymət cədvəli. Sifariş: {E_(N[0]['gorunen'])} · {E_(N[1]['gorunen'])}">
<meta property="og:image" content="{M['pdf']['link_baza']}/og.jpg">
<meta http-equiv="refresh" content="0;url={url}">
<script>location.replace("{url}");</script>
</head><body><a href="{url}">{E_(M['marka'])} Qiymət Cədvəli</a></body></html>'''
open('cixis_sehife/index.html','w',encoding='utf-8').write(page); print('sehife quruldu')
