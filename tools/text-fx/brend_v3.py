"""Brend videosu: mərkəz mətni text_fx ilə. İşlət: python3 brend_v3.py <kadr_qovluğu_giriş> <çıxış_qovluğu>"""
import sys, os, cv2, numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from text_fx import *
SRC, OUT = sys.argv[1], sys.argv[2]
LOGO = '/home/claude/qayo-claude/assets/logo/qayo-texnologiya-logo-beyaz.png'
os.makedirs(OUT, exist_ok=True)
CX = 540
logo = logo_alpha(LOGO, 460)               # QAYO + TEXNOLOGİYA (standart loqo)
LH = logo.shape[0]
LCY = 874 + LH / 2
# loqonu iki hissəyə böl: QAYO (üst) və TEXNOLOGİYA (alt); boşluq sətri tap
rows = (logo > 0.2).sum(1) > 0
gaps = np.where(~rows)[0]
split = int(gaps[(gaps > LH * 0.35) & (gaps < LH * 0.65)].mean())
q_a, t_a = logo[:split].copy(), logo[split:].copy()
q_top, t_top = 874, 874 + split
SOFT = 'SOFTWARE & INTELLIGENCE'
SOFT_SIZE = fit_text(SOFT, 465, 0.10, FONT_BOLD)
ROI = (300, 868, 790, 1190)                # x0,y0,x1,y1 köhnə mətn zonası
n_fr = len([f for f in os.listdir(SRC) if f.endswith('.png')])
for i in range(1, n_fr + 1):
    im = cv2.imread(f'{SRC}/s_{i:04d}.png')
    x0, y0, x1, y1 = ROI
    sub = im[y0:y1, x0:x1].astype(int)
    core = ((sub.min(axis=2) > 95) | ((sub[:, :, 2] > 120) & (sub[:, :, 1] < 130) & (sub[:, :, 0] < 160))).astype(np.uint8) * 255
    m = cv2.dilate(core, np.ones((23, 23), np.uint8))
    full = np.zeros(im.shape[:2], np.uint8); full[y0:y1, x0:x1] = m
    f = cv2.inpaint(im, full, 5, cv2.INPAINT_TELEA).astype(np.float32)
    t = (i - 1) / 30.0
    # QAYO: 0.00–0.55 fade + böyümə
    qo = ease_out(t / 0.55)
    if qo > 0:
        s = 0.86 + 0.14 * qo
        sp = scaled(q_a, s)
        glow(f, sp, CX, q_top + q_a.shape[0] / 2, qo, (90, 190, 255), sigma=14, strength=0.8)
        blend(f, sp, CX, q_top + q_a.shape[0] / 2, qo, WHITE)
    # TEXNOLOGİYA: 0.45–1.05 yumşaq yuxarı qalxma
    to = ease_out((t - 0.45) / 0.6)
    if to > 0:
        cy = t_top + t_a.shape[0] / 2 + (1 - to) * 14
        glow(f, t_a, CX, cy, to, (90, 190, 255), sigma=9, strength=0.7)
        blend(f, t_a, CX, cy, to, WHITE)
    # SOFTWARE & INTELLIGENCE: 1.0–1.7 hərf-hərf (canlı sian)
    n_show = int(len(SOFT) * ease_io((t - 1.0) / 0.7) + 0.999) if t >= 1.0 else 0
    if n_show > 0:
        sa, _ = text_sprite(SOFT, SOFT_SIZE, 0.10, FONT_BOLD, n=None)
        sp2, fw = text_sprite(SOFT, SOFT_SIZE, 0.10, FONT_BOLD, n=min(n_show, len(SOFT)))
        cx0 = CX - sa.shape[1] / 2 + sp2.shape[1] / 2   # soldan başlasın
        glow(f, sp2, cx0, 1148, 1.0, CYAN, sigma=8, strength=0.9)
        blend(f, sp2, cx0, 1148, 1.0, CYAN)
    # qırmızı xətt: 1.6–2.1 soldan sağa çəkilir
    lo = ease_out((t - 1.6) / 0.5)
    if lo > 0:
        L = int(346 * lo)
        line = np.zeros((6, 346), np.float32); line[:, :max(L, 1)] = 1.0
        line = cv2.GaussianBlur(line, (0, 0), 0.7)
        cx0 = CX - 346 / 2 + max(L, 1) / 2 + 0
        l2 = np.zeros((6, max(L, 1)), np.float32) + 1.0
        glow(f, l2, CX - 173 + L / 2, 1192, 1.0, RED, sigma=6, strength=1.0)
        blend(f, l2, CX - 173 + L / 2, 1192, 1.0, RED)
    cv2.imwrite(f'{OUT}/f_{i:04d}.png', np.clip(f, 0, 255).astype(np.uint8))
print('frames', n_fr, 'soft size', SOFT_SIZE)
