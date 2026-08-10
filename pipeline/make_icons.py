#!/usr/bin/env python3
"""Generate the PWA app icons with no third-party deps (no PIL on this machine).

A flat, on-brand mark: verdigris field, a paper "card" with three text lines — the app is a
reader. Pure-Python PNG encoding (zlib + the PNG chunk format). Outputs the sizes the manifest
and iOS need. Run: python3 pipeline/make_icons.py
"""
import os, zlib, struct

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
OUT = os.path.join(ROOT, 'app')

VERD = (47, 107, 99)      # #2F6B63
PAPER = (237, 237, 230)   # #EDEDE6
OCHRE = (200, 145, 47)    # #C8912F


def png(path, size, maskable=False):
    N = size
    # maskable icons need their content inside a ~80% safe circle, so shrink the card for those.
    pad = int(N * (0.20 if maskable else 0.16))
    card_x0, card_y0 = pad, int(N * (0.24 if maskable else 0.20))
    card_x1, card_y1 = N - pad, N - int(N * (0.24 if maskable else 0.20))
    radius = int(N * 0.06)

    def in_round_rect(x, y, x0, y0, x1, y1, r):
        if x < x0 or x > x1 or y < y0 or y > y1:
            return False
        if x < x0 + r and y < y0 + r: return (x - (x0 + r)) ** 2 + (y - (y0 + r)) ** 2 <= r * r
        if x > x1 - r and y < y0 + r: return (x - (x1 - r)) ** 2 + (y - (y0 + r)) ** 2 <= r * r
        if x < x0 + r and y > y1 - r: return (x - (x0 + r)) ** 2 + (y - (y1 - r)) ** 2 <= r * r
        if x > x1 - r and y > y1 - r: return (x - (x1 - r)) ** 2 + (y - (y1 - r)) ** 2 <= r * r
        return True

    # three text lines inside the card
    lines = []
    inner_l = card_x0 + int((card_x1 - card_x0) * 0.14)
    inner_r = card_x1 - int((card_x1 - card_x0) * 0.14)
    th = max(2, int(N * 0.035))
    gap = int((card_y1 - card_y0) * 0.20)
    ys = card_y0 + int((card_y1 - card_y0) * 0.26)
    widths = [1.0, 0.82, 0.55]
    for i, w in enumerate(widths):
        y = ys + i * (th + gap)
        lines.append((inner_l, y, inner_l + int((inner_r - inner_l) * w), y + th, i == 0))

    raw = bytearray()
    for y in range(N):
        raw.append(0)                                   # filter byte per scanline
        for x in range(N):
            r, g, b = VERD
            if in_round_rect(x, y, card_x0, card_y0, card_x1, card_y1, radius):
                r, g, b = PAPER
                for lx0, ly0, lx1, ly1, accent in lines:
                    if lx0 <= x <= lx1 and ly0 <= y <= ly1:
                        r, g, b = (OCHRE if accent else VERD)
            raw += bytes((r, g, b))

    def chunk(typ, data):
        c = struct.pack('>I', len(data)) + typ + data
        return c + struct.pack('>I', zlib.crc32(typ + data) & 0xffffffff)

    sig = b'\x89PNG\r\n\x1a\n'
    ihdr = struct.pack('>IIBBBBB', N, N, 8, 2, 0, 0, 0)   # 8-bit truecolor RGB
    idat = zlib.compress(bytes(raw), 9)
    with open(path, 'wb') as f:
        f.write(sig + chunk(b'IHDR', ihdr) + chunk(b'IDAT', idat) + chunk(b'IEND', b''))
    print('wrote', os.path.relpath(path, ROOT), size, 'x', size)


if __name__ == '__main__':
    png(os.path.join(OUT, 'icon-192.png'), 192, maskable=True)
    png(os.path.join(OUT, 'icon-512.png'), 512, maskable=True)
    png(os.path.join(OUT, 'apple-touch-icon.png'), 180, maskable=False)
