# Status mətnlərini mənbədən (menba.json) çıxarır.
import json, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
M=json.load(open('menba.json',encoding='utf-8'))
v=dict(marka=M['marka'],sayt_gorunen=M['sayt_gorunen'],nomre0=M['nomreler'][0]['gorunen'],nomre1=M['nomreler'][1]['gorunen'])
for f in os.listdir('cixis_status'): os.remove('cixis_status/'+f)
for ad,t in M['statuslar'].items():
    open(f'cixis_status/{ad}.txt','w',encoding='utf-8').write(t.format(**v)+'\n')
    print('---',ad); print(t.format(**v))
