# -*- coding: utf-8 -*-
"""
生成 iOS「液态玻璃」风格的 GitHub 主页横幅（碧蓝档案 · 龍華キサキ）。

用法：python scripts/make_hero.py
依赖 assets/kisaki_src/lobby.jpg（官方回忆大厅插画）。
"""
from __future__ import annotations

import os
import random
from datetime import datetime
from zoneinfo import ZoneInfo

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")
SRC = os.path.join(ASSETS, "kisaki_src")
FONT_DIR = r"C:\Windows\Fonts"

W, H = 1600, 640
BG = os.path.join(SRC, "lobby.jpg")


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


def vgrad(size, stops):
    w, h = size
    img = Image.new("RGBA", (1, h))
    px = img.load()
    for y in range(h):
        t = y / max(1, h - 1)
        for i in range(len(stops) - 1):
            p0, c0 = stops[i]
            p1, c1 = stops[i + 1]
            if p0 <= t <= p1:
                k = (t - p0) / max(1e-6, p1 - p0)
                px[0, y] = tuple(int(c0[j] + (c1[j] - c0[j]) * k) for j in range(4))
                break
    return img.resize(size, Image.BILINEAR)


def hgrad(size, stops):
    w, h = size
    img = Image.new("RGBA", (w, 1))
    px = img.load()
    for x in range(w):
        t = x / max(1, w - 1)
        for i in range(len(stops) - 1):
            p0, c0 = stops[i]
            p1, c1 = stops[i + 1]
            if p0 <= t <= p1:
                k = (t - p0) / max(1e-6, p1 - p0)
                px[x, 0] = tuple(int(c0[j] + (c1[j] - c0[j]) * k) for j in range(4))
                break
    return img.resize(size, Image.BILINEAR)


def rounded_mask(size, radius):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], radius=radius, fill=255)
    return m


def fit_cover(img: Image.Image, size, focus_y=0.5) -> Image.Image:
    w, h = size
    s = max(w / img.width, h / img.height)
    nw, nh = int(img.width * s + 0.5), int(img.height * s + 0.5)
    img = img.convert("RGBA").resize((nw, nh), Image.LANCZOS)
    left = (nw - w) // 2
    top = int((nh - h) * focus_y)
    return img.crop((left, top, left + w, top + h))


def glass_panel(base: Image.Image, box, radius=44, tint=(255, 255, 255, 26), border=76, blur=30):
    x0, y0, x1, y1 = [int(v) for v in box]
    w, h = x1 - x0, y1 - y0
    mask = rounded_mask((w, h), radius)

    backdrop = base.crop((x0, y0, x1, y1)).filter(ImageFilter.GaussianBlur(blur))
    # 让玻璃把底下的颜色“吸”上来，避免灰板
    backdrop = ImageEnhance.Color(backdrop).enhance(1.9)
    backdrop = ImageEnhance.Brightness(backdrop).enhance(1.16)

    sh = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle(
        [x0 - 8, y0 + 16, x1 + 8, y1 + 30], radius=radius + 8, fill=(2, 4, 16, 150)
    )
    base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(30)))

    panel = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    panel.paste(backdrop, (0, 0))
    panel = Image.composite(
        Image.alpha_composite(panel, Image.new("RGBA", (w, h), tint)),
        Image.new("RGBA", (w, h), (0, 0, 0, 0)), mask,
    )

    sheen = vgrad((w, h), [(0.0, (255, 255, 255, 52)), (0.40, (255, 255, 255, 4)), (1.0, (255, 255, 255, 0))])
    panel = Image.alpha_composite(panel, Image.composite(sheen, Image.new("RGBA", (w, h), (0, 0, 0, 0)), mask))

    spec = Image.new("RGBA", (w * 2, h * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(spec)
    d.polygon([(0, h * 1.7), (w * 0.85, 0), (w * 1.2, 0), (w * 0.3, h * 1.7)], fill=(255, 255, 255, 22))
    spec = spec.filter(ImageFilter.GaussianBlur(22)).crop((0, 0, w, h))
    panel = Image.alpha_composite(panel, Image.composite(spec, Image.new("RGBA", (w, h), (0, 0, 0, 0)), mask))

    edge = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ed = ImageDraw.Draw(edge)
    ed.rounded_rectangle([0, 0, w - 1, h - 1], radius=radius, outline=(255, 255, 255, border), width=2)
    ed.rounded_rectangle([3, 3, w - 4, h - 4], radius=radius - 3, outline=(255, 255, 255, 26), width=1)
    panel = Image.alpha_composite(panel, Image.composite(edge, Image.new("RGBA", (w, h), (0, 0, 0, 0)), mask))

    base.alpha_composite(panel, (x0, y0))
    return base


def blob(img, cx, cy, rx, ry, color, blur=70, alpha=90):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=color + (alpha,))
    img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(blur)))


def build() -> Image.Image:
    bg = fit_cover(Image.open(BG), (W, H), focus_y=0.40)
    bg = bg.filter(ImageFilter.GaussianBlur(1.1))
    bg = ImageEnhance.Color(bg).enhance(1.42)
    bg = ImageEnhance.Brightness(bg).enhance(1.18)
    bg = ImageEnhance.Contrast(bg).enhance(1.08)
    canvas = bg.copy()

    # 只压暗左侧，右侧保留原作的光
    canvas.alpha_composite(hgrad((W, H), [
        (0.0, (2, 4, 16, 172)), (0.34, (3, 6, 24, 104)), (0.56, (0, 0, 0, 10)), (1.0, (0, 0, 0, 0)),
    ]))
    canvas.alpha_composite(vgrad((W, H), [
        (0.0, (0, 0, 0, 30)), (0.55, (0, 0, 0, 0)), (1.0, (2, 4, 18, 110)),
    ]))
    blob(canvas, 980, 640, 520, 220, (108, 140, 255), blur=120, alpha=40)

    # 玻璃名牌：只有名字
    box = (72, 168, 800, 420)
    bw, bh = box[2] - box[0], box[3] - box[1]
    canvas = glass_panel(canvas, box, radius=40, tint=(255, 255, 255, 20), border=64, blur=40)

    d = ImageDraw.Draw(canvas)
    f_name = font("segoeuib.ttf", 96)
    b = d.textbbox((0, 0), "lonGon", font=f_name)
    nx = box[0] + 52 - b[0]
    ny = box[1] + (bh - (b[3] - b[1])) / 2 - b[1]
    d.text((nx, ny), "lonGon", font=f_name, fill=(255, 255, 255, 255))

    # 右侧：本地时间（不写地名）
    now = datetime.now(ZoneInfo("Asia/Shanghai"))
    f_time = font("segoeuib.ttf", 44)
    f_day = font("segoeui.ttf", 14)
    ts, ds = now.strftime("%H:%M"), now.strftime("%m.%d")
    d.text((box[2] - 56 - d.textlength(ts, font=f_time), box[1] + 82), ts,
           font=f_time, fill=(255, 255, 255, 232))
    d.text((box[2] - 56 - d.textlength(ds, font=f_day), box[1] + 146), ds,
           font=f_day, fill=(214, 226, 255, 165))

    # 署名
    d.text((76, 598), "Art © NEXON Games / Yostar · Blue Archive",
           font=font("segoeui.ttf", 13), fill=(214, 224, 255, 120))

    # 细颗粒
    random.seed(3)
    noise = Image.effect_noise((W, H), 7).convert("L").point(lambda v: 14 if v > 130 else 0)
    grain = Image.new("RGBA", (W, H), (255, 255, 255, 0))
    grain.putalpha(noise)
    canvas.alpha_composite(grain)

    return canvas.convert("RGB")


def main() -> None:
    img = build()
    out = os.path.join(ASSETS, "hero.png")
    img.save(out, optimize=True)
    print("wrote", out, img.size, os.path.getsize(out))


if __name__ == "__main__":
    main()
