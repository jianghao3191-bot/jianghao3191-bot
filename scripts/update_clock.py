#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
辉光管时钟（Nixie Tube Clock）· 北京时间
由 GitHub Actions 每 5 分钟运行一次，重新生成 output/clock.svg。
不依赖任何第三方库，只用标准库，方便在 Actions 里零配置运行。
"""

from __future__ import annotations

import os
from datetime import datetime
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Asia/Shanghai")

W, H = 960, 300
AMBER = "#FFA24B"
AMBER_HOT = "#FFE6CC"
AMBER_DIM = "#B4551F"
CYAN = "#7FE3FF"

WEEK = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def tube(x: float, y: float, w: float, h: float, digit: str) -> str:
    """一个辉光管：玻璃壳 + 内部辉光 + 数字 + 底座"""
    cx = x + w / 2
    return f"""
  <g class="tube">
    <rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="20"
          fill="url(#glass)" stroke="url(#rim)" stroke-width="1.1"/>
    <rect x="{x + 7:.1f}" y="{y + 7:.1f}" width="{w - 14:.1f}" height="{h - 14:.1f}" rx="15"
          fill="none" stroke="#ffffff" stroke-opacity="0.05"/>
    <ellipse cx="{cx:.1f}" cy="{y + h * 0.56:.1f}" rx="{w * 0.36:.1f}" ry="{h * 0.34:.1f}"
             fill="url(#glow)"/>
    <text x="{cx:.1f}" y="{y + h * 0.735:.1f}" class="nixie-glow">{digit}</text>
    <text x="{cx:.1f}" y="{y + h * 0.735:.1f}" class="nixie-core">{digit}</text>
    <path d="M{x + 14:.1f},{y + 18:.1f} q{w * 0.30:.1f},-9 {w * 0.62:.1f},2"
          fill="none" stroke="#ffffff" stroke-opacity="0.16" stroke-width="2.2"
          stroke-linecap="round"/>
    <path d="M{x + 12:.1f},{y + h - 26:.1f} q{w * 0.38:.1f},14 {w * 0.76:.1f},0"
          fill="none" stroke="#000000" stroke-opacity="0.28" stroke-width="10"
          stroke-linecap="round"/>
    <rect x="{x + 10:.1f}" y="{y + h - 9:.1f}" width="{w - 20:.1f}" height="14" rx="7"
          fill="url(#base)" stroke="#ffffff" stroke-opacity="0.10" stroke-width="0.8"/>
  </g>"""


def colon(x: float, y: float, h: float) -> str:
    cy1, cy2 = y + h * 0.34, y + h * 0.66
    return f"""
  <g class="colon">
    <circle cx="{x:.1f}" cy="{cy1:.1f}" r="6.5" fill="{AMBER}" opacity="0.30" filter="url(#soft)"/>
    <circle cx="{x:.1f}" cy="{cy2:.1f}" r="6.5" fill="{AMBER}" opacity="0.30" filter="url(#soft)"/>
    <circle cx="{x:.1f}" cy="{cy1:.1f}" r="5" fill="{AMBER_HOT}"/>
    <circle cx="{x:.1f}" cy="{cy2:.1f}" r="5" fill="{AMBER_HOT}"/>
  </g>"""


def build(now: datetime) -> str:
    hh, mm, ss = f"{now:%H}", f"{now:%M}", f"{now:%S}"

    tw, th, gap, cgap = 112.0, 140.0, 10.0, 30.0
    seq = [hh[0], hh[1], ":", mm[0], mm[1], ":", ss[0], ss[1]]
    total = 6 * tw + 2 * cgap + 7 * gap
    x = (W - total) / 2
    y = 82.0

    body = []
    for item in seq:
        if item == ":":
            body.append(colon(x + cgap / 2, y, th))
            x += cgap + gap
        else:
            body.append(tube(x, y, tw, th, item))
            x += tw + gap

    date_line = f"{now:%Y-%m-%d} · {WEEK[now.weekday()]}"
    stamp = f"SYNC {now:%H:%M:%S}"

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="北京时间 {now:%H:%M:%S}">
  <defs>
    <linearGradient id="card" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#0B1030"/>
      <stop offset="0.45" stop-color="#101B52"/>
      <stop offset="1" stop-color="#1D2E86"/>
    </linearGradient>
    <linearGradient id="sheen" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#ffffff" stop-opacity="0.16"/>
      <stop offset="1" stop-color="#ffffff" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="glass" x1="0" y1="0" x2="0.2" y2="1">
      <stop offset="0" stop-color="#ffffff" stop-opacity="0.13"/>
      <stop offset="0.35" stop-color="#ffffff" stop-opacity="0.04"/>
      <stop offset="1" stop-color="#000000" stop-opacity="0.35"/>
    </linearGradient>
    <linearGradient id="rim" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#ffffff" stop-opacity="0.55"/>
      <stop offset="0.5" stop-color="#9FB6FF" stop-opacity="0.20"/>
      <stop offset="1" stop-color="#ffffff" stop-opacity="0.30"/>
    </linearGradient>
    <linearGradient id="base" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#2A355F"/>
      <stop offset="1" stop-color="#0B0F26"/>
    </linearGradient>
    <radialGradient id="glow" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0" stop-color="{AMBER}" stop-opacity="0.55"/>
      <stop offset="0.55" stop-color="{AMBER}" stop-opacity="0.16"/>
      <stop offset="1" stop-color="{AMBER}" stop-opacity="0"/>
    </radialGradient>
    <filter id="soft" x="-60%" y="-60%" width="220%" height="220%">
      <feGaussianBlur stdDeviation="7"/>
    </filter>
    <filter id="halo" x="-60%" y="-60%" width="220%" height="220%">
      <feGaussianBlur stdDeviation="4"/>
    </filter>
    <style>
      .nixie-core {{
        font-family: "DIN Alternate", "Bahnschrift", "Segoe UI Variable", "Segoe UI", Consolas, monospace;
        font-size: 96px; font-weight: 700; letter-spacing: 0;
        fill: {AMBER_HOT}; text-anchor: middle;
      }}
      .nixie-glow {{
        font-family: "DIN Alternate", "Bahnschrift", "Segoe UI Variable", "Segoe UI", Consolas, monospace;
        font-size: 96px; font-weight: 700; letter-spacing: 0;
        fill: {AMBER}; text-anchor: middle; opacity: 0.85; filter: url(#halo);
      }}
      .label {{ font-family: "SF Mono", "Cascadia Code", Consolas, monospace; font-size: 13px;
                letter-spacing: 3px; fill: #C9D6FF; }}
      .dot-live {{ animation: pulse 1.6s ease-in-out infinite; }}
      .colon {{ animation: blink 2s steps(1, end) infinite; }}
      @keyframes pulse {{ 0%,100% {{ opacity: .35 }} 50% {{ opacity: 1 }} }}
      @keyframes blink {{ 0%,55% {{ opacity: 1 }} 56%,100% {{ opacity: .45 }} }}
    </style>
  </defs>

  <rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="28"
        fill="url(#card)" stroke="#ffffff" stroke-opacity="0.16"/>
  <rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="28" fill="url(#sheen)" opacity="0.55"/>
  <rect x="18" y="1.5" width="{W - 36}" height="120" rx="26" fill="url(#sheen)" opacity="0.20"/>

  <text x="40" y="46" class="label">TIME</text>
  <text x="{W - 40}" y="46" class="label" text-anchor="end">{esc(stamp)}</text>
{''.join(body)}

  <text x="{W / 2}" y="268" text-anchor="middle"
        font-family="'PingFang SC','Microsoft YaHei',sans-serif" font-size="20"
        fill="#DFE8FF" opacity="0.9">{esc(date_line)}</text>
</svg>
"""


def main() -> None:
    now = datetime.now(TZ)
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output", "clock.svg")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(build(now))
    print(f"wrote {out} at {now:%Y-%m-%d %H:%M:%S %Z}")


if __name__ == "__main__":
    main()
