#!/usr/bin/env python3
"""Draw a newspaper front page summing up 21 November 2026 world news.

Pure Python standard library only. Builds a 1024x1024 pixel buffer,
draws shapes and text with a hand-written 5x7 bitmap font encoded as
seven 5-bit rows per glyph, and encodes the PNG by hand with zlib and
struct. Deterministic: no randomness, no clock, no network, no files
read. Output goes to $MAKEFUN_OUTPUT_DIR/entry.png, else /output.
"""
import binascii
import os
import struct
import zlib

W = 1024
H = 1024
PAPER = (247, 243, 232)
INK = (18, 18, 18)
RED = (185, 28, 28)
ORANGE = (214, 96, 20)
DARK = (74, 74, 74)
WHITE = (255, 255, 255)
BLUE = (30, 64, 175)
LIGHT = (231, 225, 208)
GOLD = (176, 128, 28)
GREEN = (22, 101, 52)

# 5x7 bitmap font. Each glyph is a tuple of 7 row bitmasks, bit 4 = left.
FONT = {
    "A": (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "B": (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    "C": (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    "D": (0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    "E": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    "F": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    "G": (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    "H": (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "I": (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "J": (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    "K": (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    "L": (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    "M": (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    "N": (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    "O": (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "P": (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    "Q": (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    "R": (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    "S": (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    "T": (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    "U": (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "V": (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    "W": (0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11),
    "X": (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    "Y": (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    "Z": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    "0": (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    "1": (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "2": (0x0E, 0x11, 0x01, 0x06, 0x08, 0x10, 0x1F),
    "3": (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    "4": (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    "5": (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    "6": (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    "7": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    "8": (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    "9": (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    " ": (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00),
    ".": (0x00, 0x00, 0x00, 0x00, 0x00, 0x0C, 0x0C),
    ",": (0x00, 0x00, 0x00, 0x00, 0x0C, 0x04, 0x08),
    ":": (0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x0C, 0x00),
    ";": (0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x04, 0x08),
    "'": (0x04, 0x04, 0x08, 0x00, 0x00, 0x00, 0x00),
    '"': (0x0A, 0x0A, 0x00, 0x00, 0x00, 0x00, 0x00),
    "-": (0x00, 0x00, 0x00, 0x1F, 0x00, 0x00, 0x00),
    "(": (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ")": (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    "/": (0x01, 0x01, 0x02, 0x04, 0x08, 0x10, 0x10),
    "%": (0x19, 0x19, 0x02, 0x04, 0x08, 0x13, 0x13),
    "+": (0x00, 0x04, 0x04, 0x1F, 0x04, 0x04, 0x00),
    "=": (0x00, 0x00, 0x1F, 0x00, 0x1F, 0x00, 0x00),
    "?": (0x0E, 0x11, 0x01, 0x02, 0x04, 0x00, 0x04),
    "!": (0x04, 0x04, 0x04, 0x04, 0x04, 0x00, 0x04),
    "&": (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    "*": (0x00, 0x04, 0x15, 0x0E, 0x15, 0x04, 0x00),
}


class Canvas:
    def __init__(self):
        self.px = bytearray(PAPER * W * H)

    def put(self, x, y, color):
        if 0 <= x < W and 0 <= y < H:
            i = (y * W + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = color

    def fill(self, x0, y0, x1, y1, color):
        x0 = max(0, x0)
        y0 = max(0, y0)
        x1 = min(W, x1)
        y1 = min(H, y1)
        for y in range(y0, y1):
            base = (y * W + x0) * 3
            row = bytes(color) * (x1 - x0)
            self.px[base:base + len(row)] = row

    def hline(self, x0, x1, y, color, thick=1):
        for t in range(thick):
            self.fill(x0, y + t, x1, y + t + 1, color)

    def vline(self, x, y0, y1, color, thick=1):
        for t in range(thick):
            self.fill(x + t, y0, x + t + 1, y1, color)

    def frame(self, x0, y0, x1, y1, color, thick=2):
        self.hline(x0, x1, y0, color, thick)
        self.hline(x0, x1, y1 - thick, color, thick)
        self.vline(x0, y0, y1, color, thick)
        self.vline(x1 - thick, y0, y1, color, thick)

    def line(self, x0, y0, x1, y1, color):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.put(x0, y0, color)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, color):
        for y in range(cy - r, cy + r + 1):
            for x in range(cx - r, cx + r + 1):
                if (x - cx) * (x - cx) + (y - cy) * (y - cy) <= r * r:
                    self.put(x, y, color)

    def ring(self, cx, cy, r, color, thick=3):
        for y in range(cy - r - 1, cy + r + 2):
            for x in range(cx - r - 1, cx + r + 2):
                d2 = (x - cx) * (x - cx) + (y - cy) * (y - cy)
                if (r - thick) * (r - thick) <= d2 <= r * r:
                    self.put(x, y, color)

    def tri(self, ax, ay, bx, by, cx, cy, color):
        # Scanline-filled triangle.
        ys = sorted(((ax, ay), (bx, by), (cx, cy)), key=lambda p: p[1])
        (ax, ay), (bx, by), (cx, cy) = ys
        if ay == cy:
            return
        def edge(x0, y0, x1, y1, y):
            if y1 == y0:
                return x0
            return x0 + (x1 - x0) * (y - y0) / (y1 - y0)
        for y in range(ay, cy + 1):
            if y < by:
                xa = edge(ax, ay, bx, by, y)
                xb = edge(ax, ay, cx, cy, y)
            else:
                xa = edge(bx, by, cx, cy, y)
                xb = edge(ax, ay, cx, cy, y)
            lo, hi = (xa, xb) if xa <= xb else (xb, xa)
            self.fill(int(lo), y, int(hi) + 1, y + 1, color)


def text_w(s, scale):
    return len(s) * 6 * scale - scale


def draw_text(cv, x, y, s, scale, color):
    cx = x
    for ch in s.upper():
        glyph = FONT.get(ch, FONT["?"])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits & (1 << (4 - col)):
                    cv.fill(cx + col * scale, y + row * scale,
                            cx + (col + 1) * scale, y + (row + 1) * scale,
                            color)
        cx += 6 * scale
    return cx


def draw_centered(cv, cx, y, s, scale, color):
    draw_text(cv, cx - text_w(s, scale) // 2, y, s, scale, color)


def wrap(s, max_w, scale):
    words = s.split(" ")
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_w(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_para(cv, x, y, s, max_w, scale, color, leading=4):
    lines = wrap(s, max_w, scale)
    for ln in lines:
        draw_text(cv, x, y, ln, scale, color)
        y += 7 * scale + leading
    return y


# ---- pictograms, one per story ----

def burst(cv, cx, cy, r, color):
    # Jagged explosion star.
    import math
    pts = []
    spikes = 12
    for i in range(spikes * 2):
        ang = 3.14159265 * i / spikes
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + int(rr * math.cos(ang)),
                    cy + int(rr * math.sin(ang))))
    for i in range(len(pts)):
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % len(pts)]
        cv.tri(cx, cy, x0, y0, x1, y1, color)
    cv.disc(cx, cy, int(r * 0.30), WHITE)


def badge(cv, cx, cy, r, color):
    # Five-point police badge star.
    import math
    pts = []
    for i in range(10):
        ang = -1.5707963 + 3.14159265 * i / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + int(rr * math.cos(ang)),
                    cy + int(rr * math.sin(ang))))
    for i in range(len(pts)):
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % len(pts)]
        cv.tri(cx, cy, x0, y0, x1, y1, color)
    cv.disc(cx, cy, int(r * 0.32), PAPER)
    cv.disc(cx, cy, int(r * 0.18), color)


def globe(cv, cx, cy, r, color):
    cv.ring(cx, cy, r, color, 4)
    cv.line(cx - r, cy, cx + r, cy, color)
    cv.line(cx, cy - r, cx, cy + r, color)
    # Meridian arcs as short vertical chords.
    for dx in (-r // 2, r // 2):
        h = int((r * r - dx * dx) ** 0.5)
        cv.line(cx + dx, cy - h, cx + dx, cy + h, color)


def chart_down(cv, x0, y0, x1, y1, color):
    cv.vline(x0, y0, y1, INK, 3)
    cv.hline(x0, x1, y1, INK, 3)
    pts = [(x0 + 8, y0 + 10), (x0 + 34, y0 + 22), (x0 + 58, y0 + 16),
           (x0 + 84, y0 + 38), (x0 + 110, y0 + 30), (x0 + 136, y0 + 58)]
    for i in range(len(pts) - 1):
        ax, ay = pts[i]
        bx, by = pts[i + 1]
        cv.line(ax, ay, bx, by, color)
        cv.line(ax, ay + 1, bx, by + 1, color)
        cv.line(ax, ay + 2, bx, by + 2, color)
    ex, ey = pts[-1]
    cv.tri(ex, ey, ex - 14, ey - 4, ex - 4, ey + 12, color)


def shield(cv, cx, cy, r, color):
    cv.tri(cx - r, cy - r, cx + r, cy - r, cx, cy + r, color)
    cv.disc(cx, cy - r // 3, int(r * 0.55), PAPER)
    cv.line(cx - int(r * 0.28), cy - r // 3, cx - int(r * 0.05),
            cy + int(r * 0.12), WHITE)
    cv.line(cx - int(r * 0.05), cy + int(r * 0.12), cx + int(r * 0.35),
            cy - int(r * 0.45), WHITE)


def missile(cv, x0, y0, x1, y1, color):
    cv.line(x0, y0, x1, y1, color)
    cv.line(x0, y0 + 2, x1, y1 + 2, color)
    cv.tri(x1, y1 - 4, x1, y1 + 6, x1 + 16, y1 + 1, color)


def build():
    cv = Canvas()
    cv.frame(20, 20, 1004, 1004, INK, 3)

    # ---- masthead ----
    draw_centered(cv, 512, 42, "THE WORLD TODAY", 10, INK)
    cv.hline(40, 984, 124, INK, 4)
    draw_centered(cv, 512, 136, "SATURDAY, 21 NOVEMBER 2026", 3, RED)
    cv.hline(40, 984, 166, INK, 2)

    # ---- row 1, lead: Iran / Bahrain ----
    x = 40
    draw_text(cv, x, 196, "CONFLICT * MANAMA", 2, RED)
    burst(cv, 556, 236, 36, ORANGE)
    draw_text(cv, x, 222, "IRAN STRIKES US", 5, INK)
    draw_text(cv, x, 261, "BASES IN BAHRAIN", 5, INK)
    draw_para(cv, x, 312,
              "Iran says its Revolutionary Guards hit two US bases in "
              "Bahrain. Bahrain reports a fire at a civilian industrial "
              "site and no injuries.",
              536, 3, INK)
    cv.vline(600, 184, 492, INK, 2)

    # ---- row 1, right: Mexico capture ----
    x = 612
    draw_text(cv, x, 196, "JUSTICE * SINALOA", 2, RED)
    badge(cv, 880, 235, 28, BLUE)
    draw_text(cv, x, 222, "MEXICO", 4, INK)
    draw_text(cv, x, 254, "CAPTURES", 4, INK)
    draw_text(cv, x, 286, '"EL CHAPO', 4, INK)
    draw_text(cv, x, 318, 'ISIDRO"', 4, INK)
    draw_para(cv, x, 352,
              "FBI Top 10 fugitive Fausto Isidro Meza Flores seized in "
              "Sinaloa. Gunfights follow; 11 dead.",
              368, 3, INK)

    cv.hline(40, 984, 504, INK, 3)

    # ---- middle band: Kryvyi Rih ----
    draw_text(cv, 40, 524, "WAR * UKRAINE", 2, RED)
    draw_text(cv, 40, 546, "RUSSIAN MISSILE HITS", 4, INK)
    draw_text(cv, 40, 578, "ZELENSKYY'S HOMETOWN", 4, INK)
    missile(cv, 860, 596, 940, 580, RED)
    burst(cv, 962, 576, 16, ORANGE)
    draw_para(cv, 40, 618,
              "A ballistic strike on Kryvyi Rih kills 2 and wounds 60. "
              "Russian weapons also land in Poland.",
              944, 3, INK)

    cv.hline(40, 984, 684, INK, 3)

    # ---- bottom row: three stories ----
    boxes = [
        (28, "CLIMATE * ANTALYA", ("COP31 TALKS RUN", "INTO OVERTIME"),
         "The Antalya summit passes its deadline with no deal. "
         "Fossil fuels are missing from the draft."),
        (356, "MARKETS * NEW YORK", ("AI STOCKS", "SELL OFF"),
         "The S&P 500 falls 3.7% and the Nikkei 5.1% as the AI "
         "rally unwinds."),
        (684, "HEALTH * BRAZIL", ("DENGUE", "BREAKTHROUGH"),
         "Mosquitoes carrying bacteria cut dengue in children by "
         "69%, researchers report."),
    ]
    for bx, kicker, heads, body in boxes:
        cv.frame(bx, 696, bx + 312, 936, INK, 2)
        draw_text(cv, bx + 12, 712, kicker, 2, RED)
        y = 760
        for h in heads:
            draw_text(cv, bx + 12, y, h, 3, INK)
            y += 25
        draw_para(cv, bx + 12, 816, body, 288, 2, DARK)
    globe(cv, 300, 908, 20, BLUE)
    # Small falling chart in the markets box corner.
    cv.line(240, 726, 258, 736, RED)
    cv.line(258, 736, 276, 730, RED)
    cv.line(276, 730, 296, 750, RED)
    cv.line(240, 727, 258, 737, RED)
    cv.line(258, 737, 276, 731, RED)
    cv.line(276, 731, 296, 751, RED)
    shield(cv, 940, 742, 26, GREEN)

    # ---- footer ----
    cv.fill(28, 948, 996, 992, INK)
    draw_centered(cv, 512, 962, "21 NOV 2026 * SIX STORIES, ONE DAY", 2, WHITE)
    return cv


def chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", binascii.crc32(kind + data) & 0xFFFFFFFF)
    return out


def encode_png(cv):
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw += cv.px[y * W * 3:(y + 1) * W * 3]
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    return png


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    data = encode_png(build())
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print("wrote %s (%d bytes)" % (path, len(data)))


if __name__ == "__main__":
    main()
