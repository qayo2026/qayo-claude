# Canlıya çıxmazdan əvvəl yoxlama. Pozuntu varsa çıxış kodu 1.
import json, os, re, sys
from pypdf import PdfReader
os.chdir(os.path.dirname(os.path.abspath(__file__)))
M=json.load(open('menba.json',encoding='utf-8')); ad=M['pdf']['musteri_adi']; bad=[]
files=os.listdir('cixis')
if files!=[ad]: bad.append(f'cixis/ qovluğunda yalnız "{ad}" olmalıdır, tapıldı: {files}')
if re.search(r'_|\bV\d',ad): bad.append('ad standart deyil (_ və ya versiya var)')
ok={M['sayt']}|{n['wa'] for n in M['nomreler']}
if os.path.exists('cixis/'+ad):
    r=PdfReader('cixis/'+ad); linkler=[]
    for i,p in enumerate(r.pages):
        for a in p.get('/Annots') or []:
            u=a.get_object().get('/A',{}).get('/URI')
            if u: linkler.append((i+1,u))
    for pg,u in linkler:
        if u not in ok: bad.append(f'səhifə {pg}: mənbədə olmayan link {u}')
    for need in ok:
        if need not in {u for _,u in linkler}: bad.append(f'PDF-də yoxdur: {need}')
    # təkrar: eyni səhifədə eyni nömrə iki ayrı basılan sahə olmasın
    seen={}
    for pg,u in linkler: seen[(pg,u)]=seen.get((pg,u),0)+1
    dups=[(k,v) for k,v in seen.items() if v>1 and k[1].startswith('https://wa.me')]
    if dups: bad.append(f'təkrar WhatsApp sahəsi: {dups}')
for f in os.listdir('cixis_status'):
    t=open('cixis_status/'+f,encoding='utf-8').read()
    for n in M['nomreler']:
        if t.count(n['gorunen'])!=1: bad.append(f'{f}: nömrə {n["gorunen"]} {t.count(n["gorunen"])} dəfə (1 olmalıdır)')
    if M['sayt_gorunen'] not in t: bad.append(f'{f}: sayt yoxdur')
import re as _re
if os.path.exists('cixis_sehife/index.html'):
    h=open('cixis_sehife/index.html',encoding='utf-8').read()
    for u in _re.findall(r'href="(https?://[^"]+)"',h):
        if u not in ok: bad.append(f'səhifədə mənbədə olmayan link: {u}')
    for n in M['nomreler']:
        pass
print('RADAR: PİS' if bad else 'RADAR: TƏMİZ'); [print(' -',x) for x in bad]; sys.exit(1 if bad else 0)
