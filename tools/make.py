#!/usr/bin/env python3
"""Draws the pictures for the organisation's landing page: banner, flow, divider, buttons.
Usage: make.py OUT_DIR
Everything is plain SVG with system fonts, so it renders the same when GitHub serves it as an image.
"""
import math
import random
import sys
from pathlib import Path

OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)

SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"

THEMES = {
    'light': dict(bg1='#f6f3ee', bg2='#dcd6cb', border='rgba(40,33,24,.14)', text='#1e1c19', muted='#645e55',
                  faint='rgba(40,33,24,.075)', accent='#c8431a', accent_text='#b13a15', surface='#fbfaf7',
                  pill='rgba(40,33,24,.2)', ok='#3d7a4f', shadow='.20'),
    'dark': dict(bg1='#34312c', bg2='#171614', border='rgba(255,255,255,.12)', text='#f3f0ea', muted='#b1aa9f',
                 faint='rgba(255,255,255,.055)', accent='#ff7a4d', accent_text='#ff7a4d', surface='#262421',
                 pill='rgba(255,255,255,.22)', ok='#79c08f', shadow='.45'),
}


def f(v):
    return f'{v:.1f}'.rstrip('0').rstrip('.')


def pts(points):
    return ' '.join(f'{f(x)},{f(y)}' for x, y in points)


# ---------------------------------------------------------------- the plate: a made-up town on its terrain
A, OX, OY, ZS = 252.0, 962.0, 92.0, 252.0
RW = 0.030  # half the river's width


def P(x, y, z=0.0):
    return (OX + (x - y) * A, OY + (x + y) * A * 0.5 - z * ZS)


def river_y(x):
    return 0.70 + 0.10 * math.sin(2.4 * x + 0.4) - 0.12 * x


def h(x, y):
    d = abs(y - river_y(x))
    v = min(1.0, max(0.0, (d - RW) / 0.13))
    v = v * v * (3 - 2 * v)
    hill = 0.115 * math.exp(-((x - 0.80) ** 2 + (y - 0.15) ** 2) / 0.05)
    knoll = 0.04 * math.exp(-((x - 0.08) ** 2 + (y - 0.38) ** 2) / 0.04)
    return (hill + knoll + 0.012 + 0.006 * math.sin(6 * x) * math.cos(5 * y)) * v


def drape(poly, eps=0.0015):
    out = []
    for x, y in poly:
        x, y = min(1, max(0, x)), min(1, max(0, y))
        out.append(P(x, y, h(x, y) + eps))
    return out


def ellipse(cx, cy, rx, ry, n=36, wob=0.0, seed=0):
    r = random.Random(seed)
    ph = r.random() * 6
    return [(cx + rx * (1 + wob * math.sin(3 * t + ph)) * math.cos(t), cy + ry * (1 + wob * math.cos(2 * t + ph)) * math.sin(t))
            for t in (2 * math.pi * i / n for i in range(n))]


def shade(rgb, k):
    return '#%02x%02x%02x' % tuple(max(0, min(255, round(c * k))) for c in rgb)


PARK = (0.25, 0.25, 0.115, 0.085)
WOOD = (0.82, 0.14, 0.17, 0.135)


def in_ellipse(x, y, e, grow=1.0):
    cx, cy, rx, ry = e
    return ((x - cx) / (rx * grow)) ** 2 + ((y - cy) / (ry * grow)) ** 2 < 1


def plate():
    rnd = random.Random(11)
    o = []
    T1, T2 = 0.03, 0.068
    # soft shadow under the slab
    o.append(f'<polygon points="{pts([P(0, 1, -T2), P(1, 1, -T2), P(1, 0, -T2), P(0, 0, -T2)])}" fill="#000" '
             f'opacity="SHADOW" filter="url(#blur)" transform="translate(0,22)"/>')
    # terrain, back to front
    N = 26
    land = (234, 228, 214)
    cells = []
    for i in range(N):
        for j in range(N):
            cells.append((i + j, i, j))
    cells.sort()
    g = []
    for _, i, j in cells:
        x0, y0, x1, y1 = i / N, j / N, (i + 1) / N, (j + 1) / N
        z = [h(x0, y0), h(x1, y0), h(x1, y1), h(x0, y1)]
        dzdx = ((z[1] + z[2]) - (z[0] + z[3])) / 2 * N
        dzdy = ((z[2] + z[3]) - (z[0] + z[1])) / 2 * N
        k = max(0.80, min(1.07, 1 + 0.55 * dzdx - 0.55 * dzdy))
        c = shade(land, k)
        q = [P(x0, y0, z[0]), P(x1, y0, z[1]), P(x1, y1, z[2]), P(x0, y1, z[3])]
        g.append(f'<polygon points="{pts(q)}" fill="{c}" stroke="{c}"/>')
    o.append('<g stroke-width=".7" stroke-linejoin="round">' + ''.join(g) + '</g>')
    # woods on the hill, a park with a pond, the river
    o.append(f'<polygon points="{pts(drape(ellipse(*WOOD, wob=0.10, seed=3)))}" fill="#c3d2a8" opacity=".92"/>')
    o.append(f'<polygon points="{pts(drape(ellipse(*PARK, wob=0.08, seed=5)))}" fill="#cbd9b3"/>')
    o.append(f'<polygon points="{pts(drape(ellipse(0.64, 0.92, 0.10, 0.05, wob=0.1, seed=8)))}" fill="#cbd9b3"/>')
    o.append(f'<polygon points="{pts(drape(ellipse(0.285, 0.265, 0.036, 0.026)))}" fill="#a9c6da"/>')
    xs = [i / 50 for i in range(51)]
    bank = [(x, river_y(x) - RW * (1 + 0.2 * math.sin(9 * x))) for x in xs] + \
           [(x, river_y(x) + RW * (1 + 0.2 * math.cos(7 * x))) for x in reversed(xs)]
    o.append(f'<polygon points="{pts([P(x, y, 0.001) for x, y in bank])}" fill="#a9c6da"/>')
    # contour lines on the hill
    cont = []
    for lev in (0.045, 0.07, 0.095):
        ring = []
        for i in range(60):
            t = 2 * math.pi * i / 60
            lo, hi = 0.0, 0.5
            for _ in range(22):  # the radius where the hill drops to this level, along this ray
                mid = (lo + hi) / 2
                if h(0.80 + mid * math.cos(t), 0.15 + mid * math.sin(t)) > lev:
                    lo = mid
                else:
                    hi = mid
            x, y = 0.80 + lo * math.cos(t), 0.15 + lo * math.sin(t)
            ring.append((x, y) if 0 <= x <= 1 and 0 <= y <= 1 else None)
        run = []
        for p in ring + [ring[0]]:
            if p is None:
                if len(run) > 1:
                    cont.append(run)
                run = []
            else:
                run.append(P(p[0], p[1], h(*p) + 0.002))
        if len(run) > 1:
            cont.append(run)
    o.append('<g fill="none" stroke="#8a8f6e" stroke-width=".9" opacity=".55">' +
             ''.join(f'<polyline points="{pts(c)}"/>' for c in cont) + '</g>')
    # streets between the blocks
    step, size = 0.1583, 0.125
    b0 = 0.03
    roads = []
    for k in range(1, 6):
        r = b0 + k * step - (step - size) / 2
        for line in ([(r, t) for t in xs], [(t, r) for t in xs]):
            run = []
            for x, y in line + [(None, None)]:  # streets stop at the woods
                if (x, y) == (None, None) or in_ellipse(x, y, WOOD, 0.93):
                    if len(run) > 1:
                        roads.append(run)
                    run = []
                else:
                    run.append(P(x, y, h(x, y) + 0.002))
    o.append('<g fill="none" stroke="#fbf9f4" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round">' +
             ''.join(f'<polyline points="{pts(r)}"/>' for r in roads) + '</g>')
    # the cut sides and the base slab
    left = [P(x, 1, h(x, 1)) for x in xs] + [P(1, 1, -T1), P(0, 1, -T1)]
    right = [P(1, y, h(1, y)) for y in xs] + [P(1, 1, -T1), P(1, 0, -T1)]
    o.append(f'<polygon points="{pts(left)}" fill="#d9d1c0"/><polygon points="{pts(right)}" fill="#bcb3a0"/>')
    o.append(f'<polygon points="{pts([P(0, 1, -T1), P(1, 1, -T1), P(1, 1, -T2), P(0, 1, -T2)])}" fill="#8f7c63"/>')
    o.append(f'<polygon points="{pts([P(1, 0, -T1), P(1, 1, -T1), P(1, 1, -T2), P(1, 0, -T2)])}" fill="#6f5f4a"/>')
    # buildings
    boxes = []
    for bi in range(6):
        for bj in range(6):
            x0, y0 = b0 + bi * step, b0 + bj * step
            kind = rnd.choice(['quad', 'quad', 'bars', 'court', 'mix'])
            g2 = 0.012
            fps = []
            if kind == 'quad':
                s = (size - g2) / 2
                fps = [(x0 + a * (s + g2), y0 + b * (s + g2), s, s) for a in (0, 1) for b in (0, 1)]
            elif kind == 'bars':
                s = (size - 2 * g2) / 3
                if rnd.random() < 0.5:
                    fps = [(x0 + a * (s + g2), y0, s, size) for a in range(3)]
                else:
                    fps = [(x0, y0 + a * (s + g2), size, s) for a in range(3)]
            elif kind == 'court':
                t = 0.032
                fps = [(x0, y0, size, t), (x0, y0 + size - t, size, t), (x0, y0 + t + g2 / 2, t, size - 2 * t - g2),
                       (x0 + size - t, y0 + t + g2 / 2, t, size - 2 * t - g2)]
            else:
                s = size * 0.58
                fps = [(x0, y0, s, s), (x0 + s + g2, y0, size - s - g2, s * 0.7), (x0, y0 + s + g2, s * 0.8, size - s - g2)]
            for fx, fy, w, d in fps:
                cx, cy = fx + w / 2, fy + d / 2
                if abs(cy - river_y(cx)) < RW + 0.035 + d / 2:
                    continue
                if in_ellipse(cx, cy, PARK, 1.12) or in_ellipse(cx, cy, WOOD, 0.95) or in_ellipse(cx, cy, (0.64, 0.92, 0.10, 0.05), 1.1):
                    continue
                if rnd.random() < 0.07:
                    continue
                hb = 0.022 + 0.035 * rnd.random() + 0.10 * math.exp(-((cx - 0.50) ** 2 + (cy - 0.42) ** 2) / 0.03) * (0.5 + 0.7 * rnd.random())
                boxes.append([fx, fy, fx + w, fy + d, hb])
    # three towers in the middle
    mid = sorted(boxes, key=lambda b: (b[0] + b[2] - 1.0) ** 2 + (b[1] + b[3] - 0.84) ** 2)[:9]
    for b in rnd.sample(mid, 3):
        b[4] = 0.17 + 0.07 * rnd.random()
    boxes.sort(key=lambda b: (b[0] + b[2] + b[1] + b[3]))
    pin = max(mid, key=lambda b: b[4])
    g = []
    for x0, y0, x1, y1, hb in boxes:
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        z0 = min(h(x0, y0), h(x1, y0), h(x1, y1), h(x0, y1))
        z1 = h(cx, cy) + hb
        delay = 0.15 + 1.1 * math.hypot(cx - 0.5, cy - 0.42)
        lf = [P(x0, y1, z0), P(x1, y1, z0), P(x1, y1, z1), P(x0, y1, z1)]
        rf = [P(x1, y0, z0), P(x1, y1, z0), P(x1, y1, z1), P(x1, y0, z1)]
        tp = [P(x0, y0, z1), P(x1, y0, z1), P(x1, y1, z1), P(x0, y1, z1)]
        g.append(f'<g class="b" style="animation-delay:{delay:.2f}s"><polygon points="{pts(lf)}" fill="#e6e1d6"/>'
                 f'<polygon points="{pts(rf)}" fill="#cac3b4"/><polygon points="{pts(tp)}" fill="#fdfcf9"/></g>')
    o.append('<g stroke="#8a8173" stroke-opacity=".5" stroke-width=".55" stroke-linejoin="round">' + ''.join(g) + '</g>')
    # the pin
    px, py = P((pin[0] + pin[2]) / 2, (pin[1] + pin[3]) / 2, h((pin[0] + pin[2]) / 2, (pin[1] + pin[3]) / 2) + pin[4])
    o.append(f'<g class="pin"><circle class="pulse" cx="{f(px)}" cy="{f(py - 20)}" r="8" fill="none" stroke="#d8481c" stroke-width="2"/>'
             f'<line x1="{f(px)}" y1="{f(py)}" x2="{f(px)}" y2="{f(py - 16)}" stroke="#7d2a10" stroke-width="1.6" stroke-linecap="round"/>'
             f'<circle cx="{f(px)}" cy="{f(py - 20)}" r="6.5" fill="#d8481c"/><circle cx="{f(px - 2)}" cy="{f(py - 22)}" r="2" fill="#fff" opacity=".55"/></g>')
    return '\n'.join(o)


def backdrop(w, hgt, centres, th, uid):
    """Rounded card with faint contour rings behind the content."""
    rings = []
    r = random.Random(4)
    for cx, cy, r0, r1, st in centres:
        ph1, ph2 = r.random() * 6, r.random() * 6
        R = r0
        while R < r1:
            p = []
            for i in range(90):
                t = 2 * math.pi * i / 90
                rr = R * (1 + 0.13 * math.sin(3 * t + ph1) + 0.07 * math.sin(5 * t + ph2))
                p.append((cx + rr * math.cos(t) * 1.25, cy + rr * math.sin(t)))
            rings.append(f'<polygon points="{pts(p)}"/>')
            R += st
    return (f'<defs><linearGradient id="bg{uid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{th["bg1"]}"/>'
            f'<stop offset="1" stop-color="{th["bg2"]}"/></linearGradient>'
            f'<clipPath id="card{uid}"><rect width="{w}" height="{hgt}" rx="22"/></clipPath>'
            f'<filter id="blur" x="-20%" y="-60%" width="140%" height="220%"><feGaussianBlur stdDeviation="13"/></filter></defs>'
            f'<rect width="{w}" height="{hgt}" rx="22" fill="url(#bg{uid})"/>'
            f'<g clip-path="url(#card{uid})" fill="none" stroke="{th["faint"]}" stroke-width="1.3">{"".join(rings)}</g>'
            f'<rect x=".5" y=".5" width="{w - 1}" height="{hgt - 1}" rx="21.5" fill="none" stroke="{th["border"]}"/>')


ICON = ('<g transform="translate(72,150) scale(1.0625)"><rect width="64" height="64" rx="14" fill="#ebe6dc"/>'
        '<path d="M8 44 22 30l8 6 12-14 14 14v12H8z" fill="#b4c69c"/>'
        '<path d="M8 44 22 30l8 6 12-14 14 14v4H8z" fill="none" stroke="#6f6559" stroke-width="1.5" stroke-linejoin="round"/>'
        '<rect x="8" y="48" width="48" height="6" fill="#b3a48e"/>'
        '<rect x="19" y="24" width="7" height="14" fill="#fbfaf6" stroke="#6f6559" stroke-width="1.2"/>'
        '<rect x="35" y="16" width="8" height="20" fill="#fbfaf6" stroke="#6f6559" stroke-width="1.2"/>'
        '<circle cx="45" cy="12" r="4" fill="#c8431a"/></g>')


def banner(name):
    th = THEMES[name]
    W, H = 1280, 420
    css = ('.b{animation:rise .7s cubic-bezier(.2,.8,.2,1) both}'
           '@keyframes rise{from{opacity:0;transform:translateY(-9px)}to{opacity:1;transform:none}}'
           '.pulse{transform-box:fill-box;transform-origin:center;animation:pulse 2.8s ease-out infinite}'
           '@keyframes pulse{0%{transform:scale(1);opacity:.75}70%,100%{transform:scale(3.4);opacity:0}}'
           '.pin{animation:rise .6s 1.1s both}'
           '@media (prefers-reduced-motion:reduce){.b,.pin,.pulse{animation:none}.pulse{opacity:0}}')
    pills = []
    x = 72
    for label, col in (('Free · no account', th['ok']), ('Runs in your browser', th['pill']), ('Open source', th['pill'])):
        w = round(len(label) * 8.1 + 34)
        tc = col if col == th['ok'] else th['text']
        pills.append(f'<rect x="{x}" y="332" width="{w}" height="34" rx="17" fill="none" stroke="{col}" stroke-width="1.4"/>'
                     f'<text x="{x + w / 2}" y="354.5" text-anchor="middle" font-family="{SANS}" font-size="14.5" font-weight="600" fill="{tc}">{label}</text>')
        x += w + 12
    body = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
        f'aria-label="Your Place: any place on Earth as a 3D model"><style>{css}</style>'
        + backdrop(W, H, [(1010, 250, 60, 520, 44), (150, 470, 50, 330, 40)], th, 'b')
        + f'<text x="72" y="116" font-family="{MONO}" font-size="16" letter-spacing="3.2" fill="{th["muted"]}">ANY ADDRESS · ANYWHERE ON EARTH</text>'
        + ICON
        + f'<text x="160" y="207" font-family="{SANS}" font-size="74" font-weight="800" letter-spacing="-1.5" fill="{th["text"]}">Your Place</text>'
        + f'<text x="72" y="265" font-family="{SANS}" font-size="27" font-weight="700" fill="{th["accent_text"]}">Any place on Earth as a 3D model</text>'
        + f'<text x="72" y="302" font-family="{MONO}" font-size="17.5" fill="{th["muted"]}">address → terrain → every building → poster · STL · 3MF</text>'
        + ''.join(pills)
        + plate().replace('SHADOW', th['shadow'])
        + '</svg>')
    (OUT / f'banner-{name}.svg').write_text(body)


FLOW = [
    ('Search', 'any address or place', '<circle cx="21" cy="21" r="12"/><path d="M30 30 41 41"/>'),
    ('Build', 'terrain and every building', '<path d="M24 5 41 14.5v19L24 43 7 33.5v-19z"/><path d="M7 14.5 24 24l17-9.5M24 24v19"/>'),
    ('Shape', 'area, relief, roads, water', '<path d="M7 13h34M7 24h34M7 35h34"/><circle cx="17" cy="13" r="4" fill="FILL"/>'
                                         '<circle cx="31" cy="24" r="4" fill="FILL"/><circle cx="14" cy="35" r="4" fill="FILL"/>'),
    ('Save', 'poster, STL or colour 3MF', '<path d="M24 7v23M14.5 21.5 24 31l9.5-9.5M8 40h32"/>'),
    ('Print', 'one piece or tiles', '<path d="M24 6 42 15 24 24 6 15z"/><path d="M6 23.5 24 32.5l18-9M6 32 24 41l18-9"/>'),
]


def flow(name):
    th = THEMES[name]
    W, H = 1280, 276
    css = ('.d{animation:run 1.1s linear infinite}@keyframes run{to{stroke-dashoffset:-14}}'
           '@media (prefers-reduced-motion:reduce){.d{animation:none}}')
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
         f'aria-label="From an address to your shelf: search, build, shape, save, print"><style>{css}</style>',
         backdrop(W, H, [(640, 330, 80, 760, 52)], th, 'f'),
         f'<text x="56" y="54" font-family="{MONO}" font-size="15" letter-spacing="3.2" fill="{th["muted"]}">FROM AN ADDRESS TO YOUR SHELF</text>']
    xs = [160 + i * 240 for i in range(5)]
    for i in range(4):
        col = th['accent'] if i == 3 else th['muted']
        o.append(f'<path class="d" d="M{xs[i] + 62} 130H{xs[i + 1] - 62}" stroke="{col}" stroke-width="4" stroke-linecap="round" stroke-dasharray="0 14" fill="none" opacity=".8"/>')
    for i, (label, sub, icon) in enumerate(FLOW):
        last = i == 4
        col = th['accent'] if last else th['text']
        o.append(f'<rect x="{xs[i] - 46}" y="84" width="92" height="92" rx="22" fill="{th["surface"]}" stroke="{th["accent"] if last else th["pill"]}" stroke-width="{2 if last else 1.4}"/>'
                 f'<g transform="translate({xs[i] - 24},106)" fill="none" stroke="{col}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">{icon.replace("FILL", th["surface"])}</g>'
                 f'<text x="{xs[i]}" y="212" text-anchor="middle" font-family="{SANS}" font-size="19" font-weight="700" fill="{th["text"]}">{label}</text>'
                 f'<text x="{xs[i]}" y="236" text-anchor="middle" font-family="{SANS}" font-size="14.5" fill="{th["muted"]}">{sub}</text>')
    o.append('</svg>')
    (OUT / f'flow-{name}.svg').write_text(''.join(o))


def divider():
    W, H = 1280, 30
    p = [(x, 15 + 5.5 * math.sin(x / 58) + 2.5 * math.sin(x / 21 + 1)) for x in range(8, W - 7, 8)]
    d = p[54]
    (OUT / 'divider.svg').write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" aria-hidden="true">'
        f'<polyline points="{pts(p)}" fill="none" stroke="#9a9388" stroke-width="1.6" stroke-dasharray="6 7" stroke-linecap="round"/>'
        f'<circle cx="{f(d[0])}" cy="{f(d[1])}" r="4.5" fill="#e0592b"/></svg>')


def button(file, label, primary=False):
    w = round(len(label) * 9.4 + 46)
    fill, text, stroke = ('#c8431a', '#ffffff', '#c8431a') if primary else ('#efeae0', '#1e1c19', '#cbc3b4')
    (OUT / file).write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} 44" width="{w}" height="44" role="img" aria-label="{label}">'
        f'<rect x=".75" y=".75" width="{w - 1.5}" height="42.5" rx="21.25" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'
        f'<text x="{w / 2}" y="28" text-anchor="middle" font-family="{SANS}" font-size="16.5" font-weight="650" fill="{text}">{label}</text></svg>')


for t in THEMES:
    banner(t)
    flow(t)
divider()
button('btn-open.svg', 'Open Your Place →', True)
button('btn-data.svg', 'Data layers')
button('btn-how.svg', 'How it works')
print('ok', sorted(p.name for p in OUT.iterdir()))
