# Mənbədən (menba.json) PDF qurur. Nömrə/link heç yerdə əl ilə yazılmır.
import io, json, os, sys
from pypdf import PdfReader, PdfWriter
from pypdf.generic import RectangleObject
from pypdf.annotations import Link
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
pdfmetrics.registerFont(TTFont('B','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
M=json.load(open('menba.json',encoding='utf-8')); P=M['pdf']
def hedef(h):
    return M['sayt'] if h=='sayt' else M['nomreler'][int(h.split(':')[1])]['wa']
r=PdfReader(P['esas_fayl']); w=PdfWriter()
K=P['kapak']; PW=595.0; PH=PW*630/1200
bb=io.BytesIO(); cc=canvas.Canvas(bb,pagesize=(PW,PH)); cc.drawImage(K['sekil'],0,0,PW,PH)
sc=PW/1200.0
for x in K['regionlar_px1200x630']:
    x0,y0,x1,y1=x['sahe']; cc.linkURL(hedef(x['hedef']),(x0*sc,PH-y1*sc,x1*sc,PH-y0*sc),relative=0)
cc.save(); bb.seek(0); w.add_page(PdfReader(bb).pages[0])
for p in r.pages[K['kohne_sehifeler_cixarilir']:]: w.add_page(p)
# son səhifə: yalnız düymələr, mənbədən
Wd=595;Hc=100;b=io.BytesIO();c=canvas.Canvas(b,pagesize=(Wd,Hc));m=14;bw=Wd-2*m
def btn(x,y,wd,h,col,t,u,fs):
    c.setFillColorRGB(*col);c.roundRect(x,y,wd,h,h/2.4,fill=1,stroke=0)
    c.setFillColorRGB(1,1,1);c.setFont('B',fs);c.drawCentredString(x+wd/2,y+h/2-fs*.35,t);c.linkURL(u,(x,y,x+wd,y+h),relative=0)
btn(m,52,bw,34,(0.89,0.024,0.075),'MƏHSULLAR VƏ SİFARİŞ  →  '+M['sayt_gorunen'],M['sayt'],15)
hw=(bw-8)/2
for i,n in enumerate(M['nomreler']):
    btn(m+i*(hw+8),10,hw,36,(0.059,0.478,0.239),'WhatsApp  '+n['gorunen'],n['wa'],13)
c.save();b.seek(0);w.add_page(PdfReader(b).pages[0])
out='cixis/'+P['musteri_adi']
for f in os.listdir('cixis'): os.remove('cixis/'+f)   # bir son nüsxə: köhnə silinir
w.write(out); print('quruldu:',out)
