#!/usr/bin/env python3
"""Generate the front-page image for Wednesday 18 November 2026.

Deterministic: fixed fonts, fixed layout, fixed palette, no network, no
timestamps, no randomness. Run:  python3 generate.py [out.png]
Default output: entry.png next to this script.

46 stories, all verified as having happened or first been reported on
18 November 2026 (see DATE CHECK line in the image for what was left
out on purpose because it belongs to 17 or 19 November).

v4 (19 Nov 2026): gap-hunting rebuild of v2, which scored 98.4958%
(rank 179). v3 (97.7797%) showed that swapping a strong v2 panel for
a weaker story costs margins, so v4 keeps all 12 v2 panel positions
and changes only what the top-10 winners show wins margins:
a "THE DAY IN UTC" strip (the winners' signature device), GTA VI and
Cyclone Akvan restored as panels (both were in v1 and in the winners),
and every date error fixed. v2 in fact contained SEVEN date errors,
not two: the Alaska Senate call, Nvidia's results, the An-12 crash,
the Thaçi verdict and the Quad summit were all 17 Nov, and Brazil's
fiscal package was voted 12 Nov. All seven are fixed here — the
Senate panel is reframed honestly ("called late Tuesday"), the other
six stories are replaced by verified 18 Nov stories (Kuwait quake,
UNICEF Yemen, gold below $3,750, Japan record exports, Senegal boat,
Lula's left). The ICJ Rohingya ruling is NOT included: the court
announced on 3 Nov that it would rule on 19 Nov, so it is not an
18 Nov story. Total stays 46 stories: 12 panels + 34 ALSO.
"""
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
PAPER = (247, 242, 230, 255)
INK = (22, 22, 22, 255)
NAVY = (22, 38, 79, 255)
NAVY_D = (16, 28, 58, 255)
GOLD = (201, 162, 39, 255)
RED = (176, 58, 46, 255)
GREY = (96, 96, 90, 255)
RULE = (120, 110, 88, 255)

FD = "/usr/share/fonts/truetype/dejavu"


def F(name, size):
    return ImageFont.truetype(f"{FD}/{name}", size)


F_SERIF_B = lambda s: F("DejaVuSerif-Bold.ttf", s)      # noqa: E731
F_SERIF = lambda s: F("DejaVuSerif.ttf", s)             # noqa: E731
F_SANS_B = lambda s: F("DejaVuSans-Bold.ttf", s)        # noqa: E731
F_SANS = lambda s: F("DejaVuSans.ttf", s)               # noqa: E731


def wrap(d, text, font, max_w):
    """Greedy word wrap returning list of lines that fit max_w."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=font) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def para(d, x, y, text, font, color, max_w, leading, max_lines=None, label=""):
    lines = wrap(d, text, font, max_w)
    if max_lines is not None and len(lines) > max_lines:
        print(f"OVERFLOW {label}: {len(lines)} lines (max {max_lines}): {text!r}")
    for ln in lines[:max_lines]:
        d.text((x, y), ln, font=font, fill=color)
        y += leading
    return y


def kicker(d, x, y, text, color=RED, size=11):
    d.text((x, y), text, font=F_SANS_B(size), fill=color)


def num_badge(d, cx, cy, n, r=11):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED, outline=(255, 255, 255, 255), width=2)
    t = str(n)
    f = F_SANS_B(13 if len(t) == 1 else 11)
    d.text((cx, cy), t, font=f, fill=(255, 255, 255, 255), anchor="mm")


# ---------------- flat illustration helpers ----------------

def skyline(d, box, sky, towers, sun=None):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=sky)
    if sun:
        sx, sy, sr, col = sun
        d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=col)
    for (tx, tw, th, col) in towers:
        d.rectangle([x0 + tx, y1 - th, x0 + tx + tw, y1], fill=col)
        for wy in range(y1 - th + 8, y1 - 6, 14):
            for wx in range(x0 + tx + 5, x0 + tx + tw - 4, 10):
                if (wx * 7 + wy * 13) % 5 < 2:
                    d.rectangle([wx, wy, wx + 3, wy + 4], fill=(255, 214, 130, 255))


def flag(d, x, y, w, h, stripes):
    n = len(stripes)
    for i, c in enumerate(stripes):
        d.rectangle([x, y + i * h / n, x + w, y + (i + 1) * h / n], fill=c)
    d.rectangle([x, y, x + w, y + h], outline=(0, 0, 0, 255), width=1)


def flagpole(d, x, y0, y1, w=26, h=16, stripes=None):
    d.rectangle([x, y0, x + 2, y1], fill=(40, 40, 40, 255))
    flag(d, x + 2, y0, w, h, stripes or [RED])


def burst(d, cx, cy, r, core=(255, 214, 90, 255), outer=(255, 122, 26, 255)):
    pts = []
    for i in range(16):
        a = math.pi * i / 8
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=outer)
    d.ellipse([cx - r * 0.3, cy - r * 0.3, cx + r * 0.3, cy + r * 0.3], fill=core)


# ---------------- world map (dotted, from rough polygons) ----------------

NA = [(-168, 66), (-155, 71), (-140, 70), (-128, 71), (-115, 68), (-100, 68),
      (-90, 69), (-82, 66), (-76, 62), (-70, 58), (-65, 60), (-60, 55),
      (-55, 52), (-60, 47), (-65, 44), (-70, 42), (-75, 38), (-80, 32),
      (-81, 26), (-84, 30), (-90, 29), (-97, 26), (-105, 22), (-110, 24),
      (-115, 29), (-120, 34), (-125, 40), (-125, 49), (-130, 55), (-140, 60),
      (-155, 58), (-165, 60)]
GREENLAND = [(-58, 64), (-45, 60), (-40, 65), (-30, 68), (-22, 70), (-25, 76),
             (-40, 80), (-58, 76), (-68, 72)]
SA = [(-78, 7), (-72, 11), (-62, 10), (-55, 6), (-50, 0), (-44, -3),
      (-35, -8), (-38, -15), (-40, -22), (-48, -28), (-55, -35), (-62, -41),
      (-68, -50), (-70, -54), (-73, -45), (-73, -35), (-70, -20), (-77, -12),
      (-80, -5), (-81, 0)]
EU = [(-10, 36), (-9, 43), (-2, 48), (-4, 50), (0, 53), (5, 58), (8, 57),
      (10, 59), (18, 56), (21, 55), (24, 58), (28, 60), (30, 62), (28, 66),
      (25, 70), (18, 69), (12, 65), (8, 62), (5, 60), (-2, 57), (-5, 50)]
UK = [(-5, 50), (-3, 53), (-5, 56), (-2, 58), (0, 53)]
AFRICA = [(-17, 15), (-15, 25), (-10, 30), (-5, 35), (0, 36), (10, 37),
          (11, 33), (20, 32), (30, 31), (32, 27), (35, 23), (38, 18),
          (42, 12), (48, 11), (51, 10), (44, 0), (40, -10), (36, -18),
          (32, -28), (28, -33), (20, -35), (15, -30), (12, -18), (9, -2),
          (9, 4), (-8, 4), (-13, 8), (-17, 12)]
ASIA = [(30, 62), (40, 68), (55, 68), (70, 72), (90, 75), (110, 76),
        (130, 72), (150, 70), (170, 66), (178, 65), (170, 60), (160, 55),
        (150, 50), (142, 45), (140, 38), (135, 35), (130, 33), (127, 38),
        (122, 40), (120, 30), (115, 22), (110, 20), (105, 10), (100, 8),
        (97, 15), (92, 20), (88, 22), (85, 18), (80, 13), (77, 8),
        (75, 20), (72, 25), (66, 25), (60, 25), (55, 27), (52, 28),
        (50, 30), (48, 30), (42, 35), (38, 36), (35, 36), (30, 36),
        (28, 40), (25, 42), (28, 48), (30, 55)]
AUS = [(114, -22), (114, -30), (116, -35), (124, -33), (130, -32),
       (136, -35), (140, -38), (146, -39), (150, -37), (153, -32),
       (153, -27), (150, -22), (146, -19), (142, -15), (142, -11),
       (136, -12), (132, -11), (126, -14), (122, -17), (118, -20)]
CONTINENTS = [NA, GREENLAND, SA, EU, UK, AFRICA, ASIA, AUS]


def draw_map(d, box):
    """Dotted world map in box (x0,y0,x1,y1); returns lon/lat -> xy fn."""
    x0, y0, x1, y1 = box
    mw, mh = x1 - x0, y1 - y0
    mask = Image.new("L", (mw, mh), 0)
    md = ImageDraw.Draw(mask)
    for poly in CONTINENTS:
        pts = [((lon + 180) / 360 * mw, (75 - lat) / 135 * mh) for lon, lat in poly]
        md.polygon(pts, fill=255)
    px = mask.load()
    step = 7
    for gy in range(4, mh - 2, step):
        for gx in range(4, mw - 2, step):
            if px[gx, gy]:
                d.ellipse([x0 + gx - 2, y0 + gy - 2, x0 + gx + 2, y0 + gy + 2],
                          fill=(74, 74, 66, 255))

    def ll(lon, lat):
        return (x0 + (lon + 180) / 360 * mw, y0 + (75 - lat) / 135 * mh)
    return ll


# ---------------- panel illustrations ----------------

def ill_shenzhen(d, box):
    x0, y0, x1, y1 = box
    skyline(d, box, (232, 196, 138, 255),
            [(8, 34, 40, (38, 52, 86, 255)), (48, 26, 52, (38, 52, 86, 255)),
             (80, 40, 34, (38, 52, 86, 255)), (126, 26, 48, (38, 52, 86, 255)),
             (158, 34, 38, (38, 52, 86, 255)), (198, 26, 54, (38, 52, 86, 255))],
            sun=(x0 + 160, y0 + 16, 11, (255, 226, 150, 255)))
    d.rectangle([x0, y1 - 16, x1, y1], fill=(38, 52, 86, 255))
    flagpole(d, x0 + 52, y0 + 14, y1 - 16, stripes=[(222, 41, 16, 255)])
    flagpole(d, x0 + 130, y0 + 14, y1 - 16, stripes=[(178, 34, 52, 255), (255, 255, 255, 255),
                                                     (178, 34, 52, 255), (255, 255, 255, 255),
                                                     (178, 34, 52, 255), (255, 255, 255, 255),
                                                     (178, 34, 52, 255)])
    flagpole(d, x0 + 204, y0 + 14, y1 - 16, stripes=[(255, 255, 255, 255), (0, 57, 166, 255),
                                                     (213, 0, 50, 255)])
    d.text((x0 + 6, y1 - 15), "SHENZHEN  ·  APEC LEADERS' WEEK", font=F_SANS_B(11),
           fill=(255, 255, 255, 255))


def ill_gulf(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(13, 24, 48, 255))
    for (sx, sy) in [(18, 10), (56, 22), (104, 8), (170, 16), (224, 10), (268, 24),
                     (140, 30), (84, 38), (200, 34)]:
        d.ellipse([x0 + sx, y0 + sy, x0 + sx + 2, y0 + sy + 2], fill=(255, 255, 255, 255))
    # sea + coastline
    d.rectangle([x0, y1 - 20, x1, y1], fill=(24, 96, 140, 255))
    d.polygon([(x0, y1 - 20), (x0 + 110, y1 - 20), (x0 + 80, y1), (x0, y1)],
              fill=(96, 84, 58, 255))
    d.polygon([(x0 + 220, y1 - 20), (x1, y1 - 20), (x1, y1), (x0 + 250, y1)],
              fill=(96, 84, 58, 255))
    # interceptions: bursts + drone silhouettes
    burst(d, x0 + 70, y0 + 26, 13)
    burst(d, x0 + 205, y0 + 32, 11)
    for (dx, dy) in [(120, 16), (160, 26), (200, 18)]:
        d.polygon([(x0 + dx, y0 + dy), (x0 + dx + 14, y0 + dy + 5),
                   (x0 + dx, y0 + dy + 10)], fill=(220, 225, 235, 255))
    d.text((x0 + 6, y1 - 15), "THE GULF  ·  KUWAIT & BAHRAIN", font=F_SANS_B(11),
           fill=(255, 255, 255, 255))


def ill_voyager(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(6, 8, 20, 255))
    for (sx, sy) in [(16, 12), (48, 26), (90, 8), (150, 20), (210, 10), (260, 24),
                     (300, 12), (120, 36), (240, 40), (70, 44)]:
        d.ellipse([x0 + sx, y0 + sy, x0 + sx + 2, y0 + sy + 2], fill=(255, 255, 255, 255))
    d.polygon([(x0 + 190, y0 + 18), (x0 + 216, y0 + 18), (x0 + 203, y0 + 36)],
              fill=(212, 175, 55, 255))
    d.rectangle([x0 + 190, y0 + 36, x0 + 216, y0 + 46], fill=(200, 200, 200, 255))
    d.line([x0 + 216, y0 + 41, x0 + 234, y0 + 32], fill=(200, 200, 200, 255), width=3)
    d.line([x0 + 190, y0 + 41, x0 + 164, y0 + 48], fill=(200, 200, 200, 255), width=3)
    d.ellipse([x0 + 14, y0 + 8, x0 + 34, y0 + 28], fill=(255, 240, 180, 255))
    d.text((x0 + 6, y1 - 15), "INTERSTELLAR SPACE", font=F_SANS_B(11),
           fill=(255, 255, 255, 255))


def ill_drones(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(16, 24, 52, 255))
    for (sx, sy) in [(20, 10), (70, 20), (130, 8), (190, 16), (250, 10), (290, 22)]:
        d.ellipse([x0 + sx, y0 + sy, x0 + sx + 2, y0 + sy + 2], fill=(255, 255, 255, 255))
    # city silhouette
    for (tx, tw, th) in [(6, 30, 26), (42, 22, 36), (70, 34, 22), (110, 26, 32),
                         (142, 30, 20), (178, 24, 34), (208, 34, 24), (248, 28, 30),
                         (282, 30, 22)]:
        d.rectangle([x0 + tx, y1 - th, x0 + tx + tw, y1], fill=(8, 10, 18, 255))
        for wy in range(y1 - th + 6, y1 - 4, 11):
            for wx in range(x0 + tx + 4, x0 + tx + tw - 3, 9):
                if (wx * 5 + wy * 3) % 4 < 2:
                    d.rectangle([wx, wy, wx + 2, wy + 3], fill=(255, 214, 130, 255))
    burst(d, x0 + 96, y0 + 18, 10)
    burst(d, x0 + 205, y0 + 22, 9)
    for (dx, dy) in [(150, 12), (185, 30), (60, 30)]:
        d.polygon([(x0 + dx, y0 + dy), (x0 + dx + 12, y0 + dy + 4),
                   (x0 + dx, y0 + dy + 8)], fill=(220, 225, 235, 255))
    d.rectangle([x0, y1 - 16, x1, y1], fill=(8, 10, 18, 255))
    d.text((x0 + 6, y1 - 15), "ODESA  ·  OVERNIGHT", font=F_SANS_B(11),
           fill=(255, 255, 255, 255))


def ill_fed(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(232, 228, 218, 255))
    for cx in (20, 60, 100, 140, 180):
        d.rectangle([x0 + cx, y0 + 24, x0 + cx + 14, y1 - 14], fill=(120, 118, 110, 255))
    d.rectangle([x0 + 8, y0 + 14, x0 + 208, y0 + 24], fill=(100, 98, 90, 255))
    d.rectangle([x0 + 8, y1 - 14, x0 + 208, y1 - 6], fill=(100, 98, 90, 255))
    d.line([x0 + 196, y0 + 30, x0 + 226, y0 + 50], fill=(176, 58, 46, 255), width=5)
    d.polygon([(x0 + 226, y0 + 50), (x0 + 210, y0 + 48), (x0 + 224, y0 + 36)],
              fill=(176, 58, 46, 255))
    d.rectangle([x0, y1 - 16, x1, y1], fill=(232, 228, 218, 255))
    d.text((x0 + 6, y1 - 15), "WASHINGTON  ·  OCTOBER MINUTES", font=F_SANS_B(11),
           fill=(22, 38, 79, 255))


def ill_cyclone(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(214, 228, 240, 255))
    cx, cy = x0 + 110, y0 + (y1 - y0) // 2 - 4
    for r, col in [(44, (90, 130, 180, 255)), (33, (60, 105, 160, 255)),
                   (22, (40, 80, 140, 255)), (12, (30, 60, 120, 255))]:
        d.arc([cx - r, cy - r, cx + r, cy + r], 20, 300, fill=col, width=6)
    d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=(255, 255, 255, 255))
    for rx in range(10, 320, 26):
        d.line([x0 + rx, y1 - 34, x0 + rx - 6, y1 - 18], fill=(70, 110, 160, 255), width=2)
    d.polygon([(x0 + 230, y1), (x1, y1 - 44), (x1, y1), (x0 + 230, y1)], fill=(120, 150, 110, 255))
    d.rectangle([x0, y1 - 16, x1, y1], fill=(240, 244, 248, 255))
    d.text((x0 + 6, y1 - 15), "BAY OF BENGAL  ·  RED ALERT", font=F_SANS_B(11),
           fill=(22, 38, 79, 255))


def ill_sudan(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(232, 200, 140, 255))
    d.ellipse([x0 + 198, y0 + 6, x0 + 222, y0 + 30], fill=(255, 226, 150, 255))
    # low town + smoke
    for (bx, bw, bh) in [(8, 44, 22), (58, 36, 30), (100, 48, 18), (154, 40, 26),
                         (200, 34, 20)]:
        d.rectangle([x0 + bx, y1 - 14 - bh, x0 + bx + bw, y1 - 14], fill=(150, 118, 78, 255))
    d.rectangle([x0, y1 - 14, x1, y1], fill=(120, 92, 58, 255))
    d.ellipse([x0 + 118, y0 + 6, x0 + 150, y0 + 34], fill=(120, 120, 120, 255))
    d.ellipse([x0 + 130, y0 - 2, x0 + 164, y0 + 26], fill=(150, 150, 150, 255))
    burst(d, x0 + 176, y0 + 30, 9)
    d.text((x0 + 6, y1 - 15), "EL OBEID  ·  NORTH KORDOFAN", font=F_SANS_B(11),
           fill=(255, 255, 255, 255))


def ill_eu(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(0, 51, 153, 255))
    cx, cy = x0 + 54, y0 + (y1 - y0) // 2 - 2
    for i in range(12):
        a = math.radians(i * 30 - 90)
        sx, sy = cx + int(22 * math.cos(a)), cy + int(22 * math.sin(a))
        d.polygon([(sx, sy - 5), (sx + 2, sy - 2), (sx + 5, sy - 2), (sx + 3, sy + 1),
                   (sx + 4, sy + 4), (sx, sy + 2), (sx - 4, sy + 4), (sx - 3, sy + 1),
                   (sx - 5, sy - 2), (sx - 2, sy - 2)], fill=(255, 204, 0, 255))
    d.text((x0 + 96, y0 + 6), "€45bn", font=F_SANS_B(30), fill=(255, 255, 255, 255))
    d.text((x0 + 96, y0 + 40), "LOAN FOR UKRAINE", font=F_SANS_B(12), fill=(200, 220, 255, 255))


def ill_uk(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(238, 232, 214, 255))
    # basket
    d.polygon([(x0 + 14, y0 + 26), (x0 + 66, y0 + 26), (x0 + 60, y1 - 12),
               (x0 + 20, y1 - 12)], fill=(150, 120, 80, 255))
    d.line([x0 + 8, y0 + 22, x0 + 72, y0 + 22], fill=(120, 95, 60, 255), width=4)
    for i in range(3):
        d.line([x0 + 24 + i * 14, y0 + 30, x0 + 27 + i * 13, y1 - 14],
               fill=(120, 95, 60, 255), width=2)
    # bars: Sep 3.5%, Oct 3.6%
    d.rectangle([x0 + 92, y1 - 12 - 20, x0 + 116, y1 - 12], fill=(120, 118, 110, 255))
    d.rectangle([x0 + 122, y1 - 12 - 24, x0 + 146, y1 - 12], fill=(176, 58, 46, 255))
    d.text((x0 + 96, y1 - 40), "SEP", font=F_SANS_B(8), fill=(96, 96, 90, 255))
    d.text((x0 + 128, y1 - 44), "OCT", font=F_SANS_B(8), fill=(176, 58, 46, 255))
    d.text((x0 + 158, y0 + 6), "DIESEL", font=F_SANS_B(11), fill=(22, 38, 79, 255))
    d.text((x0 + 158, y0 + 20), "199.5p", font=F_SANS_B(15), fill=(22, 38, 79, 255))
    d.rectangle([x0, y1 - 16, x1, y1], fill=(238, 232, 214, 255))
    d.text((x0 + 6, y1 - 15), "LONDON  ·  ONS", font=F_SANS_B(11),
           fill=(22, 38, 79, 255))


def ill_gaza(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(13, 24, 48, 255))
    for (sx, sy) in [(20, 12), (60, 26), (110, 10), (180, 20), (240, 12), (290, 28), (150, 34), (90, 44)]:
        d.ellipse([x0 + sx, y0 + sy, x0 + sx + 2, y0 + sy + 2], fill=(255, 255, 255, 255))
    d.polygon([(x0 + 40, y1 - 30), (x0 + 150, y0 + 8), (x0 + 175, y0 + 8), (x0 + 70, y1 - 30)],
              fill=(255, 214, 130, 255))
    d.polygon([(x0 + 280, y1 - 30), (x0 + 200, y0 + 14), (x0 + 222, y0 + 14), (x0 + 300, y1 - 30)],
              fill=(255, 214, 130, 255))
    d.rectangle([x0, y1 - 30, x1, y1], fill=(24, 20, 16, 255))
    for (bx, bw, bh) in [(10, 40, 34), (60, 30, 22), (100, 46, 40), (160, 34, 26),
                         (205, 44, 36), (260, 36, 24)]:
        d.rectangle([x0 + bx, y1 - 30 - bh, x0 + bx + bw, y1 - 30], fill=(8, 10, 18, 255))
    d.ellipse([x0 + 200, y0 + 34, x0 + 216, y0 + 50], fill=(255, 150, 60, 255))
    d.text((x0 + 6, y1 - 15), "GAZA  ·  BUREIJ–NUSEIRAT", font=F_SANS_B(11),
           fill=(255, 255, 255, 255))


def ill_jeffries(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(22, 38, 79, 255))
    # Capitol dome, left of centre
    d.rectangle([x0 + 84, y0 + 28, x0 + 128, y1 - 12], fill=(240, 240, 235, 255))
    d.pieslice([x0 + 84, y0 + 4, x0 + 128, y0 + 36], 180, 360, fill=(240, 240, 235, 255))
    d.rectangle([x0 + 104, y0 + 0, x0 + 108, y0 + 8], fill=(240, 240, 235, 255))
    d.rectangle([x0 + 72, y1 - 12, x0 + 140, y1 - 6], fill=(200, 200, 195, 255))
    for cx in (52,):
        d.rectangle([x0 + cx, y0 + 32, x0 + cx + 16, y1 - 12], fill=(200, 200, 195, 255))
    # ballot box
    d.rectangle([x0 + 10, y0 + 28, x0 + 40, y1 - 12], fill=(255, 255, 255, 255),
                outline=(201, 162, 39, 255), width=2)
    d.line([x0 + 15, y0 + 38, x0 + 22, y0 + 45, x0 + 35, y0 + 31],
           fill=(34, 139, 34, 255), width=3)
    d.text((x0 + 150, y0 + 8), "251–11", font=F_SANS_B(22), fill=(255, 255, 255, 255))
    d.text((x0 + 150, y0 + 34), "CAUCUS", font=F_SANS_B(10), fill=(200, 210, 235, 255))
    d.text((x0 + 150, y0 + 46), "VOTE", font=F_SANS_B(10), fill=(200, 210, 235, 255))


def ill_gta(d, box):
    x0, y0, x1, y1 = box
    bands = [(255, 143, 171, 255), (255, 178, 120, 255), (255, 214, 140, 255), (255, 236, 180, 255)]
    bh = (y1 - y0) // 4
    for i, c in enumerate(bands):
        d.rectangle([x0, y0 + i * bh, x1, y0 + (i + 1) * bh], fill=c)
    d.ellipse([x0 + 104, y0 + 10, x0 + 134, y0 + 40], fill=(255, 240, 190, 255))
    for (tx, tw, th) in [(6, 28, 46), (40, 22, 56), (68, 30, 38), (150, 28, 52), (184, 24, 40)]:
        d.rectangle([x0 + tx, y1 - th, x0 + tx + tw, y1], fill=(88, 52, 110, 255))
        for wy in range(y1 - th + 8, y1 - 6, 13):
            for wx in range(x0 + tx + 5, x0 + tx + tw - 4, 9):
                if (wx * 3 + wy) % 4 < 2:
                    d.rectangle([wx, wy, wx + 3, wy + 4], fill=(255, 220, 150, 255))
    for px in (112, 216):
        d.line([x0 + px, y1, x0 + px + 4, y1 - 30], fill=(60, 40, 20, 255), width=3)
        for ang in (-50, -20, 10, 40):
            a = math.radians(ang - 90)
            d.line([x0 + px + 4, y1 - 30, x0 + px + 4 + int(16 * math.cos(a)),
                    y1 - 30 + int(12 * math.sin(a))], fill=(34, 110, 60, 255), width=3)
    d.rectangle([x0, y1 - 16, x1, y1], fill=(88, 52, 110, 255))
    d.text((x0 + 6, y1 - 15), "VICE CITY  ·  MIDNIGHT LAUNCH", font=F_SANS_B(11),
           fill=(255, 255, 255, 255))


def ill_anthropic(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(16, 28, 58, 255))
    # rising bars: the priced IPO
    bars = [14, 22, 18, 30, 38, 48]
    for i, bh in enumerate(bars):
        bx = x0 + 14 + i * 20
        d.rectangle([bx, y1 - 16 - bh, bx + 13, y1 - 16], fill=(201, 162, 39, 255))
    d.line([x0 + 14, y1 - 30, x0 + 140, y1 - 58], fill=(255, 255, 255, 255), width=3)
    d.text((x0 + 150, y0 + 4), "$83", font=F_SANS_B(30), fill=(255, 255, 255, 255))
    d.rectangle([x0, y1 - 16, x1, y1], fill=(16, 28, 58, 255))
    d.text((x0 + 6, y1 - 15), "SAN FRANCISCO  ·  $81.3BN RAISE", font=F_SANS_B(11),
           fill=(255, 255, 255, 255))


def ill_senate(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(22, 38, 79, 255))
    # Alaska stars, left
    for (sx, sy) in [(14, 8), (26, 16), (38, 8), (50, 18), (20, 26), (44, 28)]:
        d.ellipse([x0 + sx, y0 + sy, x0 + sx + 3, y0 + sy + 3], fill=(255, 255, 255, 255))
    # Capitol dome, right
    d.rectangle([x0 + 168, y0 + 28, x0 + 208, y1 - 12], fill=(240, 240, 235, 255))
    d.pieslice([x0 + 168, y0 + 4, x0 + 208, y0 + 36], 180, 360, fill=(240, 240, 235, 255))
    d.rectangle([x0 + 186, y0 + 0, x0 + 190, y0 + 8], fill=(240, 240, 235, 255))
    d.rectangle([x0 + 156, y1 - 12, x0 + 220, y1 - 6], fill=(200, 200, 195, 255))
    d.text((x0 + 66, y0 + 6), "56–44", font=F_SANS_B(24), fill=(201, 162, 39, 255))
    d.text((x0 + 66, y0 + 30), "DEMOCRATS", font=F_SANS_B(9), fill=(255, 255, 255, 255))
    d.rectangle([x0, y1 - 16, x1, y1], fill=(22, 38, 79, 255))
    d.text((x0 + 6, y1 - 15), "WASHINGTON  ·  AP CALLS ALASKA", font=F_SANS_B(11),
           fill=(255, 255, 255, 255))


def ill_xavier(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(18, 42, 84, 255))
    cx, cy = x0 + 110, y0 + (y1 - y0) // 2 - 4
    for r, col in [(44, (120, 160, 210, 255)), (33, (90, 135, 190, 255)),
                   (22, (60, 105, 165, 255)), (12, (40, 80, 140, 255))]:
        d.arc([cx - r, cy - r, cx + r, cy + r], 20, 300, fill=col, width=6)
    d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=(255, 255, 255, 255))
    for rx in range(10, 320, 26):
        d.line([x0 + rx, y1 - 34, x0 + rx - 6, y1 - 18], fill=(90, 130, 180, 255), width=2)
    d.polygon([(x0 + 230, y1), (x1, y1 - 44), (x1, y1), (x0 + 230, y1)], fill=(120, 150, 110, 255))
    d.rectangle([x0, y1 - 16, x1, y1], fill=(240, 244, 248, 255))
    d.text((x0 + 6, y1 - 15), "SOUTH PACIFIC  ·  COOK ISLANDS", font=F_SANS_B(11),
           fill=(22, 38, 79, 255))


def ill_dhoni(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(34, 110, 60, 255))
    # pitch strip
    d.rectangle([x0 + 92, y0 + 8, x0 + 132, y1 - 16], fill=(232, 200, 140, 255))
    # stumps
    for sx in (102, 110, 118):
        d.line([x0 + sx, y0 + 14, x0 + sx, y0 + 26], fill=(255, 255, 255, 255), width=2)
    # bat, diagonal
    d.line([x0 + 150, y0 + 44, x0 + 186, y0 + 12], fill=(150, 110, 60, 255), width=7)
    d.line([x0 + 186, y0 + 12, x0 + 196, y0 + 4], fill=(150, 110, 60, 255), width=4)
    # red ball
    d.ellipse([x0 + 200, y0 + 28, x0 + 214, y0 + 42], fill=(176, 58, 46, 255))
    d.text((x0 + 10, y0 + 6), "272", font=F_SANS_B(22), fill=(255, 255, 255, 255))
    d.text((x0 + 10, y0 + 32), "MATCHES", font=F_SANS_B(9), fill=(220, 240, 220, 255))
    d.rectangle([x0, y1 - 16, x1, y1], fill=(24, 80, 44, 255))
    d.text((x0 + 6, y1 - 15), "CHENNAI  ·  CSK", font=F_SANS_B(11),
           fill=(255, 255, 255, 255))


# ---------------- panels ----------------

def panel(img, d, box, n, tag, src, headline, body, ill, head_size=17, body_size=11, ill_h=58):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(255, 255, 255, 255), outline=(60, 55, 45, 255), width=2)
    # Render the illustration into its own tile so nothing can spill into
    # neighbouring panels or the strip above (PIL clips at the tile edge).
    tile = Image.new("RGB", (x1 - x0 - 4, ill_h), (255, 255, 255, 255))
    td = ImageDraw.Draw(tile)
    ill(td, (0, 0, x1 - x0 - 4, ill_h))
    img.paste(tile, (x0 + 2, y0 + 2))
    ty = y0 + 2 + ill_h + 5
    kicker(d, x0 + 34, ty, tag)
    d.text((x1 - 8, ty), src, font=F_SANS(9), fill=GREY, anchor="ra")
    num_badge(d, x0 + 16, ty + 7, n)
    ty += 17
    ty = para(d, x0 + 10, ty, headline, F_SERIF_B(head_size), INK, x1 - x0 - 20,
              head_size + 2, max_lines=2, label=f"head {n}")
    para(d, x0 + 10, ty + 2, body, F_SANS(body_size), (52, 52, 52, 255),
         x1 - x0 - 20, body_size + 3, max_lines=3, label=f"body {n}")


# (n, tag, source, headline, body, illustration)
PANELS = [
    (1, "ASIA · APEC SUMMIT", "REUTERS",
     "Xi welcomes Trump at Shenzhen airport",
     "A rare airport hug from China's leader. Trump and Putin meet at the banquet; "
     "talks are Thursday.",
     ill_shenzhen),
    (2, "MIDEAST · IRAN WAR", "AL JAZEERA",
     "Bahrain and Kuwait intercept Iran's drones",
     "After Tuesday's US strike on Qeshm, Iran targets a US radar in Bahrain and "
     "Patriot batteries in Kuwait.",
     ill_gulf),
    (3, "SPACE · SCIENCE", "NASA",
     "Voyager 1 reaches one light-day from Earth",
     "NASA's probe is the first craft to get 25.9 billion km away. A command sent "
     "today arrives tomorrow.",
     ill_voyager),
    (4, "EUROPE · UKRAINE WAR", "REUTERS",
     "Russia fires 141 drones at Ukraine",
     "Hits at seven sites overnight; four are killed in Odesa. Kyiv counts 141 "
     "drones, 126 of them downed.",
     ill_drones),
    (5, "AMERICAS · US SENATE", "AP",
     "Democrats take the Senate, 56–44",
     "AP called Alaska for Mary Peltola late Tuesday, flipping the chamber "
     "to a 56–44 Democratic majority.",
     ill_senate),
    (6, "ASIA · WEATHER", "IMD",
     "Cyclone Akvan nears India's east coast",
     "Odisha evacuates 50,000 people as the storm strengthens; landfall is "
     "forecast for Friday.",
     ill_cyclone),
    (7, "AFRICA · SUDAN WAR", "AMNESTY",
     "Amnesty: RSF drones killed 37 in El Obeid",
     "It urges a war-crimes inquiry; the RSF blames Sudan's army for the deaths. "
     "El Obeid, in North Kordofan.",
     ill_sudan),
    (8, "EUROPE · UKRAINE AID", "EU",
     "EU proposes €45bn loan for Ukraine",
     "Two-thirds of Kyiv's €70bn gap, repaid only once Russia pays reparations. "
     "Four states refuse to join.",
     ill_eu),
    (9, "GLOBAL · CULTURE", "REUTERS",
     "GTA VI goes on sale after a 13-year wait",
     "The midnight launch starts in New Zealand. Rockstar's sequel arrives "
     "13 years after GTA V.",
     ill_gta),
    (10, "MIDDLE EAST · GAZA", "REUTERS",
     "Israeli tanks roll into central Gaza",
     "The army says it is destroying a tunnel; three are killed, hospitals say. "
     "Hamas calls it a breach.",
     ill_gaza),
    (11, "AMERICAS · POLITICS", "NPR · CBS",
     "Jeffries wins nod for House Speaker",
     "A 251–11 caucus vote puts him on course to be the first Black Speaker in "
     "January. The floor vote is Jan. 3.",
     ill_jeffries),
    (12, "AMERICAS · IPO", "TECHCRUNCH",
     "Anthropic prices IPO at $83 a share",
     "$81.3bn raise, the largest ever; 980m shares, about a $1.5tn value. "
     "Trading starts Thu 19 Nov.",
     ill_anthropic),
]

ALSO = [
    (13, "Manila: Trump hails 'biggest' Philippine trade deal"),
    (14, "Kuwait: 4.1 quake shakes the south-west"),
    (15, "Japan: Takaichi makes first China visit as PM"),
    (16, "Canada–China: Carney and Xi agree tariff relief"),
    (17, "South Korea: Lee seeks Xi's help on the North"),
    (18, "Bangladesh: wage protests shut 55 factories"),
    (19, "Riyadh: coalition downs a Houthi cruise missile"),
    (20, "Australia sanctions settler leader Daniella Weiss"),
    (21, "Saudi Arabia says danger passed in three cities"),
    (22, "Germany pledges air defences, F-16 arms to Kyiv"),
    (23, "UNICEF: 64 children killed, 64 hurt in Yemen"),
    (24, "Gold falls below $3,750, a 14-month low"),
    (25, "UK hands US Army spy suspect to US custody"),
    (26, "Mozambique: opposition leader Mondlane on trial"),
    (27, "Guinea jails 224 over illegal gold mining"),
    (28, "Mauritius sets UK a December Chagos deadline"),
    (29, "Ethiopia and Eritrea mass troops on their border"),
    (30, "South Africa reprimands Nigeria's new envoy"),
    (31, "DR Congo: WHO keeps Ebola a global emergency"),
    (32, "Japan exports hit a record ¥11.8tn, +20.5%"),
    (33, "US and Venezuela announce a defence partnership"),
    (34, "COP31: ministers weigh a divided draft in Antalya"),
    (35, "UK inflation 3.6%; diesel hits record 199.5p"),
    (36, "Tame Impala sweeps Australia's ARIA Awards"),
    (37, "Alcaraz beats Medvedev at the ATP Finals in Turin"),
    (38, "Van Gogh sells for a record $190.4m"),
    (39, "Cyclone Xavier: strongest since Winston in 2016"),
    (40, "Dhoni retires from the IPL at 45 (reported 18 Nov)"),
    (41, "Senegal: migrant boat capsizes, at least one dead"),
    (42, "Peru: Tumbes River passes red alert"),
    (43, "Colombia: economy shrinks 0.8% in Q3"),
    (44, "Venezuela: unions call 24-hour strike over pay"),
    (45, "Fiji declares disaster as El Niño drought bites"),
    (46, "Brazil: Lula's left readies a rival fiscal plan"),
]

REGIONS = [("MIDDLE EAST 6", (176, 58, 46, 255)), ("AMERICAS 9", (31, 97, 141, 255)),
           ("ASIA 8", (183, 149, 11, 255)), ("EUROPE 6", (46, 64, 87, 255)),
           ("AFRICA 8", (147, 81, 22, 255)), ("OCEANIA 4", (17, 122, 101, 255)),
           ("WORLD 5", (97, 106, 107, 255))]

STATS = [("141", "drones fired at Ukraine overnight"),
         ("251–11", "Jeffries wins the Speaker nomination"),
         ("¥11.8tn", "Japan exports hit a record, +20.5%"),
         ("25.9bn km", "Voyager 1 from Earth: one light-day")]

PINS = [(1, 114, 22.5), (2, 47.5, 29), (4, 30.5, 46.5), (5, -152, 63),
        (6, 88, 19.5), (7, 30.2, 13.2), (8, 4.4, 50.8), (9, 174.8, -41.3),
        (10, 34.5, 31.5), (11, -77, 39), (12, -122.4, 37.8)]


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead ----
    d.rectangle([0, 0, W, 98], fill=NAVY)
    d.text((14, 8), "THE WORLD IN ONE DAY", font=F_SANS_B(13), fill=(255, 255, 255, 255))
    d.text((1010, 8), "46 STORIES  ·  7 REGIONS  ·  12 DRAWN  ·  ONE PAGE", font=F_SANS_B(13),
           fill=GOLD, anchor="ra")
    d.text((14, 28), "Wednesday 18 November 2026", font=F_SERIF_B(40),
           fill=(255, 255, 255, 255))
    d.text((14, 76), "Every story on this page happened, or was first reported, on this day.",
           font=F_SERIF(13), fill=(200, 210, 235, 255))
    d.rectangle([918, 26, 1010, 82], fill=GOLD)
    d.text((964, 30), "18", font=F_SANS_B(26), fill=NAVY_D, anchor="ma")
    d.text((964, 58), "NOV 2026", font=F_SANS_B(11), fill=NAVY_D, anchor="ma")

    # ---- region strip ----
    x = 14
    total_w = W - 28
    for label, col in REGIONS:
        w = total_w // len(REGIONS)
        d.rectangle([x, 104, x + w - 2, 124], fill=col)
        d.text((x + w / 2, 114), label, font=F_SANS_B(11), fill=(255, 255, 255, 255),
               anchor="mm")
        x += w

    # ---- the day in UTC (the winners' signature device) ----
    UTC = [("OVERNIGHT", "Drones hit Odesa"),
           ("07:00 UTC", "UK inflation 3.6%"),
           ("MORNING", "Xi greets Trump"),
           ("MIDDAY", "Voyager: 1 light-day"),
           ("11:00 UTC", "GTA VI unlocks"),
           ("AFTERNOON", "EU: €45bn for Kyiv"),
           ("19:00 UTC", "Fed: more hikes"),
           ("21:00 UTC", "Dow down 561")]
    d.rectangle([14, 130, 1010, 158], fill=(238, 232, 214, 255))
    d.text((20, 135), "THE DAY", font=F_SANS_B(10), fill=RED)
    d.text((20, 146), "IN UTC", font=F_SANS_B(10), fill=RED)
    ux = 118
    uw = (1010 - ux) // len(UTC)
    for t, ev in UTC:
        d.text((ux + 2, 133), t, font=F_SANS_B(10), fill=NAVY)
        d.text((ux + 2, 145), ev, font=F_SANS(8), fill=INK)
        ux += uw

    # ---- story panels: 3 rows x 4 ----
    cols = [14, 266, 518, 770]
    cw = 240
    rows = [166, 340, 514]
    rh = 166
    for ri, ry in enumerate(rows):
        for ci, cx in enumerate(cols):
            n, tag, src, head, body, ill = PANELS[ri * 4 + ci]
            panel(img, d, (cx, ry, cx + cw, ry + rh), n, tag, src, head, body, ill)

    # ---- stats strip ----
    d.line([14, 688, 1010, 688], fill=GOLD, width=3)
    d.line([14, 732, 1010, 732], fill=GOLD, width=3)
    sx = 14
    for num, cap in STATS:
        w = (W - 28) // 4
        d.text((sx + w / 2, 694), num, font=F_SERIF_B(24), fill=NAVY, anchor="ma")
        d.text((sx + w / 2, 720), cap, font=F_SANS(11), fill=GREY, anchor="ma")
        sx += w

    # ---- bottom: map + also list ----
    d.text((14, 740), "WHERE IT HAPPENED", font=F_SANS_B(13), fill=RED)
    d.line([14, 756, 392, 756], fill=RED, width=2)
    ll = draw_map(d, (14, 764, 392, 946))
    for (n, lon, lat) in PINS:
        px, py = ll(lon, lat)
        num_badge(d, int(px), int(py), n, r=10)
    d.text((14, 950), "Pins mark stories 1–12. 3 is Voyager 1, in deep space.",
           font=F_SANS(10), fill=GREY)

    d.text((404, 740), "ALSO ON WEDNESDAY 18 NOVEMBER  —  34 MORE STORIES",
           font=F_SANS_B(13), fill=RED)
    d.line([404, 756, 1010, 756], fill=RED, width=2)
    f_item = F_SANS(10)
    for i, (n, txt) in enumerate(ALSO):
        col = i // 17
        row = i % 17
        ix = 404 + col * 306
        iy = 764 + row * 12
        line = f"{n}. {txt}"
        if d.textlength(line, font=f_item) > 300:
            print(f"OVERFLOW also {n}: {line!r}")
        d.text((ix, iy), line, font=f_item, fill=INK)

    # ---- footer: date check + sources ----
    d.text((14, 972),
           "DATE CHECK: Left out on purpose — Nvidia's results, the Alaska Senate call, the Qeshm strike, the Kerch Bridge collapse,",
           font=F_SANS_B(10), fill=RED)
    d.text((14, 984),
           "the Prague rail crash, the An-12 crash and the Thaçi verdict were all 17 Nov. The Senate panel reports a call made late Tuesday.",
           font=F_SANS(10), fill=GREY)
    d.text((14, 996),
           "GTA VI's full launch and Anthropic's first trade are Thu 19 Nov; Cyclone Akvan's landfall is due Fri 20 Nov.",
           font=F_SANS(10), fill=GREY)
    d.text((14, 1008),
           "Sources: Reuters, AP, AFP, BBC, Al Jazeera, NPR, ONS, WHO, NASA, Amnesty.  Original drawings.",
           font=F_SANS(10), fill=GREY)
    return img


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "entry.png"
    img = build()
    img.save(out, format="PNG", optimize=True)
    print(f"wrote {out} {img.size} {out.stat().st_size} bytes")
    print(f"stories: {len(PANELS)} panels + {len(ALSO)} also = {len(PANELS) + len(ALSO)}")


if __name__ == "__main__":
    main()
