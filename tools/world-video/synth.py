"""QAYO DÜNYA axtarışı: Gemini videosu + QAYO başlıq + ölkə paneli. Mətn animasiyası text_fx-dən."""
import sys, os, cv2, numpy as np
sys.path.insert(0, '/home/claude/qayo-claude/tools/text-fx')
from text_fx import *
from PIL import Image, ImageDraw, ImageFont
W, H, FPS, DUR = 1080, 1920, 30, 10.0
OUT = sys.argv[1] if len(sys.argv) > 1 else 'fr'
os.makedirs(OUT, exist_ok=True)
FB = '/usr/share/fonts/opentype/inter/Inter-Bold.otf'
FBL = '/usr/share/fonts/opentype/inter/Inter-Black.otf'
EMO = '/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf'
BGT, BGB = np.float32([4, 18, 40]), np.float32([2, 9, 24])   # RGB

# ---------- fon
yy = np.linspace(0, 1, H)[:, None, None]
bg = (BGT * (1 - yy) + BGB * yy) * np.ones((1, W, 1), np.float32)
bg = bg[:, :, ::-1].copy()                                    # BGR
rng = np.random.RandomState(7)
for _ in range(110):
    x, y = rng.randint(0, W), rng.randint(0, H)
    cv2.circle(bg, (x, y), 1, (150, 120, 70), -1)

# ---------- ölkələr
C = [('AZƏRBAYCAN', '🇦🇿'), ('TÜRKİYƏ', '🇹🇷'), ('ALMANİYA', '🇩🇪'), ('FRANSA', '🇫🇷'), ('BƏƏ', '🇦🇪'),
     ('ABŞ', '🇺🇸'), ('BÖYÜK BRİTANİYA', '🇬🇧'), ('HİNDİSTAN', '🇮🇳'), ('ÇİN', '🇨🇳'), ('YAPONİYA', '🇯🇵')]
def flag(e, h=34):
    im = Image.new('RGBA', (136, 128), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((0, 0), e, font=ImageFont.truetype(EMO, 109), embedded_color=True)
    bb = im.getbbox(); im = im.crop(bb)
    w = int(im.width * h / im.height)
    return np.asarray(im.resize((w, h), Image.LANCZOS)).astype(np.float32)
CW, CH, GX, GY = 490, 66, 12, 14
PX0, PY0 = 30, 1290
COLS = 2
chips = []
for i, (n, e) in enumerate(C):
    sc = Image.new('RGBA', (CW, CH), (0, 0, 0, 0)); d = ImageDraw.Draw(sc)
    d.rounded_rectangle([0, 0, CW - 1, CH - 1], radius=CH // 2, fill=(6, 30, 70, 235), outline=(60, 160, 255, 255), width=2)
    sc = np.asarray(sc).astype(np.float32)
    fl = flag(e, 40); fh, fw = fl.shape[:2]
    y0 = (CH - fh) // 2
    a = fl[:, :, 3:4] / 255
    sc[y0:y0 + fh, 18:18 + fw, :3] = sc[y0:y0 + fh, 18:18 + fw, :3] * (1 - a) + fl[:, :, :3] * a
    sc[y0:y0 + fh, 18:18 + fw, 3:4] = np.maximum(sc[y0:y0 + fh, 18:18 + fw, 3:4], fl[:, :, 3:4])
    size = 33
    tx, _ = text_sprite(n, size, 0.02, FB)
    th, tw = tx.shape
    tx0 = 18 + fw + 14
    avail = CW - tx0 - 14
    if tw > avail:
        tx = cv2.resize(tx, (avail, th), interpolation=cv2.INTER_AREA); tw = avail
    ty = (CH - th) // 2
    sc[ty:ty + th, tx0:tx0 + tw, :3] = sc[ty:ty + th, tx0:tx0 + tw, :3] * (1 - tx[..., None]) + 255 * tx[..., None]
    sc[ty:ty + th, tx0:tx0 + tw, 3:4] = np.maximum(sc[ty:ty + th, tx0:tx0 + tw, 3:4], tx[..., None] * 255)
    chips.append(sc)
def chip_pos(i):
    r, c = divmod(i, COLS)
    return PX0 + 14 + c * (CW + GX), PY0 + 20 + r * (CH + GY)
T_CHIP0, T_STEP = 1.8, 0.55
# ---------- panel çərçivəsi
panel = np.zeros((H, W, 4), np.float32)
pm = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(pm)
d.rounded_rectangle([PX0, PY0, W - PX0, PY0 + 450], radius=36, fill=(3, 14, 38, 170), outline=(50, 150, 255, 255), width=3)
panel = np.asarray(pm).astype(np.float32)

# ---------- mətn
HEAD = [('QAYO', 150, 0.06, FBL, WHITE, 168, 0.0), ('QAYO QLOBAL BİZNES ŞƏBƏKƏSİ', 40, 0.04, FB, WHITE, 300, 0.5),
        ('RƏQƏMSAL BİZNES PLATFORMASI', 30, 0.12, FB, CYAN, 362, 0.9), ('SİSTEMLƏR · DATA · BİZNES PAKETLƏRİ', 26, 0.14, FB, CYAN, 410, 1.2)]
spr = []
for t, s, tr, f, col, y, st in HEAD:
    full, _ = text_sprite(t, s, tr, f)
    wpx = full.shape[1]
    if wpx > W - 60:
        s = int(s * (W - 60) / wpx); full, _ = text_sprite(t, s, tr, f)
    spr.append((t, s, tr, f, col, y, st, full.shape[1]))
def draw_head(img, t):
    for t_, s, tr, f, col, y, st, wpx in spr:
        k = (t - st)
        if k < 0: continue
        n = int(len(t_) * ease_io(k / 0.7) + 0.999)
        n = min(n, len(t_))
        sp, _ = text_sprite(t_, s, tr, f, n=n)
        full, _ = text_sprite(t_, s, tr, f)
        cx = W / 2 - full.shape[1] / 2 + sp.shape[1] / 2
        glow(img, sp, cx, y, 1.0, col, sigma=10 if s > 100 else 6, strength=0.9 if s > 100 else 0.6)
        blend(img, sp, cx, y, 1.0, col)
# ---------- video
cap = cv2.VideoCapture('gem.mp4'); frames = []
while True:
    ok, f = cap.read()
    if not ok: break
    frames.append(f)
print('gem frames', len(frames))
VY0, VH = 440, 790
s = VH / 720.0
vw = int(round(1280 * s)); xo = (vw - W) // 2
fade = np.ones((VH, 1, 1), np.float32)
ramp = np.clip(np.arange(VH) / 70.0, 0, 1) ** 1.5
fade[:, 0, 0] = np.minimum(ramp, ramp[::-1])
def vid(t):
    k = min(int(t * 24 + 0.5), len(frames) - 1)
    f = cv2.resize(frames[k], (vw, VH), interpolation=cv2.INTER_AREA)[:, xo:xo + W]
    return f.astype(np.float32)
# ---------- alt yazı
BOT, BS = 'QAYO AZƏRBAYCAN', 46
bsp, _ = text_sprite(BOT, BS, 0.06, FB)
fa = flag('🇦🇿', 40)
def compose(i):
    t = i / FPS
    img = bg.copy()
    # video
    v = vid(t)
    y0 = VY0
    img[y0:y0 + VH] = img[y0:y0 + VH] * (1 - fade) + v * fade
    # panel
    po = ease_out((t - 1.0) / 0.5)
    if po > 0:
        a = panel[:, :, 3:4] / 255 * po
        img[:] = img * (1 - a) + panel[:, :, [2, 1, 0]] * a
    # çiplər
    for k in range(len(C)):
        tk = T_CHIP0 + k * T_STEP
        o = ease_out((t - tk) / 0.35)
        if o <= 0: continue
        x, y = chip_pos(k); y += int((1 - o) * -60)          # yuxarıdan (kürədən) enir
        sc = chips[k]; h, w = sc.shape[:2]
        a = sc[:, :, 3:4] / 255 * o
        # axtarış işıltısı: yeni çip qısa müddət parlaq
        fl = max(0.0, 1 - (t - tk) / 0.5) * 0.55
        col = sc[:, :, [2, 1, 0]] * (1 - fl) + np.float32([255, 255, 255])[::-1] * fl if False else sc[:, :, [2, 1, 0]]
        col = np.clip(col + np.float32([90, 70, 20]) * fl, 0, 255)
        img[y:y + h, x:x + w] = img[y:y + h, x:x + w] * (1 - a) + col * a
    draw_head(img, t)
    # giriş/çıxış
    g = ease_out(t / 0.4)
    img *= g
    if t > DUR - 0.3: img *= max(0.0, (DUR - t) / 0.3) * 0.0 + 1.0
    return np.clip(img, 0, 255).astype(np.uint8)
if __name__ == '__main__':
    only = [int(x) for x in sys.argv[2:]] if len(sys.argv) > 2 else range(int(DUR * FPS))
    for i in only:
        cv2.imwrite('%s/f_%04d.png' % (OUT, i), compose(i))
