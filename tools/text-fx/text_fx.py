"""QAYO MƏTN ANİMASİYASI (text-fx) v1
Hər videoda mətnin yazılması, canlanması və işığı bu moduldan gedir.
Əl ilə yenidən çəkmə yoxdur: loqo yalnız assets/logo fayllarından, şrift Inter.
Animasiya növləri: fade_scale, letter_reveal, typewriter, line_draw.
Rəng qaydası: təmiz ağ, canlı sian (#5CE1FF), canlı qırmızı (#FF3B54). Solğun/boz mətn olmaz.
"""
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

FONT_BOLD = '/usr/share/fonts/opentype/inter/Inter-Bold.otf'
FONT_SEMI = '/usr/share/fonts/opentype/inter/Inter-SemiBold.otf'
WHITE, CYAN, RED = (255, 255, 255), (92, 225, 255), (255, 59, 84)

def ease_out(t):
    t = min(max(t, 0.0), 1.0); return 1 - (1 - t) ** 3

def ease_io(t):
    t = min(max(t, 0.0), 1.0); return t * t * (3 - 2 * t)

def text_sprite(text, size, tracking_em=0.0, font=FONT_BOLD, n=None):
    """Mətn sprite-ı (alpha, float 0..1). n verilsə, yalnız ilk n hərf (typewriter)."""
    f = ImageFont.truetype(font, size)
    tr = tracking_em * size
    shown = text if n is None else text[:n]
    full_w = sum(f.getlength(c) for c in text) + tr * (len(text) - 1)
    asc, desc = f.getmetrics()
    im = Image.new('L', (int(full_w) + 8, asc + desc + 8), 0)
    d = ImageDraw.Draw(im); x = 4.0
    for c in shown:
        d.text((x, 4), c, font=f, fill=255); x += f.getlength(c) + tr
    return np.asarray(im, np.float32) / 255.0, full_w

def fit_text(text, width, tracking_em, font=FONT_BOLD):
    size = 10
    while True:
        f = ImageFont.truetype(font, size)
        w = sum(f.getlength(c) for c in text) + tracking_em * size * (len(text) - 1)
        if w >= width: return size
        size += 1

def logo_alpha(path, width):
    a = cv2.imread(path, cv2.IMREAD_UNCHANGED)[:, :, 3].astype(np.float32) / 255.0
    return cv2.resize(a, (width, int(round(width * a.shape[0] / a.shape[1]))), interpolation=cv2.INTER_AREA)

def blend(dst, a, cx, cy, op, color):
    """dst: BGR float32. a: alpha sprite. color: RGB."""
    H, W = dst.shape[:2]; h, w = a.shape
    x, y = int(round(cx - w / 2)), int(round(cy - h / 2))
    xa, ya, xb, yb = max(x, 0), max(y, 0), min(x + w, W), min(y + h, H)
    if xb <= xa or yb <= ya: return
    sa = a[ya - y:yb - y, xa - x:xb - x] * op
    for c, v in enumerate((color[2], color[1], color[0])):
        dst[ya:yb, xa:xb, c] = dst[ya:yb, xa:xb, c] * (1 - sa) + v * sa

def glow(dst, a, cx, cy, op, color, sigma=10, strength=0.6):
    P = int(sigma * 4)
    g = cv2.GaussianBlur(np.pad(a, P), (0, 0), sigma)
    blend(dst, np.clip(g * 1.6, 0, 1), cx, cy, op * strength, color)

def scaled(a, s):
    return cv2.resize(a, (max(int(a.shape[1] * s), 2), max(int(a.shape[0] * s), 2)), interpolation=cv2.INTER_AREA if s < 1 else cv2.INTER_LINEAR)
