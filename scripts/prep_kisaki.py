# -*- coding: utf-8 -*-
"""从官方立绘裁出头像，并把介绍页缩成角色卡。"""
from __future__ import annotations

import os

from PIL import Image, ImageEnhance

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "assets", "kisaki_src")
SRC2 = os.path.join(ROOT, "assets", "kisaki_src")
OUT = os.path.join(ROOT, "assets", "kisaki")


def main() -> None:
    os.makedirs(OUT, exist_ok=True)

    bust = Image.open(os.path.join(SRC, "bust.png")).convert("RGBA")
    avatar = bust.crop((175, 55, 835, 715)).resize((640, 640), Image.LANCZOS)
    avatar.save(os.path.join(OUT, "avatar.png"), optimize=True)

    card = Image.open(os.path.join(SRC2, "card_src.png")).convert("RGB")
    card = card.resize((760, int(card.height * 760 / card.width)), Image.LANCZOS)
    card = ImageEnhance.Brightness(card).enhance(1.04)
    # 只保留上半部分：标题 + 立绘 + 学校标签，去掉大段英文简介
    card = card.crop((0, 0, card.width, int(card.width * 1.36)))
    card.save(os.path.join(OUT, "card.png"), optimize=True)

    for n in ("avatar.png", "card.png"):
        p = os.path.join(OUT, n)
        print(n, Image.open(p).size, os.path.getsize(p))


if __name__ == "__main__":
    main()
