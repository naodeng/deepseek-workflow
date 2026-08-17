#!/usr/bin/env python3
"""Generate the DeepSeek workflow icon (256x256 PNG) with pure Python.

Draws a rounded blue tile (DeepSeek brand blue gradient) with a simple white
whale mark, supersampled 4x and box-downsampled for smooth edges. No PIL needed.
"""

import struct
import zlib

SIZE = 256
SS = 4  # supersampling factor
W = H = SIZE * SS

# --- Colour helpers ---------------------------------------------------------
def blend(fg, bg, a):
    return tuple(round(fg[i] * a + bg[i] * (1 - a)) for i in range(3))

def lerp(a, b, t):
    return a + (b - a) * t

TOP = (93, 124, 255)     # #5D7CFF
BOTTOM = (58, 85, 250)   # #3A55FA
WHITE = (255, 255, 255)
DEEP = (24, 42, 130)     # dark blue for the eye

# --- Shape tests (coordinates in 256-space, scaled by SS) -------------------
def inside_rounded_rect(x, y, x0, y0, x1, y1, r):
    if x < x0 or x > x1 or y < y0 or y > y1:
        return False
    cx = min(max(x, x0 + r), x1 - r)
    cy = min(max(y, y0 + r), y1 - r)
    return (x - cx) ** 2 + (y - cy) ** 2 <= r * r

def inside_ellipse(x, y, cx, cy, rx, ry):
    return ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0

def sign(p1, p2, p3):
    return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])

def inside_triangle(x, y, a, b, c):
    d1 = sign((x, y), a, b)
    d2 = sign((x, y), b, c)
    d3 = sign((x, y), c, a)
    neg = d1 < 0 or d2 < 0 or d3 < 0
    pos = d1 > 0 or d2 > 0 or d3 > 0
    return not (neg and pos)

# --- Whale geometry (256-space) ---------------------------------------------
BODY = (152, 142, 72, 40)          # cx, cy, rx, ry
TAIL_UPPER = [(84, 128), (58, 90), (50, 124)]
TAIL_LOWER = [(84, 156), (58, 194), (50, 172)]
DORSAL = [(148, 102), (166, 62), (190, 98)]
EYE = (200, 134, 5.2)              # cx, cy, r

def inside_whale(x, y):
    if inside_ellipse(x, y, *BODY):
        return True
    if inside_triangle(x, y, *TAIL_UPPER) or inside_triangle(x, y, *TAIL_LOWER):
        return True
    return inside_triangle(x, y, *DORSAL)

def inside_eye(x, y):
    cx, cy, r = EYE
    return (x - cx) ** 2 + (y - cy) ** 2 <= r * r

# --- Render ------------------------------------------------------------------
canvas = [[(0, 0, 0, 0) for _ in range(W)] for _ in range(H)]

for py in range(H):
    y = py / SS
    t = y / SIZE  # 0..1 for gradient
    for px in range(W):
        x = px / SS
        if not inside_rounded_rect(x, y, 0, 0, SIZE, SIZE, 58):
            continue
        bg = (round(lerp(TOP[0], BOTTOM[0], t)),
              round(lerp(TOP[1], BOTTOM[1], t)),
              round(lerp(TOP[2], BOTTOM[2], t)))
        if inside_whale(x, y):
            colour = DEEP if inside_eye(x, y) else WHITE
            canvas[py][px] = colour + (255,)
        else:
            canvas[py][px] = bg + (255,)

# --- Box-downsample ----------------------------------------------------------
out = [[(0, 0, 0, 0) for _ in range(SIZE)] for _ in range(SIZE)]
for oy in range(SIZE):
    for ox in range(SIZE):
        rs = gs = bs = as_ = 0
        for dy in range(SS):
            for dx in range(SS):
                r, g, b, a = canvas[oy * SS + dy][ox * SS + dx]
                rs += r
                gs += g
                bs += b
                as_ += a
        n = SS * SS
        out[oy][ox] = (rs // n, gs // n, bs // n, as_ // n)

# --- Write PNG ---------------------------------------------------------------
def chunk(tag, data):
    return (struct.pack(">I", len(data)) + tag + data +
            struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))

raw = b""
for row in out:
    raw += b"\x00" + bytes(v for px in row for v in px)

png = (b"\x89PNG\r\n\x1a\n"
       + chunk(b"IHDR", struct.pack(">IIBBBBB", SIZE, SIZE, 8, 6, 0, 0, 0))
       + chunk(b"IDAT", zlib.compress(raw, 9))
       + chunk(b"IEND", b""))

with open("Workflow/icon.png", "wb") as handle:
    handle.write(png)
print("Wrote Workflow/icon.png", len(png), "bytes")
