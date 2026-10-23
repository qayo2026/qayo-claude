import numpy as np, cv2, math, os, sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
card = cv2.imread('card_full.png')            # BGR
under = cv2.imread('under.png')

# ---- 1. QAYO sprite (white text -> alpha), then erase both words from the card
x0, y0, x1, y1 = 300, 800, 780, 1020
reg = card[y0:y1, x0:x1].astype(np.float32)
lum = reg.mean(axis=2)
# QAYO is the upper block (y 820..935), Texnologiya the lower (y 940..1010)
alpha_all = np.clip((lum - 70) / 150.0, 0, 1)
qy0, qy1 = 820 - y0, 937 - y0
q_alpha = np.zeros_like(alpha_all); q_alpha[qy0:qy1] = alpha_all[qy0:qy1]
q_rgb = np.full(reg.shape, 255, np.float32)

mask = (alpha_all > 0.02).astype(np.uint8) * 255
mask = cv2.dilate(mask, np.ones((9, 9), np.uint8))
full_mask = np.zeros((H, W), np.uint8); full_mask[y0:y1, x0:x1] = mask
clean = cv2.inpaint(card, full_mask, 6, cv2.INPAINT_TELEA)
cv2.imwrite('card_clean.png', clean)

# crop tight QAYO sprite
ys, xs = np.where(q_alpha > 0.05)
bx0, bx1, by0, by1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
q_a = q_alpha[by0:by1, bx0:bx1]
QW, QH = q_a.shape[1], q_a.shape[0]
print('QAYO bbox', QW, QH, 'at', x0 + bx0, y0 + by0)
Q_SCALE = 1.22
q_sprite_a = cv2.resize(q_a, (int(QW * Q_SCALE), int(QH * Q_SCALE)), interpolation=cv2.INTER_LANCZOS4)
q_sprite_a = np.clip(q_sprite_a, 0, 1)
_lg = cv2.imread('/home/claude/logo/qayo-logo-beyaz.png', cv2.IMREAD_UNCHANGED)[:, :, 3].astype(np.float32) / 255.0
_w = q_sprite_a.shape[1]
q_sprite_a = cv2.resize(_lg, (_w, int(round(_w * _lg.shape[0] / _lg.shape[1]))), interpolation=cv2.INTER_AREA)

# ---- 2. Texnologiya, rendered in Inter SemiBold, big
FONT = '/usr/share/fonts/opentype/inter/Inter-Bold.otf'
TEXT = 'TEXNOLOGİYA'
target_w = int(q_sprite_a.shape[1] * 1.08)
size = 40
while True:
    f = ImageFont.truetype(FONT, size)
    bb = f.getbbox(TEXT)
    if bb[2] - bb[0] + 0.035 * size * (len(TEXT) - 1) >= target_w: break
    size += 1
f = ImageFont.truetype(FONT, size)
print('font size', size)

# per-letter sprites with true advances
letters = []
x = 0
full_bb = f.getbbox(TEXT)
TRACK = 0.035 * size
tot_w = full_bb[2] - full_bb[0] + TRACK * (len(TEXT) - 1)
for i, ch in enumerate(TEXT):
    pre = f.getlength(TEXT[:i]) + TRACK * i
    letters.append((ch, pre))
asc, desc = f.getmetrics()
th = asc + desc + 10

CX = 540
Q_CY = 858
T_CY = 998
ring_cx, ring_cy = 538, 890

def ease_out(t):
    t = min(max(t, 0), 1)
    return 1 - (1 - t) ** 3

def ease_io(t):
    t = min(max(t, 0), 1)
    return t * t * (3 - 2 * t)

def blend_alpha(dst, sprite_a, cx, cy, op, color=(255, 255, 255)):
    h, w = sprite_a.shape
    x = int(round(cx - w / 2)); y = int(round(cy - h / 2))
    xa, ya = max(x, 0), max(y, 0)
    xb, yb = min(x + w, W), min(y + h, H)
    if xb <= xa or yb <= ya: return
    sa = sprite_a[ya - y:yb - y, xa - x:xb - x] * op
    for c in range(3):
        d = dst[ya:yb, xa:xb, c]
        dst[ya:yb, xa:xb, c] = d * (1 - sa) + color[c] * sa

def glow(dst, sprite_a, cx, cy, op):
    P = 60
    g = cv2.GaussianBlur(np.pad(sprite_a, P), (0, 0), 14) * 0.9
    blend_alpha(dst, g, cx, cy, op * 0.55, color=(255, 190, 90))   # BGR: light blue glow

# circular mask for the spinning ring
yy, xx = np.mgrid[0:H, 0:W]
rr = np.sqrt((xx - ring_cx) ** 2 + (yy - ring_cy) ** 2)
R_IN, R_OUT = 470, 540
ring_mask = np.clip((R_OUT - rr) / (R_OUT - R_IN), 0, 1).astype(np.float32)[..., None]

T0 = 9.1          # first replaced moment (absolute)
T1 = 12.0
FPS = 30
N = int(round((T1 - T0) * FPS))
os.makedirs('fr', exist_ok=True)

for i in range(N):
    t = T0 + i / FPS          # absolute time
    # card fade-in 9.2 .. 9.95
    fade = ease_io((t - 9.2) / 0.75)
    # spin settles over 9.2 .. 10.9
    p = ease_out((t - 9.2) / 1.7)
    ang = -140.0 * (1 - p)
    sc = 0.88 + 0.12 * ease_out((t - 9.2) / 1.2)

    # transform the clean card around the ring centre
    M = cv2.getRotationMatrix2D((ring_cx, ring_cy), ang, sc)
    rot = cv2.warpAffine(clean, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
    spun = (rot.astype(np.float32) * ring_mask + clean.astype(np.float32) * (1 - ring_mask))
    # underlay (map scene, frozen) fades out
    base = under.astype(np.float32) * (1 - fade) + spun * fade
    # subtle pulse of ring glow right after text lands
    frame = base

    # QAYO
    qo = ease_out((t - 9.75) / 0.6)
    if qo > 0:
        s = 0.80 + 0.20 * ease_out((t - 9.75) / 0.7)
        sp = cv2.resize(q_sprite_a, (max(int(q_sprite_a.shape[1] * s), 2), max(int(q_sprite_a.shape[0] * s), 2)), interpolation=cv2.INTER_AREA if s < 1 else cv2.INTER_LINEAR)
        glow(frame, sp, CX, Q_CY, qo)
        blend_alpha(frame, sp, CX, Q_CY, qo)

    # Texnologiya letter by letter 10.25 .. 11.25
    n = len(TEXT)
    for k, (ch, pre) in enumerate(letters):
        st = 10.25 + k * (0.7 / n)
        lo = ease_out((t - st) / 0.35)
        if lo <= 0 or ch == ' ': continue
        im = Image.new('L', (int(f.getlength(ch)) + 12, th), 0)
        ImageDraw.Draw(im).text((6, 5), ch, font=f, fill=255)
        la = np.asarray(im, np.float32) / 255.0
        rise = (1 - lo) * 22
        lx = CX - tot_w / 2 + pre + la.shape[1] / 2 - 6 - full_bb[0]
        ly = T_CY - (5 + (full_bb[1] + full_bb[3]) / 2) + th / 2 + rise
        glow(frame, la, lx, ly, lo * 0.6)
        blend_alpha(frame, la, lx, ly, lo)
    cv2.imwrite(f'fr/f_{i:04d}.png', np.clip(frame, 0, 255).astype(np.uint8))
print('frames', N)
