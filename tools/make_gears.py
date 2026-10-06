#!/usr/bin/env python3
"""Generates src/gears.svg: the 'Never Stop' gear wall. Gears turn continuously; once per cycle every
gear returns to its home position and the pieces of the MAFCO logo they carry line up.
Tooth counts are all divisors of 72, so one cycle = 72 tooth-passes brings every gear home together."""
import math, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
M = 10.0                      # gear module: pitch radius = M * teeth / 2
W, H = 1200, 560
RED, DEEP, STEEL, DARK, SAND, MID = "#C21421", "#9A0E19", "#6E6A6A", "#3A3836", "#C3B59B", "#8D8886"

class Gear:
    def __init__(s, name, n, x, y, color, z, logo=True, dirn=1, phase=0.0):
        s.name, s.n, s.x, s.y, s.color, s.z, s.logo = name, n, x, y, color, z, logo
        s.r = M * n / 2; s.dir = dirn; s.phase = phase
    @property
    def k(s): return s.dir * 72 // s.n
    @property
    def root(s): return s.r - 1.25 * M

def mesh(a, name, n, alpha_deg, color, z=None, logo=True):
    """Place a new gear touching gear a, in the direction alpha, with teeth correctly interlocked."""
    al = math.radians(alpha_deg); rb = M * n / 2
    x, y = a.x + (a.r + rb) * math.cos(al), a.y + (a.r + rb) * math.sin(al)
    p = math.pi * M
    pb = al + math.pi - (a.r * (a.phase - al) - p / 2) / rb
    return Gear(name, n, x, y, color, a.z if z is None else z, logo, -a.dir, pb)

def teeth_path(g):
    n, r = g.n, g.r; ro, rt = r - 1.25 * M, r + 0.95 * M
    step = 2 * math.pi / n; pts = []
    for i in range(n):
        c = g.phase + i * step
        for ang, rad in [(-0.30, ro), (-0.21, r - 0.2 * M), (-0.10, rt), (0.10, rt), (0.21, r - 0.2 * M), (0.30, ro)]:
            a = c + ang * step
            pts.append((g.x + rad * math.cos(a), g.y + rad * math.sin(a)))
    return "M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + "Z"

def layout():
    G = []
    a = Gear("a", 36, 262, 296, RED, 0, phase=0.05); G.append(a)
    b = mesh(a, "b", 24, -13, DARK); G.append(b)
    c = mesh(b, "c", 36, 15, DEEP); G.append(c)
    d = mesh(c, "d", 24, -9, STEEL); G.append(d)
    # front layer, over the joints
    e = Gear("e", 24, 438, 412, STEEL, 1, dirn=-1, phase=0.2); G.append(e)
    f = mesh(e, "f", 18, -4, RED); G.append(f)
    g = Gear("g", 18, 420, 150, DEEP, 1, dirn=1, phase=0.1); G.append(g)
    h = Gear("h", 24, 668, 150, RED, 1, dirn=-1, phase=0.3); G.append(h)
    i = Gear("i", 18, 1012, 420, DARK, 1, dirn=1, phase=0.0); G.append(i)
    j = Gear("j", 18, 1000, 138, RED, 1, dirn=-1, phase=0.4); G.append(j)
    # top layer: two small gears sitting over the points where the big gears mesh
    G.append(Gear("q", 12, 437, 262, MID, 2, dirn=1, phase=0.15))
    G.append(Gear("r", 12, 1024, 281, MID, 2, dirn=-1, phase=0.35))
    # small gears with no logo piece, around the edges
    G.append(mesh(a, "k", 12, 118, SAND, logo=False))
    G.append(mesh(a, "l", 12, 212, MID, logo=False))
    G.append(mesh(d, "m", 12, 62, SAND, logo=False))
    G.append(mesh(g, "n", 12, 200, MID, z=1, logo=False))
    G.append(mesh(f, "o", 12, 40, SAND, z=1, logo=False))
    G.append(mesh(h, "p", 12, -35, MID, z=1, logo=False))
    return G

def logo_block():
    svg = (ROOT / "src/assets/mafco-logo-white.svg").read_text()
    paths = "".join(re.findall(r"<path [^>]*/>", svg))
    lw = 880; s = lw / 168; lh = 50.2 * s
    x0, y0 = (W - lw) / 2 + 6, (H - lh) / 2 - 4
    return f'<g id="gw-logo" transform="translate({x0:.1f} {y0:.1f}) scale({s:.4f}) translate(-37 -44.5)">{paths}</g>', (x0, y0, lw, lh)

def build():
    G = layout(); logo, box = logo_block()
    out = [f'<svg class="gearwall" viewBox="0 0 {W} {H}" role="img" aria-label="Turning gears that line up to spell MAFCO, since 1987">',
           f'<defs>{logo}' + "".join(f'<clipPath id="gw-c-{g.name}"><path d="{teeth_path(g)}"/></clipPath>' for g in G if g.logo) + '</defs>',
           f'<rect width="{W}" height="{H}" fill="#1D1D1B"/>']
    for z in (0, 1, 2):
        for g in [g for g in G if g.z == z]:
            d = teeth_path(g); st = f'style="--k:{g.k};transform-origin:{g.x:.1f}px {g.y:.1f}px"'
            if z >= 1:
                out.append(f'<g class="gw-g" {st}><path d="{d}" fill="#000" opacity=".22" transform="translate(3 5)"/></g>')
            frag = f'<g clip-path="url(#gw-c-{g.name})"><use href="#gw-logo"/></g>' if g.logo else f'<circle cx="{g.x:.1f}" cy="{g.y:.1f}" r="9" fill="#1D1D1B"/>'
            out.append(f'<g class="gw-g" {st}><path d="{d}" fill="{g.color}" />{frag}<path d="{d}" fill="none" stroke="#1D1D1B" stroke-opacity=".5" stroke-width="1.5"/></g>')
    out.append("</svg>")
    (ROOT / "src/gears.svg").write_text("\n".join(out))
    return G, box

if __name__ == "__main__":
    G, box = build()
    print("gears", len(G), "logo box", [round(v) for v in box])
    for g in G: print(g.name, g.n, round(g.x), round(g.y), "k", g.k)
