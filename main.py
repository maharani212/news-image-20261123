#!/usr/bin/env python3
"""World News - Monday 23 November 2026. Front-page image, 1024x1024, deterministic.

Writes /output/entry.png. No network, no randomness, no timestamps.
All artwork is drawn with PIL primitives; all text uses DejaVu fonts.
Every illustration is drawn on its own layer clipped to its panel, so no
artwork can spill into neighbouring text.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

NAVY = (20, 33, 61)
PAPER = (247, 243, 234)
RED = (193, 18, 31)
GOLD = (224, 168, 0)
INK = (24, 24, 24)
GREY = (90, 90, 90)
CARD = (255, 255, 255)
BORDER = (200, 196, 186)
WHITE = (255, 255, 255)


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for wd in words:
        test = (cur + " " + wd).strip()
        if draw.textlength(test, font=fnt) <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def star_points(cx, cy, r_out, r_in, n=5, rot=-90):
    pts = []
    for i in range(2 * n):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(rot + i * 180.0 / n)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def draw_flame(d, cx, cy, s, c1=(255, 120, 0), c2=(255, 200, 0)):
    pts = [
        (cx, cy - s),
        (cx + 0.55 * s, cy - 0.25 * s),
        (cx + 0.45 * s, cy + 0.35 * s),
        (cx + 0.28 * s, cy + 0.62 * s),
        (cx, cy + 0.75 * s),
        (cx - 0.28 * s, cy + 0.62 * s),
        (cx - 0.45 * s, cy + 0.35 * s),
        (cx - 0.55 * s, cy - 0.25 * s),
    ]
    d.polygon(pts, fill=c1)
    pts2 = [
        (cx, cy - 0.35 * s),
        (cx + 0.28 * s, cy + 0.05 * s),
        (cx + 0.18 * s, cy + 0.45 * s),
        (cx, cy + 0.55 * s),
        (cx - 0.18 * s, cy + 0.45 * s),
        (cx - 0.28 * s, cy + 0.05 * s),
    ]
    d.polygon(pts2, fill=c2)


def draw_ship(d, x0, y0, w, h, hull=(40, 60, 90)):
    cx = x0 + w / 2
    # flame above the mast (kept inside the box)
    draw_flame(d, cx, y0 + 0.16 * h, 0.11 * h)
    # mast
    d.line([(cx, y0 + 0.26 * h), (cx, y0 + 0.55 * h)], fill=hull, width=4)
    # hull
    d.polygon(
        [
            (cx - 0.45 * w, y0 + 0.55 * h),
            (cx + 0.45 * w, y0 + 0.55 * h),
            (cx + 0.32 * w, y0 + 0.82 * h),
            (cx - 0.32 * w, y0 + 0.82 * h),
        ],
        fill=hull,
    )
    # waves
    d.line([(x0 + 4, y0 + 0.90 * h), (x0 + w - 4, y0 + 0.90 * h)], fill=WHITE, width=3)


def draw_building_burst(d, x0, y0, w, h, col=(70, 90, 120)):
    cx = x0 + w / 2
    bw, bh = 0.5 * w, 0.62 * h
    top = y0 + 0.28 * h
    d.rectangle([cx - bw / 2, top, cx + bw / 2, top + bh], fill=col)
    for r in range(3):
        for c in range(3):
            wx = cx - bw / 2 + 0.12 * w + c * 0.16 * w
            wy = top + 0.10 * h + r * 0.16 * h
            d.rectangle([wx, wy, wx + 0.07 * w, wy + 0.07 * h], fill=(255, 230, 120))
    d.polygon(star_points(cx + 0.30 * w, y0 + 0.16 * h, 0.14 * h, 0.06 * h), fill=(255, 200, 0))


def draw_factory(d, x0, y0, w, h, col=(120, 60, 30)):
    cx = x0 + w / 2
    # chimney + flame (inside the box)
    d.rectangle([cx + 0.28 * w, y0 + 0.14 * h, cx + 0.42 * w, y0 + 0.85 * h], fill=(80, 40, 20))
    draw_flame(d, cx + 0.35 * w, y0 + 0.10 * h, 0.07 * h)
    # sawtooth roof + body
    d.polygon(
        [
            (cx - 0.5 * w, y0 + 0.85 * h),
            (cx - 0.5 * w, y0 + 0.45 * h),
            (cx - 0.25 * w, y0 + 0.28 * h),
            (cx, y0 + 0.45 * h),
            (cx + 0.25 * w, y0 + 0.28 * h),
            (cx + 0.5 * w, y0 + 0.45 * h),
            (cx + 0.5 * w, y0 + 0.85 * h),
        ],
        fill=col,
    )
    # windows
    for c in range(3):
        wx = cx - 0.42 * w + c * 0.28 * w
        d.rectangle([wx, y0 + 0.58 * h, wx + 0.14 * w, y0 + 0.72 * h], fill=(255, 230, 120))


def draw_shield(d, x0, y0, w, h, col=(140, 30, 30)):
    cx, cy = x0 + w / 2, y0 + h / 2
    d.polygon(
        [
            (cx - 0.38 * w, cy - 0.42 * h),
            (cx + 0.38 * w, cy - 0.42 * h),
            (cx + 0.38 * w, cy + 0.05 * h),
            (cx, cy + 0.46 * h),
            (cx - 0.38 * w, cy + 0.05 * h),
        ],
        fill=col,
    )
    d.line([(cx - 0.20 * w, cy), (cx - 0.05 * w, cy + 0.16 * h), (cx + 0.22 * w, cy - 0.20 * h)],
           fill=WHITE, width=5)


def draw_flags(d, x0, y0, w, h):
    cx, cy = x0 + w / 2, y0 + h / 2
    d.line([(cx - 0.28 * w, cy - 0.48 * h), (cx - 0.28 * w, cy + 0.48 * h)], fill=(60, 60, 60), width=4)
    d.line([(cx + 0.28 * w, cy - 0.48 * h), (cx + 0.28 * w, cy + 0.48 * h)], fill=(60, 60, 60), width=4)
    d.rectangle([cx - 0.28 * w, cy - 0.48 * h, cx + 0.02 * w, cy - 0.16 * h], fill=(220, 40, 40))
    d.rectangle([cx + 0.28 * w, cy - 0.48 * h, cx + 0.58 * w, cy - 0.32 * h], fill=(255, 153, 51))
    d.rectangle([cx + 0.28 * w, cy - 0.32 * h, cx + 0.58 * w, cy - 0.16 * h], fill=(255, 255, 255))
    d.rectangle([cx + 0.28 * w, cy - 0.16 * h, cx + 0.58 * w, cy - 0.0 * h], fill=(19, 136, 8))


def draw_robot(d, x0, y0, w, h, ban=False):
    cx = x0 + w / 2
    # antenna dot + line (inside the box)
    d.ellipse([cx - 0.06 * w, y0 + 0.03 * h, cx + 0.06 * w, y0 + 0.11 * h], fill=(220, 40, 40))
    d.line([(cx, y0 + 0.11 * h), (cx, y0 + 0.20 * h)], fill=(60, 60, 60), width=4)
    # head
    d.rounded_rectangle([cx - 0.36 * w, y0 + 0.20 * h, cx + 0.36 * w, y0 + 0.58 * h],
                        radius=12, fill=(90, 90, 150))
    d.ellipse([cx - 0.19 * w, y0 + 0.32 * h, cx - 0.05 * w, y0 + 0.44 * h], fill=(120, 255, 220))
    d.ellipse([cx + 0.05 * w, y0 + 0.32 * h, cx + 0.19 * w, y0 + 0.44 * h], fill=(120, 255, 220))
    d.line([(cx - 0.17 * w, y0 + 0.51 * h), (cx + 0.17 * w, y0 + 0.51 * h)], fill=(120, 255, 220), width=4)
    # body
    d.rectangle([cx - 0.26 * w, y0 + 0.64 * h, cx + 0.26 * w, y0 + 0.88 * h], fill=(60, 60, 110))
    if ban:
        d.ellipse([cx - 0.44 * w, y0 + 0.02 * h, cx + 0.44 * w, y0 + 0.98 * h],
                  outline=(220, 30, 30), width=7)
        d.line([(cx - 0.33 * w, y0 + 0.86 * h), (cx + 0.33 * w, y0 + 0.14 * h)],
               fill=(220, 30, 30), width=7)


def draw_star_icon(d, x0, y0, w, h, col=(200, 30, 30)):
    cx, cy = x0 + w / 2, y0 + h / 2
    d.polygon(star_points(cx, cy, 0.40 * h, 0.17 * h), fill=col)


def draw_badge(d, x0, y0, w, h, col=(30, 120, 60)):
    cx, cy = x0 + w / 2, y0 + h / 2
    d.ellipse([cx - 0.40 * h, cy - 0.40 * h, cx + 0.40 * h, cy + 0.40 * h], fill=col)
    d.polygon(star_points(cx, cy, 0.25 * h, 0.11 * h), fill=(255, 215, 0))


def draw_batball(d, x0, y0, w, h):
    cx, cy = x0 + w / 2, y0 + h / 2
    d.polygon(
        [
            (cx - 0.40 * w, cy + 0.40 * h),
            (cx - 0.28 * w, cy + 0.28 * h),
            (cx + 0.28 * w, cy - 0.40 * h),
            (cx + 0.40 * w, cy - 0.28 * h),
        ],
        fill=(180, 130, 60),
    )
    d.ellipse([cx - 0.05 * w, cy - 0.05 * h, cx + 0.33 * w, cy + 0.33 * h],
              fill=WHITE, outline=(180, 30, 30), width=3)
    d.arc([cx - 0.05 * w, cy - 0.05 * h, cx + 0.33 * w, cy + 0.33 * h], 200, 340, fill=(180, 30, 30), width=3)


def draw_tennis(d, x0, y0, w, h):
    cx, cy = x0 + w / 2, y0 + h / 2
    d.ellipse([cx - 0.38 * h, cy - 0.38 * h, cx + 0.38 * h, cy + 0.38 * h], fill=(190, 220, 60))
    d.arc([cx - 0.38 * h, cy - 0.38 * h, cx + 0.38 * h, cy + 0.38 * h], 300, 60, fill=WHITE, width=5)
    d.arc([cx - 0.38 * h, cy - 0.38 * h, cx + 0.38 * h, cy + 0.38 * h], 120, 240, fill=WHITE, width=5)


def draw_megaphone(d, x0, y0, w, h, col=(200, 160, 0)):
    cx, cy = x0 + w / 2, y0 + h / 2
    d.polygon(
        [
            (cx - 0.33 * w, cy - 0.10 * h),
            (cx + 0.15 * w, cy - 0.38 * h),
            (cx + 0.15 * w, cy + 0.38 * h),
            (cx - 0.33 * w, cy + 0.10 * h),
        ],
        fill=col,
    )
    d.rectangle([cx - 0.46 * w, cy - 0.10 * h, cx - 0.31 * w, cy + 0.10 * h], fill=(120, 90, 0))
    d.rectangle([cx - 0.14 * w, cy + 0.10 * h, cx - 0.01 * w, cy + 0.44 * h], fill=(90, 90, 90))
    d.arc([cx + 0.20 * w, cy - 0.22 * h, cx + 0.38 * w, cy + 0.22 * h], 300, 60, fill=(60, 60, 60), width=4)
    d.arc([cx + 0.28 * w, cy - 0.32 * h, cx + 0.46 * w, cy + 0.32 * h], 300, 60, fill=(60, 60, 60), width=4)


def draw_globe(d, x0, y0, w, h):
    cx, cy = x0 + w / 2, y0 + h / 2
    r = 0.36 * h
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(30, 90, 140))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(180, 220, 255), width=3)
    d.ellipse([cx - 0.45 * r, cy - r, cx + 0.45 * r, cy + r], outline=(180, 220, 255), width=2)
    d.line([(cx - r, cy), (cx + r, cy)], fill=(180, 220, 255), width=2)
    d.arc([cx - r, cy - 0.55 * r, cx + r, cy + 0.55 * r], 0, 360, fill=(180, 220, 255), width=2)
    d.ellipse([cx - 0.55 * r, cy - 0.60 * r, cx + 0.05 * r, cy - 0.05 * r], fill=(60, 160, 90))
    d.ellipse([cx - 0.10 * r, cy + 0.10 * r, cx + 0.60 * r, cy + 0.60 * r], fill=(60, 160, 90))
    d.line([(cx - 0.55 * r, cy - 0.75 * r), (cx - 0.25 * r, cy - 0.35 * r),
            (cx - 0.50 * r, cy - 0.05 * r), (cx - 0.15 * r, cy + 0.35 * r)],
           fill=(255, 60, 40), width=4)
    draw_flame(d, cx + 0.55 * r, cy + 0.55 * r, 0.26 * r)


ICONS = {
    "flame_ship": lambda d, x, y, w, h: draw_ship(d, x, y, w, h),
    "building": lambda d, x, y, w, h: draw_building_burst(d, x, y, w, h),
    "factory": lambda d, x, y, w, h: draw_factory(d, x, y, w, h),
    "shield": lambda d, x, y, w, h: draw_shield(d, x, y, w, h),
    "flags": lambda d, x, y, w, h: draw_flags(d, x, y, w, h),
    "robot": lambda d, x, y, w, h: draw_robot(d, x, y, w, h),
    "robot_ban": lambda d, x, y, w, h: draw_robot(d, x, y, w, h, ban=True),
    "star": lambda d, x, y, w, h: draw_star_icon(d, x, y, w, h),
    "badge": lambda d, x, y, w, h: draw_badge(d, x, y, w, h),
    "batball": lambda d, x, y, w, h: draw_batball(d, x, y, w, h),
    "tennis": lambda d, x, y, w, h: draw_tennis(d, x, y, w, h),
    "megaphone": lambda d, x, y, w, h: draw_megaphone(d, x, y, w, h),
    "globe": lambda d, x, y, w, h: draw_globe(d, x, y, w, h),
}


def icon_layer(icon_key, w, h, bg):
    """Render one illustration clipped to its own panel (no spillover)."""
    layer = Image.new("RGB", (w, h), bg)
    d = ImageDraw.Draw(layer)
    ICONS[icon_key](d, 0, 0, w, h)
    return layer


# (tag, headline, panel colour, icon key)
STORIES = [
    ("MIDDLE EAST", "Tankers ablaze as Iran-US war widens", (120, 20, 20), "flame_ship"),
    ("UKRAINE", "Drone hits Kyiv block; 14 missing", (52, 68, 96), "building"),
    ("BALTIC", "Russian cargo ship burns off Finland", (20, 90, 100), "flame_ship"),
    ("INDONESIA", "Factory fire: 7 dead, 50 missing", (200, 90, 20), "factory"),
    ("AFRICA", "24 civilians killed in South Sudan", (110, 70, 40), "shield"),
    ("SUDAN", "Drones hit homes, UN site in Khartoum", (90, 90, 90), "building"),
    ("SOUTH ASIA", "Nepal PM meets Modi in Delhi", (200, 120, 20), "flags"),
    ("EAST ASIA", "Seoul minister quits in AI exam scandal", (100, 60, 140), "robot"),
    ("EAST ASIA", "Kim: North Korea wants security", (160, 30, 30), "star"),
    ("TECH", "UN keeps talks on killer-robot ban", (30, 60, 120), "robot_ban"),
    ("AMERICAS", "Mexico nabs cartel boss 'El Chapo Isidro'", (30, 120, 60), "badge"),
    ("SPORT", "India's record 720/9 stuns New Zealand", (30, 110, 60), "batball"),
    ("SPORT", "Alcaraz wins first ATP Finals crown", (40, 90, 180), "tennis"),
    ("EUROPE", "Thousands march in Lisbon on costs", (190, 160, 0), "megaphone"),
]

TAG_COLOURS = {
    "MIDDLE EAST": (178, 24, 24),
    "UKRAINE": (40, 70, 140),
    "BALTIC": (16, 110, 120),
    "INDONESIA": (200, 90, 20),
    "AFRICA": (140, 80, 30),
    "SUDAN": (90, 90, 90),
    "SOUTH ASIA": (190, 110, 10),
    "EAST ASIA": (120, 50, 160),
    "TECH": (30, 60, 140),
    "AMERICAS": (20, 120, 60),
    "SPORT": (20, 110, 70),
    "EUROPE": (170, 140, 0),
}


def main():
    img = Image.new("RGB", (W, H), PAPER)

    # --- masthead ---
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 118], fill=NAVY)
    d.text((W // 2, 20), "WORLD NEWS", font=font(FONT_BOLD, 62), fill=WHITE, anchor="ma")
    d.text((W // 2, 86), "MONDAY 23 NOVEMBER 2026", font=font(FONT_BOLD, 24), fill=GOLD, anchor="ma")
    d.rectangle([0, 118, W, 122], fill=RED)

    # --- hero: COP31 (illustration clipped to its panel) ---
    img.paste(icon_layer("globe", 284, 166, (20, 60, 80)), (16, 130))
    d = ImageDraw.Draw(img)
    tx = 316
    d.text((tx, 138), "CLIMATE", font=font(FONT_BOLD, 16), fill=RED)
    d.text((tx, 162), "COP31 COLLAPSES", font=font(FONT_BOLD, 34), fill=INK)
    d.text((tx, 202), "WITHOUT A DEAL", font=font(FONT_BOLD, 34), fill=INK)
    d.text((tx, 248),
           "Turkiye's final draft drops 'fossil fuels';",
           font=font(FONT_REG, 15), fill=GREY)
    d.text((tx, 270),
           "talks end with no cover decision.",
           font=font(FONT_REG, 15), fill=GREY)

    # --- grid: 5 cols x 3 rows, 14 stories + 1 footer cell ---
    cw, ch = 192, 228
    rows_y = [304, 540, 776]
    cols_x = [16, 216, 416, 616, 816]
    tag_f = font(FONT_BOLD, 11)
    head_f = font(FONT_BOLD, 15)

    for idx, (tag, headline, colour, icon) in enumerate(STORIES):
        r, c = divmod(idx, 5)
        x0, y0 = cols_x[c], rows_y[r]
        d.rectangle([x0, y0, x0 + cw, y0 + ch], fill=CARD, outline=BORDER, width=1)
        # illustration panel, clipped to its own layer
        img.paste(icon_layer(icon, cw - 2, 106, colour), (x0 + 1, y0 + 1))
        d = ImageDraw.Draw(img)
        d.text((x0 + 8, y0 + 116), tag, font=tag_f, fill=TAG_COLOURS[tag])
        lines = wrap(d, headline, head_f, cw - 16)
        ly = y0 + 136
        for ln in lines[:4]:
            d.text((x0 + 8, ly), ln, font=head_f, fill=INK)
            ly += 20

    # footer cell (bottom-right): story count + sources
    fx0, fy0 = cols_x[4], rows_y[2]
    d.rectangle([fx0, fy0, fx0 + cw, fy0 + ch], fill=NAVY)
    d.text((fx0 + cw // 2, fy0 + 26), "15", font=font(FONT_BOLD, 54), fill=WHITE, anchor="ma")
    d.text((fx0 + cw // 2, fy0 + 92), "STORIES", font=font(FONT_BOLD, 18), fill=GOLD, anchor="ma")
    d.text((fx0 + cw // 2, fy0 + 132), "FROM AROUND", font=font(FONT_REG, 13), fill=WHITE, anchor="ma")
    d.text((fx0 + cw // 2, fy0 + 152), "THE WORLD", font=font(FONT_REG, 13), fill=WHITE, anchor="ma")
    d.text((fx0 + cw // 2, fy0 + 192), "Sources: AFP, Reuters,",
           font=font(FONT_REG, 11), fill=(200, 200, 200), anchor="ma")
    d.text((fx0 + cw // 2, fy0 + 208), "AP, NAMPA",
           font=font(FONT_REG, 11), fill=(200, 200, 200), anchor="ma")

    out = "/output/entry.png"
    os.makedirs("/output", exist_ok=True)
    img.save(out, format="PNG")
    print("wrote", out, img.size)


if __name__ == "__main__":
    main()
