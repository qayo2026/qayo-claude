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
for p in r.pages: w.add_page(p)
pi=P['elaqe_sehifesi_nomresi']-1
H=float(w.pages[pi].mediabox.height); s=float(w.pages[pi].mediabox.width)/827.0
for x in P['elaqe_sehifesi_regionlari_px827']:
    x0,y0,x1,y1=x['sahe']
    w.add_annotation(page_number=pi,annotation=Link(rect=(x0*s,H-y1*s,x1*s,H-y0*s),url=hedef(x['hedef'])))
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
