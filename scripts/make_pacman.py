#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成赛博吃豆人动画 SVG（纯 CSS 动画，可被 GitHub <img> 直接加载）。"""

from __future__ import annotations

import math
import os

W, H = 1100, 230
LANE_Y = 112
R = 30
X0, X1 = 130, 1010
T = 10.0  # 一个循环 10 秒
N_DOTS = 20
DOT_R = 6.5
GHOSTS = [
    {"color": "#7FE3FF", "delay": -1.4, "dx": 0, "name": "CYAN"},
    {"color": "#FF7AD9", "delay": -2.8, "dx": 0, "name": "PINK"},
    {"color": "#A78BFA", "delay": -4.2, "dx": 0, "name": "VIOLET"},
]


def pac_path(cx: float, cy: float, r: float, half_deg: float) -> str:
    """吃豆人：圆盘减去一个楔形缺口。half_deg 是缺口半角。"""
    a = math.radians(half_deg)
    p1x, p1y = cx + r * math.cos(a), cy + r * math.sin(a)
    p2x, p2y = cx + r * math.cos(-a), cy + r * math.sin(-a)
    large = 1 if (360 - 2 * half_deg) > 180 else 0
    return (
        f"M{cx:.2f},{cy:.2f} L{p1x:.2f},{p1y:.2f} "
        f"A{r:.2f},{r:.2f} 0 {large},1 {p2x:.2f},{p2y:.2f} Z"
    )


def ghost(cx: float, cy: float, r: float, color: str) -> str:
    x, y = cx - r, cy - r
    top = y
    bottom = y + 2 * r
    scallop = 2 * r / 4
    d = f"M{x:.1f},{bottom:.1f} L{x:.1f},{top + r:.1f} "
    d += f"A{r:.1f},{r:.1f} 0 0,1 {x + 2 * r:.1f},{top + r:.1f} "
    d += f"L{x + 2 * r:.1f},{bottom:.1f} "
    # 底部三个波浪
    xs = x + 2 * r
    for i in range(4):
        nx = xs - scallop
        d += f"Q{nx + scallop / 2:.1f},{bottom + r * 0.42:.1f} {nx:.1f},{bottom:.1f} "
        xs = nx
    d += "Z"
    return f"""
  <g class="ghost" style="--d:{GHOSTS_DELAY.get(color, 0)}s">
    <path d="{d}" fill="{color}" fill-opacity="0.34" stroke="{color}" stroke-width="2"/>
    <path d="{d}" fill="{color}" fill-opacity="0.10" filter="url(#gblur)"/>
    <ellipse cx="{cx - r * 0.3:.1f}" cy="{cy - r * 0.22:.1f}" rx="{r * 0.24:.1f}" ry="{r * 0.30:.1f}" fill="#FFFFFF"/>
    <ellipse cx="{cx + r * 0.34:.1f}" cy="{cy - r * 0.22:.1f}" rx="{r * 0.24:.1f}" ry="{r * 0.30:.1f}" fill="#FFFFFF"/>
    <circle cx="{cx - r * 0.24:.1f}" cy="{cy - r * 0.18:.1f}" r="{r * 0.11:.1f}" fill="#0A0F2C"/>
    <circle cx="{cx + r * 0.40:.1f}" cy="{cy - r * 0.18:.1f}" r="{r * 0.11:.1f}" fill="#0A0F2C"/>
  </g>"""


GHOSTS_DELAY = {}


def build() -> str:
    dots = []
    keys = []
    step = (X1 - 40 - (X0 + 40)) / (N_DOTS - 1)
    for i in range(N_DOTS):
        dx = X0 + 40 + step * i
        t_hit = (dx - R - X0) / (X1 - X0) * T
        p = max(0.0, min(100.0, t_hit / T * 100))
        keys.append(
            f"@keyframes dot{i} {{ 0%,{p - 0.4:.2f}% {{opacity:1}} {p + 0.6:.2f}%,100% {{opacity:0}} }}"
        )
        dots.append(
            f'<circle class="dot" cx="{dx:.1f}" cy="{LANE_Y}" r="{DOT_R}" '
            f'style="animation-name:dot{i}"/>'
        )

    # 透视网格
    grid = []
    for i in range(-6, 7):
        gx = W / 2 + i * 120
        grid.append(
            f'<line x1="{W / 2 + i * 40:.1f}" y1="{LANE_Y + 34}" x2="{gx:.1f}" y2="{H}" '
            f'stroke="#5B7BFF" stroke-opacity="0.18" stroke-width="1"/>'
        )
    for j in range(1, 5):
        gy = LANE_Y + 34 + (H - LANE_Y - 34) * (j / 4) ** 1.7
        grid.append(
            f'<line x1="0" y1="{gy:.1f}" x2="{W}" y2="{gy:.1f}" '
            f'stroke="#5B7BFF" stroke-opacity="{0.16 - j * 0.02:.2f}" stroke-width="1"/>'
        )

    mouth_open = pac_path(0, 0, R, 42)
    mouth_mid = pac_path(0, 0, R, 20)
    mouth_shut = pac_path(0, 0, R, 1)

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="赛博吃豆人">
  <defs>
    <linearGradient id="panel" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#070B1E"/>
      <stop offset="0.6" stop-color="#0C1233"/>
      <stop offset="1" stop-color="#141C4A"/>
    </linearGradient>
    <linearGradient id="sheen" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#ffffff" stop-opacity="0.10"/>
      <stop offset="1" stop-color="#ffffff" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="pacbody" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#FFE27A"/>
      <stop offset="1" stop-color="#FFB02E"/>
    </linearGradient>
    <filter id="gblur" x="-80%" y="-80%" width="260%" height="260%">
      <feGaussianBlur stdDeviation="6"/>
    </filter>
    <linearGradient id="sweep" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#7FE3FF" stop-opacity="0"/><stop offset="0.5" stop-color="#7FE3FF" stop-opacity="0.10"/><stop offset="1" stop-color="#7FE3FF" stop-opacity="0"/></linearGradient>`r`n    <filter id="pglow" x="-80%" y="-80%" width="260%" height="260%">
      <feGaussianBlur stdDeviation="7"/>
    </filter>
    <style>
      .dot {{ fill:#FFE9A8; animation:{T}s linear infinite; animation-delay:0s; }}
      .pac-run {{ animation: run {T}s linear infinite; }}
      .ghost {{ animation: run {T}s linear infinite; animation-delay: var(--d); }}
      .ghost .eye-glow {{ animation: none; }}
      .bob {{ animation: bob 1.1s ease-in-out infinite alternate; }}
      .scan {{ animation: scan 5s linear infinite; }}
      .hud {{ font-family:"SF Mono","Cascadia Code",Consolas,monospace; font-size:13px;
              letter-spacing:2.5px; fill:#9FB6FF; }}
      .jp {{ font-family:"Yu Gothic","Meiryo","Microsoft YaHei",sans-serif; font-size:12px;
             letter-spacing:4px; fill:#7FE3FF; opacity:.55; }}
      @keyframes run {{ from {{ transform: translateX(0) }} to {{ transform: translateX({X1 - X0}px) }} }}
      @keyframes bob {{ from {{ transform: translateY(-2px) }} to {{ transform: translateY(2px) }} }}
      @keyframes scan {{ from {{ transform: translateY(0) }} to {{ transform: translateY({H}px) }} }}
      {''.join(keys)}
    </style>
  </defs>

  <rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="24"
        fill="url(#panel)" stroke="#ffffff" stroke-opacity="0.15"/>
  <rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="24" fill="url(#sheen)" opacity="0.7"/>
  {''.join(grid)}
  <g opacity="0.7">
    <circle cx="180" cy="96" r="1.6" fill="#7FE3FF"><animate attributeName="opacity" values="0.1;0.9;0.1" dur="3.2s" repeatCount="indefinite"/></circle>
    <circle cx="420" cy="72" r="1.4" fill="#FF7AD9"><animate attributeName="opacity" values="0.8;0.1;0.8" dur="2.6s" repeatCount="indefinite"/></circle>
    <circle cx="660" cy="104" r="1.8" fill="#A78BFA"><animate attributeName="opacity" values="0.2;1;0.2" dur="4.1s" repeatCount="indefinite"/></circle>
    <circle cx="880" cy="80" r="1.3" fill="#7FE3FF"><animate attributeName="opacity" values="0.9;0.15;0.9" dur="2.2s" repeatCount="indefinite"/></circle>
    <circle cx="990" cy="112" r="1.5" fill="#FFE9A8"><animate attributeName="opacity" values="0.15;0.85;0.15" dur="3.6s" repeatCount="indefinite"/></circle>
  </g>
  <rect x="-140" y="0" width="140" height="{H}" fill="url(#sweep)">
    <animate attributeName="x" values="-140;{W}" dur="6s" repeatCount="indefinite"/>
  </rect>
  <rect x="0" y="{LANE_Y + 30}" width="{W}" height="1.4" fill="#6C8CFF" opacity="0.5"/>
  <rect x="0" y="{LANE_Y + 30}" width="{W}" height="6" fill="#6C8CFF" opacity="0.12" filter="url(#gblur)"/>


  {''.join(dots)}

  <g class="pac-run">
    <g class="bob">
      <path d="{mouth_open}" fill="#FFB02E" opacity="0.55" filter="url(#pglow)" transform="translate({X0},{LANE_Y})">
        <animate attributeName="d" dur="0.42s" repeatCount="indefinite"
                 values="{mouth_open};{mouth_mid};{mouth_shut};{mouth_mid};{mouth_open}"/>
      </path>
      <path d="{mouth_open}" fill="url(#pacbody)" stroke="#FFF3C4" stroke-width="1.2" transform="translate({X0},{LANE_Y})">
        <animate attributeName="d" dur="0.42s" repeatCount="indefinite"
                 values="{mouth_open};{mouth_mid};{mouth_shut};{mouth_mid};{mouth_open}"/>
      </path>
      <circle cx="{X0 + R * 0.42}" cy="{LANE_Y - R * 0.55}" r="2.2" fill="#0A0F2C" opacity="0.8"/>
    </g>
  </g>


  <rect x="0" y="0" width="{W}" height="3" fill="#7FE3FF" opacity="0.0" class="scan"/>
</svg>
"""


def main() -> None:
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(root, "assets", "pacman.svg")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(build())
    print("wrote", out)


if __name__ == "__main__":
    main()
